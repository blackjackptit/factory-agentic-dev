# Orchestrator Agents Docker Image
# Contains Claude Code CLI and Python environment for running design, implementation, and testing agents

FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for AI interaction
RUN pip3 install --no-cache-dir \
    anthropic \
    boto3

# Set working directory
WORKDIR /workspace

# Copy orchestrator code
COPY design_agent.py /workspace/
COPY implementation_agent.py /workspace/
COPY testing_agent.py /workspace/
COPY claude_api.py /workspace/
COPY docker_agent_executor.py /workspace/

# Create output directory
RUN mkdir -p /output

# Set Python to unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python3", "docker_agent_executor.py"]
