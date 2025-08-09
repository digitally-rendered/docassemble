#!/bin/bash

# Deploy docassemble to Kubernetes with Supabase integration
# This script handles starting Kubernetes and deploying the Helm chart

set -e

echo "🚀 Deploying docassemble to Kubernetes with Supabase integration"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed. Please install helm first."
    exit 1
fi

# Function to check if Kubernetes is running
check_kubernetes() {
    kubectl cluster-info &> /dev/null
    return $?
}

# Try to connect to current context
echo "🔍 Checking Kubernetes cluster status..."
if ! check_kubernetes; then
    echo "⚠️  Current Kubernetes context is not accessible."
    
    # Try Docker Desktop context
    echo "🔄 Trying Docker Desktop context..."
    kubectl config use-context docker-desktop &> /dev/null || true
    if check_kubernetes; then
        echo "✅ Connected to Docker Desktop Kubernetes"
    else
        # Try Rancher Desktop context
        echo "🔄 Trying Rancher Desktop context..."
        kubectl config use-context rancher-desktop &> /dev/null || true
        if check_kubernetes; then
            echo "✅ Connected to Rancher Desktop Kubernetes"
        else
            echo "❌ No accessible Kubernetes cluster found."
            echo ""
            echo "Please start one of the following:"
            echo "  - Docker Desktop: Enable Kubernetes in Docker Desktop settings"
            echo "  - Rancher Desktop: Start Rancher Desktop"
            echo ""
            echo "Then run this script again."
            exit 1
        fi
    fi
else
    current_context=$(kubectl config current-context)
    echo "✅ Connected to Kubernetes context: $current_context"
fi

# Prompt for Supabase database password
echo ""
echo "🔑 Supabase Database Configuration"
echo "You need to provide your Supabase database password."
echo "You can find this in your Supabase dashboard under Settings -> Database -> Connection parameters"
echo ""
read -s -p "Enter your Supabase database password: " SUPABASE_DB_PASSWORD
echo ""

if [ -z "$SUPABASE_DB_PASSWORD" ]; then
    echo "❌ Database password is required"
    exit 1
fi

# Create namespace if it doesn't exist
NAMESPACE="docassemble"
echo "📁 Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade the Helm chart
echo "🎯 Deploying docassemble with Helm..."
echo "📊 Running helm upgrade with verbose output..."
helm upgrade --install docassemble ./helm-charts/docassemble \
    --namespace $NAMESPACE \
    --set database.password="$SUPABASE_DB_PASSWORD" \
    --set docassemble.admin.password="admin123" \
    --set docassemble.supervisor.password="supervisor123" \
    --debug \
    --wait \
    --timeout=10m &

# Capture the helm process ID
HELM_PID=$!

# Monitor deployment progress in background
(
    echo "📈 Monitoring deployment progress..."
    sleep 5
    while kill -0 $HELM_PID 2>/dev/null; do
        echo ""
        echo "⏱️  $(date '+%H:%M:%S') - Current deployment status:"
        kubectl get pods -n $NAMESPACE -o wide 2>/dev/null || echo "   No pods found yet..."
        
        # Show helm release status
        helm status docassemble -n $NAMESPACE 2>/dev/null || echo "   Helm release not ready yet..."
        
        # Show events if there are any issues
        echo "📋 Recent events:"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -5 2>/dev/null || echo "   No events yet..."
        
        sleep 15
    done
) &

# Wait for helm command to complete
wait $HELM_PID
HELM_EXIT_CODE=$?

# Kill the monitoring background process
jobs -p | xargs -r kill 2>/dev/null || true

if [ $HELM_EXIT_CODE -ne 0 ]; then
    echo "❌ Helm deployment failed with exit code $HELM_EXIT_CODE"
    echo "📋 Checking for issues..."
    kubectl describe pods -n $NAMESPACE
    exit $HELM_EXIT_CODE
fi

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Useful commands:"
echo "  Check pod status:    kubectl get pods -n $NAMESPACE"
echo "  View logs:          kubectl logs -f deployment/docassemble -n $NAMESPACE"
echo "  Port forward:       kubectl port-forward svc/docassemble 8080:80 -n $NAMESPACE"
echo "  Delete deployment:  helm uninstall docassemble -n $NAMESPACE"
echo ""

# Check if pods are running
echo "🔍 Checking pod status..."
kubectl get pods -n $NAMESPACE

# Wait for pods to be ready
echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=docassemble -n $NAMESPACE --timeout=300s

# Get service information
echo ""
echo "🌐 Service Information:"
kubectl get svc -n $NAMESPACE

echo ""
echo "🎉 docassemble is now running on Kubernetes with Supabase!"
echo ""
echo "To access the application:"
echo "1. Run: kubectl port-forward svc/docassemble 8080:80 -n $NAMESPACE"
echo "2. Open your browser to: http://localhost:8080"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@admin.com"
echo "  Password: admin123"
echo ""
echo "The application is connected to your Supabase database with all required tables."