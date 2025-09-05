# Docassemble Docker Startup Fixes

## Problem Summary
The Docassemble Docker image fails to start correctly due to two missing critical files:
1. `/usr/share/docassemble/webapp/docassemble.wsgi` - The WSGI entry point file
2. `/var/www/.pypirc` - PyPI configuration file

## Solutions Provided

### Solution 1: Fix in Docker Image (Permanent)
The Dockerfile has been updated to:
- Copy and execute `fix-startup.sh` during build
- Run `fix-startup.sh` on every container start via CMD

To apply this fix:
```bash
# Rebuild the Docker image
docker build -t docassemble:fixed .

# Or use docker-compose
docker-compose build
docker-compose up
```

### Solution 2: Fix in Kubernetes (Without Rebuilding)
For existing deployments, apply the fix without rebuilding the image:

#### Step 1: Apply the ConfigMap
```bash
kubectl apply -f k8s-startup-fix.yaml
```

#### Step 2: Patch the Deployment
Option A - Direct patch:
```bash
kubectl patch deployment docassemble --patch-file deployment-patch.yaml
```

Option B - Using Helm:
```bash
helm upgrade <release-name> <chart> -f helm-values-fix.yaml
```

### Solution 3: Manual Fix (Quick)
If you need to fix a running container immediately:
```bash
# Copy the fix script to the container
kubectl cp Docker/fix-startup.sh <pod-name>:/tmp/fix-startup.sh

# Execute the fix
kubectl exec <pod-name> -- bash /tmp/fix-startup.sh

# Restart the container
kubectl delete pod <pod-name>
```

## Files Created

### Core Fix Script
- `Docker/fix-startup.sh` - The main script that fixes startup issues

### Docker Files
- `Dockerfile` - Updated to include the fix
- `docker-compose.yml` - Complete Docker Compose setup for local testing

### Kubernetes Files
- `k8s-startup-fix.yaml` - ConfigMap containing the fix script
- `deployment-patch.yaml` - Kubernetes deployment patch
- `helm-values-fix.yaml` - Helm values override file

## What the Fix Does

1. **Creates WSGI file**: Copies from nested location or creates from scratch
2. **Creates .pypirc file**: Ensures PyPI configuration exists with proper permissions
3. **Creates directories**: Ensures all required directories exist
4. **Fixes permissions**: Sets correct ownership for www-data user
5. **Starts supervisord**: Launches the main process manager

## Testing

After applying the fix, verify the container starts correctly:

```bash
# Check pod status
kubectl get pods

# Check logs
kubectl logs <pod-name>

# Verify files exist
kubectl exec <pod-name> -- ls -la /usr/share/docassemble/webapp/docassemble.wsgi
kubectl exec <pod-name> -- ls -la /var/www/.pypirc
```

## Notes

- The fix script is idempotent - it can be run multiple times safely
- The script checks if files exist before creating them
- All operations include error handling with `|| true` to prevent failures
- The script maintains compatibility with mounted volumes in Kubernetes