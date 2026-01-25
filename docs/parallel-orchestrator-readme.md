# Parallel Task Orchestrator

> AI-powered task queue system with dynamic executor allocation, Docker containers, SLURM HPC, and AWS ParallelCluster support

## Overview

The Parallel Task Orchestrator is an intelligent system that coordinates multiple executor agents to work on tasks in parallel. It uses AI to analyze complexity and create an optimal task breakdown, then dynamically allocates work across configurable execution backends.

### Key Innovation: Multi-Backend Execution

```
Backends Available:
1. Threading (default) - Local multi-threaded execution
2. Docker - Containerized parallel execution with AWS Bedrock
3. SLURM - HPC cluster execution with job scheduling
4. AWS ParallelCluster - Cloud HPC with S3 state sync

Budget: 3 executors (M workers)
AI creates: 6 tasks (N tasks, where N > M)
Execution: 3 workers continuously pull from queue of 6 tasks
Result: Optimal parallelization with automatic load balancing
```

## Architecture Overview

```
                                      ParallelOrchestrator
                                              |
                                      ExecutionBackend (ABC)
                            /         |           |           \
          ThreadingBackend    DockerBackend   SlurmBackend   AWSParallelCluster
             (default)        (containers)    (local HPC)     (cloud HPC)
                 |                |               |                |
            In-memory        Volume mounts    File-based       S3-synced
            threading        isolation        sbatch jobs      state mgmt
```

### Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│                   User Requirements                      │
│              + Backend Selection (--docker/--slurm/--aws)│
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Parallel Orchestrator                       │
│  - Coordinates workflow                                  │
│  - Creates appropriate backend                           │
│  - Manages task queue                                    │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
         ▼              ▼              ▼
┌────────────┐  ┌─────────────┐  ┌──────────────┐
│ Executor 1 │  │ Executor 2  │  │ Executor M   │
│            │  │             │  │              │
│ Thread/    │  │ Thread/     │  │ Thread/      │
│ Container/ │  │ Container/  │  │ Container/   │
│ SLURM Job/ │  │ SLURM Job/  │  │ SLURM Job/   │
│ AWS Job    │  │ AWS Job     │  │ AWS Job      │
└────────────┘  └─────────────┘  └──────────────┘
         │              │              │
         └──────────────┴──────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Consolidated Output                         │
│  - src/       : All implementation files                 │
│  - tests/     : All test files                           │
│  - docs/      : Documentation                            │
│  - README.md  : Combined documentation                   │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### Flexible Executor Budget
- **You specify the budget** (max executors): Set your resource constraints
- **AI decides optimal task count**: Creates N tasks (can be > budget)
- **Example**: Budget of 3 executors can dynamically handle 6 tasks

### AI-Powered Planning
- Uses **Claude Code** for intelligent complexity analysis
- Determines optimal number of tasks to create
- **Domain-agnostic**: Works for ML, games, mobile, data analytics, web, etc.
- Automatic dependency detection and ordering

### Multi-Backend Support

| Backend | Use Case | State Management | Scaling |
|---------|----------|------------------|---------|
| **Threading** | Local development, small tasks | In-memory | Single machine |
| **Docker** | Parallel containers, isolation | Volume mounts | Single machine, 2-50 containers |
| **SLURM** | HPC clusters, research computing | File-based | Cluster-wide |
| **AWS ParallelCluster** | Cloud HPC, large-scale jobs | S3-synced | Multi-node cloud |

### AWS Bedrock Integration (Docker Backend)
- **No Anthropic API Key Required**: Use AWS credentials instead
- **Cost Tracking**: Bedrock usage shows up in AWS billing
- **Enterprise Integration**: Works with AWS SSO and IAM roles
- **Same Performance**: Local Docker execution with cloud AI

### Docker Planner Mode
- **Planner in Docker**: Run planner in isolated container
- **Consistent Environment**: Same Claude CLI version as executors
- **CI/CD Friendly**: Everything runs in containers

### GPU Support (SLURM/AWS)
- Request GPUs with `--slurm-gpus=N`
- Specify GPU partition with `--slurm-gpu-partition`
- Automatic `--gres=gpu:N` generation for SLURM jobs

### Auto-Retry for Failed Jobs
- Configurable retry attempts (default: 3)
- Exponential backoff between retries
- Per-task retry tracking
- Detailed failure logging

## Quick Start

### Threading Mode (Default)

```bash
# Simple task with default budget (max 5 executors)
python3 orchestrator.py "Create a calculator function"

# Moderate task with custom budget
python3 orchestrator.py "Build todo list with backend and frontend" --max-executors 3

# Complex task with large budget
python3 orchestrator.py "Build microservices platform" --max-executors 10

# Generate real code (slower but functional)
python3 orchestrator.py "Build a chess game" --max-executors 5 --real
```

### Docker Mode (Recommended for Production)

```bash
# Build Docker image first (one-time setup)
cd parallel-orchestrator/docker
./build.sh

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
```

### SLURM Mode (Local HPC)

```bash
# Basic SLURM execution
python3 orchestrator.py "Build ML pipeline" \
    --slurm \
    --slurm-partition=compute \
    --max-executors 10

# SLURM with custom resources
python3 orchestrator.py "Process large dataset" \
    --slurm \
    --slurm-partition=compute \
    --slurm-time=02:00:00 \
    --slurm-mem=16G \
    --slurm-cpus=4 \
    --max-executors 20

# SLURM with GPU
python3 orchestrator.py "Train ML models" \
    --slurm \
    --slurm-partition=gpu \
    --slurm-gpus=1 \
    --slurm-mem=32G \
    --max-executors 8
```

### AWS ParallelCluster Mode

```bash
# AWS ParallelCluster execution
python3 orchestrator.py "Build platform" \
    --aws \
    --aws-cluster-name=my-cluster \
    --aws-s3-bucket=my-bucket \
    --aws-region=eu-central-1 \
    --max-executors 50

# AWS with GPU (p3/p4 instances)
python3 orchestrator.py "Train deep learning models" \
    --aws \
    --aws-cluster-name=gpu-cluster \
    --aws-s3-bucket=ml-bucket \
    --slurm-partition=gpu \
    --slurm-gpus=1 \
    --max-executors 20
```

## Command-Line Options

```bash
python3 orchestrator.py <requirements> [OPTIONS]

Required:
  requirements              Project requirements description

General Options:
  -o, --output-dir DIR     Output directory
  -m, --max-executors N    Maximum number of executors (default: 5)
  --real                   Use real Claude API calls for actual code generation

Backend Selection (mutually exclusive):
  --docker                 Enable Docker backend
  --slurm                  Enable local SLURM backend
  --aws                    Enable AWS ParallelCluster backend

Docker Options:
  --docker-planner-in-docker        Run planner in Docker container
  --docker-use-bedrock              Use AWS Bedrock instead of Anthropic API
  --docker-bedrock-region REGION    AWS region (default: eu-central-1)
  --docker-bedrock-model MODEL      Model ID (default: global.anthropic.claude-sonnet-4-5-20250929-v1:0)
  --docker-image IMAGE              Docker image (default: parallel-orchestrator:latest)
  --docker-network NETWORK          Docker network name
  --docker-aws-access-key-id KEY    AWS Access Key ID
  --docker-aws-secret-access-key    AWS Secret Access Key
  --docker-aws-session-token        AWS Session Token (optional)

SLURM Options:
  --slurm-partition NAME   SLURM partition name (default: default)
  --slurm-time TIME        Job time limit (default: 01:00:00)
  --slurm-mem SIZE         Memory per job (default: 4G)
  --slurm-cpus N           CPUs per task (default: 1)
  --slurm-gpus N           GPUs per task (default: 0)
  --slurm-gpu-partition    GPU-specific partition name

AWS ParallelCluster Options:
  --aws-cluster-name NAME  ParallelCluster name (required for --aws)
  --aws-region REGION      AWS region (default: eu-central-1)
  --aws-s3-bucket BUCKET   S3 bucket for state sync (required for --aws)

Retry Options:
  --max-retries N          Max retry attempts for failed jobs (default: 3)
```

## State Management

### Threading Backend
- In-memory state with thread locks
- No external dependencies
- Best for: local development, quick testing

### Docker Backend
```
Host Machine:
outputs/
├── planner/                # Planner output (if using --docker-planner-in-docker)
└── parallel-orchestrator/  # Final outputs
    ├── executor_0/         # Container 0 output (volume mount)
    ├── executor_1/         # Container 1 output (volume mount)
    └── ...

Docker Containers:
- Volume mounts for input/output
- Environment variables for credentials
- Isolated execution environment
```

### SLURM Backend
```
{output_dir}/.slurm_state/
├── jobs.json           # job_id -> task_id mapping
├── tasks.json          # task status tracking
├── results/            # one JSON per completed task
├── scripts/            # generated sbatch scripts
├── logs/               # SLURM output logs
└── task_definitions/   # task JSON files
```

### AWS ParallelCluster Backend
```
Local (same as SLURM):
{output_dir}/.slurm_state/

S3 (synced):
s3://bucket/parallel-orchestrator/{run-id}/
├── state/              # sync'd to/from local
├── tasks/              # task definitions
└── results/            # completed results
```

## Project Structure

### Input Structure
```
parallel-orchestrator/
├── orchestrator.py          # Main orchestrator
├── planner_agent.py         # AI-powered planning agent
├── executor_agent.py        # Individual executor
├── config.py                # Configuration and CLI parsing
├── docker_planner.py        # Docker planner script
├── docker_executor.py       # Docker executor script
├── slurm_executor.py        # SLURM compute node script
├── docker/                  # Docker image build
│   ├── Dockerfile           # Multi-stage container image
│   ├── build.sh             # Build automation script
│   └── README.md            # Docker setup guide
├── backends/
│   ├── __init__.py          # Package exports
│   ├── base.py              # Abstract base class
│   ├── threading_backend.py # Threading implementation
│   ├── docker_backend.py    # Docker implementation
│   ├── slurm_backend.py     # SLURM implementation
│   └── aws_parallel_cluster_backend.py  # AWS ParallelCluster
└── demo.py                  # Demo script with scenarios
```

### Output Structure
```
../outputs/parallel-orchestrator/project-name/
├── src/                     # All implementation files
├── tests/                   # All test files
├── docs/                    # Execution documentation
├── README.md                # Combined documentation
├── orchestrator.log         # Execution logs
├── execution_summary.json   # Results and metrics
├── .slurm_state/            # SLURM state (if using SLURM/AWS)
└── executor_*/              # Raw executor outputs
```

## How It Works

### Step 1: AI-Powered Complexity Analysis
The **PlannerAgent** analyzes your requirements using Claude Code:
- Estimates project scope and complexity (0-100 scale)
- Determines optimal number of tasks to create
- Considers dependencies and execution order

### Step 2: Backend Creation
Based on CLI flags, creates appropriate execution backend:
- **Threading**: In-memory, thread-based execution
- **Docker**: Container-based with volume mounts and environment variables
- **SLURM**: File-based state, sbatch job submission
- **AWS ParallelCluster**: S3-synced state, ParallelCluster integration

### Step 3: Task Submission
- Tasks are submitted to the backend
- Dependencies are tracked
- State is initialized (memory/volumes/files/S3)

### Step 4: Parallel Execution
- **Threading**: Worker threads pull from queue
- **Docker**: Containers started with task assignments, results written to volumes
- **SLURM**: Jobs submitted with `--dependency=afterok:job_id`
- **AWS ParallelCluster**: Same as SLURM + S3 sync for cross-node state

### Step 5: Result Collection & Retry
- Results collected from all executors
- Failed tasks are retried (up to `--max-retries`)
- Final metrics calculated

### Step 6: Output Consolidation
- Merges all executor outputs into unified structure
- Organizes files by type (src, tests, docs)
- Preserves raw executor outputs for debugging

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
python3 orchestrator.py "Run hyperparameter sweep for ML model" \
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

### Data Pipeline Processing
```bash
python3 orchestrator.py "ETL pipeline: extract, transform, load" \
    --slurm \
    --slurm-partition=data \
    --slurm-mem=64G \
    --max-executors 20
```

## Performance Optimization

### Choosing the Right Backend

| Scenario | Recommended Backend | Why |
|----------|---------------------|-----|
| Quick prototyping | Threading | No setup, instant start |
| Production code gen | Docker | Isolation, Bedrock integration |
| University cluster | SLURM | Native integration |
| Large-scale ML | AWS ParallelCluster | Scalable, GPU support |
| CI/CD pipelines | Docker | Containerizable, reproducible |
| Long-running jobs | SLURM/AWS | Job persistence, recovery |

### Choosing the Right Budget

| Task Complexity | Recommended Budget | Example |
|----------------|-------------------|---------|
| Simple (1-3 tasks) | 1-2 executors | Calculator, simple utility |
| Moderate (4-8 tasks) | 3-5 executors | Todo app, blog, REST API |
| Complex (9-15 tasks) | 6-10 executors | E-commerce, CMS, dashboard |
| Very Complex (16+ tasks) | 10-50 executors | Microservices, ML pipelines |

## Real-World Performance

Based on production testing (January 2026):

| Metric | Result |
|--------|--------|
| **Success Rate** | 100% (10/10 tests) |
| **Avg Time per Project** | 3-4 minutes |
| **Files Generated** | 16-24 per project |
| **Lines of Code** | 5,000-10,000 per project |
| **Parallel Efficiency** | 3x speedup with 3 executors |

**Test Projects**:
- Contact form with validation (4 tasks, 16 files, 5,671 LOC, 188s)
- Todo list with local storage (6 tasks, 24 files, 9,633 LOC, 195s)

## Troubleshooting

### Docker Issues

**Issue**: Docker image not found
- **Solution**: Run `cd docker && ./build.sh`

**Issue**: AWS Bedrock credentials error
- **Solution**: Check credentials with `aws sts get-caller-identity`
- **Solution**: Set env vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

**Issue**: Model access denied
- **Solution**: Request model access in AWS Bedrock console

### SLURM Issues

**Issue**: Jobs pending indefinitely
- **Solution**: Check partition availability with `sinfo`
- **Solution**: Verify resource requests match available nodes

**Issue**: Jobs failing immediately
- **Solution**: Check `.slurm_state/logs/*.err` for error details
- **Solution**: Verify Python environment on compute nodes

### AWS ParallelCluster Issues

**Issue**: S3 sync fails
- **Solution**: Verify AWS credentials and bucket permissions
- **Solution**: Check `aws s3 ls s3://bucket/` works

**Issue**: Jobs not finding state
- **Solution**: Ensure shared filesystem or S3 sync is working
- **Solution**: Check network connectivity between nodes

### General Issues

**Issue**: Executors timing out
- **Solution**: Increase `--slurm-time` for SLURM jobs
- **Solution**: Simplify requirements or reduce task count

**Issue**: Retry exhausted
- **Solution**: Check logs for root cause
- **Solution**: Increase `--max-retries` if transient failures

## Additional Resources

- **[Architecture Documentation](parallel-orchestrator-architecture.md)** - Complete architecture with diagrams
- **[Quick Start Guide](parallel-orchestrator-quickstart.md)** - Step-by-step tutorial
- **[Main README](../README.md)** - Project overview
- **[Docker Backend](../parallel-orchestrator/docs/docker-backend.md)** - Docker details
- **[Docker with Bedrock](../parallel-orchestrator/docs/docker-bedrock-usage.md)** - AWS Bedrock setup

## Contributing

Contributions are welcome! Please see the main project repository for guidelines.

## License

This project is part of the Factory Agentic Dev framework. See the main repository for license information.

---

**Last Updated:** January 2026

**Version:** 5.0 - Docker Backend with Bedrock Integration
