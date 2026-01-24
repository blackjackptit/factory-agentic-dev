# AI Agent Instructions for Factory Agentic Dev

## Project Overview

**Factory Agentic Dev** is an AI-powered orchestration system that automatically generates complete full-stack web applications by coordinating three specialized subagents:
- **Design Agent**: Creates UI/UX specifications
- **Implementation Agent**: Generates React frontend + Python backend
- **Testing Agent**: Produces comprehensive test suites (Jest, Cypress, accessibility tests)

Entry point: `orchestrator/build_website.py "your app description"`

## Architecture

The system uses a **pipeline orchestration pattern**:

```
User Requirements → WebsiteOrchestrator → Design Agent → Implementation Agent → Testing Agent → JSON Results
```

**Key architectural decisions:**
- **No external dependencies** in orchestrator (uses standard library only)
- **Claude Code CLI as primary execution engine** - orchestrator delegates tasks via `claude --dangerously-skip-permissions -p "prompt"`
- **JSON-based result storage** - all outputs saved with timestamps for auditability
- **Sequential delegation** - each subagent operates on previous stage context
- **File extraction from Claude responses** - regex patterns extract code blocks from Claude's output and write to disk

## Core Components

### 1. WebsiteOrchestrator (`orchestrator/orchestrator.py`)
**Responsibilities:**
- Coordinates workflow between subagents
- Calls `ClaudeAPI.query()` to invoke Claude Code CLI
- Manages output directory and result persistence
- Aggregates results into `complete_summary_*.json`

**Key methods:**
- `build_website(requirements)` - main orchestration flow
- `delegate_to_subagent(name, prompt, context)` - sends tasks to subagents
- `save_result(stage, data)` - persists JSON with timestamp
- `check_claude_available()` - validates Claude Code CLI

**Must-know patterns:**
- Timestamp format: `%Y%m%d_%H%M%S`
- Each stage saves independently: `{stage}_{timestamp}.json`
- Full results saved as: `complete_summary_{timestamp}.json`

### 2. ClaudeAPI (`orchestrator/claude_api.py`)
**Single responsibility:** Execute Claude Code CLI commands with subprocess

**Critical implementation:**
```python
subprocess.run([
    "claude",
    "--dangerously-skip-permissions",  # Required for automated execution
    "--print",                          # Outputs to stdout
    "-p", prompt                        # The actual prompt
], cwd=working_dir, capture_output=True, text=True, timeout=600)
```

**Exit code handling:**
- `returncode == 0` → success, use `stdout`
- `returncode != 0` → failure, include `stderr` in error message

### 3. Subagents (`orchestrator/subagents/`)

All three subagents follow the same pattern:

**DesignAgent** → Generates UI/UX specs with 5-step logging:
```
[Step 1/5] Analyzing requirements...
[Step 2/5] Building design prompt...
[Step 3/5] Requesting design from Claude...
[Step 4/5] Processing design response...
[Step 5/5] Saving design results...
```

**ImplementationAgent** → Generates React + Python (9 steps):
- Frontend steps (1-5): Components, state management, styling
- Backend steps (6-9): API routes, models, requirements, setup docs
- Extracts code via regex: `r'```(?:python|py|text)\s*\n(?:#|\/\/)\s*(?:filename:|path:|file:)\s*([^\n]+?)\s*\n(.*?)```'`

**TestingAgent** → Generates Jest/Cypress tests (7 steps):
- Unit tests for components
- E2E tests via Cypress
- Accessibility tests
- Extracts code via regex: `r'```(?:javascript|jsx?|typescript|tsx?)\s*\n(?:\/\/|#)\s*(?:filename:|path:|file:)\s*([^\n]+?)\s*\n(.*?)```'`

## Critical Workflows

### Build a Website
```bash
cd orchestrator
python build_website.py "todo app with add, delete, mark complete"
```

Generates 37+ files with 137,000+ characters in ~3-4 minutes.

### Result Structure
```
output/
├── design_YYYYMMDD_HHMMSS.json          # Design phase output
├── implementation_YYYYMMDD_HHMMSS.json  # React + Python code
├── testing_YYYYMMDD_HHMMSS.json         # Test suite
├── complete_summary_YYYYMMDD_HHMMSS.json # Full aggregation
├── backend/                             # Python backend files
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   └── schemas/
├── src/                                 # React frontend
│   ├── components/
│   ├── pages/
│   └── App.jsx
└── __tests__/                           # Test files
    ├── jest.config.js
    ├── cypress.config.js
    └── cypress/
```

### Key Prompting Patterns

**Design Agent Prompt Structure:**
- Requires complete requirement analysis
- Specifies 5 major sections: overview, components, visual system, layout, specifications
- Outputs design JSON with structured specifications

**Implementation Agent Prompt Structure:**
- Receives design specs from previous stage
- Generates both React components AND Python FastAPI backend
- Code blocks marked with comments: `# filename: path/to/file.py`
- Must include setup documentation

**Testing Agent Prompt Structure:**
- Uses design + implementation context
- Generates Jest configs, test files, Cypress E2E tests
- Includes coverage configuration

## Development Patterns

### Code Generation Best Practices
- Code is extracted from Claude's markdown blocks
- File paths must be explicit in comments/markers
- Regex extraction is strict - maintain exact comment format
- Both `python` and `py` language markers work

### Error Handling
- Claude Code CLI failures capture stderr + stdout
- Timeouts: default 600 seconds for orchestrator, 300 seconds for API
- Health checks via `shutil.which("claude")` before operations

### Output Management
- All outputs go to `output/` by default (configurable via `--output-dir`)
- Timestamps ensure no collisions
- Each stage saves independently before moving to next

## Testing Generated Code

See [TEST_RESULTS.md](orchestrator/TEST_RESULTS.md) for patterns:
- Jest configs expect `src/` directory structure
- Cypress tests run in `__tests__/cypress/` 
- Backend tests in `backend/tests/`
- Run setup from generated `README.md` in each project folder

## API Server (Optional)

[api/server.py](api/server.py) provides REST interface:
- `POST /query` - execute Claude Code with response text
- `POST /query/stream` - stream responses via Server-Sent Events
- Always set `cwd` parameter for codebase context

## Troubleshooting Guide

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| "Claude Code CLI is not available" | `claude` not in PATH | Install Claude Code CLI, verify with `claude --version` |
| Timeout errors | Long-running stage (>600s) | Simpler requirements, check Claude availability |
| Missing files in output | Regex pattern mismatch | Ensure `# filename:` or `// path:` markers in Claude output |
| CORS errors in frontend | Backend not running | Set up backend first: `cd backend && python main.py` |

## Files to Know

**Essential:**
- [orchestrator/orchestrator.py](orchestrator/orchestrator.py) - Core orchestration logic
- [orchestrator/build_website.py](orchestrator/build_website.py) - CLI entry point
- [orchestrator/subagents/](orchestrator/subagents/) - All three agent implementations

**Reference:**
- [orchestrator/README.md](orchestrator/README.md) - Architecture details
- [orchestrator/QUICKSTART.md](orchestrator/QUICKSTART.md) - Quick examples
- [orchestrator/examples/](orchestrator/examples/) - Pre-configured workflows

**Generated outputs:**
- [outputs/booking-page/](outputs/booking-page/) - Full example booking app (React + Python backend + tests)
- [outputs/calculator-test/](outputs/calculator-test/) - Full example calculator (Jest + Cypress)
