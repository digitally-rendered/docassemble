#!/bin/bash

# Docassemble Service Port-Forward Script
# This script sets up port-forwarding to the docassemble service
# instead of directly to a pod, ensuring persistence across pod restarts

NAMESPACE="docassemble"
SERVICE="docassemble"
LOCAL_PORT="${1:-8080}"
REMOTE_PORT="80"

echo "🔌 Setting up port-forward to docassemble service..."
echo "📍 Namespace: $NAMESPACE"
echo "🎯 Service: $SERVICE"
echo "🔗 Local port: $LOCAL_PORT -> Remote port: $REMOTE_PORT"
echo ""
echo "✨ Access docassemble at: http://localhost:$LOCAL_PORT"
echo ""
echo "Press Ctrl+C to stop port-forwarding"
echo "----------------------------------------"

# Kill any existing port-forward processes
pkill -f "kubectl port-forward.*svc/$SERVICE" 2>/dev/null

# Start port-forwarding to the service
kubectl port-forward -n "$NAMESPACE" "svc/$SERVICE" "$LOCAL_PORT:$REMOTE_PORT"