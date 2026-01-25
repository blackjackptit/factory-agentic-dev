# Parallel Task Orchestrator

A production-ready system for parallel code generation using Claude AI with multiple execution backends.

## Overview

The Parallel Task Orchestrator automatically:
1. **Analyzes** project complexity using AI
2. **Plans** optimal task breakdown and execution strategy
3. **Executes** tasks in parallel across multiple workers
4. **Aggregates** results into a unified codebase

## Key Features

- ✅ **Intelligent Planning**: AI-powered complexity analysis and task decomposition
- ✅ **Parallel Execution**: Multiple executors working simultaneously
- ✅ **Multiple Backends**: Docker, AWS Batch, SLURM, AWS ParallelCluster
- ✅ **AWS Bedrock Support**: Use AWS credentials instead of Anthropic API keys
- ✅ **Docker Planner**: Run planner in isolated container
- ✅ **Production Ready**: 100% success rate in testing

## Quick Start

### Prerequisites

- **Docker**: For Docker backend (recommended for local development)
- **AWS Account**: For Bedrock authentication (optional, alternative to Anthropic API)
- **Claude API Key** OR **AWS Bedrock Access**: One of these is required

### 1. Build Docker Image

```bash
cd parallel-orchestrator/docker
./build.sh
```

### 2. Run Your First Project

#### Using AWS Bedrock (Recommended)

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# Generate a complete application
python3 orchestrator.py "Build a todo list app with add/delete/complete" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --max-executors 3 \
    --real
```

#### Using Anthropic API

```bash
# Set API key
export ANTHROPIC_API_KEY="your-key"

# Generate a complete application
python3 orchestrator.py "Build a contact form" \
    --docker \
    --docker-planner-in-docker \
    --max-executors 2 \
    --real
```

## Configuration

### Default Settings

- **Region**: `eu-central-1`
- **Model**: `global.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **Max Executors**: 5
- **Backend**: Threading (local)

### CLI Options

#### Core Options
```bash
--max-executors N         # Number of parallel workers (default: 5)
--real                    # Use real Claude API (omit for simulation)
--output-dir DIR          # Output directory for generated code
```

#### Docker Backend Options
```bash
--docker                              # Enable Docker backend
--docker-planner-in-docker            # Run planner in Docker
--docker-image IMAGE                  # Docker image (default: parallel-orchestrator:latest)
--docker-network NETWORK              # Docker network name
```

#### AWS Bedrock Options
```bash
--docker-use-bedrock                  # Use AWS Bedrock instead of Anthropic API
--docker-bedrock-region REGION        # AWS region (default: eu-central-1)
--docker-bedrock-model MODEL          # Model ID (default: global.anthropic...)
--docker-aws-access-key-id KEY        # AWS Access Key
--docker-aws-secret-access-key KEY    # AWS Secret Key
--docker-aws-session-token TOKEN      # AWS Session Token (optional)
```

#### AWS Batch Options
```bash
--batch                               # Enable AWS Batch backend
--batch-job-queue QUEUE               # Batch job queue name
--batch-job-definition DEF            # Batch job definition name
--batch-region REGION                 # AWS region (default: eu-central-1)
--batch-s3-bucket BUCKET              # S3 bucket for state
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 Orchestrator                    │
│  - Coordinates workflow                         │
│  - Manages backends                             │
└────────────┬────────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼──────┐
│ Planner  │    │ Executors │
│  Agent   │    │  (1..N)   │
│          │    │           │
│ - Analyze│    │ - Generate│
│ - Plan   │    │ - Execute │
└──────────┘    └───────────┘
```

### Execution Backends

| Backend | Use Case | Infrastructure |
|---------|----------|----------------|
| **Threading** | Local dev, testing | Single machine |
| **Docker** | Local parallel, isolation | Docker containers |
| **AWS Batch** | Cloud, large scale | AWS Fargate/EC2 |
| **SLURM** | HPC clusters | SLURM scheduler |
| **AWS ParallelCluster** | AWS HPC | SLURM on AWS |

## Examples

### Simple Web Application

```bash
python3 orchestrator.py "Build a landing page with contact form" \
    --docker \
    --docker-use-bedrock \
    --max-executors 2 \
    --real
```

### Full-Stack Application

```bash
python3 orchestrator.py "Build a task management system with:
- React frontend with TypeScript
- Node.js/Express backend
- PostgreSQL database
- Authentication
- REST API
- Docker setup" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --max-executors 8 \
    --real \
    --output-dir outputs/task-manager
```

### With Custom Model

```bash
python3 orchestrator.py "Build a calculator app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-model "anthropic.claude-3-5-sonnet-20240620-v1:0" \
    --max-executors 2 \
    --real
```

## Documentation

- **[Docker Backend](docs/docker-backend.md)** - Local Docker execution
- **[Docker with Bedrock](docs/docker-bedrock-usage.md)** - AWS Bedrock setup and usage
- **[Docker Planner](docs/docker-planner.md)** - Running planner in Docker
- **[Bedrock Model Setup](docs/bedrock-model-setup.md)** - Model configuration and troubleshooting

## Performance

Based on real-world testing:

| Metric | Value |
|--------|-------|
| **Success Rate** | 100% |
| **Average Time** | ~3 minutes per application |
| **Files Generated** | 16-24 per project |
| **Lines of Code** | 5,000-10,000 per project |
| **Parallel Efficiency** | Near-linear scaling up to 8 executors |

## Requirements

### Python Dependencies
- Python 3.9+
- boto3 (for AWS integration)
- docker (for Docker backend)

### External Dependencies
- Docker (for Docker backend)
- AWS CLI (for AWS Batch/Bedrock)
- Claude Code CLI (installed in Docker image)

## Testing

Run in simulation mode (no API calls):

```bash
python3 orchestrator.py "Build a simple app" \
    --docker \
    --max-executors 2
```

Run with real code generation:

```bash
python3 orchestrator.py "Build a simple app" \
    --docker \
    --docker-use-bedrock \
    --max-executors 2 \
    --real
```

## Project Structure

```
parallel-orchestrator/
├── orchestrator.py           # Main orchestrator
├── planner_agent.py          # Planning agent
├── executor_agent.py         # Execution agent
├── config.py                 # Configuration management
├── docker_planner.py         # Docker planner script
├── docker_executor.py        # Docker executor script
├── batch_executor.py         # AWS Batch executor script
├── backends/                 # Execution backends
│   ├── base.py
│   ├── docker_backend.py
│   ├── aws_batch_backend.py
│   └── ...
├── docker/                   # Docker image
│   ├── Dockerfile
│   ├── build.sh
│   └── README.md
└── docs/                     # Documentation
    ├── docker-backend.md
    ├── docker-bedrock-usage.md
    ├── docker-planner.md
    └── bedrock-model-setup.md
```

## Troubleshooting

### Docker Image Not Found

```bash
cd parallel-orchestrator/docker
./build.sh
```

### AWS Bedrock Authentication

```bash
# Check credentials
aws sts get-caller-identity

# List available models
aws bedrock list-foundation-models --region eu-central-1
```

### Model Access Error

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access for Claude models
4. Wait for approval (usually instant)

## Best Practices

1. **Start Small**: Test with 2-3 executors first
2. **Use Simulation**: Test workflows without API costs
3. **Monitor Resources**: Watch Docker/AWS resource usage
4. **Version Control**: Tag Docker images for reproducibility
5. **Credentials**: Use environment variables, never hardcode

## Contributing

This is a research/development project. For production use:

1. Review and test in your environment
2. Adjust configurations for your use case
3. Monitor costs (AWS Bedrock charges per token)
4. Implement additional error handling as needed

## License

[Specify your license here]

## Support

For issues:
1. Check documentation in `docs/`
2. Review test results in `outputs/TEST_RESULTS_SUMMARY.md`
3. Check Docker logs: `docker logs <container-name>`
4. Verify AWS Bedrock access in console

## Acknowledgments

- Built with Claude AI by Anthropic
- Uses AWS Bedrock for cloud AI inference
- Docker for containerization
- AWS Batch for serverless batch processing
