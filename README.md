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

# ⚡ Parallel Task Orchestrator

> AI-powered task queue system with dynamic executor allocation

## Features

### 💰 Flexible Executor Budget
- You specify the budget (max executors), AI decides optimal task count
- Example: Budget of 3 executors can handle 6 tasks dynamically

### 🤖 AI-Powered Planning
- Uses Claude Code for intelligent complexity analysis
- Determines optimal number of tasks to create (N)
- Creates detailed task descriptions with dependencies and effort estimates
- Domain-agnostic: works for ML, games, mobile, data analytics, web, etc.

### ⚡ Task Queue Execution
- M executor workers process N tasks dynamically (N can be > M)
- Automatic load balancing: fast workers handle more tasks
- Dependency-aware: tasks wait for prerequisites automatically
- Thread-safe operations with proper locks

### 🔄 Dynamic Task Allocation
- Executors continuously pull tasks from queue
- Check dependencies before executing
- Graceful shutdown when queue is empty

## How It Works

```
1. User sets budget: --max-executors 3
2. AI analyzes and creates 6 tasks
3. Orchestrator spawns 3 executor workers
4. Workers continuously pull tasks from queue
5. Check dependencies before executing
6. Complete task and pick next available
7. Shut down when all tasks done
```

## Quick Start

```bash
cd parallel-orchestrator

# Simple task with default budget (max 5 executors)
python3 orchestrator.py "Create a calculator function"

# Moderate task with custom budget
python3 orchestrator.py "Build todo list with backend and frontend" --max-executors 3

# Complex task with large budget
python3 orchestrator.py "Build microservices platform" --max-executors 10

# Custom output directory (default: ../outputs/parallel-orchestrator/)
python3 orchestrator.py "Your requirements" --output-dir ../outputs/parallel-orchestrator/my-project --max-executors 8

# View all options
python3 orchestrator.py --help
```

## Example Execution

**Input:**
```bash
python3 orchestrator.py "Build a todo list app with backend API and frontend UI" --max-executors 3
```

**Result:**
- ✅ AI created 6 tasks for 3 executors (2:1 ratio)
- ✅ 3 executor workers spawned
- ✅ Dynamic task allocation worked perfectly
- ✅ Executor-1 completed 2 tasks (task_1, task_2)
- ✅ Executor-2 completed 4 tasks (task_3, task_4, task_5, task_6)
- ✅ Executor-3 correctly shut down (dependencies covered)
- ✅ 100% success rate, 18 files created, 1400 LOC

## Task Queue Benefits

✅ **Better Parallelization**: Can create more tasks than executors (e.g., 10 tasks for 5 executors)
✅ **Automatic Load Balancing**: Fast executors naturally handle more tasks
✅ **Dependency Management**: Tasks automatically wait for prerequisites
✅ **No Idle Workers**: Executors continuously work until queue is empty
✅ **Resource Efficiency**: Only spawn workers needed, never more than budget

## Python API

```python
from orchestrator import ParallelOrchestrator

# Create orchestrator with budget
orchestrator = ParallelOrchestrator(
    requirements="Build enterprise system with microservices",
    output_dir="enterprise-project"
)
orchestrator.max_executors = 10  # Budget of 10 executors

# Run orchestration (planner decides optimal task count)
summary = orchestrator.run()

# Check results
print(f"Tasks created: {summary['total_tasks']}")
print(f"Executors used: {min(summary['total_tasks'], 10)}")
print(f"Success rate: {summary['success_rate']}")
print(f"Files created: {summary['total_files_created']}")
```

📖 **[Quick Start Guide](docs/parallel-orchestrator-quickstart.md)** | 🏗️ **[Architecture](docs/parallel-orchestrator-architecture.md)**

---

# 📁 Project Structure

```
factory-agentic-dev/
├── orchestrator/                      # Website Generator
│   ├── orchestrator.py                # Main orchestration logic
│   ├── claude_api.py                  # Claude Code CLI integration
│   ├── build_website.py               # CLI entry point
│   └── subagents/
│       ├── design_agent.py            # UI/UX design generation
│       ├── implementation_agent.py    # Full-stack code generation
│       └── testing_agent.py           # Test suite generation
│
├── parallel-orchestrator/             # Parallel Task Orchestrator
│   ├── orchestrator.py                # Main orchestrator with task queue
│   ├── planner_agent.py               # AI-powered planning agent
│   ├── executor_agent.py              # Individual executor implementation
│   └── demo.py                        # Demo script with scenarios
│
├── docs/                              # Centralized Documentation
│   ├── website-orchestrator-quickstart.md
│   ├── website-orchestrator-structure.md
│   ├── website-orchestrator-test-results.md
│   ├── parallel-orchestrator-quickstart.md
│   └── parallel-orchestrator-architecture.md
│
├── outputs/                           # Centralized Outputs (gitignored)
│   ├── website-orchestrator/          # Website generator outputs
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
- [ ] Cloud deployment (distributed workers)
- [ ] Real-time dashboard (Web UI)
- [ ] Quality scoring
- [ ] Auto-retry logic
- [ ] Resource limits per worker
- [ ] Distributed task queues (Redis, RabbitMQ)

---

# 📊 Stats

## Website Orchestrator
- **Languages:** Python, JavaScript, TypeScript
- **Frameworks:** React, FastAPI, Flask, Jest, Cypress
- **Generated Files:** 30-50 per project
- **Code Generated:** 100,000+ lines per full-stack app

## Parallel Task Orchestrator
- **Language:** Python (standard library only)
- **AI Integration:** Claude Code API
- **Execution Model:** Task queue with M workers for N tasks
- **Domains Supported:** Web, ML, Games, Mobile, Data, Media, etc.

---

# 📚 Documentation

- **[Documentation Index](docs/README.md)** - Complete documentation for both orchestrators
- **[Website Orchestrator Quick Start](docs/website-orchestrator-quickstart.md)** - Generate web applications
- **[Parallel Orchestrator Overview](docs/parallel-orchestrator-readme.md)** - Execute parallel tasks
- **[Architecture Diagrams](docs/parallel-orchestrator-architecture.md)** - System architecture

---

**Last Updated:** January 2026
**Version:** 2.0 - Unified Documentation Structure
