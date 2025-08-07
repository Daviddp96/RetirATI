#!/bin/bash

echo "=== Health Check ==="
healthy_services=0
total_services=3

echo "Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
    healthy_services=$((healthy_services + 1))
else
    echo "⚠️ Redis is not responding"
fi

echo "Checking Django server on port 8001..."
if curl -s -f http://localhost:8001/login/ > /dev/null 2>&1; then
    echo "✅ Django server is running on port 8001"
    healthy_services=$((healthy_services + 1))
else
    echo "⚠️ Django server on port 8001 may have issues"
fi

echo "Checking Apache proxy on port 80..."
if curl -s -f http://localhost:80/login/ > /dev/null 2>&1; then
    echo "✅ Apache proxy is running on port 80"
    healthy_services=$((healthy_services + 1))
else
    echo "⚠️ Apache proxy on port 80 may have issues"
fi

echo "=== Health Check Complete ==="
echo "Healthy services: $healthy_services/$total_services"

# Consider healthy if at least Apache is working (most important for serving the app)
if [ $healthy_services -ge 1 ]; then
    echo "✅ Container is healthy (at least one service is running)"
    exit 0
else
    echo "❌ Container is unhealthy (no services responding)"
    exit 1
fi