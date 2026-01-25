#!/bin/bash
# Build Docker image for orchestrator agents

set -e

echo "🔨 Building Orchestrator Agents Docker Image..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ORCHESTRATOR_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Orchestrator directory: $ORCHESTRATOR_DIR"
echo "📁 Docker context: $SCRIPT_DIR"
echo ""

# Build the image
echo "🐳 Building Docker image: orchestrator-agents:latest"
cd "$ORCHESTRATOR_DIR"
docker build -f docker/Dockerfile -t orchestrator-agents:latest .

echo ""
echo "✓ Build complete!"
echo ""
echo "Image: orchestrator-agents:latest"
echo ""
echo "Test the image:"
echo "  docker run --rm orchestrator-agents:latest python3 -c 'import sys; print(sys.version)'"
echo ""
