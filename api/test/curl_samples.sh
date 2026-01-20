#!/bin/bash
# Curl samples for Claude Code API Server

BASE_URL="http://localhost:8000"

echo "=== Health Check ==="
curl -X GET "$BASE_URL/health"
echo -e "\n\n"

echo "=== Basic Query (Non-streaming) ==="
curl -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What files are in this directory?",
    "cwd": "/Users/nghia.dinh/factory-agentic-dev"
  }'
echo -e "\n\n"

echo "=== Streaming Query (SSE) ==="
curl -X POST "$BASE_URL/query/stream" \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "prompt": "Explain what this project does",
    "cwd": "/Users/nghia.dinh/factory-agentic-dev"
  }'
echo -e "\n\n"

echo "=== Raw Streaming Query ==="
curl -X POST "$BASE_URL/query/stream/raw" \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "prompt": "List the main features of this codebase",
    "cwd": "/Users/nghia.dinh/factory-agentic-dev"
  }'
echo -e "\n\n"

echo "=== Query with custom working directory ==="
curl -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me the structure of this project",
    "cwd": "/path/to/your/project"
  }'
echo -e "\n\n"
