# Dockerfile for Parallel Orchestrator AWS Batch
# Contains Node.js, Python, AWS CLI, and Claude Code CLI

FROM node:20-slim

# Install Python and AWS CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user for Claude Code CLI
# Claude Code CLI doesn't allow --dangerously-skip-permissions with root
RUN useradd -m -s /bin/bash executor \
    && mkdir -p /app /output \
    && chown -R executor:executor /app /output

# Create working directory
WORKDIR /app

# Copy executor scripts from parent directory
COPY --chown=executor:executor ../batch_executor.py /app/
COPY --chown=executor:executor ../docker_executor.py /app/
COPY --chown=executor:executor ../docker_planner.py /app/
COPY --chown=executor:executor ../executor_agent.py /app/
COPY --chown=executor:executor ../planner_agent.py /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/executor

# Switch to non-root user
USER executor

# Default command
CMD ["python3", "/app/batch_executor.py"]
