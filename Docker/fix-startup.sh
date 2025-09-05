#!/bin/bash
# Fix startup issues for Docassemble container

echo "Fixing Docassemble startup files..."

# 1. Create/fix the WSGI file
echo "Checking for WSGI file..."
if [ ! -f /usr/share/docassemble/webapp/docassemble.wsgi ] || [ ! -s /usr/share/docassemble/webapp/docassemble.wsgi ]; then
    echo "Creating/fixing WSGI file..."
    if [ -f /usr/share/docassemble/webapp/docassemble_webapp/docassemble.wsgi ]; then
        # Copy from nested location if it exists
        cp /usr/share/docassemble/webapp/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/docassemble.wsgi
        echo "WSGI file copied from nested location"
    else
        # Create it from scratch
        echo "from docassemble.webapp.run import application" > /usr/share/docassemble/webapp/docassemble.wsgi
        echo "WSGI file created from scratch"
    fi
    chown www-data:www-data /usr/share/docassemble/webapp/docassemble.wsgi
    chmod 644 /usr/share/docassemble/webapp/docassemble.wsgi
    echo "WSGI file permissions set"
else
    echo "WSGI file already exists"
fi

# 2. Create/fix the .pypirc file
echo "Checking for PyPI configuration..."
mkdir -p /var/www
if [ ! -f /var/www/.pypirc ]; then
    echo "Creating missing .pypirc file..."
    touch /var/www/.pypirc
    chown www-data:www-data /var/www/.pypirc
    chmod 600 /var/www/.pypirc
    echo "PyPI RC file created and permissions set"
else
    echo "PyPI RC file already exists"
fi

# 3. Ensure /var/www directory has proper ownership
chown www-data:www-data /var/www

# 4. Create necessary directories if they don't exist
echo "Ensuring required directories exist..."
mkdir -p /usr/share/docassemble/log
mkdir -p /usr/share/docassemble/files
mkdir -p /var/run/docassemble
mkdir -p /var/log/apache2
mkdir -p /var/log/nginx

# 5. Fix permissions on key directories
echo "Setting directory permissions..."
chown -R www-data:www-data /usr/share/docassemble/log 2>/dev/null || true
chown -R www-data:www-data /usr/share/docassemble/files 2>/dev/null || true
chown www-data:www-data /var/log/apache2 2>/dev/null || true
chown www-data:www-data /var/log/nginx 2>/dev/null || true

# 6. Set up YAML watcher for auto-reload
echo "Setting up YAML watcher for auto-reload..."

# Check if inotify-tools is installed
if ! command -v inotifywait &> /dev/null; then
    echo "Installing inotify-tools for file watching..."
    apt-get update > /dev/null 2>&1
    apt-get install -y inotify-tools > /dev/null 2>&1
    echo "inotify-tools installed"
fi

# Copy the watch script (prefer robust version)
echo "Setting up watch-yaml-changes script..."
mkdir -p /usr/share/docassemble/scripts

# Try to use the robust version first
if [ -f /tmp/Docker/watch-yaml-robust.sh ]; then
    cp /tmp/Docker/watch-yaml-robust.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    echo "Using robust yaml watcher"
elif [ -f /usr/share/docassemble/webapp/watch-yaml-robust.sh ]; then
    cp /usr/share/docassemble/webapp/watch-yaml-robust.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    echo "Using robust yaml watcher from webapp"
elif [ -f /tmp/Docker/watch-yaml-simple.sh ]; then
    cp /tmp/Docker/watch-yaml-simple.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    echo "Using simple yaml watcher"
elif [ -f /tmp/Docker/watch-yaml-changes-fixed.sh ]; then
    cp /tmp/Docker/watch-yaml-changes-fixed.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    echo "Using fixed yaml watcher"
elif [ -f /tmp/Docker/watch-yaml-changes.sh ]; then
    cp /tmp/Docker/watch-yaml-changes.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh
    echo "Using original yaml watcher"
fi

if [ -f /usr/share/docassemble/scripts/watch-yaml-changes.sh ]; then
    chmod +x /usr/share/docassemble/scripts/watch-yaml-changes.sh
    chown www-data:www-data /usr/share/docassemble/scripts/watch-yaml-changes.sh
    echo "watch-yaml-changes script installed"
fi

# Copy the start-yaml-watcher script
if [ -f /tmp/Docker/start-yaml-watcher.sh ]; then
    cp /tmp/Docker/start-yaml-watcher.sh /usr/share/docassemble/scripts/start-yaml-watcher.sh
    chmod +x /usr/share/docassemble/scripts/start-yaml-watcher.sh
    echo "start-yaml-watcher script installed"
elif [ -f /usr/share/docassemble/webapp/start-yaml-watcher.sh ]; then
    cp /usr/share/docassemble/webapp/start-yaml-watcher.sh /usr/share/docassemble/scripts/start-yaml-watcher.sh
    chmod +x /usr/share/docassemble/scripts/start-yaml-watcher.sh
    echo "start-yaml-watcher script installed from webapp"
fi

# Ensure the supervisor config for yaml watcher exists
if [ ! -f /etc/supervisor/conf.d/supervisor-yaml-watcher.conf ] && [ -f /tmp/Docker/supervisor-yaml-watcher.conf ]; then
    cp /tmp/Docker/supervisor-yaml-watcher.conf /etc/supervisor/conf.d/
    echo "Supervisor yaml-watcher config installed"
elif [ ! -f /etc/supervisor/conf.d/supervisor-yaml-watcher.conf ] && [ -f /usr/share/docassemble/webapp/supervisor-yaml-watcher.conf ]; then
    cp /usr/share/docassemble/webapp/supervisor-yaml-watcher.conf /etc/supervisor/conf.d/
    echo "Supervisor yaml-watcher config installed from webapp"
fi

echo "Startup fixes completed successfully"