# Quick Start Guide

Get your website built in 5 minutes!

## Prerequisites

Choose one of these options:

**Option A: Claude CLI (Recommended)**
```bash
# Install Claude Code CLI
# See: https://github.com/anthropics/claude-code

# Verify installation
claude --version
```

**Option B: Docker**
```bash
# Just need Docker installed
docker --version
```

## Step 1: Setup Environment

**For Claude CLI + Bedrock (Recommended):**
```bash
export CLAUDE_CODE_USE_BEDROCK=1
export BEDROCK_MODEL="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

**For Claude CLI + Anthropic:**
```bash
# Claude CLI will use your configured credentials
# Or set explicitly:
export ANTHROPIC_API_KEY="sk-ant-..."
```

**For Docker + Bedrock:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

## Step 2: Navigate to Orchestrator

```bash
cd orchestrator
```

## Step 3: Build Your First Website

**Using Claude CLI (fastest):**
```bash
python build_website.py "Build a todo list app with add, edit, delete features"
```

**Using Docker (isolated):**
```bash
python build_website.py "Build a todo list app with add, edit, delete features" \
    --docker \
    --docker-use-bedrock
```

## Step 4: Watch the Magic

The orchestrator will:
1. 🎨 Create design specifications
2. ⚛️ Generate React code
3. 🧪 Build test suite

This takes about 3-4 minutes.

## Step 5: Check Results

Results are saved to `../outputs/website-orchestrator/` directory by default:

```bash
ls -la ../outputs/website-orchestrator/
```

You'll see:
```
outputs/website-orchestrator/
├── design/
│   ├── design_spec.md          # Design specifications
│   └── design_phase.json       # Raw design output
├── implementation/
│   ├── components/             # React components
│   ├── styles/                 # CSS/styling files
│   ├── package.json            # Project dependencies
│   └── setup_instructions.md   # Setup guide
├── testing/
│   ├── tests/                  # Test files
│   └── test_plan.md           # Testing strategy
└── orchestration_report.json   # Execution metrics
```

## Step 6: Use the Code

1. Read the setup instructions:
   ```bash
   cat ../outputs/website-orchestrator/implementation/setup_instructions.md
   ```

2. Copy the generated project:
   ```bash
   cp -r ../outputs/website-orchestrator/implementation/* ./my-website/
   ```

3. Install dependencies and run:
   ```bash
   cd my-website
   npm install
   npm start
   ```

4. Run tests:
   ```bash
   npm test
   ```

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

## What's Next?

- Read the full [Website Orchestrator README](website-orchestrator-readme.md) for detailed documentation
- Check the [Architecture Documentation](website-orchestrator-architecture.md) for system design
- Explore Docker mode for production deployments
- Try different AI backends (Anthropic vs Bedrock)

## Common Issues

**"Claude Code CLI is not available"**
- Install Claude Code CLI: https://github.com/anthropics/claude-code
- Make sure `claude` command is in your PATH
- Alternative: Use Docker mode with `--docker` flag

**"AWS credentials not found" (when using Bedrock)**
- Set AWS credentials:
  ```bash
  export AWS_ACCESS_KEY_ID="your-key"
  export AWS_SECRET_ACCESS_KEY="your-secret"
  ```
- Or configure AWS CLI: `aws configure`

**"Docker image not found"**
- Build the Docker image first:
  ```bash
  cd orchestrator/docker
  ./build.sh
  ```

**Takes too long**
- Normal for complex websites (3-5 minutes)
- Complex requirements take longer to process
- CLI mode is faster than Docker mode

**Bedrock model errors**
- Verify model ID matches your region
- Use global model IDs for cross-region support
- Check AWS Bedrock console for available models

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

---

## 📚 Related Documentation

- **[Main README](../README.md)** - Project overview
- **[Website Orchestrator README](../orchestrator/README.md)** - Detailed documentation
- **[Project Structure](website-orchestrator-structure.md)** - Architecture details
- **[Test Results](website-orchestrator-test-results.md)** - Example outputs
- **[Documentation Index](README.md)** - All documentation

---

**Last Updated:** January 2026
**Version:** 2.0 - Unified Documentation Structure
