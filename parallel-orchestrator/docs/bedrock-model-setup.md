# AWS Bedrock Model Setup and Troubleshooting

## Common Issues with Bedrock Models

### Issue: "The provided model identifier is invalid"

This error occurs when:
1. **Model access not requested** - You need to request access in AWS Bedrock console
2. **Wrong region** - Model not available in your selected region
3. **Incorrect model ID** - Model ID format has changed or is invalid

## How to Enable Model Access

### Step 1: Check Available Models

```bash
# List available models in your region
aws bedrock list-foundation-models --region eu-central-1 \
    --query "modelSummaries[?contains(modelId, 'claude')].{ModelId:modelId,Name:modelName}" \
    --output table
```

### Step 2: Request Model Access

1. Go to AWS Bedrock Console: https://console.aws.amazon.com/bedrock/
2. Select your region (e.g., eu-central-1)
3. Navigate to "Model access" in the left sidebar
4. Click "Manage model access"
5. Check the boxes for Claude models you want to use:
   - ✅ Claude 3.5 Sonnet
   - ✅ Claude 3 Haiku (optional, for faster/cheaper tasks)
6. Click "Request model access"
7. Wait for approval (usually instant)

### Step 3: Verify Access

```bash
# Check your model access
aws bedrock list-foundation-models --region eu-central-1 \
    --by-provider anthropic \
    --output json | jq '.modelSummaries[] | {modelId, modelName, status}'
```

## Correct Model IDs by Region

### Global Inference Profile (Recommended)

**Works in all regions - Use this as default:**
```bash
# Claude Sonnet 4.5 (latest, recommended)
global.anthropic.claude-sonnet-4-5-20250929-v1:0

# Claude 3.5 Sonnet v2
global.anthropic.claude-3-5-sonnet-20241022-v2:0

# Claude 3 Haiku (direct model ID, no inference profile needed)
anthropic.claude-3-haiku-20240307-v1:0
```

### Regional Inference Profiles (Optional)

**EU Region (eu-central-1, eu-west-1):**
```bash
# Claude Sonnet 4.5
eu.anthropic.claude-sonnet-4-5-20250929-v1:0

# Claude 3.5 Sonnet v2
eu.anthropic.claude-3-5-sonnet-20241022-v2:0
```

**US Region (us-east-1, us-west-2):**
```bash
# Claude Sonnet 4.5
us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Claude 3.5 Sonnet v2
us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

## Testing Your Setup

### Test 1: Check AWS Credentials

```bash
aws sts get-caller-identity
```

Should return your AWS account info.

### Test 2: List Models You Have Access To

```bash
aws bedrock list-foundation-models \
    --region eu-central-1 \
    --by-provider anthropic
```

### Test 3: Try Invoking a Model Directly

```bash
aws bedrock-runtime invoke-model \
    --region eu-central-1 \
    --model-id "anthropic.claude-3-haiku-20240307-v1:0" \
    --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
    --cli-binary-format raw-in-base64-out \
    /tmp/response.json

cat /tmp/response.json
```

## Recommended Models for Testing

### Start with Claude 3 Haiku

Claude 3 Haiku is the fastest to get approved and cheapest for testing:

```bash
python3 orchestrator.py "Build a simple hello world page" \
    --docker \
    --docker-use-bedrock \
    --docker-bedrock-model "anthropic.claude-3-haiku-20240307-v1:0" \
    --docker-aws-access-key-id "$AWS_ACCESS_KEY_ID" \
    --docker-aws-secret-access-key "$AWS_SECRET_ACCESS_KEY" \
    --max-executors 2 \
    --real
```

### Then Upgrade to Claude 3.5 Sonnet

Once Haiku works, try the default Sonnet 4.5 for best quality (uses global model by default):

```bash
python3 orchestrator.py "Build a contact form" \
    --docker \
    --docker-use-bedrock \
    --docker-aws-access-key-id "$AWS_ACCESS_KEY_ID" \
    --docker-aws-secret-access-key "$AWS_SECRET_ACCESS_KEY" \
    --max-executors 2 \
    --real
```

## Common Error Messages and Solutions

### Error: "You don't have access to the model"

**Solution:** Request model access in Bedrock console (see Step 2 above)

### Error: "The provided model identifier is invalid"

**Solutions:**
1. Check model ID format matches examples above
2. Verify model is available in your region
3. Use `aws bedrock list-foundation-models` to see available IDs

### Error: "Unable to locate credentials"

**Solution:**
```bash
# Set credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# Or pass via CLI
--docker-aws-access-key-id "..." \
--docker-aws-secret-access-key "..."
```

### Error: "Rate limit exceeded"

**Solution:** Reduce `--max-executors` or add delays:
```bash
--max-executors 2  # Instead of 10
```

## Current Default Configuration

The orchestrator currently defaults to:
- **Region**: eu-central-1
- **Model**: `global.anthropic.claude-sonnet-4-5-20250929-v1:0`

This global inference profile works across all AWS regions and provides:
- ✅ No region-specific model ID needed
- ✅ Automatic routing to the best available endpoint
- ✅ Consistent behavior across deployments
- ✅ Latest Claude Sonnet 4.5 model

**To use a different model:**
```bash
# Use CLI flag to override (e.g., Claude 3.5 Sonnet v2):
--docker-bedrock-model "global.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

## Verification Checklist

Before running with `--real`:

- [ ] AWS credentials configured (`aws sts get-caller-identity` works)
- [ ] Model access requested in Bedrock console
- [ ] Model ID verified with `aws bedrock list-foundation-models`
- [ ] Test invocation successful (see Test 3 above)
- [ ] Correct region specified
- [ ] Correct model ID for your region

## Support Resources

- [AWS Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
- [Anthropic Models on Bedrock](https://docs.anthropic.com/en/api/claude-on-amazon-bedrock)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

## Example: Full Working Setup

```bash
# 1. Request model access (do once in AWS console)

# 2. Verify setup
aws bedrock list-foundation-models --region eu-central-1 --by-provider anthropic

# 3. Run orchestrator with working model
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

python3 orchestrator.py "Build a simple webpage" \
    --docker \
    --docker-planner-in-docker \
    --docker-use-bedrock \
    --docker-bedrock-region eu-central-1 \
    --docker-bedrock-model "global.anthropic.claude-sonnet-4-5-20250929-v1:0" \
    --max-executors 2 \
    --real
```

## Next Steps

1. **Request model access** in AWS Bedrock console
2. **Test with Haiku** first (fastest approval, cheapest)
3. **Upgrade to Sonnet** once Haiku works
4. **Update default model** in config.py once you know which model works for your account
