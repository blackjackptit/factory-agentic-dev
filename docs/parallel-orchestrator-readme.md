# Parallel Task Orchestrator ⚡

> AI-powered task queue system with dynamic executor allocation and intelligent planning

## Overview

The Parallel Task Orchestrator is an intelligent system that coordinates multiple executor agents to work on tasks in parallel. Unlike traditional parallel processing, it uses AI to analyze complexity and create an optimal task breakdown, then dynamically allocates work across a configurable number of executors.

### Key Innovation: Task Queue Model

```
Budget: 3 executors (M workers)
AI creates: 6 tasks (N tasks, where N > M)
Execution: 3 workers continuously pull from queue of 6 tasks
Result: Optimal parallelization with automatic load balancing
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   User Requirements                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Parallel Orchestrator                       │
│  - Coordinates workflow                                  │
│  - Manages task queue                                    │
│  - Dynamic executor allocation                           │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
         ▼              ▼              ▼
┌────────────┐  ┌─────────────┐  ┌──────────────┐
│ Executor 1 │  │ Executor 2  │  │ Executor M   │
│            │  │             │  │              │
│ Pulls from │  │ Pulls from  │  │ Pulls from   │
│ task queue │  │ task queue  │  │ task queue   │
│            │  │             │  │              │
│ Completes  │  │ Completes   │  │ Completes    │
│ task_1     │  │ task_2      │  │ task_3       │
│ task_4     │  │ task_5      │  │ ...          │
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

## 🎯 Key Features

### 💰 Flexible Executor Budget
- **You specify the budget** (max executors): Set your resource constraints
- **AI decides optimal task count**: Creates N tasks (can be > budget)
- **Example**: Budget of 3 executors can dynamically handle 6 tasks

### 🤖 AI-Powered Planning
- Uses **Claude Code** for intelligent complexity analysis
- Determines optimal number of tasks to create
- **Domain-agnostic**: Works for ML, games, mobile, data analytics, web, etc.
- Automatic dependency detection and ordering

### ⚡ Task Queue Execution
- **M executor workers** process **N tasks** dynamically (N can be > M)
- Automatic load balancing: fast workers handle more tasks
- Dependency-aware: tasks wait for prerequisites automatically
- Continuous task pulling until queue is empty

### 🔄 Dynamic Task Allocation
- Executors continuously pull tasks from queue
- Check dependencies before executing
- Thread-safe task queue operations
- Graceful shutdown when queue is empty
- Real-time progress tracking

### 📦 Automatic Output Consolidation
- Consolidates all executor outputs at project root
- Organizes implementation files into `src/` directory
- Groups test files into `tests/` directory
- Combines documentation into single README
- Preserves raw executor outputs for reference

## 🚀 Quick Start

### Basic Usage

```bash
# Simple task with default budget (max 5 executors)
python3 orchestrator.py "Create a calculator function"

# Moderate task with custom budget
python3 orchestrator.py "Build todo list with backend and frontend" --max-executors 3

# Complex task with large budget
python3 orchestrator.py "Build microservices platform" --max-executors 10

# With custom output directory
python3 orchestrator.py "Build chat app" --output-dir ./my-project --max-executors 3

# Generate real code (slower but functional)
python3 orchestrator.py "Build a chess game" --max-executors 5 --real
```

### Command-Line Options

```bash
python3 orchestrator.py <requirements> [OPTIONS]

Required:
  requirements              Project requirements description

Options:
  -o, --output-dir DIR     Output directory (default: ../outputs/parallel-orchestrator/)
  -m, --max-executors N    Maximum number of executors (default: 5)
  --real                   Use real Claude API calls for actual code generation
  -h, --help               Show help message
```

## 📊 Example Execution

### Input
```bash
python3 orchestrator.py "Build a todo list app with backend API and frontend UI" --max-executors 3
```

### AI Planning Phase
```
Analyzing complexity...
✓ Complexity score: 65/100
✓ Optimal task breakdown: 6 tasks
✓ Executor budget: 3 workers

Tasks created:
1. Database schema and migrations
2. REST API endpoints
3. Authentication system
4. Frontend React components
5. State management
6. Integration tests
```

### Execution Phase
```
Spawning 3 executor workers...

[Executor-1] Starting task_1: Database schema
[Executor-2] Starting task_2: REST API endpoints
[Executor-3] Starting task_3: Authentication system
[Executor-1] ✓ Completed task_1 (45s)
[Executor-1] Starting task_4: Frontend React components
[Executor-2] ✓ Completed task_2 (52s)
[Executor-2] Starting task_5: State management
[Executor-3] ✓ Completed task_3 (48s)
[Executor-3] Starting task_6: Integration tests
[Executor-1] ✓ Completed task_4 (67s)
[Executor-2] ✓ Completed task_5 (43s)
[Executor-3] ✓ Completed task_6 (71s)

All executor workers finished
✓ Total tasks completed: 6
```

### Results
- ✅ 100% success rate
- ✅ 18 files created
- ✅ 2,847 lines of code
- ✅ 94.2% test coverage
- ✅ Execution time: 3m 12s

## 🏗️ Project Structure

### Input Structure
```
parallel-orchestrator/
├── orchestrator.py          # Main orchestrator with task queue
├── planner_agent.py         # AI-powered planning agent
├── executor_agent.py        # Individual executor implementation
├── demo.py                  # Demo script with scenarios
└── README.md               # Quick start (points to docs)
```

### Output Structure
```
../outputs/parallel-orchestrator/project-name/
├── src/                     # ✨ All implementation files
│   ├── database.py
│   ├── api.py
│   ├── auth.py
│   └── ...
├── tests/                   # ✨ All test files
│   ├── test_database.py
│   ├── test_api.py
│   └── ...
├── docs/                    # ✨ Execution documentation
│   └── execution_plan.json
├── README.md                # ✨ Combined documentation
├── orchestrator.log         # Execution logs
├── execution_summary.json   # Results and metrics
├── executor_1/              # Raw executor 1 outputs (preserved)
│   ├── task_1/
│   └── task_4/
├── executor_2/              # Raw executor 2 outputs (preserved)
│   ├── task_2/
│   └── task_5/
└── executor_3/              # Raw executor 3 outputs (preserved)
    ├── task_3/
    └── task_6/
```

## 🎓 How It Works

### Step 1: AI-Powered Complexity Analysis
The **PlannerAgent** analyzes your requirements using Claude Code:
- Estimates project scope and complexity (0-100 scale)
- Determines optimal number of tasks to create
- Considers dependencies and execution order

### Step 2: Intelligent Task Planning
Creates detailed execution plan:
- Breaks project into N independent tasks
- Identifies dependencies between tasks
- Assigns priorities and estimates duration
- Generates task descriptions and acceptance criteria

### Step 3: Dynamic Parallel Execution
- Spawns M executor workers (your specified budget)
- Workers continuously pull tasks from thread-safe queue
- Each executor:
  1. Checks if task dependencies are satisfied
  2. Executes task using Claude Code
  3. Reports results and pulls next task
- Automatic load balancing based on executor speed

### Step 4: Result Aggregation
- Collects metrics from all executors
- Calculates success rate, LOC, test coverage
- Generates execution summary

### Step 5: Output Consolidation
- Merges all executor outputs into unified structure
- Organizes files by type (src, tests, docs)
- Combines README files into single documentation
- Preserves raw executor outputs for debugging

## 💡 Use Cases

### Software Development
```bash
# Full-stack application
python3 orchestrator.py "Build e-commerce platform with product catalog, cart, and checkout" --max-executors 8

# Microservices architecture
python3 orchestrator.py "Create microservices: user service, product service, order service, payment gateway" --max-executors 6

# Mobile app
python3 orchestrator.py "Build React Native app for task management with offline sync" --max-executors 4
```

### Data & ML
```bash
# Data pipeline
python3 orchestrator.py "ETL pipeline: extract from APIs, transform data, load to warehouse" --max-executors 3

# ML model development
python3 orchestrator.py "Train classification model: data preprocessing, feature engineering, model training, evaluation" --max-executors 5
```

### Game Development
```bash
# Simple game
python3 orchestrator.py "Create 2D platformer game with physics, levels, enemies, and scoring" --max-executors 6

# Chess game (real example)
python3 orchestrator.py "Build multiplayer chess game with WebSocket, ELO rating, and game history" --max-executors 5 --real
```

## 📈 Performance Optimization

### Choosing the Right Budget

| Task Complexity | Recommended Budget | Example |
|----------------|-------------------|---------|
| Simple (1-3 tasks) | 1-2 executors | Calculator, simple utility |
| Moderate (4-8 tasks) | 3-5 executors | Todo app, blog, REST API |
| Complex (9-15 tasks) | 6-10 executors | E-commerce, CMS, dashboard |
| Very Complex (16+ tasks) | 10-15 executors | Microservices, game engine |

### Optimization Tips

1. **Start with defaults** (5 executors) and adjust based on results
2. **More executors ≠ faster** - there's a point of diminishing returns
3. **Consider dependencies** - highly dependent tasks may not benefit from parallelization
4. **Use `--real` flag judiciously** - it's slower but generates actual working code

## 🔍 Troubleshooting

### Common Issues

**Issue**: Executors timing out
- **Solution**: Increase max_executors or simplify requirements

**Issue**: Tasks failing with dependencies
- **Solution**: Check execution_plan.json to verify dependency graph

**Issue**: Low test coverage
- **Solution**: Add "with comprehensive tests" to requirements

**Issue**: Output not consolidated
- **Solution**: Check orchestrator.log for merge errors

## 📚 Additional Resources

- **[Architecture Documentation](parallel-orchestrator-architecture.md)** - Complete architecture with 9 Mermaid diagrams
- **[Quick Start Guide](parallel-orchestrator-quickstart.md)** - Step-by-step tutorial
- **[Main Documentation Index](README.md)** - All orchestrator documentation
- **[Project Repository](https://github.com/blackjackptit/factory-agentic-dev)** - Source code and issues

## 🤝 Contributing

Contributions are welcome! Please see the main project repository for guidelines.

## 📄 License

This project is part of the Factory Agentic Dev framework. See the main repository for license information.

---

**Last Updated:** January 2026

**Version:** 2.0 - Unified Documentation Structure
