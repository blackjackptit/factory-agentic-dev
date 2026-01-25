# Documentation Index 📚

Centralized documentation for Factory Agentic Dev - covering both the Website Orchestrator and Parallel Task Orchestrator.

---

## 🌐 Website Orchestrator Documentation

### Quick Start
- **[Quick Start Guide](website-orchestrator-quickstart.md)** - Get started with generating web applications
- **[Project Structure](website-orchestrator-structure.md)** - Detailed project architecture
- **[Test Results](website-orchestrator-test-results.md)** - Example test results and validation

### Key Features
- Design Subagent - UI/UX design generation
- Implementation Subagent - Full-stack code generation
- Testing Subagent - Comprehensive test suite creation

### Example Output
- 10 React components
- 9 Python backend files
- 17 comprehensive test files
- Complete documentation

---

## ⚡ Parallel Task Orchestrator Documentation

### Quick Start
- **[Overview & Features](parallel-orchestrator-readme.md)** - Complete system overview and usage guide
- **[Quick Start Guide](parallel-orchestrator-quickstart.md)** - Get up and running quickly
- **[Architecture](parallel-orchestrator-architecture.md)** - Complete architecture with 9 Mermaid diagrams

### Key Capabilities
- **AI-Powered Planning** - Claude Code determines optimal task breakdown
- **Multi-Backend Support** - Threading, Docker, SLURM HPC, AWS ParallelCluster
- **AWS Bedrock Integration** - Use AWS credentials instead of Anthropic API keys
- **Docker Isolation** - Containerized parallel execution with consistent environment
- **Task Queue Model** - M workers process N tasks dynamically (N can be > M)
- **Automatic Load Balancing** - Fast workers handle more tasks
- **Dependency Management** - Tasks wait for prerequisites automatically

### Execution Model
```
Budget: 3 executors
AI creates: 6 tasks
Execution: 3 workers work through 6 tasks dynamically
Result: Optimal parallelization with automatic load balancing
```

---

## 📖 Documentation Structure

```
docs/
├── README.md                                          # This index
│
├── website-orchestrator-quickstart.md                 # Website generator quick start
├── website-orchestrator-structure.md                  # Website project structure
├── website-orchestrator-test-results.md               # Website test results
│
├── parallel-orchestrator-readme.md                    # Parallel orchestrator overview
├── parallel-orchestrator-quickstart.md                # Parallel quick start guide
└── parallel-orchestrator-architecture.md              # Architecture with 9 Mermaid diagrams
```

---

## 🔍 Finding What You Need

### I want to...

**Generate a full-stack web application**
→ Start with [Website Orchestrator Quick Start](website-orchestrator-quickstart.md)

**Execute tasks in parallel with AI planning**
→ Start with [Parallel Orchestrator Quick Start](parallel-orchestrator-quickstart.md)

**Understand the system architecture**
→ See [Website Project Structure](website-orchestrator-structure.md) or [Parallel Architecture](parallel-orchestrator-architecture.md)

**Learn about parallel task orchestration**
→ Read [Parallel Orchestrator Overview](parallel-orchestrator-readme.md)

**See example results and metrics**
→ Check [Website Test Results](website-orchestrator-test-results.md)

---

## 📊 Quick Comparison

| Feature | Website Orchestrator | Parallel Task Orchestrator |
|---------|---------------------|---------------------------|
| **Purpose** | Generate web apps | Execute parallel tasks |
| **AI Usage** | Fixed workflow | Dynamic task planning |
| **Backends** | Threading | Threading, Docker, SLURM, AWS |
| **Parallelization** | 3 sequential subagents | M workers, N tasks (N > M) |
| **Output** | Complete web app | Task results & metrics |
| **Bedrock Support** | No | Yes (Docker backend) |
| **Documentation** | [Quick Start](website-orchestrator-quickstart.md) | [Overview](parallel-orchestrator-readme.md) |

---

## 🚀 Getting Started

1. **Choose Your Tool:**
   - Building a web application? → Website Orchestrator
   - Need parallel task execution? → Parallel Task Orchestrator

2. **Read the Documentation:**
   - Follow the quick start guide for your chosen tool
   - Review the architecture documentation

3. **Run Your First Task:**
   - Website: `python orchestrator/build_website.py "your app"`
   - Parallel: `python parallel-orchestrator/orchestrator.py "your requirements"`

---

## 📞 Additional Resources

- **Main README:** [../README.md](../README.md) - Complete project overview
- **Website Orchestrator Code:** [../orchestrator/](../orchestrator/)
- **Parallel Orchestrator Code:** [../parallel-orchestrator/](../parallel-orchestrator/)
- **GitHub Issues:** [Report Issues](https://github.com/blackjackptit/factory-agentic-dev/issues)
- **GitHub Discussions:** [Ask Questions](https://github.com/blackjackptit/factory-agentic-dev/discussions)

---

**Last Updated:** January 2026

**Version:** 5.0 - Docker Backend with Bedrock Integration
