#!/bin/bash
# Build script for parallel-orchestrator Docker image
# Runs from docker/ directory but uses parent directory as build context

set -e

echo "Building parallel-orchestrator Docker image..."
echo "Build context: parent directory (parallel-orchestrator/)"
echo "Dockerfile: docker/Dockerfile"
echo ""

# Build from parent directory with docker/ as the Dockerfile path
cd ..
docker build -f docker/Dockerfile -t parallel-orchestrator:latest .

echo ""
echo "✓ Build complete!"
echo "Image: parallel-orchestrator:latest"
