# Parallel Task Orchestrator ⚡

> AI-powered task queue system with dynamic executor allocation

**📚 All documentation has been moved to the centralized location: [`../docs/`](../docs/)**

---

## 🚀 Quick Start

```bash
# Simple task with default budget (max 5 executors, outputs to ../outputs/parallel-orchestrator/)
python3 orchestrator.py "Create a calculator function"

# Moderate task with custom budget
python3 orchestrator.py "Build todo list with backend and frontend" --max-executors 3

# Complex task with large budget
python3 orchestrator.py "Build microservices platform" --max-executors 10

# View all options
python3 orchestrator.py --help
```

---

## 📖 Documentation

All documentation is now centralized in the [`docs/`](../docs/) directory:

- **[Quick Start Guide](../docs/parallel-orchestrator-quickstart.md)** - Get up and running quickly
- **[Architecture](../docs/parallel-orchestrator-architecture.md)** - Complete architecture with 9 Mermaid diagrams
- **[Documentation Index](../docs/README.md)** - Complete documentation index for all orchestrators

---

## 🎯 Key Features

### 💰 Flexible Executor Budget
- You specify the budget (max executors), AI decides optimal task count
- Example: Budget of 3 executors can handle 6 tasks dynamically

### 🤖 AI-Powered Planning
- Uses Claude Code for intelligent complexity analysis
- Determines optimal number of tasks to create (N)
- Domain-agnostic: ML, games, mobile, data analytics, web, etc.

### ⚡ Task Queue Execution
- M executor workers process N tasks dynamically (N can be > M)
- Automatic load balancing: fast workers handle more tasks
- Dependency-aware: tasks wait for prerequisites automatically

### 🔄 Dynamic Task Allocation
- Executors continuously pull tasks from queue
- Check dependencies before executing
- Graceful shutdown when queue is empty

---

## 📊 Example Execution

**Input:**
```bash
python3 orchestrator.py "Build a todo list app with backend API and frontend UI" --max-executors 3
```

**Result:**
- ✅ AI created 6 tasks for 3 executors (2:1 ratio)
- ✅ 3 executor workers spawned
- ✅ Executor-1 completed 2 tasks (task_1, task_2)
- ✅ Executor-2 completed 4 tasks (task_3, task_4, task_5, task_6)
- ✅ 100% success rate, 18 files created

---

## 🏗️ Project Structure

```
parallel-orchestrator/
├── orchestrator.py          # Main orchestrator with task queue
├── planner_agent.py         # AI-powered planning agent
├── executor_agent.py        # Individual executor implementation
├── demo.py                  # Demo script with scenarios
├── output/                  # Generated outputs
└── README.md               # This file (redirect to docs)
```

---

## 🔗 Quick Links

- **[Main Project README](../README.md)** - Complete project overview
- **[Centralized Docs](../docs/)** - All documentation
- **[GitHub Issues](https://github.com/blackjackptit/factory-agentic-dev/issues)** - Report issues
- **[GitHub Discussions](https://github.com/blackjackptit/factory-agentic-dev/discussions)** - Ask questions

---

**For complete documentation, please visit [`docs/`](../docs/)**
