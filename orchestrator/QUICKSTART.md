# Quick Start Guide

Get your website built in 5 minutes!

## Step 1: Verify Claude Code CLI

Make sure you have Claude Code CLI installed:

```bash
claude --version
```

If not installed, get it from: https://github.com/anthropics/claude-code

## Step 2: Navigate to Orchestrator

```bash
cd orchestrator
```

No dependencies needed - the orchestrator uses Claude Code CLI directly!

## Step 3: Build Your First Website

```bash
python build_website.py "Build a todo list app with add, edit, delete features"
```

## Step 4: Watch the Magic

The orchestrator will:
1. 🎨 Create design specifications
2. ⚛️ Generate React code
3. 🧪 Build test suite

This takes about 3-4 minutes.

## Step 5: Check Results

Results are saved to `output/` directory:

```bash
ls -la output/
```

You'll see:
- `design_*.json` - UI/UX specifications
- `implementation_*.json` - React code
- `testing_*.json` - Test suite
- `complete_summary_*.json` - Everything combined

## Step 6: Use the Code

1. Open the `implementation_*.json` file
2. Follow the setup instructions
3. Copy the React components
4. Run the tests

## Quick Examples

### Todo App
```bash
python build_website.py "Todo app with add, edit, delete, and filters"
```

### Landing Page
```bash
python build_website.py "Landing page with hero, features, and contact form"
```

### Dashboard
```bash
python build_website.py "Analytics dashboard with charts and data tables"
```

### E-commerce
```bash
python build_website.py "Product catalog with cart and checkout"
```

## Using Example Scripts

```bash
cd examples

# Pre-configured todo app
python todo_app.py

# Pre-configured dashboard
python dashboard.py
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Explore more complex examples
- Customize the subagents for your needs
- Try different types of websites

## Common Issues

**"Claude Code CLI is not available"**
- Install Claude Code CLI: https://github.com/anthropics/claude-code
- Make sure `claude` command is in your PATH

**Takes too long**
- Normal for complex websites (3-5 minutes)
- Complex requirements take longer to process

## Tips for Better Results

1. **Be specific** - "Todo app with dark mode" is better than "an app"
2. **List features** - Bullet points work great
3. **Mention style** - "modern, minimalist design" helps
4. **Note responsiveness** - "mobile-friendly" or "responsive"

## Example Requirements Format

```bash
python build_website.py "
Build a blog website with:
- Homepage showing recent posts in a grid
- Individual post pages with comments section
- About page with author bio
- Responsive navigation bar
- Search functionality
- Dark mode toggle
- Clean, modern design with blue accent colors
"
```

Happy building! 🚀
