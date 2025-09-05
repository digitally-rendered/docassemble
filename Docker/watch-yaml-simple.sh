#!/bin/bash
# Simple and robust YAML file watcher for Docassemble
# This version focuses on reliability over complexity

echo "Starting simple YAML file watcher..."

# Configuration
WATCH_DIR="${YAML_WATCH_DIR:-/usr/share/docassemble/files/questions}"
WSGI_FILE="/usr/share/docassemble/webapp/docassemble.wsgi"
CHECK_INTERVAL="${YAML_CHECK_INTERVAL:-3}"

# Ensure watch directory exists
if [ ! -d "$WATCH_DIR" ]; then
    echo "Watch directory does not exist: $WATCH_DIR"
    echo "Waiting for it to be created..."
    while [ ! -d "$WATCH_DIR" ]; do
        sleep 10
    done
fi

echo "Watching directory: $WATCH_DIR"
echo "Check interval: ${CHECK_INTERVAL} seconds"
echo "WSGI file: $WSGI_FILE"

# Function to trigger reload
trigger_reload() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Triggering reload..."
    
    # Touch WSGI file to trigger Apache/mod_wsgi reload
    if [ -f "$WSGI_FILE" ]; then
        touch "$WSGI_FILE"
        echo "  - Touched WSGI file"
    fi
    
    # Try to restart uwsgi if it's running
    if supervisorctl status uwsgi > /dev/null 2>&1; then
        supervisorctl restart uwsgi > /dev/null 2>&1
        echo "  - Restarted uwsgi"
    fi
    
    # Try to reload nginx if it's running
    if [ -f /var/run/nginx.pid ]; then
        nginx -s reload > /dev/null 2>&1
        echo "  - Reloaded nginx"
    fi
    
    echo "  - Reload complete"
}

# Main loop using simple modification time checking
echo "Starting watch loop..."
LAST_CHECK=""

while true; do
    # Get the most recent modification time of any YAML file
    if [ -d "$WATCH_DIR" ]; then
        CURRENT_CHECK=$(find "$WATCH_DIR" -name "*.yml" -o -name "*.yaml" 2>/dev/null | \
                        xargs -r stat -c %Y 2>/dev/null | \
                        sort -n 2>/dev/null | \
                        tail -1 2>/dev/null)
        
        # Check if there were any changes
        if [ ! -z "$CURRENT_CHECK" ] && [ "$CURRENT_CHECK" != "$LAST_CHECK" ]; then
            if [ ! -z "$LAST_CHECK" ]; then
                # This is not the first run, so files have changed
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] YAML files changed"
                trigger_reload
            fi
            LAST_CHECK="$CURRENT_CHECK"
        fi
    fi
    
    # Wait before next check
    sleep "$CHECK_INTERVAL"
done