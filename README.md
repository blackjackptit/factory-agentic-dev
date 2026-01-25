# Factory Agentic Dev 🏭

> AI-Powered Development Orchestration System using Claude Code

An intelligent orchestration platform with two powerful systems: a **Website Generator** for full-stack applications and a **Parallel Task Orchestrator** for dynamic multi-agent execution with AI-powered task planning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Factory Agentic Dev provides two complementary AI orchestration systems:

### 1. Website Orchestrator 🌐
Automatically generates complete, production-ready web applications using specialized AI subagents (Design, Implementation, Testing).

### 2. Parallel Task Orchestrator ⚡
Intelligent task queue system where M executor workers dynamically process N tasks (N can be > M) with AI-powered planning and automatic load balancing.

---

# 🌐 Website Orchestrator

> Generate full-stack web applications automatically

## Features

### 🎨 Design Subagent
- Creates comprehensive UI/UX design specifications
- Defines component structure and hierarchy
- Specifies color schemes, typography, and spacing
- Generates accessibility guidelines
- **5-step progress logging** with detailed metrics

### ⚛️ Implementation Subagent
- Generates React components with hooks and state management
- Creates Python backend with FastAPI (routes, models, schemas)
- Configures CORS for frontend-backend integration
- Generates package.json and requirements.txt
- Creates setup documentation
- **9-step progress logging** (frontend + backend)

### 🧪 Testing Subagent
- Generates Jest unit tests for components
- Creates Cypress E2E tests for user flows
- Adds accessibility tests (ARIA, keyboard navigation)
- Provides test utilities and fixtures
- Includes coverage configuration
- **7-step progress logging** with file tracking

## What It Generates

- **React Frontend** - Modern, component-based UI with CSS styling
- **Python Backend** - FastAPI/Flask RESTful APIs with CORS configuration
- **Complete Test Suite** - Jest, Cypress, and accessibility tests
- **Documentation** - Setup instructions, API docs, testing guides

## Quick Start

### Generate a Web Application

```bash
cd orchestrator
python build_website.py "your app description"

# Or specify custom output location
python build_website.py "your app description" --output-dir ../outputs/website-orchestrator/my-app
```

**Examples:**

```bash
# Todo List Application
python build_website.py "build a todo list with add, edit, and delete features"

# Calculator App
python build_website.py "build a calculator with basic operations"

# E-commerce Product Catalog
python build_website.py "build a product catalog with shopping cart"
```

### Run the Generated Application

**Backend (Python/FastAPI):**
```bash
cd ../outputs/website-orchestrator/<project-name>/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs on: http://localhost:8000

**Frontend (React):**
```bash
cd ../outputs/website-orchestrator/<project-name>
npm install
npm start
```
Frontend runs on: http://localhost:3000

**Run Tests:**
```bash
npm test                    # Unit tests
npm run cypress:open       # E2E tests
```

## Example Output

A single command generates a complete application:

```bash
python orchestrator/build_website.py "build a todo list app"
```

**Result:** 37+ files with 137,000+ characters of production-ready code
- 10 React components
- 9 Python backend files
- 17 comprehensive test files
- Complete documentation

📖 **[Full Documentation](docs/website-orchestrator-quickstart.md)**

---

# Parallel Task Orchestrator

> AI-powered task queue system with dynamic executor allocation, SLURM HPC, AWS ParallelCluster, and AWS Batch support

## Features

### Multi-Backend Execution
- **Threading** (default): Local multi-threaded execution
- **SLURM**: HPC cluster execution with job scheduling
- **AWS ParallelCluster**: Cloud HPC with S3 state synchronization
- **AWS Batch**: Serverless batch job execution on AWS

### Flexible Executor Budget
- You specify the budget (max executors), AI decides optimal task count
- Example: Budget of 3 executors can handle 6 tasks dynamically

### AI-Powered Planning
- Uses Claude Code for intelligent complexity analysis
- Determines optimal number of tasks to create (N)
- Creates detailed task descriptions with dependencies and effort estimates
- Domain-agnostic: works for ML, games, mobile, data analytics, web, etc.

### GPU Support (SLURM/AWS)
- Request GPUs with `--slurm-gpus=N`
- Automatic `--gres=gpu:N` generation for SLURM jobs
- GPU partition selection with `--slurm-gpu-partition`

### Auto-Retry for Failed Jobs
- Configurable retry attempts (default: 3)
- Exponential backoff between retries
- Per-task retry tracking

## Quick Start

### Threading Mode (Default)
```bash
cd parallel-orchestrator

# Simple task with default budget (max 5 executors)
python3 orchestrator.py "Create a calculator function"

# Custom budget and output
python3 orchestrator.py "Build microservices platform" --max-executors 10
```

### SLURM Mode (HPC Cluster)
```bash
# Basic SLURM execution
python3 orchestrator.py "Build ML pipeline" \
    --slurm \
    --slurm-partition=compute \
    --max-executors 10

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
# AWS execution
python3 orchestrator.py "Build platform" \
    --aws \
    --aws-cluster-name=my-cluster \
    --aws-s3-bucket=my-bucket \
    --max-executors 50

# AWS with GPU
python3 orchestrator.py "Train deep learning" \
    --aws \
    --aws-cluster-name=gpu-cluster \
    --aws-s3-bucket=ml-bucket \
    --slurm-gpus=4 \
    --max-executors 20
```

### AWS Batch Mode (Serverless)
```bash
# AWS Batch execution
python3 orchestrator.py "Build a website" \
    --batch \
    --batch-job-queue=my-queue \
    --batch-job-definition=parallel-orchestrator-job \
    --batch-s3-bucket=my-bucket \
    --max-executors 10

# AWS Batch with custom resources
python3 orchestrator.py "Train ML model" \
    --batch \
    --batch-job-queue=gpu-queue \
    --batch-job-definition=ml-job-def \
    --batch-s3-bucket=ml-bucket \
    --batch-vcpus=4 \
    --batch-memory=16384 \
    --max-executors 8
```

## Architecture

```
                      ParallelOrchestrator
                              |
                      ExecutionBackend (ABC)
                /         |           |          \
   ThreadingBackend  SlurmBackend  AWSParallelCluster  AWSBatchBackend
     (in-memory)    (file-based)     (S3-synced)      (S3-synced)
```

## Command-Line Options

```bash
python3 orchestrator.py <requirements> [OPTIONS]

General:
  -o, --output-dir       Output directory
  -m, --max-executors    Max executors (default: 5)
  --real                 Use real Claude API

Backend Selection:
  --slurm                Enable SLURM backend
  --aws                  Enable AWS ParallelCluster backend
  --batch                Enable AWS Batch backend

SLURM Options:
  --slurm-partition      Partition name
  --slurm-time           Time limit (default: 01:00:00)
  --slurm-mem            Memory (default: 4G)
  --slurm-cpus           CPUs per task (default: 1)
  --slurm-gpus           GPUs per task (default: 0)
  --slurm-gpu-partition  GPU partition

AWS ParallelCluster Options:
  --aws-cluster-name     Cluster name (required)
  --aws-region           Region (default: us-east-1)
  --aws-s3-bucket        S3 bucket (required)

AWS Batch Options:
  --batch-job-queue      Job queue (required)
  --batch-job-definition Job definition (required)
  --batch-region         Region (default: us-east-1)
  --batch-s3-bucket      S3 bucket (required)
  --batch-vcpus          vCPUs per job (default: 1)
  --batch-memory         Memory in MB (default: 2048)
  --batch-timeout        Timeout in seconds (default: 3600)

Retry:
  --max-retries          Max retries (default: 3)
```

## Python API

```python
from orchestrator import ParallelOrchestrator
from config import OrchestratorConfig, SlurmConfig

# Threading mode
orchestrator = ParallelOrchestrator(
    requirements="Build enterprise system",
    output_dir="enterprise-project"
)
orchestrator.max_executors = 10
summary = orchestrator.run()

# SLURM mode (programmatic)
config = OrchestratorConfig(
    requirements="Train ML model",
    backend_type="slurm",
    slurm=SlurmConfig(enabled=True, partition="gpu", gpus_per_task=1)
)
orchestrator = ParallelOrchestrator(config.requirements, config=config)
summary = orchestrator.run()
```

## Documentation

### Website Orchestrator
- **[README](docs/website-orchestrator-readme.md)** - Complete documentation and usage guide
- **[Architecture](docs/website-orchestrator-architecture.md)** - System design and diagrams

### Parallel Task Orchestrator
- **[Quick Start Guide](docs/parallel-orchestrator-quickstart.md)** - Get started quickly
- **[Complete Overview](docs/parallel-orchestrator-readme.md)** - Full documentation
- **[Architecture](docs/parallel-orchestrator-architecture.md)** - System diagrams

---

# 📁 Project Structure

```
factory-agentic-dev/
├── orchestrator/                      # Website Orchestrator
│   ├── orchestrator.py                # Main orchestration logic
│   ├── claude_api.py                  # Claude API integration (Anthropic/Bedrock)
│   ├── build_website.py               # CLI entry point
│   ├── design_agent.py                # UI/UX design generation
│   ├── implementation_agent.py        # Full-stack code generation
│   ├── testing_agent.py               # Test suite generation
│   ├── docker_agent_executor.py       # Docker container executor
│   └── docker/                        # Docker infrastructure
│       ├── Dockerfile                 # Container image with Python SDKs
│       └── build.sh                   # Build automation script
│
├── parallel-orchestrator/             # Parallel Task Orchestrator
│   ├── orchestrator.py                # Main orchestrator with backend support
│   ├── planner_agent.py               # AI-powered planning agent
│   ├── executor_agent.py              # Individual executor implementation
│   ├── config.py                      # Configuration and CLI parsing
│   ├── slurm_executor.py              # SLURM compute node executor
│   ├── batch_executor.py              # AWS Batch container executor
│   ├── docker_executor.py             # Docker container executor
│   ├── backends/                      # Execution backends
│   │   ├── base.py                    # Abstract ExecutionBackend class
│   │   ├── threading_backend.py       # Local threading backend
│   │   ├── docker_backend.py          # Docker container backend
│   │   ├── slurm_backend.py           # SLURM HPC backend
│   │   ├── aws_parallel_cluster_backend.py  # AWS ParallelCluster backend
│   │   └── aws_batch_backend.py       # AWS Batch backend
│   └── demo.py                        # Demo script with scenarios
│
├── docs/                              # Centralized Documentation
│   ├── website-orchestrator-readme.md
│   ├── website-orchestrator-architecture.md
│   ├── parallel-orchestrator-quickstart.md
│   ├── parallel-orchestrator-readme.md
│   └── parallel-orchestrator-architecture.md
│
├── outputs/                           # Centralized Outputs (gitignored)
│   ├── website-orchestrator/          # Website orchestrator outputs
│   └── parallel-orchestrator/         # Parallel task orchestrator outputs
│
├── api/                               # Claude Code API server (optional)
└── README.md                          # This file
```

---

# 🚀 Installation

### Prerequisites

- Python 3.8+
- Node.js 18+ (for Website Orchestrator)
- [Claude Code CLI](https://github.com/anthropics/claude-code) installed and configured
- Git

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/blackjackptit/factory-agentic-dev.git
cd factory-agentic-dev
```

2. **Install Python dependencies**
```bash
# For Website Orchestrator
pip install -r orchestrator/requirements.txt

# Parallel Orchestrator uses Python standard library only
```

3. **Verify Claude Code CLI**
```bash
claude --version
```

---

# 🔧 Configuration

## Website Orchestrator Settings

Edit `orchestrator/orchestrator.py` to customize:
- Output directory location
- API timeout settings
- Subagent behavior

## Parallel Orchestrator Settings

Configure via CLI or Python API:
```bash
# CLI
python3 orchestrator.py "requirements" --max-executors 10 --output-dir my-project

# Python API
orchestrator = ParallelOrchestrator(requirements="...", output_dir="...")
orchestrator.max_executors = 10
```

---

# 📊 Comparison

| Feature | Website Orchestrator | Parallel Task Orchestrator |
|---------|---------------------|---------------------------|
| **Purpose** | Generate full-stack web apps | Execute complex tasks in parallel |
| **AI Planning** | Fixed subagent workflow | Dynamic AI-powered task breakdown |
| **Parallelization** | 3 subagents (sequential phases) | M workers process N tasks dynamically |
| **Output** | Complete web application | Task results and metrics |
| **Use Case** | Web app generation | General parallel task execution |
| **Task Count** | Fixed (3 subagents) | Dynamic (AI decides N tasks) |
| **Load Balancing** | N/A | Automatic (task queue model) |

---

# 🔍 Troubleshooting

### Claude Code CLI Issues

**Problem:** `Claude Code CLI is not available!`

**Solution:** Install Claude Code CLI and ensure it's in your PATH
```bash
which claude
claude --version
```

**Problem:** API timeout

**Solution:** Increase timeout in `claude_api.py` or orchestrator settings

### Generation Issues

**Problem:** Few or no files generated

**Solution:** Check the output logs for warnings:
```
⚠️ WARNING: Response seems too short for full code implementation
⚠️ WARNING: Very few frontend files created
```

The orchestrator includes automatic detection and warnings for incomplete responses.

---

# 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# 🙏 Acknowledgments

- Inspired by agentic AI development patterns

---

# 📞 Support

- **Issues:** [GitHub Issues](https://github.com/blackjackptit/factory-agentic-dev/issues)
- **Discussions:** [GitHub Discussions](https://github.com/blackjackptit/factory-agentic-dev/discussions)

---

# 🗺️ Roadmap

## Website Orchestrator
- [ ] Add Vue.js frontend support
- [ ] Add Django backend option
- [ ] Docker containerization templates
- [ ] CI/CD pipeline generation
- [ ] Database schema generation
- [ ] Authentication/authorization templates
- [ ] Deployment configuration (Vercel, AWS, GCP)

## Parallel Task Orchestrator
- [x] Task queue execution model
- [x] AI-powered planning
- [x] Dynamic dependency management
- [x] Automatic load balancing
- [x] SLURM HPC backend
- [x] AWS ParallelCluster backend
- [x] AWS Batch backend (serverless)
- [x] GPU support (--slurm-gpus)
- [x] Auto-retry logic with exponential backoff
- [x] File-based state management
- [x] S3 state synchronization (AWS)
- [ ] Kubernetes backend
- [ ] Real-time dashboard (Web UI)
- [ ] Distributed task queues (Redis, RabbitMQ)
- [ ] Checkpoint/resume for long-running jobs

---

# 📊 Stats

## Website Orchestrator
- **Languages:** Python, JavaScript, TypeScript
- **Frameworks:** React, FastAPI, Flask, Jest, Cypress
- **Generated Files:** 30-50 per project
- **Code Generated:** 100,000+ lines per full-stack app

## Parallel Task Orchestrator
- **Language:** Python 3.8+
- **AI Integration:** Claude Code API
- **Execution Backends:** Threading, SLURM, AWS ParallelCluster, AWS Batch
- **Execution Model:** Task queue with M workers for N tasks
- **HPC Support:** SLURM job scheduling, GPU allocation, S3 state sync
- **Serverless:** AWS Batch with container-based execution
- **Domains Supported:** Web, ML, Games, Mobile, Data, Media, etc.

---

# 📚 Documentation

- **[Documentation Index](docs/README.md)** - Complete documentation for both orchestrators
- **[Website Orchestrator Quick Start](docs/website-orchestrator-quickstart.md)** - Generate web applications
- **[Parallel Orchestrator Overview](docs/parallel-orchestrator-readme.md)** - Execute parallel tasks
- **[Architecture Diagrams](docs/parallel-orchestrator-architecture.md)** - System architecture

---

**Last Updated:** January 2026
**Version:** 4.0 - Added AWS Batch Backend Support
