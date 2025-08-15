#!/bin/bash
# Docassemble YAML File Watcher for Development
# Monitors YAML files and automatically reloads when changes are detected
# Uses polling mode for compatibility with Docker volume mounts on macOS

WATCH_DIR="/usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/data/questions"
WSGI_FILE="/usr/share/docassemble/webapp/docassemble.wsgi"
REDIS_HOST="${REDIS:-redis://docassemble-redis:6379}"

# Extract just the host from Redis URL
REDIS_HOST_ONLY=$(echo $REDIS_HOST | sed 's|redis://||' | cut -d: -f1)

echo "📁 Watching for YAML changes in: $WATCH_DIR"
echo "🔄 Will reload via: $WSGI_FILE"
echo "📦 Redis host: $REDIS_HOST_ONLY"

# For Docker volume mounts (especially on macOS), polling is more reliable
echo "🔍 Using polling mode for file monitoring (Docker volume mount compatible)"

# Track file modification times
declare -A file_mtimes

# Initialize with current state
while IFS= read -r -d '' file; do
    mtime=$(stat -c %Y "$file" 2>/dev/null)
    file_mtimes["$file"]=$mtime
done < <(find "$WATCH_DIR" -name "*.yml" -type f -print0)

echo "📊 Monitoring ${#file_mtimes[@]} YAML files"

# Main polling loop
while true; do
    changed=false
    
    # Check all YAML files for changes
    while IFS= read -r -d '' file; do
        current_mtime=$(stat -c %Y "$file" 2>/dev/null)
        
        # Check if file is new or modified
        if [[ -z "${file_mtimes[$file]}" ]] || [[ "${file_mtimes[$file]}" != "$current_mtime" ]]; then
            echo "🔄 YAML file changed: $file at $(date)"
            file_mtimes["$file"]=$current_mtime
            changed=true
        fi
    done < <(find "$WATCH_DIR" -name "*.yml" -type f -print0)
    
    # Check for deleted files
    for file in "${!file_mtimes[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "🗑️ YAML file deleted: $file at $(date)"
            unset file_mtimes["$file"]
            changed=true
        fi
    done
    
    # If changes detected, trigger reload
    if [[ "$changed" == "true" ]]; then
        echo "🔧 Processing changes..."
        
        # Clear Python cache
        find /usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/__pycache__ -name "*.pyc" -delete 2>/dev/null
        find /usr/share/docassemble/webapp/__pycache__ -name "*.pyc" -delete 2>/dev/null
        
        # Clear Redis cache
        redis-cli -h "$REDIS_HOST_ONLY" FLUSHALL > /dev/null 2>&1
        
        # Touch WSGI file to trigger reload
        touch "$WSGI_FILE"
        
        # Also send reload signal to uwsgi via supervisor
        supervisorctl restart uwsgi > /dev/null 2>&1 || true
        
        # Clear docassemble's internal cache
        python -c "
import sys
sys.path.insert(0, '/usr/share/docassemble/local3.12/lib/python3.12/site-packages')
from docassemble.base.functions import clear_cache
clear_cache()
print('Cache cleared')
" 2>/dev/null || true
        
        echo "✅ Reload triggered"
        
        # Wait before next check to allow system to stabilize
        sleep 3
    else
        # No changes, short sleep before next check
        sleep 2
    fi
done