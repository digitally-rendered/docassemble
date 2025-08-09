# DocAssemble Kubernetes Deployment with Supabase

This guide will help you deploy docassemble to Kubernetes with Supabase PostgreSQL integration.

## Prerequisites

1. **Docker Desktop** or **Rancher Desktop** installed and running
2. **Kubernetes enabled** in Docker Desktop or Rancher Desktop running
3. **kubectl** installed and configured
4. **Helm** installed (v3.x)
5. **Supabase project** with database password

## Quick Start

### 1. Enable Kubernetes

**For Docker Desktop:**
1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for Kubernetes to start (status shows green)

**For Rancher Desktop:**
1. Start Rancher Desktop application
2. Wait for it to fully initialize
3. Kubernetes should be available automatically

### 2. Get Your Supabase Database Password

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to Settings → Database
4. In the "Connection parameters" section, find your database password
5. Copy the password (you'll need it for deployment)

### 3. Deploy DocAssemble

Run the deployment script:

```bash
cd /Users/draw/development/docassemble
./deploy.sh
```

The script will:
- Check and configure Kubernetes contexts
- Prompt for your Supabase database password
- Create the necessary Kubernetes namespace
- Deploy docassemble using Helm
- Set up all required secrets and configurations

### 4. Access the Application

Once deployed, forward the port to access locally:

```bash
kubectl port-forward svc/docassemble 8080:80 -n docassemble
```

Then open your browser to: http://localhost:8080

**Default Login:**
- Email: `admin@admin.com`
- Password: `admin123`

## What Was Deployed

### Database
- ✅ Complete docassemble schema created in Supabase
- ✅ All 21 required tables with proper relationships
- ✅ Indexes for performance optimization
- ✅ Row Level Security (RLS) policies
- ✅ Default roles and helper functions

### Kubernetes Resources
- **Deployment**: Main docassemble application
- **Service**: ClusterIP service for internal communication
- **Ingress**: HTTP routing (configured for `docassemble.local`)
- **Secrets**: Database passwords and admin credentials
- **PVC**: Persistent storage for docassemble files
- **Redis**: Internal Redis deployment for caching

### Environment Configuration
- Database connection to Supabase PostgreSQL
- SSL-enabled connection (`sslmode=require`)
- Internal Redis for session management
- Persistent storage for uploaded files
- Health checks and resource limits

## Useful Commands

```bash
# Check deployment status
kubectl get pods -n docassemble

# View application logs
kubectl logs -f deployment/docassemble -n docassemble

# Access Redis logs
kubectl logs -f deployment/docassemble-redis -n docassemble

# Check all resources
kubectl get all -n docassemble

# Delete everything
helm uninstall docassemble -n docassemble

# Port forward to access locally
kubectl port-forward svc/docassemble 8080:80 -n docassemble
```

## Troubleshooting

### Kubernetes Not Starting
- **Docker Desktop**: Restart Docker Desktop, wait 2-3 minutes
- **Rancher Desktop**: Restart the application, may take longer to initialize
- Check available resources (RAM/CPU)

### Pod Fails to Start
```bash
# Check pod events
kubectl describe pod -l app.kubernetes.io/name=docassemble -n docassemble

# Check logs
kubectl logs -f deployment/docassemble -n docassemble
```

### Database Connection Issues
- Verify Supabase database password is correct
- Check network connectivity to Supabase
- Ensure SSL mode is configured properly

### Image Pull Issues
```bash
# Use local image if available
helm upgrade docassemble ./helm-charts/docassemble \
  --namespace docassemble \
  --set image.repository=your-local-image \
  --set image.tag=latest
```

## Customization

### Use Custom Image
If you want to use your locally built docassemble image:

```bash
# Build your custom image first
docker build -t my-docassemble:latest .

# Deploy with custom image
helm upgrade docassemble ./helm-charts/docassemble \
  --namespace docassemble \
  --set image.repository=my-docassemble \
  --set image.tag=latest \
  --set database.password="YOUR_SUPABASE_PASSWORD"
```

### Modify Resources
Edit `helm-charts/docassemble/values.yaml` to adjust:
- CPU/Memory limits
- Storage size
- Replica count
- Environment variables

## Production Considerations

For production deployment:

1. **Security**: Use Kubernetes secrets management
2. **SSL**: Enable HTTPS with proper certificates
3. **Ingress**: Configure proper ingress controller
4. **Monitoring**: Add logging and monitoring
5. **Backups**: Set up automated backups
6. **Scaling**: Configure horizontal pod autoscaling

## Support

The deployment includes:
- ✅ Supabase PostgreSQL integration
- ✅ Complete database schema
- ✅ Kubernetes-native configuration
- ✅ Health checks and monitoring
- ✅ Persistent storage
- ✅ Redis caching
- ✅ Security policies

Your docassemble instance is now ready for development and testing with full Supabase integration!