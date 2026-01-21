# Website Development Orchestrator

AI-powered orchestrator that coordinates specialized subagents to build complete React websites from requirements.

## Overview

The orchestrator manages three specialized AI subagents that work together to transform website requirements into production-ready code:

1. **🎨 Design Agent** - Creates comprehensive UI/UX specifications
2. **⚛️ Implementation Agent** - Builds React components and application code
3. **🧪 Testing Agent** - Generates automated test suite

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Requirements                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Website Orchestrator                        │
│  - Coordinates workflow                                  │
│  - Calls Claude Code CLI directly                        │
│  - Aggregates and stores results                         │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
         ▼              ▼              ▼
┌────────────┐  ┌─────────────┐  ┌──────────────┐
│  Design    │  │ Implement   │  │   Testing    │
│  Agent     │→ │ Agent       │→ │   Agent      │
│            │  │             │  │              │
│ Calls:     │  │ Calls:      │  │ Calls:       │
│ claude CLI │  │ claude CLI  │  │ claude CLI   │
│            │  │             │  │              │
│ Creates:   │  │ Creates:    │  │ Creates:     │
│ - UI/UX    │  │ - React     │  │ - Unit tests │
│ - Layout   │  │   code      │  │ - E2E tests  │
│ - Colors   │  │ - State mgmt│  │ - Test utils │
│ - Components  │ - Styling   │  │ - Coverage   │
└────────────┘  └─────────────┘  └──────────────┘
```

## Prerequisites

1. **Claude Code CLI**: Must be installed
   ```bash
   # Verify installation
   claude --version
   ```

   If not installed, get it from: https://github.com/anthropics/claude-code

2. **Python**: Python 3.7 or higher (standard library only, no external dependencies)

## Quick Start

### Basic Usage

```bash
python build_website.py "Build a todo list app with add, edit, and delete features"
```

### With Options

```bash
python build_website.py "Build a blog website" \
  --project-dir ./my-blog \
  --output-dir ./results
```

## Command Line Options

```
python build_website.py "<requirements>" [options]

Arguments:
  requirements          Website requirements description

Options:
  --project-dir DIR     Project directory (default: current directory)
  --output-dir DIR      Output directory for results (default: ./output)
  -h, --help           Show help message
```

## Examples

### Example 1: Todo App

```bash
python build_website.py "Build a todo list application with:
- Add, edit, delete tasks
- Mark tasks as complete
- Filter by status
- Responsive design"
```

### Example 2: E-commerce Site

```bash
python build_website.py "Create a product catalog with:
- Product grid with images
- Search and filter
- Shopping cart
- Checkout flow
- Product details page"
```

### Example 3: Dashboard

```bash
python build_website.py "Build an analytics dashboard with:
- Summary cards for key metrics
- Line and bar charts
- Data table with sorting
- Responsive layout
- Dark mode support"
```

### Using Example Scripts

```bash
cd examples

# Build todo app
python todo_app.py

# Build dashboard
python dashboard.py
```

## Output Structure

After running the orchestrator, results are saved to the output directory:

```
output/
├── design_YYYYMMDD_HHMMSS.json          # Design specifications
├── implementation_YYYYMMDD_HHMMSS.json  # React code and setup
├── testing_YYYYMMDD_HHMMSS.json        # Test suite
└── complete_summary_YYYYMMDD_HHMMSS.json # Full results
```

Each JSON file contains:
- `success`: Boolean indicating if stage completed
- `response`: The agent's output
- `timestamp`: When the stage completed
- `subagent`: Which agent produced it

## Subagents in Detail

### Design Agent

**Responsibilities:**
- Analyze requirements
- Create UI/UX specifications
- Define component structure
- Specify color schemes, typography, layouts
- Generate design system guidelines
- Consider accessibility

**Output:**
- Design overview and concept
- Component hierarchy
- Visual design system (colors, fonts, spacing)
- Layout specifications
- Component details
- Accessibility guidelines

### Implementation Agent

**Responsibilities:**
- Convert design specs to React code
- Write clean, maintainable components
- Implement state management
- Set up styling approach
- Follow React best practices
- Provide setup instructions

**Output:**
- Project structure
- Complete React components
- State management implementation
- Styling code
- Custom hooks and utilities
- Package dependencies
- Setup and build instructions

### Testing Agent

**Responsibilities:**
- Generate comprehensive test suite
- Write unit tests for components
- Create integration tests
- Develop E2E tests
- Set up testing infrastructure
- Provide coverage analysis

**Output:**
- Testing strategy
- Unit test files
- Integration tests
- E2E test scenarios
- Test utilities and helpers
- Testing dependencies
- Test run commands
- Coverage goals

## Programmatic Usage

You can use the orchestrator in your own Python scripts:

```python
from orchestrator import WebsiteOrchestrator

# Create orchestrator
orchestrator = WebsiteOrchestrator(
    project_dir="./my-project",
    output_dir="./results"
)

# Build website
result = orchestrator.build_website("""
Build a landing page with:
- Hero section
- Feature cards
- Contact form
- Responsive design
""")

# Check results
if result["success"]:
    print("Success!")
    print(f"Design: {result['stages']['design']['success']}")
    print(f"Implementation: {result['stages']['implementation']['success']}")
    print(f"Testing: {result['stages']['testing']['success']}")
```

## Advanced Usage

### Custom Subagent Integration

You can extend the orchestrator with custom subagents:

```python
from orchestrator import WebsiteOrchestrator

class CustomAgent:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.name = "custom"

    def execute(self, requirements):
        prompt = f"Custom task: {requirements}"
        return self.orchestrator.delegate_to_subagent(
            subagent_name=self.name,
            prompt=prompt,
            context={"phase": "custom"}
        )

# Use in orchestrator
orchestrator = WebsiteOrchestrator()
custom_agent = CustomAgent(orchestrator)
result = custom_agent.execute("My custom requirements")
```

### Direct Subagent Usage

You can also use individual subagents:

```python
from subagents.design_agent import DesignAgent
from orchestrator import WebsiteOrchestrator

orchestrator = WebsiteOrchestrator()
design_agent = DesignAgent(orchestrator)

result = design_agent.execute("Build a login form")
print(result["response"])
```

## Workflow

1. **Check API Health**: Verify Claude API server is running
2. **Design Phase**: Design agent creates specifications
3. **Implementation Phase**: Implementation agent builds React code
4. **Testing Phase**: Testing agent generates test suite
5. **Save Results**: All outputs saved to JSON files
6. **Summary**: Complete summary with all stages

If any stage fails, the orchestration stops and returns partial results.

## Best Practices

### Writing Good Requirements

✅ **Good:**
```
Build a blog website with:
- Homepage with recent posts grid
- Individual post pages with comments
- About page
- Responsive navigation
- Dark mode toggle
- Search functionality
```

❌ **Too vague:**
```
Build a website
```

❌ **Too technical:**
```
Use React 18, TypeScript, Zustand for state, Tailwind CSS,
implement lazy loading with React.lazy()...
```

### Tips

1. **Be specific about features** - List clear functionality
2. **Describe the UI** - Mention layout, colors, style preferences
3. **Note important behaviors** - Interactions, animations, responsiveness
4. **Mention technical requirements** - If you need specific integrations
5. **Keep it focused** - One website concept per run

## Troubleshooting

### Claude Code CLI Not Available

```bash
# Check if Claude is installed
claude --version

# Check if it's in your PATH
which claude

# Install Claude Code CLI if needed
# Visit: https://github.com/anthropics/claude-code
```

### Subagent Failures

If a subagent fails:
1. Check the output JSON files for error details
2. Review the prompt sent to the agent
3. Try simplifying requirements
4. Check API server logs

### Timeout Errors

For complex requirements, increase timeout:

```python
orchestrator = WebsiteOrchestrator()
orchestrator.api.query(prompt, timeout=1200)  # 20 minutes
```

## Performance

- **Design Phase**: ~30-60 seconds
- **Implementation Phase**: ~60-120 seconds
- **Testing Phase**: ~60-90 seconds
- **Total Time**: ~2.5-4.5 minutes per website

Times vary based on complexity and API response time.

## Limitations

- Generates code specifications, not complete deployable apps
- Requires manual setup of generated code
- Best for prototyping and planning
- May need human review and refinement
- Limited to React framework for implementation

## Future Enhancements

- [ ] Support for other frameworks (Vue, Angular, Svelte)
- [ ] Direct code generation to files
- [ ] Integration with version control
- [ ] Deployment agent for automatic deployment
- [ ] Backend API generation agent
- [ ] Database schema agent
- [ ] Visual design mockup generation
- [ ] Real-time collaboration features

## Contributing

To add a new subagent:

1. Create a new file in `subagents/`
2. Implement the agent class with `execute()` method
3. Import and use in `orchestrator.py`
4. Update documentation

## License

Part of the factory-agentic-dev project.

## Support

For issues and questions, refer to the main project repository.
