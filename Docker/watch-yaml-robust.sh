#!/bin/bash
# Robust YAML file watcher for Docassemble with startup delay and path detection

echo "[YAML-WATCHER] Starting robust YAML file watcher..."

# Wait for system to stabilize after container start
STARTUP_DELAY="${YAML_STARTUP_DELAY:-30}"
echo "[YAML-WATCHER] Waiting ${STARTUP_DELAY} seconds for system initialization..."
sleep "$STARTUP_DELAY"

# Try multiple possible watch directories
POSSIBLE_DIRS=(
    "/usr/share/docassemble/files/questions"
    "/usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/data/questions"
    "/usr/share/docassemble/webapp/docassemble_webapp/docassemble/webapp/data/questions"
    "/tmp/files/questions"
)

WATCH_DIR=""
for dir in "${POSSIBLE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        WATCH_DIR="$dir"
        echo "[YAML-WATCHER] Found questions directory: $WATCH_DIR"
        break
    fi
done

# If no directory found, wait and try to create the expected one
if [ -z "$WATCH_DIR" ]; then
    WATCH_DIR="/usr/share/docassemble/files/questions"
    echo "[YAML-WATCHER] No questions directory found, will watch: $WATCH_DIR when it's created"
    mkdir -p "$WATCH_DIR"
    chown -R www-data:www-data /usr/share/docassemble/files 2>/dev/null || true
fi

# Configuration
WSGI_FILE="/usr/share/docassemble/webapp/docassemble.wsgi"
CHECK_INTERVAL="${YAML_CHECK_INTERVAL:-3}"
DEBOUNCE_DELAY="${YAML_DEBOUNCE_DELAY:-2}"

echo "[YAML-WATCHER] Configuration:"
echo "  Watch directory: $WATCH_DIR"
echo "  WSGI file: $WSGI_FILE"
echo "  Check interval: ${CHECK_INTERVAL}s"
echo "  Debounce delay: ${DEBOUNCE_DELAY}s"

# Create WSGI file if it doesn't exist
if [ ! -f "$WSGI_FILE" ]; then
    echo "[YAML-WATCHER] Creating missing WSGI file..."
    echo "from docassemble.webapp.run import application" > "$WSGI_FILE"
    chown www-data:www-data "$WSGI_FILE"
    chmod 644 "$WSGI_FILE"
fi

# Function to trigger reload
trigger_reload() {
    echo "[YAML-WATCHER] $(date '+%Y-%m-%d %H:%M:%S') - Changes detected, triggering reload..."
    
    # Clear Python cache
    find /usr/share/docassemble -name "*.pyc" -delete 2>/dev/null
    find /usr/share/docassemble -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    
    # Touch WSGI file
    if [ -f "$WSGI_FILE" ]; then
        touch "$WSGI_FILE"
        echo "[YAML-WATCHER]   - Touched WSGI file"
    fi
    
    # Restart services based on what's running
    if pgrep -x "uwsgi" > /dev/null; then
        # Try supervisor first
        if command -v supervisorctl > /dev/null 2>&1; then
            supervisorctl restart uwsgi 2>/dev/null && echo "[YAML-WATCHER]   - Restarted uwsgi via supervisor"
        else
            # Direct signal to uwsgi
            killall -HUP uwsgi 2>/dev/null && echo "[YAML-WATCHER]   - Sent HUP to uwsgi"
        fi
    fi
    
    # Reload nginx if running
    if [ -f /var/run/nginx.pid ]; then
        nginx -s reload 2>/dev/null && echo "[YAML-WATCHER]   - Reloaded nginx"
    fi
    
    # Reload Apache if running
    if [ -f /var/run/apache2/apache2.pid ]; then
        apache2ctl graceful 2>/dev/null && echo "[YAML-WATCHER]   - Reloaded Apache"
    fi
    
    echo "[YAML-WATCHER]   - Reload complete"
}

# Check if inotifywait is available and the filesystem supports it
USE_INOTIFY=false
if command -v inotifywait > /dev/null 2>&1; then
    # Test if inotify works on the watch directory
    timeout 2 inotifywait -t 1 "$WATCH_DIR" > /dev/null 2>&1
    if [ $? -eq 0 ] || [ $? -eq 2 ]; then
        USE_INOTIFY=true
        echo "[YAML-WATCHER] Using inotify for file monitoring"
    else
        echo "[YAML-WATCHER] inotify not supported on this filesystem, using polling"
    fi
else
    echo "[YAML-WATCHER] inotifywait not available, using polling"
fi

# Main watch loop
if [ "$USE_INOTIFY" = true ]; then
    # inotify mode with debouncing
    LAST_EVENT_TIME=0
    
    while true; do
        # Wait for directory to exist
        while [ ! -d "$WATCH_DIR" ]; do
            echo "[YAML-WATCHER] Waiting for directory: $WATCH_DIR"
            sleep 10
        done
        
        # Watch for changes
        inotifywait -m -r -e modify,create,delete,move,close_write "$WATCH_DIR" \
            --format '%w%f %e %T' --timefmt '%s' \
            --include '\.(yml|yaml)$' 2>/dev/null |
        while IFS=' ' read file event timestamp; do
            CURRENT_TIME=$(date +%s)
            TIME_DIFF=$((CURRENT_TIME - LAST_EVENT_TIME))
            
            # Debounce: only trigger if enough time has passed since last event
            if [ $TIME_DIFF -ge $DEBOUNCE_DELAY ]; then
                echo "[YAML-WATCHER] File changed: $file ($event)"
                trigger_reload
                LAST_EVENT_TIME=$CURRENT_TIME
            fi
        done
        
        # If inotifywait exits, restart it
        echo "[YAML-WATCHER] inotifywait exited, restarting in 5 seconds..."
        sleep 5
    done
else
    # Polling mode
    echo "[YAML-WATCHER] Starting polling mode..."
    LAST_HASH=""
    
    while true; do
        # Wait for directory to exist
        while [ ! -d "$WATCH_DIR" ]; do
            echo "[YAML-WATCHER] Waiting for directory: $WATCH_DIR"
            sleep 10
        done
        
        # Calculate hash of all YAML files
        CURRENT_HASH=$(find "$WATCH_DIR" \( -name "*.yml" -o -name "*.yaml" \) -type f 2>/dev/null | \
                       xargs -r stat -c "%Y %s %n" 2>/dev/null | \
                       md5sum 2>/dev/null | \
                       cut -d' ' -f1)
        
        # Check if hash changed
        if [ ! -z "$CURRENT_HASH" ] && [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
            if [ ! -z "$LAST_HASH" ]; then
                # Not the first run, files have changed
                echo "[YAML-WATCHER] YAML files changed (hash: ${CURRENT_HASH:0:8}...)"
                trigger_reload
                
                # Extra delay after reload to let system stabilize
                sleep "$DEBOUNCE_DELAY"
            fi
            LAST_HASH="$CURRENT_HASH"
        fi
        
        # Wait before next check
        sleep "$CHECK_INTERVAL"
    done
fi