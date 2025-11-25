#!/bin/bash
# Deploy script for t3.micro

set -e

echo "=== Binko.ai Deploy ==="

# Check .env exists
if [ ! -f .env.prod ]; then
    echo "ERROR: .env.prod not found"
    echo "Copy .env.prod.example to .env.prod and fill in values"
    exit 1
fi

# Load env
export $(cat .env.prod | grep -v '#' | xargs)

# Pull latest
echo "Pulling latest code..."
git pull origin main

# Build and start
echo "Building containers..."
docker compose -f docker-compose.prod.yml build

echo "Starting services..."
docker compose -f docker-compose.prod.yml up -d

# Wait for health
echo "Waiting for services..."
sleep 10

# Check health
if curl -s http://localhost/health | grep -q "healthy"; then
    echo "=== Deploy SUCCESS ==="
    echo "Site live at http://$(curl -s ifconfig.me)"
else
    echo "=== Deploy FAILED ==="
    docker compose -f docker-compose.prod.yml logs
    exit 1
fi
