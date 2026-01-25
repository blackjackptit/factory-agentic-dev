# Using AWS Bedrock with Docker Backend

The Docker backend now supports AWS Bedrock, allowing you to use Claude via AWS without needing an Anthropic API key. This is useful for organizations that have AWS accounts and want to avoid managing separate API keys.

## Benefits

- ✅ **No Anthropic API Key Required**: Use your existing AWS credentials
- ✅ **Cost Tracking**: Bedrock usage shows up in AWS billing
- ✅ **Enterprise Integration**: Works with AWS SSO and IAM roles
- ✅ **Same Performance**: Local Docker execution with cloud AI

## Prerequisites

1. **AWS Account** with Bedrock access enabled
2. **AWS Credentials** configured
3. **Docker** installed and running
4. **Bedrock Model Access** - ensure you have access to Claude models in your AWS region

## Setup

### 1. Enable Bedrock Access

In your AWS account:
1. Navigate to AWS Bedrock console
2. Request model access for Claude models
3. Wait for approval (usually instant for Claude Sonnet)

### 2. Configure AWS Credentials

You have several options:

#### Option A: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_SESSION_TOKEN="your-session-token"  # Optional, for temporary credentials
```

#### Option B: AWS CLI Configuration

```bash
aws configure
# Follow prompts to enter credentials
```

#### Option C: AWS SSO

```bash
aws sso login --profile your-profile
export AWS_PROFILE=your-profile
```

#### Option D: Command Line Arguments

```bash
python3 orchestrator.py "Build an app" \
    --docker \
    --docker-use-bedrock \
    --docker-aws-access-key-id "your-key-id" \
    --docker-aws-secret-access-key "your-secret-key" \
    --real
```

### 3. Build Docker Image

```bash
# Option 1: Using the build script (recommended)
cd parallel-orchestrator/docker
./build.sh

# Option 2: Manual build
cd parallel-orchestrator
docker build -f docker/Dockerfile -t parallel-orchestrator:latest .
```

## Usage Examples

### Basic Usage (Environment Variables)

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Run with Bedrock
python3 orchestrator.py "Build a todo list app with React" \
    --docker \
    --docker-use-bedrock \
    --max-executors 4 \
    --real \
    --output-dir outputs/todo-app
```

### Specify Region and Model

```bash
python3 orchestrator.py "Build a calculator app" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --max-executors 2 \
    --real
```

Note: Using defaults (global model, eu-central-1 region). To specify Claude 3.5 Sonnet instead:

```bash
python3 orchestrator.py "Build a blog platform" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --docker-bedrock-model "global.anthropic.claude-3-5-sonnet-20241022-v2:0" \
    --max-executors 6 \
    --real
```

### With AWS SSO

```bash
# Login to AWS SSO
aws sso login --profile my-company

# Export profile
export AWS_PROFILE=my-company

# Run orchestrator (credentials are automatically picked up)
python3 orchestrator.py "Build microservices" \
    --docker \
    --docker-use-bedrock \
    --max-executors 4 \
    --real
```

### Full-Stack Application Example

```bash
python3 orchestrator.py "Build a full-stack e-commerce platform with:
- React frontend with TypeScript
- Node.js/Express backend
- PostgreSQL database
- Payment integration
- Admin dashboard
- Docker setup" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-region us-west-2 \
    --max-executors 8 \
    --real \
    --output-dir outputs/ecommerce
```

## Available Bedrock Models

### Claude Sonnet 4.5 (Recommended)

**Global Inference Profile (Default):**
- `global.anthropic.claude-sonnet-4-5-20250929-v1:0` (works in all regions)

**Regional Inference Profiles:**
- **EU**: `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` (eu-central-1, eu-west-1)
- **US**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (us-east-1, us-west-2)

**Asia Pacific:**
- `ap.anthropic.claude-sonnet-4-5-20250929-v1:0` (ap-northeast-1, ap-southeast-1)

### Claude Sonnet 3.5

**Global:**
- `anthropic.claude-3-5-sonnet-20241022-v2:0`

### Model Selection Guidelines

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| Claude Sonnet 4.5 | Complex apps, best quality | Higher | Slower |
| Claude Sonnet 3.5 | General purpose | Medium | Fast |
| Claude Haiku 3.5 | Simple tasks, testing | Lower | Fastest |

## Configuration Options

### Docker Bedrock Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--docker-use-bedrock` | Enable Bedrock mode | `false` |
| `--docker-bedrock-region` | AWS region | `eu-central-1` |
| `--docker-bedrock-model` | Model ID | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `--docker-aws-access-key-id` | AWS Access Key ID | From env |
| `--docker-aws-secret-access-key` | AWS Secret Access Key | From env |
| `--docker-aws-session-token` | AWS Session Token (optional) | From env |

## How It Works

```
1. User runs orchestrator with --docker-use-bedrock
        ↓
2. Docker backend passes AWS credentials to containers
        ↓
3. Containers set CLAUDE_CODE_USE_BEDROCK=1
        ↓
4. ExecutorAgent detects Bedrock mode
        ↓
5. Claude CLI called with --model flag
        ↓
6. Claude CLI uses AWS SDK to call Bedrock
        ↓
7. Code generated and saved to volume
        ↓
8. Results aggregated on host
```

## Architecture

```
Host Machine
├── Python Orchestrator
│   └── Docker Backend (backends/docker_backend.py)
│       └── Passes AWS credentials as env vars
│
├── Docker Containers (parallel execution)
│   ├── Container 0 (executor_0)
│   │   ├── docker_executor.py
│   │   │   └── Sets CLAUDE_CODE_USE_BEDROCK=1
│   │   ├── executor_agent.py
│   │   │   └── Calls Claude CLI with --model
│   │   └── Claude CLI
│   │       └── AWS SDK → Bedrock API
│   │
│   └── Container 1 (executor_1)
│       └── ...
│
└── Volume Mounts
    └── /output → host outputs/
```

## Cost Considerations

### Bedrock Pricing (as of 2024)

**Claude Sonnet 4.5:**
- Input: $0.003 per 1K tokens
- Output: $0.015 per 1K tokens

**Typical Project Costs:**

| Project Size | Tokens | Estimated Cost |
|-------------|--------|---------------|
| Simple app (4 tasks) | ~50K | $0.15 - $0.50 |
| Medium app (8 tasks) | ~100K | $0.30 - $1.00 |
| Large app (12 tasks) | ~200K | $0.60 - $2.00 |
| Full-stack (20 tasks) | ~400K | $1.20 - $4.00 |

**vs. Anthropic API Direct:**
- Pricing is similar
- Bedrock includes AWS infrastructure and billing integration

## Troubleshooting

### Error: "Unable to locate credentials"

**Cause:** AWS credentials not configured

**Solution:**
```bash
# Check credentials
aws sts get-caller-identity

# If fails, configure:
aws configure

# Or export env vars:
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

### Error: "You don't have access to the model"

**Cause:** Bedrock model access not enabled

**Solution:**
1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access for Claude models
4. Wait for approval (usually instant)

### Error: "Region not supported"

**Cause:** Claude not available in your region

**Solution:** Use a supported region:
```bash
--docker-bedrock-region eu-central-1
# or
--docker-bedrock-region eu-central-1
```

### Error: "Invalid model ID"

**Cause:** Wrong model ID for your region or using unsupported model identifier

**Solution:** Use global inference profile (recommended):
```bash
--docker-bedrock-model global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

Or use region-specific model ID if you need regional optimization:
- US: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- EU: `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- AP: `ap.anthropic.claude-sonnet-4-5-20250929-v1:0`

### Slow Performance

**Cause:** Cross-region latency

**Solution:** Choose a region close to you:
```bash
# If in Europe
--docker-bedrock-region eu-central-1 \
--docker-bedrock-model eu.anthropic.claude-sonnet-4-5-20250929-v1:0

# If in Asia
--docker-bedrock-region ap-northeast-1 \
--docker-bedrock-model ap.anthropic.claude-sonnet-4-5-20250929-v1:0
```

## Security Best Practices

### 1. Never Hardcode Credentials

❌ **Bad:**
```bash
--docker-aws-access-key-id AKIAIOSFODNN7EXAMPLE
```

✅ **Good:**
```bash
export AWS_ACCESS_KEY_ID="..."
# Credentials read from environment
```

### 2. Use IAM Roles When Possible

If running on EC2 or ECS, use IAM roles instead of credentials:
```bash
# Instance role provides credentials automatically
python3 orchestrator.py "Build app" \
    --docker \
    --docker-use-bedrock \
    --real
```

### 3. Use AWS SSO for Organizations

```bash
aws sso login --profile company-dev
export AWS_PROFILE=company-dev
# Temporary credentials with MFA
```

### 4. Rotate Credentials Regularly

- Use AWS Secrets Manager
- Rotate keys every 90 days
- Use temporary credentials when possible

### 5. Limit Permissions

Create IAM policy with minimal permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
      ]
    }
  ]
}
```

## Comparison: Bedrock vs. Anthropic API

| Feature | AWS Bedrock | Anthropic API |
|---------|-------------|---------------|
| **Setup** | AWS account + Bedrock access | API key only |
| **Billing** | AWS consolidated billing | Separate Anthropic billing |
| **Enterprise** | AWS SSO, IAM integration | API key management |
| **Regions** | Multiple AWS regions | Global |
| **Latency** | Depends on region | Global CDN |
| **Monitoring** | CloudWatch | Anthropic dashboard |
| **Cost** | ~Same as direct API | Baseline |
| **Best For** | AWS-first orgs | Startups, simple setup |

## Advanced Usage

### Multi-Region Deployment

```bash
# US West for California-based team
python3 orchestrator.py "Build feature A" \
    --docker --docker-use-bedrock \
    --docker-bedrock-region us-west-2 \
    --max-executors 4 --real &

# EU Central for European team
python3 orchestrator.py "Build feature B" \
    --docker --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --docker-bedrock-model eu.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --max-executors 4 --real &

wait
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Generate Code with Bedrock
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  run: |
    python3 orchestrator.py "${{ github.event.inputs.requirement }}" \
      --docker \
      --docker-use-bedrock \
      --max-executors 4 \
      --real
```

### Cost Monitoring

```bash
# Check costs after run
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter file://bedrock-filter.json

# bedrock-filter.json
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["Amazon Bedrock"]
  }
}
```

## Support

For issues:
- AWS Bedrock: AWS Support
- Docker Backend: GitHub Issues
- Claude Models: Anthropic Documentation

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude on Bedrock Guide](https://docs.anthropic.com/claude/docs/claude-on-amazon-bedrock)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Docker Backend Documentation](docker-backend.md)
