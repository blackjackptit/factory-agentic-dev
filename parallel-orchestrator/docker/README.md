# Docker Image for Parallel Orchestrator

This directory contains the Dockerfile and build scripts for the parallel-orchestrator Docker image.

## Build Structure

The Dockerfile is designed to avoid file duplication:
- **Dockerfile location**: `docker/Dockerfile`
- **Build context**: Parent directory (`parallel-orchestrator/`)
- **Source files**: Copied from parent directory at build time

This means:
- ✅ No duplicate Python files in `docker/` directory
- ✅ Single source of truth for executor scripts
- ✅ Automatic updates when source files change

## Building the Image

### Option 1: Using the Build Script (Recommended)

```bash
cd parallel-orchestrator/docker
./build.sh
```

### Option 2: Manual Build Command

```bash
cd parallel-orchestrator
docker build -f docker/Dockerfile -t parallel-orchestrator:latest .
```

**Important**: The build context must be the parent directory (`parallel-orchestrator/`), not the `docker/` directory, so that the Dockerfile can access source files with `../` paths.

## Image Contents

The image includes:
- **Base**: Node.js 20 (slim)
- **Python**: 3.x with pip
- **AWS CLI**: v2 (for AWS Batch backend)
- **Claude Code CLI**: Latest version from npm
- **Executor Scripts**:
  - `batch_executor.py` - AWS Batch task executor
  - `docker_executor.py` - Docker backend task executor
  - `docker_planner.py` - Docker planner executor
  - `executor_agent.py` - Core executor agent
  - `planner_agent.py` - Task planning agent

## Non-Root User

The image creates a non-root user (`executor`) because:
- Claude Code CLI requires non-root execution for safety
- Better security practices
- Matches production container best practices

## Environment Variables

The container expects these environment variables:

### For Docker Backend (Executors)
- `EXECUTOR_ID` - Executor identifier (0, 1, 2, ...)
- `OUTPUT_DIR` - Output directory path (`/output`)
- `REQUIREMENTS` - Project requirements string
- `USE_REAL_EXECUTORS` - "1" for real API calls, "0" for simulation

### For Docker Planner
- `OUTPUT_DIR` - Output directory path (`/output`)
- `REQUIREMENTS` - Project requirements string
- `MAX_EXECUTORS` - Executor budget (number of parallel workers)

### For Anthropic API
- `ANTHROPIC_API_KEY` - Anthropic API key

### For AWS Bedrock
- `USE_BEDROCK` - "1" to enable Bedrock mode
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_SESSION_TOKEN` - AWS session token (optional)
- `BEDROCK_REGION` - AWS region (e.g., us-east-1)
- `BEDROCK_MODEL` - Bedrock model ID

### For AWS Batch
- `TASK_ID` - Task identifier
- `S3_BUCKET` - S3 bucket name
- `S3_PREFIX` - S3 prefix for state files
- `AWS_REGION` - AWS region

## Volume Mounts

Typical volume mount:
```bash
docker run -v /host/path:/output parallel-orchestrator:latest
```

The `/output` directory in the container is where:
- Task results are written
- Generated code is saved
- Logs are stored

## Testing the Image

### Test Executor
Quick test with simulated execution:
```bash
docker run --rm \
  -e EXECUTOR_ID=0 \
  -e OUTPUT_DIR=/output \
  -e USE_REAL_EXECUTORS=0 \
  -e REQUIREMENTS="Build a simple calculator" \
  -v $(pwd)/test-output:/output \
  parallel-orchestrator:latest \
  python3 /app/docker_executor.py
```

### Test Planner
Test planner (requires API key or Bedrock credentials):
```bash
docker run --rm \
  -e OUTPUT_DIR=/output \
  -e REQUIREMENTS="Build a todo app" \
  -e MAX_EXECUTORS=3 \
  -e ANTHROPIC_API_KEY="your-key" \
  -v $(pwd)/test-planner:/output \
  parallel-orchestrator:latest \
  python3 /app/docker_planner.py
```

## Maintenance

### Updating Source Files

When you update executor scripts:
1. Edit files in `parallel-orchestrator/` directory (NOT in `docker/`)
2. Rebuild the image: `cd docker && ./build.sh`
3. No need to copy files manually - the build script handles it

### Verifying Image Contents

```bash
# List files in the image
docker run --rm parallel-orchestrator:latest ls -la /app

# Check Python scripts
docker run --rm parallel-orchestrator:latest ls -la /app/*.py

# Verify Claude CLI installation
docker run --rm parallel-orchestrator:latest claude --version

# Check user
docker run --rm parallel-orchestrator:latest whoami
```

## Multi-Architecture Builds

To build for multiple architectures (e.g., ARM64 for M1 Macs):

```bash
cd parallel-orchestrator

docker buildx build \
  -f docker/Dockerfile \
  --platform linux/amd64,linux/arm64 \
  -t parallel-orchestrator:latest \
  --push \
  .
```

## Size Optimization

Current image size: ~600MB

The image includes:
- Node.js runtime (~200MB)
- Python + AWS CLI (~250MB)
- Claude Code CLI (~50MB)
- System dependencies (~100MB)

To reduce size, you could:
- Use `node:20-alpine` instead of `node:20-slim` (saves ~50MB)
- Remove AWS CLI if not using AWS Batch (saves ~100MB)
- Use multi-stage build to separate build and runtime dependencies

## Troubleshooting

### Error: "No such file or directory: '../batch_executor.py'"

**Cause**: Building from wrong directory

**Solution**: Build from parent directory:
```bash
cd parallel-orchestrator  # Not docker/
docker build -f docker/Dockerfile -t parallel-orchestrator:latest .
```

Or use the build script:
```bash
cd parallel-orchestrator/docker
./build.sh
```

### Error: "permission denied: /app"

**Cause**: Not using non-root user

**Solution**: The Dockerfile already switches to the `executor` user. If you override the user, switch back:
```bash
docker run --user executor ...
```

### Error: "Claude CLI not found"

**Cause**: PATH or installation issue

**Solution**: Verify installation:
```bash
docker run --rm parallel-orchestrator:latest which claude
docker run --rm parallel-orchestrator:latest claude --version
```

## Related Documentation

- [Docker Backend Documentation](../docs/docker-backend.md)
- [Docker Backend with Bedrock](../docs/docker-bedrock-usage.md)
- [Main README](../README.md)
