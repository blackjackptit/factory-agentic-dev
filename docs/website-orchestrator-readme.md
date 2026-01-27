# Website Orchestrator

An intelligent AI-powered system that coordinates three specialized agents to build complete websites from natural language requirements. Supports three execution modes: Claude CLI (local), Docker containers, and direct SDK calls with Anthropic API or AWS Bedrock.

## Overview

The Website Orchestrator automates the entire website development process through three sequential AI agents:

1. **🎨 Design Agent** - Analyzes requirements and creates comprehensive UI/UX specifications
2. **⚛️ Implementation Agent** - Builds React components and project structure
3. **🧪 Testing Agent** - Generates Jest/React Testing Library test suites

### Key Features

- **Sequential Agent Workflow**: Each agent builds on the previous agent's output
- **Three Execution Modes**: Claude CLI (local), Docker containers, or direct SDK calls
- **Flexible AI Backend**: Use Anthropic API or AWS Bedrock for inference
- **CLI + Bedrock Support**: Use CLAUDE_CODE_USE_BEDROCK=1 for Bedrock via CLI
- **Context Preservation**: Full traceability from requirements to tests
- **Production Ready**: Docker support for reproducible builds

## Quick Start

### Prerequisites

**For Claude CLI Mode (Local - Recommended):**
- Python 3.10+
- Claude CLI installed (`claude` command available)
- AWS credentials (if using Bedrock via CLAUDE_CODE_USE_BEDROCK=1)
- Or Anthropic API key (for direct API usage)

**For Docker Mode:**
- Docker installed and running
- AWS credentials (for Bedrock mode)

**For SDK Mode:**
- Python 3.10+
- `anthropic` or `boto3` Python package
- Anthropic API key or AWS credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/blackjackptit/factory-agentic-dev.git
cd factory-agentic-dev
```

2. Build the Docker image (if using Docker mode):
```bash
cd orchestrator/docker
./build.sh
```

### Basic Usage

**Claude CLI with AWS Bedrock (Recommended):**
```bash
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

python orchestrator/build_website.py "Build a todo list app with add, edit, and delete functionality"
```

**Claude CLI with Anthropic (Default):**
```bash
# Uses default Claude CLI configuration
python orchestrator/build_website.py "Build a blog website with posts and comments"
```

**Docker execution with AWS Bedrock:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

python orchestrator/build_website.py "Build a dashboard app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1
```

## Architecture

See [Website Orchestrator Architecture](website-orchestrator-architecture.md) for detailed system design, component diagrams, and execution flows.

### System Flow

```
User Requirements
       ↓
Design Agent → Design Specifications
       ↓
Implementation Agent → React Components + Setup
       ↓
Testing Agent → Test Suite
       ↓
Complete Website Package
```

## CLI Reference

### Basic Command

```bash
python build_website.py <requirements> [options]
```

### Required Arguments

- `requirements` - Natural language description of the website to build

### Optional Arguments

#### General Options
- `--project-dir DIR` - Project directory (default: current directory)
- `--output-dir DIR` - Output directory (default: ../outputs/website-orchestrator/)

#### Docker Execution
- `--docker` - Run agents in Docker containers
- `--docker-image IMAGE` - Docker image to use (default: orchestrator-agents:latest)

#### AWS Bedrock Options
- `--docker-use-bedrock` - Use AWS Bedrock instead of Anthropic API
- `--docker-bedrock-region REGION` - AWS region (default: eu-central-1)
- `--docker-bedrock-model MODEL` - Bedrock model ID (default: global.anthropic.claude-sonnet-4-5-20250929-v1:0)

## Examples

### Simple Todo App (Local)

```bash
python build_website.py "Create a todo list app with these features:
- Add new tasks
- Mark tasks as complete
- Delete tasks
- Filter by status (all/active/completed)
- Responsive design"
```

### E-commerce Site (Docker + Bedrock)

```bash
python build_website.py "Build an e-commerce website with:
- Product catalog with search and filters
- Shopping cart
- Checkout flow
- User authentication
- Order history
- Admin dashboard" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region us-east-1
```

### Blog Platform (Custom Output)

```bash
python build_website.py "Create a blog platform with:
- Markdown post editor
- Category management
- Comments system
- User profiles
- RSS feed" \
    --output-dir ./my-blog-output \
    --docker
```

### Dashboard Application

```bash
python build_website.py "Build an analytics dashboard with:
- Data visualization charts
- Real-time updates
- Export to PDF/Excel
- User permissions
- Dark mode support" \
    --docker \
    --docker-use-bedrock
```

## Output Structure

After execution, the orchestrator generates:

```
outputs/website-orchestrator/
├── design/
│   ├── design_spec.md          # Complete design specifications
│   └── design_phase.json       # Raw agent output
├── implementation/
│   ├── components/             # React component code
│   ├── styles/                 # CSS/styling files
│   ├── package.json            # Dependencies
│   ├── setup_instructions.md   # How to run the project
│   └── implementation_phase.json
├── testing/
│   ├── tests/                  # Jest test files
│   ├── test_plan.md           # Testing strategy
│   └── testing_phase.json
└── orchestration_report.json   # Execution metrics
```

## Execution Modes

### Local Mode (Claude CLI)

**Advantages:**
- Fast iteration
- Direct feedback
- Lower latency
- No Docker overhead
- Works with both Anthropic API and AWS Bedrock

**Use when:**
- Rapid prototyping
- Development iteration
- Testing requirements
- Local development with Claude CLI installed

**Example with Bedrock (Recommended):**
```bash
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

python build_website.py "Build a calculator app"
```

**Example with Anthropic API:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python build_website.py "Build a calculator app"
```

### Docker Mode

**Advantages:**
- Environment isolation
- Reproducible builds
- Production-ready
- No local dependencies

**Use when:**
- Production deployment
- Team collaboration
- CI/CD pipelines
- Consistent environments

**Example:**
```bash
python build_website.py "Build a calculator app" \
    --docker \
    --docker-use-bedrock
```

## Configuration

### Environment Variables

#### Claude CLI with Bedrock (Recommended)
```bash
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."  # Optional for temporary credentials
```

#### Claude CLI with Anthropic API
```bash
# Uses default Claude CLI configuration
# No additional environment variables needed if Claude CLI is configured
export ANTHROPIC_API_KEY="sk-ant-..."  # Optional override
```

#### AWS Bedrock SDK Mode (Docker)
```bash
export USE_BEDROCK=1
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."  # Optional
export BEDROCK_REGION="eu-central-1"
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

#### Anthropic API SDK Mode
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Docker Configuration

Build custom image with additional tools:

```dockerfile
# Custom Dockerfile
FROM orchestrator-agents:latest

# Install additional tools
RUN apt-get update && apt-get install -y nodejs npm

# Add custom configuration
COPY custom_config.json /workspace/
```

Build and use:
```bash
docker build -t my-orchestrator:v1 .

python build_website.py "Build app" \
    --docker \
    --docker-image my-orchestrator:v1
```

## Agent Details

### Design Agent

**Input:** User requirements
**Output:** Comprehensive design specifications

**Generates:**
- Component hierarchy
- Page layouts
- Styling guidelines
- User flow diagrams
- Responsive design considerations

**Example Output:**
```markdown
# Design Specifications

## Component Structure
- App (root)
  - Header (navigation)
  - TodoList (main container)
    - TodoItem (individual task)
    - AddTodo (input form)
  - Footer (stats and filters)

## Styling
- Primary color: #007bff
- Font family: Inter, sans-serif
- Mobile-first responsive design
...
```

### Implementation Agent

**Input:** Design specifications
**Output:** Complete React project

**Generates:**
- React components (JSX/TSX)
- CSS/styled-components
- package.json with dependencies
- Project structure
- Setup instructions
- Build configuration

**Example Output:**
```javascript
// TodoItem.jsx
import React from 'react';
import './TodoItem.css';

const TodoItem = ({ task, onToggle, onDelete }) => {
  return (
    <div className={`todo-item ${task.completed ? 'completed' : ''}`}>
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />
      <span className="task-text">{task.text}</span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </div>
  );
};

export default TodoItem;
```

### Testing Agent

**Input:** Implementation code
**Output:** Comprehensive test suite

**Generates:**
- Jest test files
- React Testing Library tests
- Unit tests for components
- Integration tests
- Test configuration
- Coverage setup

**Example Output:**
```javascript
// TodoItem.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import TodoItem from './TodoItem';

describe('TodoItem', () => {
  it('renders task text', () => {
    const task = { id: 1, text: 'Buy milk', completed: false };
    render(<TodoItem task={task} />);
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', () => {
    const onToggle = jest.fn();
    const task = { id: 1, text: 'Buy milk', completed: false };
    render(<TodoItem task={task} onToggle={onToggle} />);
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onToggle).toHaveBeenCalledWith(1);
  });
});
```

## Advanced Usage

### Custom Project Directory

Work in a specific directory:
```bash
python build_website.py "Build app" \
    --project-dir /path/to/project
```

### Custom Docker Network

Use specific Docker network:
```bash
# Create network
docker network create orchestrator-net

# Use network (requires custom Docker backend implementation)
python build_website.py "Build app" \
    --docker \
    --docker-image orchestrator-agents:latest
```

### AWS Bedrock Regions

Use different AWS regions:
```bash
# EU Central (Frankfurt)
python build_website.py "Build app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1

# US East (Virginia)
python build_website.py "Build app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region us-east-1

# Asia Pacific (Tokyo)
python build_website.py "Build app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region ap-northeast-1
```

### Different Models

**Local CLI with Bedrock:**
```bash
# Latest Sonnet (default)
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
python build_website.py "Build app"

# Opus (if available in your region)
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="anthropic.claude-opus-4-5-..."
python build_website.py "Build app"
```

**Docker with Bedrock:**
```bash
# Latest Sonnet
python build_website.py "Build app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-model "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Opus (if available)
python build_website.py "Build app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-model "anthropic.claude-opus-4-5-..."
```

## Troubleshooting

### CLI Issues

**Problem:** Claude CLI not found
```
WARNING: Claude CLI not found, falling back to SDK mode
```

**Solution:**
```bash
# Install Claude CLI (follow official instructions)
# Verify installation
claude --version

# Configure with API key or AWS credentials
claude config
```

**Problem:** Claude CLI Bedrock configuration
```
ERROR: Failed to call Claude API with Bedrock
```

**Solution:**
```bash
# Ensure AWS credentials are properly set
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."

# Verify Bedrock model ID matches your region
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Test Claude CLI with Bedrock
claude --model "$BEDROCK_MODEL" -p "Hello"
```

### Docker Issues

**Problem:** Docker not available
```
ERROR: Docker is not available!
```

**Solution:**
```bash
# Check Docker is running
docker ps

# Start Docker
open -a Docker  # macOS
sudo systemctl start docker  # Linux
```

**Problem:** Image not found
```
ERROR: Image orchestrator-agents:latest not found
```

**Solution:**
```bash
# Build the image
cd orchestrator/docker
./build.sh
```

### API/Credentials Issues

**Problem:** Anthropic API key not set
```
ERROR: ANTHROPIC_API_KEY environment variable not set
```

**Solution:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Problem:** AWS credentials not configured
```
ERROR: AWS credentials not found
```

**Solution:**
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
```

### Agent Execution Issues

**Problem:** Agent timeout
```
ERROR: Claude API timeout
```

**Solution:**
- Simplify requirements
- Break into smaller chunks
- Check network connectivity
- Increase timeout (code modification needed)

**Problem:** Invalid response format
```
ERROR: Failed to parse agent response
```

**Solution:**
- Review agent prompts
- Check model compatibility
- Verify API responses
- Check orchestrator logs

## Performance Tips

### Optimize Requirements

**Good:**
```bash
python build_website.py "Build a todo app with:
- Task list display
- Add/edit/delete tasks
- Local storage persistence
- Filter by status"
```

**Too Vague:**
```bash
python build_website.py "Build a website"
```

**Too Complex:**
```bash
python build_website.py "Build a complete social media platform with real-time chat, video calls, stories, marketplace, and AI recommendations..."
```

### Execution Speed

**Fastest:** Local CLI (Anthropic or Bedrock)
```bash
# With Bedrock (Recommended)
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
python build_website.py "Build app"

# With Anthropic API
python build_website.py "Build app"
```

**Balanced:** Docker + Bedrock
```bash
python build_website.py "Build app" --docker --docker-use-bedrock
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/generate-website.yml
name: Generate Website
on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: |
          cd orchestrator/docker
          ./build.sh

      - name: Generate website
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          python build_website.py "${{ github.event.head_commit.message }}" \
            --docker \
            --docker-use-bedrock \
            --output-dir ./generated

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: website-code
          path: ./generated
```

### Python Script Integration

```python
import subprocess
import json
from pathlib import Path

def generate_website(requirements, output_dir="./output"):
    """Generate website using orchestrator"""

    cmd = [
        "python", "orchestrator/build_website.py",
        requirements,
        "--docker",
        "--docker-use-bedrock",
        "--output-dir", output_dir
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Read orchestration report
        report_path = Path(output_dir) / "orchestration_report.json"
        with open(report_path) as f:
            report = json.load(f)

        return {
            "success": True,
            "output_dir": output_dir,
            "report": report
        }
    else:
        return {
            "success": False,
            "error": result.stderr
        }

# Usage
result = generate_website("Build a todo app")
print(f"Generated website in: {result['output_dir']}")
```

## Comparison with Parallel Orchestrator

| Feature | Website Orchestrator | Parallel Orchestrator |
|---------|---------------------|---------------------|
| **Use Case** | Website development | General parallel tasks |
| **Execution** | Sequential (3 agents) | Parallel (N tasks) |
| **Complexity** | Fixed workflow | Dynamic planning |
| **Agents** | Design/Impl/Test | Generic executors |
| **Backends** | Local, Docker | Threading, Docker, SLURM, AWS |
| **Best For** | Structured web projects | Large-scale task execution |

## Contributing

Contributions are welcome! Areas for improvement:

1. Additional agent types (deployment, monitoring)
2. More execution backends (SLURM, AWS Batch)
3. Parallel agent execution
4. Streaming output
5. Agent response caching
6. Multi-framework support (Vue, Angular)

## License

MIT License - See LICENSE file for details

## Support

- **Documentation**: [Website Orchestrator Architecture](website-orchestrator-architecture.md)
- **Issues**: https://github.com/blackjackptit/factory-agentic-dev/issues
- **Parallel Orchestrator**: [Parallel Orchestrator README](parallel-orchestrator-readme.md)

## Related Documentation

- [Parallel Orchestrator README](parallel-orchestrator-readme.md) - General parallel task execution
- [Parallel Orchestrator Architecture](parallel-orchestrator-architecture.md) - Parallel system design
- [Parallel Orchestrator Quick Start](parallel-orchestrator-quickstart.md) - Quick start guide
- [Website Orchestrator Architecture](website-orchestrator-architecture.md) - This system's architecture
