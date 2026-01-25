# Docker Backend for Parallel Orchestrator

The Docker backend enables parallel execution of tasks using local Docker containers, providing a cloud-free alternative to AWS Batch while maintaining similar capabilities.

## Features

- **Local Parallel Execution**: Run multiple executor containers in parallel on your local machine
- **No Cloud Dependencies**: All execution happens locally - no AWS account needed
- **Volume Mounting**: Seamless file sharing between host and containers
- **Network Support**: Optional Docker network for container communication
- **Resource Isolation**: Each executor runs in its own isolated container
- **Consistent with Cloud**: Similar interface to AWS Batch backend

## Prerequisites

1. **Docker**: Docker Desktop or Docker Engine installed and running
2. **Docker Image**: Build the executor image first
3. **API Key** (optional): Anthropic API key if using `--real` mode

## Quick Start

### 1. Build the Docker Image

```bash
# Option 1: Using the build script (recommended)
cd parallel-orchestrator/docker
./build.sh

# Option 2: Manual build
cd parallel-orchestrator
docker build -f docker/Dockerfile -t parallel-orchestrator:latest .
```

### 2. Run with Docker Backend

```bash
# Simple example with simulated executors
python3 orchestrator.py "Build a todo list app" --docker --max-executors 3

# With real Claude API calls
export ANTHROPIC_API_KEY="your-key-here"
python3 orchestrator.py "Build a blog platform" --docker --max-executors 4 --real

# Custom image and network
python3 orchestrator.py "Build microservices" \
    --docker \
    --docker-image=my-orchestrator:v1 \
    --docker-network=orchestrator-net \
    --max-executors 6 \
    --real
```

## CLI Options

### Docker-Specific Options

- `--docker`: Enable Docker backend
- `--docker-image IMAGE`: Docker image name (default: `parallel-orchestrator:latest`)
- `--docker-network NETWORK`: Docker network name (optional, will be created if doesn't exist)
- `--docker-api-key KEY`: Anthropic API key (or use `ANTHROPIC_API_KEY` env var)

### General Options

- `--max-executors N`: Number of parallel containers (default: 5)
- `--real`: Use real Claude API calls instead of simulation
- `--output-dir DIR`: Output directory for generated files

## Architecture

### Container Lifecycle

```
1. Submit Tasks
   ├─ Distribute tasks across N executors
   └─ Write tasks.json to executor directories

2. Start Containers
   ├─ Create container for each executor
   ├─ Mount executor directory to /output
   ├─ Pass environment variables
   └─ Run batch_executor.py

3. Monitor Execution
   ├─ Poll container status every 5 seconds
   ├─ Check exit codes
   └─ Collect container logs if failures

4. Collect Results
   ├─ Read result.json from each task directory
   ├─ Aggregate metrics
   └─ Return consolidated results

5. Cleanup
   ├─ Stop running containers
   └─ Remove containers
```

### File Structure

```
output/
├── executor_0/
│   ├── tasks.json              # Input: tasks for this executor
│   ├── task_1/
│   │   ├── result.json         # Output: task result
│   │   ├── claude_response.txt # Claude's response
│   │   └── generated files...
│   └── task_2/
│       └── ...
├── executor_1/
│   └── ...
└── orchestrator.log
```

### Environment Variables

Containers receive:
- `EXECUTOR_ID`: Executor number (0, 1, 2, ...)
- `OUTPUT_DIR`: Mount point for outputs (`/output`)
- `REQUIREMENTS`: Original requirements string
- `USE_REAL_EXECUTORS`: "1" for real API, "0" for simulation
- `ANTHROPIC_API_KEY`: API key (if provided)

## Docker Image

The executor image must contain:
- Python 3.9+
- Claude Code CLI installed
- `batch_executor.py` script at `/app/batch_executor.py`
- Non-root user for Claude CLI compatibility

### Building Custom Images

```dockerfile
FROM python:3.14-slim

# Install Claude Code CLI
RUN pip install claude-code

# Copy executor scripts
COPY batch_executor.py /app/
COPY executor_agent.py /app/

# Create non-root user
RUN useradd -m -s /bin/bash executor && \
    mkdir -p /output && \
    chown executor:executor /output

USER executor
WORKDIR /app

CMD ["python3", "batch_executor.py"]
```

## Networking

### Default Behavior

Containers run on the default Docker bridge network with no special configuration.

### Custom Networks

Create an isolated network for your containers:

```bash
# Create network
docker network create orchestrator-net

# Use network
python3 orchestrator.py "Build app" \
    --docker \
    --docker-network=orchestrator-net \
    --max-executors 4
```

Benefits of custom networks:
- Better isolation
- Container name-based DNS resolution
- Network-level security policies

## Performance Considerations

### Resource Limits

Docker containers inherit resource limits from Docker Desktop/Engine settings.

To configure:
```bash
# Docker Desktop: Settings → Resources
# Docker Engine: /etc/docker/daemon.json
```

### Optimal Executor Count

| Machine | CPU Cores | RAM | Recommended Executors |
|---------|-----------|-----|----------------------|
| Laptop | 4-8 | 8-16GB | 2-4 |
| Workstation | 8-16 | 16-32GB | 4-8 |
| Server | 16+ | 32GB+ | 8-16 |

### Disk Space

Each executor may generate significant files:
- Plan for ~100MB per task
- Monitor disk usage during execution
- Use `--output-dir` to control location

## Troubleshooting

### Docker Daemon Not Running

```
Error: Failed to connect to Docker
```

**Solution**: Start Docker Desktop or Docker Engine

### Image Not Found

```
Error: Docker image not found: parallel-orchestrator:latest
```

**Solution**: Build the image first
```bash
cd parallel-orchestrator/docker
./build.sh
```

### Permission Denied

```
Error: PermissionError: [Errno 13] Permission denied
```

**Solution**: Ensure executor user has write permissions to /output in container

### Container Failures

Check container logs:
```bash
# List containers
docker ps -a | grep po-executor

# View logs
docker logs po-executor-0

# Interactive debug
docker run -it --rm \
    -v $(pwd)/outputs/executor_0:/output \
    parallel-orchestrator:latest \
    bash
```

### API Key Issues

```
Warning: No Anthropic API key provided
```

**Solutions**:
1. Set environment variable: `export ANTHROPIC_API_KEY="your-key"`
2. Use CLI flag: `--docker-api-key your-key`
3. Use simulated mode without `--real`

## Comparison with AWS Batch

| Feature | Docker Backend | AWS Batch |
|---------|---------------|-----------|
| Infrastructure | Local machine | AWS Cloud |
| Setup | Docker only | AWS account, ECR, IAM, Batch |
| Cost | Free (local resources) | Pay per vCPU-hour |
| Scalability | Limited by local resources | Unlimited |
| Network speed | Native | Depends on region |
| Persistence | Local disk | S3 |
| Best for | Development, testing | Production, large scale |

## Examples

### Full-Stack Application

```bash
python3 orchestrator.py "Build a full-stack task management app with:
- React frontend with TypeScript
- Node.js/Express backend with JWT auth
- PostgreSQL database schema
- Docker Compose setup
- Comprehensive tests" \
    --docker \
    --max-executors 6 \
    --real
```

### Microservices Architecture

```bash
python3 orchestrator.py "Build a microservices platform with:
- API Gateway service
- User service with auth
- Product service with catalog
- Order service with workflow
- Docker containers for each service
- Kubernetes deployment configs" \
    --docker \
    --docker-network=microservices-net \
    --max-executors 8 \
    --real
```

### Machine Learning Pipeline

```bash
python3 orchestrator.py "Build an ML training pipeline with:
- Data preprocessing scripts
- Model training with PyTorch
- Evaluation and metrics
- Model deployment API
- Complete tests and documentation" \
    --docker \
    --max-executors 4 \
    --real
```

## Advanced Usage

### Integration with CI/CD

```yaml
# GitHub Actions example
name: Test Docker Orchestrator

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build image
        run: |
          cd parallel-orchestrator/docker
          ./build.sh
      - name: Run orchestrator
        run: |
          python3 orchestrator.py "Build test project" \
            --docker \
            --max-executors 2
```

### Custom Executor Scripts

Modify `batch_executor.py` to add custom behavior:
- Pre-processing hooks
- Custom logging
- Metrics collection
- Integration with other tools

### Multi-Stage Execution

Run multiple orchestrator passes:

```bash
# Stage 1: Generate core services
python3 orchestrator.py "Core services" --docker -m 4 --real

# Stage 2: Generate integration tests
python3 orchestrator.py "Integration tests for core services" \
    --docker -m 2 --real \
    --output-dir outputs/integration-tests
```

## Best Practices

1. **Resource Management**
   - Don't exceed your machine's CPU core count
   - Monitor memory usage during execution
   - Clean up old output directories regularly

2. **Image Updates**
   - Rebuild image after code changes
   - Version your images (e.g., `orchestrator:v1.2`)
   - Test image changes before production use

3. **Error Handling**
   - Always check exit codes
   - Review container logs for failures
   - Implement retry logic for transient failures

4. **Security**
   - Don't hardcode API keys in scripts
   - Use environment variables or secrets management
   - Limit container network access if needed
   - Run containers as non-root users

5. **Development Workflow**
   - Start with simulated mode (no `--real`)
   - Test with 2-3 executors first
   - Scale up gradually
   - Use custom networks for isolation

## Future Enhancements

Planned features:
- GPU support for ML workloads
- Resource limits per container
- Automatic image building
- Container caching for faster startup
- Distributed Docker Swarm support
- Real-time progress streaming

## Support

For issues or questions:
- Check container logs first
- Verify Docker daemon is running
- Ensure image is built correctly
- Review troubleshooting section above
- Check GitHub issues for similar problems
