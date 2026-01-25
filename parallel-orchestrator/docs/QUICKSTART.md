# Quick Start Guide

Get up and running with Parallel Orchestrator in 5 minutes.

## 1. Prerequisites Check

```bash
# Check Docker is running
docker ps

# Check AWS credentials (if using Bedrock)
aws sts get-caller-identity
```

## 2. Build Docker Image

```bash
cd parallel-orchestrator/docker
./build.sh
```

Output should end with: `✓ Build complete!`

## 3. Choose Your Authentication Method

### Option A: AWS Bedrock (Recommended)

✅ No Anthropic API key needed
✅ Enterprise AWS integration
✅ Consolidated billing

```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### Option B: Anthropic API

✅ Direct API access
✅ Simple setup

```bash
export ANTHROPIC_API_KEY="your-key"
```

## 4. Run Your First Test

### Simulation Mode (No API Calls)

```bash
python3 orchestrator.py "Build a simple calculator" \
    --docker \
    --max-executors 2
```

Expected output:
- ✓ Plan created
- ✓ 2-4 tasks completed
- ✓ Files consolidated
- Success rate: 100%

### Real Code Generation

```bash
# With AWS Bedrock
python3 orchestrator.py "Build a todo list app" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --max-executors 3 \
    --real

# OR with Anthropic API
python3 orchestrator.py "Build a todo list app" \
    --docker \
    --docker-planner-in-docker \
    --max-executors 3 \
    --real
```

Expected output:
- ✓ Planner analyzes complexity
- ✓ Creates 4-6 tasks
- ✓ 3 executors run in parallel
- ✓ Generates HTML/CSS/JS files
- Time: ~3 minutes

## 5. Check Your Results

```bash
# List generated files
ls -la outputs/parallel-orchestrator/

# View generated HTML
open outputs/parallel-orchestrator/executor_*/task_*/index.html
```

## Common Commands

### Generate Different Types of Applications

```bash
# Simple landing page
python3 orchestrator.py "Build a landing page with hero section" \
    --docker --docker-use-bedrock --max-executors 2 --real

# Contact form
python3 orchestrator.py "Build a contact form with validation" \
    --docker --docker-use-bedrock --max-executors 2 --real

# Dashboard
python3 orchestrator.py "Build a dashboard with charts and tables" \
    --docker --docker-use-bedrock --max-executors 4 --real
```

### Adjust Parallelism

```bash
# Small project: 2 executors
--max-executors 2

# Medium project: 4 executors
--max-executors 4

# Large project: 8 executors
--max-executors 8
```

### Custom Output Directory

```bash
python3 orchestrator.py "Build an app" \
    --docker \
    --docker-use-bedrock \
    --max-executors 3 \
    --real \
    --output-dir outputs/my-project
```

## Troubleshooting Quick Fixes

### "Docker image not found"

```bash
cd parallel-orchestrator/docker
./build.sh
```

### "Unable to locate credentials"

```bash
# Check AWS credentials
aws sts get-caller-identity

# If that fails, set them:
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### "Model access denied"

1. Go to https://console.aws.amazon.com/bedrock/
2. Navigate to "Model access"
3. Click "Manage model access"
4. Enable "Claude" models
5. Submit request (usually instant approval)

### "Container failed"

```bash
# Check container logs
docker logs po-executor-0

# Check if containers are running
docker ps -a | grep po-executor
```

## Next Steps

- **[Full Documentation](../README.md)** - Complete feature overview
- **[Docker Backend](docker-backend.md)** - Detailed Docker configuration
- **[AWS Bedrock Setup](bedrock-model-setup.md)** - Model configuration
- **[Docker Planner](docker-planner.md)** - Planner containerization

## Example Workflow

```bash
# 1. Set credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# 2. Build image (first time only)
cd parallel-orchestrator/docker && ./build.sh && cd ../..

# 3. Test with simulation
python3 orchestrator.py "Build a calculator" --docker --max-executors 2

# 4. Generate real code
python3 orchestrator.py "Build a todo app" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --max-executors 3 \
    --real

# 5. Check results
ls outputs/parallel-orchestrator/
```

## Performance Tips

1. **Start with 2-3 executors** - Test before scaling up
2. **Use simulation mode first** - Verify workflow without API costs
3. **Monitor resource usage** - Check Docker Desktop stats
4. **Choose appropriate model** - Global model works everywhere
5. **Clean up old outputs** - Remove old output directories

## Getting Help

If you encounter issues:

1. **Check logs**: `cat outputs/parallel-orchestrator/orchestrator.log`
2. **Verify setup**: Run simulation mode first
3. **Review docs**: Check relevant documentation file
4. **Test credentials**: Ensure AWS/Anthropic auth is working

## Success Indicators

You'll know it's working when you see:

```
✓ Planner completed successfully
✓ Container started
✓ Collected result for task_X
✓ All containers finished
Tasks completed: X / X
Success Rate: 100.0%
```

Your generated code will be in: `outputs/parallel-orchestrator/`

Happy coding! 🚀
