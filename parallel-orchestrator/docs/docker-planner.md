# Docker Planner Mode

The parallel orchestrator now supports running the planner agent in a Docker container, providing the same isolation and environment consistency benefits for planning as for execution.

## Overview

By default, the planner agent runs locally on your machine. With `--docker-planner-in-docker`, the planner runs in an isolated Docker container, useful for:

- **Consistent Environment**: Same Claude CLI version and Python environment as executors
- **Isolation**: Planner runs in isolated environment, separate from host
- **Parallel Setup**: Both planning and execution use Docker
- **CI/CD Integration**: Entire orchestration (plan + execute) runs in containers

## Usage

### Basic Usage

```bash
# Run planner in Docker, executors locally (threading backend)
python3 orchestrator.py "Build a calculator app" \
    --docker-planner-in-docker \
    --max-executors 3 \
    --real

# Run planner AND executors in Docker
python3 orchestrator.py "Build a blog platform" \
    --docker \
    --docker-planner-in-docker \
    --max-executors 4 \
    --real
```

### With Anthropic API

```bash
export ANTHROPIC_API_KEY="your-api-key"

python3 orchestrator.py "Build a todo app" \
    --docker \
    --docker-planner-in-docker \
    --max-executors 3 \
    --real
```

### With AWS Bedrock

```bash
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

python3 orchestrator.py "Build a chat app" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --max-executors 4 \
    --real
```

Or pass credentials via CLI:

```bash
python3 orchestrator.py "Build microservices" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --docker-aws-access-key-id "your-key" \
    --docker-aws-secret-access-key "your-secret" \
    --docker-bedrock-region eu-central-1 \
    --docker-bedrock-model global.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --max-executors 6 \
    --real
```

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ Host Machine                                                 │
│                                                              │
│  1. Orchestrator starts                                      │
│     └─> Check --docker-planner-in-docker flag               │
│                                                              │
│  2. Docker planner container                                 │
│     ├─> Mount: outputs/planner → /output                    │
│     ├─> Env: REQUIREMENTS, MAX_EXECUTORS, credentials       │
│     ├─> Run: docker_planner.py                              │
│     │   ├─> PlannerAgent.analyze_complexity()               │
│     │   └─> PlannerAgent.create_plan()                      │
│     └─> Save: /output/planner_output.json                   │
│                                                              │
│  3. Orchestrator reads plan                                  │
│     └─> Load: outputs/planner/planner_output.json           │
│                                                              │
│  4. Execute tasks (Docker backend or other)                  │
│     └─> Normal execution with generated plan                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Container Structure

### Planner Container

**Name**: `po-planner`

**Environment Variables**:
- `OUTPUT_DIR=/output` - Output mount point
- `REQUIREMENTS` - Project requirements string
- `MAX_EXECUTORS` - Executor budget

**For Anthropic API**:
- `ANTHROPIC_API_KEY` - API key

**For AWS Bedrock**:
- `USE_BEDROCK=1` - Enable Bedrock mode
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_SESSION_TOKEN` - Session token (optional)
- `BEDROCK_REGION` - AWS region
- `BEDROCK_MODEL` - Model ID

**Volume Mount**:
```
outputs/planner/ → /output (read-write)
```

**Output File**:
```json
{
  "success": true,
  "num_tasks": 5,
  "plan": {
    "num_tasks": 5,
    "executor_budget": 3,
    "execution_model": "task_queue",
    "tasks": [...],
    "dependencies": {...},
    "execution_strategy": "...",
    "notes": "..."
  }
}
```

## CLI Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--docker-planner-in-docker` | Run planner in Docker container | `false` |

All other Docker flags (credentials, image, etc.) apply to both planner and executor containers.

## Architecture Comparison

### Local Planner (Default)

```
Host Machine
├── PlannerAgent (local Python)
│   └── Claude CLI (local)
└── Executor Backend
    ├── Threading (local)
    ├── SLURM (cluster)
    ├── AWS Batch (cloud)
    └── Docker (containers)
```

### Docker Planner

```
Host Machine
├── Docker Planner Container
│   └── PlannerAgent + Claude CLI
└── Executor Backend
    └── Docker Containers
        └── ExecutorAgent + Claude CLI
```

## Benefits

### 1. Environment Consistency

**Problem**: Different Claude CLI versions on host vs containers
**Solution**: Same Docker image for planner and executors

### 2. Clean Separation

**Problem**: Planner creates files in host filesystem
**Solution**: All outputs go to volume-mounted directory

### 3. Reproducibility

**Problem**: Local environment affects planning
**Solution**: Planner runs in controlled container environment

### 4. CI/CD Friendly

**Problem**: CI agents need Claude CLI installed
**Solution**: Everything runs in containers, no host dependencies

## When to Use Docker Planner

### Use Docker Planner When:

✅ Running entire workflow in CI/CD
✅ Need consistent environment between plan and execution
✅ Already using Docker backend for executors
✅ Want complete isolation from host machine
✅ Testing with different Claude CLI versions

### Use Local Planner When:

✅ Rapid iteration during development
✅ Executor backend is not Docker (SLURM, AWS Batch, etc.)
✅ Want faster planning (no container startup overhead)
✅ Using different credentials for planning vs execution

## Performance Considerations

### Container Startup Overhead

Docker planner adds ~2-5 seconds for container startup. For long-running projects (many tasks), this overhead is negligible.

### Disk I/O

Volume mounting is fast on modern Docker. No significant performance impact.

### Network

If using Bedrock, container makes API calls just like local planner. No additional latency.

## Troubleshooting

### Error: "Docker image not found"

```bash
# Build the image first
cd parallel-orchestrator/docker
./build.sh
```

### Error: "Claude CLI error"

**Cause**: No credentials available

**Solutions**:
```bash
# Option 1: Anthropic API
export ANTHROPIC_API_KEY="your-key"

# Option 2: AWS Bedrock
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
python3 orchestrator.py ... --docker-use-bedrock
```

### Error: "Planner did not produce output file"

**Cause**: Planner crashed or failed to write output

**Debug**:
```bash
# Check planner output directory
ls -la outputs/planner/

# Check container logs (if container still exists)
docker logs po-planner
```

### Planner Container Stuck

**Cause**: Waiting for Claude API response

**Solution**: Check network connectivity, API key validity

## Examples

### Simple App with Docker Planner

```bash
python3 orchestrator.py "Build a weather dashboard" \
    --docker \
    --docker-planner-in-docker \
    --max-executors 3 \
    --real
```

### Full-Stack App with Bedrock

```bash
python3 orchestrator.py "Build e-commerce platform with:
- React frontend
- Node.js backend
- PostgreSQL database
- Docker setup
- Tests" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --docker-bedrock-region us-west-2 \
    --max-executors 8 \
    --real
```

### Multi-Region Setup

```bash
# US team
python3 orchestrator.py "Feature A" \
    --docker --docker-planner-in-docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --max-executors 4 --real &

# EU team
python3 orchestrator.py "Feature B" \
    --docker --docker-planner-in-docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --docker-bedrock-model global.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --max-executors 4 --real &

wait
```

## Integration with Other Backends

Docker planner works with any executor backend:

```bash
# Docker planner + AWS Batch executors
python3 orchestrator.py "Build app" \
    --docker-planner-in-docker \
    --batch \
    --batch-job-queue my-queue \
    --batch-job-definition my-def \
    --batch-s3-bucket my-bucket \
    --max-executors 10 \
    --real

# Docker planner + SLURM executors
python3 orchestrator.py "Build app" \
    --docker-planner-in-docker \
    --slurm \
    --slurm-partition compute \
    --max-executors 8 \
    --real
```

## Best Practices

1. **Use Same Image**: Planner and executors use the same Docker image
2. **Test Locally First**: Use `--docker-planner-in-docker` without `--real` to test
3. **Version Control**: Tag Docker images for reproducibility
4. **Credentials**: Use environment variables, not CLI arguments for secrets
5. **Output Inspection**: Check `outputs/planner/planner_output.json` for plan details

## Related Documentation

- [Docker Backend](docker-backend.md) - Docker executor backend
- [Docker with Bedrock](docker-bedrock-usage.md) - Using AWS Bedrock
- [Main README](../README.md) - General orchestrator documentation
