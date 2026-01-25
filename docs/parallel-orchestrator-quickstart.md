# Parallel Orchestrator - Quick Start Guide

## What Was Created

A complete **Parallel Task Orchestrator** system with **AI-powered planning** and **multi-backend execution** supporting Threading, Docker, SLURM HPC, and AWS ParallelCluster.

### Project Structure

```
parallel-orchestrator/
├── orchestrator.py              # Main orchestrator (coordinates executors)
├── planner_agent.py             # AI-powered planner using Claude Code
├── executor_agent.py            # Individual executor agent implementation
├── config.py                    # Configuration and CLI argument parsing
├── docker_planner.py            # Docker planner container script
├── docker_executor.py           # Docker executor container script
├── slurm_executor.py            # SLURM compute node executor script
├── docker/                      # Docker image build
│   ├── Dockerfile               # Multi-stage container image
│   ├── build.sh                 # Build automation script
│   └── README.md                # Docker setup guide
├── backends/
│   ├── __init__.py              # Package exports
│   ├── base.py                  # Abstract ExecutionBackend class
│   ├── threading_backend.py     # Local threading backend
│   ├── docker_backend.py        # Docker containers backend
│   ├── slurm_backend.py         # SLURM HPC backend
│   └── aws_parallel_cluster_backend.py  # AWS ParallelCluster backend
└── ../outputs/parallel-orchestrator/  # Generated outputs (centralized)
```

## Quick Test

### Threading Mode (Default)

```bash
cd parallel-orchestrator

# Simple task
python3 orchestrator.py "Build a simple todo list application"

# With custom executor count
python3 orchestrator.py "Build REST API with authentication" --max-executors 4

# Generate real code
python3 orchestrator.py "Build a chess game" --max-executors 5 --real
```

### Docker Mode (Recommended for Production)

```bash
# Build Docker image first (one-time setup)
cd docker && ./build.sh && cd ..

# Basic Docker execution with AWS Bedrock
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

python3 orchestrator.py "Build a todo list app" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --max-executors 3 \
    --real

# Docker with Anthropic API
export ANTHROPIC_API_KEY="your-key"

python3 orchestrator.py "Build a contact form" \
    --docker \
    --docker-planner-in-docker \
    --max-executors 2 \
    --real

# Docker with custom model
python3 orchestrator.py "Build a calculator" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-model "global.anthropic.claude-3-5-sonnet-20241022-v2:0" \
    --max-executors 2 \
    --real
```

### SLURM Mode (HPC Cluster)

```bash
# Basic SLURM execution
python3 orchestrator.py "Process ML dataset" \
    --slurm \
    --slurm-partition=compute \
    --max-executors 10

# SLURM with GPU
python3 orchestrator.py "Train neural network" \
    --slurm \
    --slurm-partition=gpu \
    --slurm-gpus=1 \
    --slurm-mem=32G \
    --max-executors 8
```

### AWS ParallelCluster Mode

```bash
# AWS execution
python3 orchestrator.py "Build distributed platform" \
    --aws \
    --aws-cluster-name=my-cluster \
    --aws-s3-bucket=my-bucket \
    --max-executors 50

# AWS with GPU
python3 orchestrator.py "Train deep learning models" \
    --aws \
    --aws-cluster-name=gpu-cluster \
    --aws-s3-bucket=ml-bucket \
    --slurm-gpus=4 \
    --max-executors 20
```

## How It Works

### 1. AI-Powered Complexity Analysis
The **PlannerAgent** uses Claude Code to intelligently analyze your requirements:

```python
# Simple task -> 1-3 tasks
"Create a hello world function"

# Medium task -> 3-8 tasks
"Build a todo list with add, delete, complete features"

# Complex task -> 8-15+ tasks
"Create an e-commerce platform with authentication and payments"
```

### 2. Backend Selection
Based on CLI flags, the orchestrator creates the appropriate backend:

| Flag | Backend | Use Case |
|------|---------|----------|
| (none) | ThreadingBackend | Local development |
| `--docker` | DockerBackend | Containerized parallel execution |
| `--slurm` | SlurmBackend | HPC clusters |
| `--aws` | AWSParallelClusterBackend | Cloud HPC |

### 3. Task Queue Execution
M executor workers process N tasks dynamically from a queue:

```
Task Queue: [Task1][Task2][Task3][Task4][Task5][Task6]
                   ↓       ↓       ↓
Executor 1 ───> Task1 → Task4 (done)
Executor 2 ───> Task2 → Task5 (done)
Executor 3 ───> Task3 → Task6 (done)

Benefits:
- Automatic load balancing
- Dependency-aware execution
- No idle executors when work available
```

### 4. Result Aggregation & Output Consolidation
- Collects outputs from all executors
- Calculates metrics (success rate, LOC, coverage)
- Consolidates into unified project structure

## Command-Line Options

```bash
python3 orchestrator.py <requirements> [OPTIONS]

General Options:
  -o, --output-dir DIR     Output directory
  -m, --max-executors N    Maximum executors (default: 5)
  --real                   Use real Claude API

Backend Selection:
  --docker                 Enable Docker backend
  --slurm                  Enable SLURM backend
  --aws                    Enable AWS ParallelCluster backend

Docker Options:
  --docker-planner-in-docker        Run planner in Docker
  --docker-use-bedrock              Use AWS Bedrock instead of Anthropic API
  --docker-bedrock-region REGION    AWS region (default: eu-central-1)
  --docker-bedrock-model MODEL      Model ID (default: global.anthropic.claude-sonnet-4-5-20250929-v1:0)
  --docker-image IMAGE              Docker image (default: parallel-orchestrator:latest)
  --docker-network NETWORK          Docker network name
  --docker-aws-access-key-id KEY    AWS Access Key
  --docker-aws-secret-access-key    AWS Secret Key

SLURM Options:
  --slurm-partition NAME   Partition name (default: default)
  --slurm-time TIME        Time limit (default: 01:00:00)
  --slurm-mem SIZE         Memory per job (default: 4G)
  --slurm-cpus N           CPUs per task (default: 1)
  --slurm-gpus N           GPUs per task (default: 0)
  --slurm-gpu-partition    GPU partition name

AWS ParallelCluster Options:
  --aws-cluster-name NAME  Cluster name (required)
  --aws-region REGION      AWS region (default: eu-central-1)
  --aws-s3-bucket BUCKET   S3 bucket (required)

Retry Options:
  --max-retries N          Max retry attempts (default: 3)
```

## Python API Usage

```python
from orchestrator import ParallelOrchestrator
from config import OrchestratorConfig, DockerConfig, SlurmConfig

# Threading mode (default)
orchestrator = ParallelOrchestrator(
    requirements="Build an e-commerce platform",
    output_dir="ecommerce-project"
)
orchestrator.max_executors = 10
summary = orchestrator.run()

# Docker mode with Bedrock
config = OrchestratorConfig(
    requirements="Build a todo app",
    max_executors=3,
    backend_type="docker",
    docker=DockerConfig(
        enabled=True,
        use_bedrock=True,
        bedrock_region="eu-central-1",
        planner_in_docker=True
    )
)
orchestrator = ParallelOrchestrator(
    config.requirements,
    config.output_dir,
    config=config
)
summary = orchestrator.run()
```

## Output Structure

After execution, check these files:

```bash
../outputs/parallel-orchestrator/project-name/
├── src/                     # All implementation files
├── tests/                   # All test files
├── docs/                    # Execution documentation
├── README.md                # Combined documentation
├── orchestrator.log         # Execution logs
├── execution_summary.json   # Results and metrics
├── execution_plan.json      # Task breakdown plan
├── .slurm_state/            # SLURM state (if using SLURM/AWS)
│   ├── jobs.json            # Job ID mappings
│   ├── tasks.json           # Task status
│   ├── results/             # Task results
│   ├── scripts/             # Generated sbatch scripts
│   └── logs/                # SLURM output logs
└── executor_*/              # Raw executor outputs
```

## View Output

```bash
# View execution log
cat ../outputs/parallel-orchestrator/orchestrator.log

# View execution plan
cat ../outputs/parallel-orchestrator/execution_plan.json

# View summary
cat ../outputs/parallel-orchestrator/execution_summary.json

# For SLURM: View job logs
cat ../outputs/parallel-orchestrator/.slurm_state/logs/*.out
cat ../outputs/parallel-orchestrator/.slurm_state/logs/*.err
```

## Real-World Performance

Based on production testing (January 2026):

| Project | Tasks | Files | Lines | Time | Success |
|---------|-------|-------|-------|------|---------|
| Contact form with validation | 4 | 16 | 5,671 | 188s | 100% |
| Todo list with local storage | 6 | 24 | 9,633 | 195s | 100% |

## Scaling Examples

| Requirements | Backend | Executors | Output |
|-------------|---------|-----------|--------|
| "Hello world" | Threading | 1 | 1-2 files |
| "Todo list app" | Docker | 2-3 | 16-24 files |
| "REST API" | Docker | 3-5 | 8-12 files |
| "ML pipeline" | SLURM | 10-20 | 15-25 files |
| "Distributed system" | AWS | 50-100 | 50+ files |

## Use Cases

### Local Development (Threading)
```bash
python3 orchestrator.py "Build REST API with authentication" --max-executors 4
```

### Containerized Development (Docker)
```bash
python3 orchestrator.py "Build a todo app" \
    --docker \
    --docker-use-bedrock \
    --max-executors 3 \
    --real
```

### Research Computing (SLURM)
```bash
python3 orchestrator.py "Run hyperparameter sweep" \
    --slurm \
    --slurm-partition=research \
    --slurm-gpus=1 \
    --max-executors 50
```

### Cloud ML Training (AWS)
```bash
python3 orchestrator.py "Train ensemble models on ImageNet" \
    --aws \
    --aws-cluster-name=ml-training \
    --aws-s3-bucket=ml-data \
    --slurm-gpus=4 \
    --max-executors 100
```

## Troubleshooting

### Docker Issues
**Problem:** Docker image not found
**Solution:** Run `cd docker && ./build.sh`

**Problem:** AWS Bedrock credentials error
**Solution:**
```bash
# Check credentials
aws sts get-caller-identity

# Set if needed
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

**Problem:** Model access denied
**Solution:** Request model access in AWS Bedrock console

### Threading Issues
**Problem:** Tasks timing out
**Solution:** Reduce task complexity or increase timeout

### SLURM Issues
**Problem:** Jobs pending
**Solution:** Check partition with `sinfo`, verify resources

**Problem:** Jobs failing
**Solution:** Check `.slurm_state/logs/*.err`

### AWS ParallelCluster Issues
**Problem:** S3 sync fails
**Solution:** Verify credentials with `aws s3 ls s3://bucket/`

**Problem:** Jobs not finding state
**Solution:** Check network connectivity, S3 permissions

## Key Advantages

- **Multi-Backend**: Threading, Docker, SLURM, AWS ParallelCluster
- **AWS Bedrock Support**: Use AWS credentials instead of Anthropic API keys
- **Docker Isolation**: Consistent environment, parallel containers
- **GPU Support**: `--slurm-gpus=N` for GPU workloads
- **Auto-Retry**: Failed jobs retry up to 3 times
- **Task Queue Model**: N tasks for M workers (N can be > M)
- **AI Planning**: Claude Code determines optimal task breakdown
- **Automatic Load Balancing**: Fast workers handle more tasks
- **Dependency Management**: Tasks wait for prerequisites

## Related Documentation

- **[Main README](../README.md)** - Project overview
- **[Quick Start](../parallel-orchestrator/docs/QUICKSTART.md)** - 5-minute setup
- **[Docker Backend](../parallel-orchestrator/docs/docker-backend.md)** - Docker details
- **[Docker with Bedrock](../parallel-orchestrator/docs/docker-bedrock-usage.md)** - AWS Bedrock setup
- **[Architecture](parallel-orchestrator-architecture.md)** - Detailed diagrams

---

**Last Updated:** January 2026
**Version:** 5.0 - Docker Backend with Bedrock Integration
