#!/bin/bash
# Watch for YAML file changes and reload docassemble

WATCH_DIR="/usr/share/docassemble/local3.12/lib/python3.12/site-packages/docassemble/webapp/data/questions"
WSGI_FILE="/usr/share/docassemble/webapp/docassemble.wsgi"

echo "Watching for YAML changes in $WATCH_DIR"

# Use inotifywait if available, otherwise use a simple polling loop
if command -v inotifywait &> /dev/null; then
    while true; do
        inotifywait -r -e modify,create,delete,move "$WATCH_DIR" --include '.*\.yml$'
        echo "YAML file changed, triggering reload..."
        touch "$WSGI_FILE"
        redis-cli -h docassemble-redis FLUSHALL > /dev/null
        echo "Reload triggered at $(date)"
    done
else
    # Fallback to polling if inotifywait is not available
    echo "inotifywait not found, using polling mode..."
    
    # Store initial state
    find "$WATCH_DIR" -name "*.yml" -type f -exec stat -c "%Y %n" {} \; > /tmp/yaml_state.txt
    
    while true; do
        sleep 5
        find "$WATCH_DIR" -name "*.yml" -type f -exec stat -c "%Y %n" {} \; > /tmp/yaml_state_new.txt
        
        if ! diff -q /tmp/yaml_state.txt /tmp/yaml_state_new.txt > /dev/null 2>&1; then
            echo "YAML files changed, triggering reload..."
            touch "$WSGI_FILE"
            redis-cli -h docassemble-redis FLUSHALL > /dev/null
            echo "Reload triggered at $(date)"
            mv /tmp/yaml_state_new.txt /tmp/yaml_state.txt
        fi
    done
fi