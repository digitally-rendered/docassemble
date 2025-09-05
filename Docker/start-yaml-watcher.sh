#!/bin/bash
# Script to start the YAML watcher after system is fully initialized

echo "[START-YAML-WATCHER] Checking system readiness..."

# Wait for key services to be running
MAX_WAIT=120
WAITED=0

# Check if uwsgi or apache is running
while [ $WAITED -lt $MAX_WAIT ]; do
    if supervisorctl status uwsgi 2>/dev/null | grep -q RUNNING || \
       supervisorctl status apache2 2>/dev/null | grep -q RUNNING || \
       [ -f /var/run/apache2/apache2.pid ] || \
       pgrep -x uwsgi > /dev/null; then
        echo "[START-YAML-WATCHER] Web server is running"
        break
    fi
    echo "[START-YAML-WATCHER] Waiting for web server to start... ($WAITED/$MAX_WAIT)"
    sleep 5
    WAITED=$((WAITED + 5))
done

# Ensure the watch script exists
if [ ! -f /usr/share/docassemble/scripts/watch-yaml-changes.sh ]; then
    echo "[START-YAML-WATCHER] Creating watch script..."
    mkdir -p /usr/share/docassemble/scripts
    
    # Try to copy from various locations
    if [ -f /usr/share/docassemble/webapp/watch-yaml-robust.sh ]; then
        cp /usr/share/docassemble/webapp/watch-yaml-robust.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    elif [ -f /tmp/Docker/watch-yaml-robust.sh ]; then
        cp /tmp/Docker/watch-yaml-robust.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    elif [ -f /usr/share/docassemble/webapp/watch-yaml-simple.sh ]; then
        cp /usr/share/docassemble/webapp/watch-yaml-simple.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    else
        # Create inline script as fallback
        cat > /usr/share/docassemble/scripts/watch-yaml-changes.sh << 'WATCHSCRIPT'
#!/bin/bash
echo "[YAML-WATCHER] Starting fallback watcher..."
WATCH_DIR="/usr/share/docassemble/files/questions"
WSGI_FILE="/usr/share/docassemble/webapp/docassemble.wsgi"

# Wait for directory
while [ ! -d "$WATCH_DIR" ]; do
    mkdir -p "$WATCH_DIR"
    sleep 10
done

echo "[YAML-WATCHER] Watching: $WATCH_DIR"
LAST=""

while true; do
    CURRENT=$(find "$WATCH_DIR" -name "*.yml" -o -name "*.yaml" 2>/dev/null | \
              xargs -r stat -c "%Y" 2>/dev/null | sort -n | tail -1)
    if [ "$CURRENT" != "$LAST" ] && [ ! -z "$CURRENT" ] && [ ! -z "$LAST" ]; then
        echo "[YAML-WATCHER] Changes detected"
        touch "$WSGI_FILE"
        supervisorctl restart uwsgi 2>/dev/null || true
    fi
    LAST="$CURRENT"
    sleep 3
done
WATCHSCRIPT
    fi
    
    chmod +x /usr/share/docassemble/scripts/watch-yaml-changes.sh
    chown www-data:www-data /usr/share/docassemble/scripts/watch-yaml-changes.sh
fi

# Start the yaml watcher via supervisor
echo "[START-YAML-WATCHER] Starting YAML watcher service..."
supervisorctl start yamlwatcher

# Check if it started successfully
sleep 5
if supervisorctl status yamlwatcher 2>/dev/null | grep -q RUNNING; then
    echo "[START-YAML-WATCHER] YAML watcher started successfully"
else
    echo "[START-YAML-WATCHER] Failed to start YAML watcher, checking logs..."
    supervisorctl tail -100 yamlwatcher stderr
fi