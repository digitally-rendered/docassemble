# YAML Auto-Reload for Docassemble Development

## Overview
This enhancement adds automatic YAML file change detection and reloading to the Docassemble Docker container, making local development much smoother.

## Features
- **Automatic Detection**: Monitors all `.yml` files in the questions directory
- **Smart Reloading**: Clears caches and triggers uwsgi reload when changes are detected
- **Efficient Monitoring**: Uses `inotifywait` for efficient file system monitoring
- **Fallback Support**: Falls back to polling if `inotifywait` is not available

## How It Works

### Components Added:
1. **`watch-yaml-changes.sh`**: Main script that monitors YAML files
2. **`supervisor-yaml-watcher.conf`**: Supervisor configuration to keep the watcher running
3. **`inotify-tools`**: System package for efficient file monitoring

### When a YAML file changes:
1. The watcher detects the change immediately
2. Python bytecode cache is cleared
3. Redis session cache is flushed
4. uwsgi is triggered to reload via touching the WSGI file
5. Your changes are immediately available in the browser

## Building the Enhanced Image

```bash
# Build the new image with auto-reload support
docker build -t docassemble:latest-dev .

# Tag it appropriately
docker tag docassemble:latest-dev docassemble:latest
```

## Using with Kubernetes

Update your deployment to use the new image:

```yaml
spec:
  containers:
  - name: docassemble
    image: docassemble:latest-dev
    # ... rest of your configuration
```

Or update the running deployment:

```bash
kubectl set image deployment/docassemble docassemble=docassemble:latest-dev -n docassemble
```

## Verifying It's Working

1. Check that the watcher is running:
```bash
kubectl exec -n docassemble <pod-name> -- supervisorctl status yamlwatcher
```

2. Monitor the watcher logs:
```bash
kubectl exec -n docassemble <pod-name> -- tail -f /var/log/supervisor/yamlwatcher-stdout*
```

3. Test by creating or modifying a YAML file - you should see:
```
🔄 YAML file changed at <timestamp>
✅ Reload triggered
```

## Development Workflow

1. **Edit your YAML files locally** in your IDE
2. **Save the file** - the watcher detects the change immediately
3. **Refresh your browser** (Cmd+Shift+R) to see the changes
4. **No manual reload needed!**

## Troubleshooting

### Changes not appearing?
- Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
- Check watcher is running: `supervisorctl status yamlwatcher`
- Check logs for errors: `tail -f /var/log/supervisor/yamlwatcher-stderr*`

### Watcher not starting?
- Ensure inotify-tools is installed: `apt-get install -y inotify-tools`
- Check supervisor configuration is loaded
- Restart supervisor: `supervisorctl reload`

## Performance Considerations

- The watcher has a 2-second delay after changes to prevent rapid reloads
- Only `.yml` files trigger reloads (not Python files or templates)
- Redis cache clearing is fast but may affect active sessions

## Future Enhancements

Potential improvements:
- Add configuration to enable/disable in production
- Support for watching Python modules
- Selective cache clearing based on file type
- WebSocket notification to browser for auto-refresh