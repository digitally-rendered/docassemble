#!/bin/bash
# Docassemble YAML File Watcher for Development
# Monitors YAML files and automatically reloads when changes are detected

WATCH_DIR="/usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/data/questions"
WSGI_FILE="/usr/share/docassemble/webapp/docassemble.wsgi"
REDIS_HOST="${REDIS:-redis://docassemble-redis:6379}"

# Extract just the host from Redis URL
REDIS_HOST_ONLY=$(echo $REDIS_HOST | sed 's|redis://||' | cut -d: -f1)

echo "📁 Watching for YAML changes in: $WATCH_DIR"
echo "🔄 Will reload via: $WSGI_FILE"
echo "📦 Redis host: $REDIS_HOST_ONLY"

# Install inotify-tools if not present
if ! command -v inotifywait &> /dev/null; then
    echo "📥 Installing inotify-tools..."
    apt-get update && apt-get install -y inotify-tools
fi

# Main watch loop
if command -v inotifywait &> /dev/null; then
    echo "✅ Using inotifywait for file monitoring"
    
    # Use a simpler approach - monitor and react
    inotifywait -m -r -e modify,create,delete,move "$WATCH_DIR" \
        --format '%w%f %e' \
        --include '\.yml$' |
    while read file event; do
        echo "🔄 YAML file changed: $file ($event) at $(date)"
        
        # Debounce - wait a bit to collect rapid changes
        sleep 2
        
        # Clear Python cache
        find /usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/__pycache__ -name "*.pyc" -delete 2>/dev/null
        find /usr/share/docassemble/webapp/__pycache__ -name "*.pyc" -delete 2>/dev/null
        
        # Clear Redis cache
        redis-cli -h "$REDIS_HOST_ONLY" FLUSHALL > /dev/null 2>&1
        
        # Touch WSGI file to trigger reload
        touch "$WSGI_FILE"
        
        echo "✅ Reload triggered"
    done
else
    echo "⚠️  inotifywait not available, using polling mode"
    
    # Fallback polling mode
    LAST_MODIFIED=""
    
    while true; do
        CURRENT_MODIFIED=$(find "$WATCH_DIR" -name "*.yml" -type f -exec stat -c %Y {} \; 2>/dev/null | sort -n | tail -1)
        
        if [ "$CURRENT_MODIFIED" != "$LAST_MODIFIED" ] && [ ! -z "$CURRENT_MODIFIED" ]; then
            echo "🔄 YAML files changed at $(date)"
            
            # Clear caches and reload
            find /usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/__pycache__ -name "*.pyc" -delete 2>/dev/null
            redis-cli -h "$REDIS_HOST_ONLY" FLUSHALL > /dev/null 2>&1
            touch "$WSGI_FILE"
            
            echo "✅ Reload triggered"
            LAST_MODIFIED="$CURRENT_MODIFIED"
        fi
        
        sleep 5
    done
fi