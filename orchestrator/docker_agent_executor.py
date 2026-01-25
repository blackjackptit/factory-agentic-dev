#!/usr/bin/env python3
"""
Docker Agent Executor
Runs design, implementation, or testing agent inside a Docker container
"""

import os
import json
import sys
import subprocess
from pathlib import Path


def setup_bedrock_environment():
    """Configure environment for AWS Bedrock if enabled"""
    use_bedrock = os.environ.get("USE_BEDROCK", "0") == "1"

    if use_bedrock:
        print("🔧 Configuring AWS Bedrock mode...")
        os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"

        # Set AWS credentials from environment
        aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_session_token = os.environ.get("AWS_SESSION_TOKEN")
        bedrock_region = os.environ.get("BEDROCK_REGION", "eu-central-1")
        bedrock_model = os.environ.get("BEDROCK_MODEL", "global.anthropic.claude-sonnet-4-5-20250929-v1:0")

        if not aws_access_key or not aws_secret_key:
            print("❌ Error: AWS credentials not provided")
            sys.exit(1)

        print(f"  Region: {bedrock_region}")
        print(f"  Model: {bedrock_model}")
        print("  Credentials: Configured")
    else:
        print("🔧 Using Anthropic API mode...")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_key:
            print("❌ Error: ANTHROPIC_API_KEY not provided")
            sys.exit(1)
        print("  API Key: Configured")


def read_task():
    """Read task definition from /input/task.json"""
    task_file = "/input/task.json"

    if not os.path.exists(task_file):
        print(f"❌ Error: Task file not found: {task_file}")
        sys.exit(1)

    with open(task_file, 'r') as f:
        task = json.load(f)

    return task


def execute_agent(task):
    """Execute the specified agent with the task"""
    agent_name = task.get("agent")
    prompt = task.get("prompt")
    context = task.get("context", {})

    print(f"\n{'='*70}")
    print(f"🤖 Executing {agent_name.upper()} Agent")
    print(f"{'='*70}\n")

    # Determine which agent to use
    if agent_name == "design":
        from design_agent import DesignAgent
        # Create a minimal orchestrator mock
        class MockOrchestrator:
            def __init__(self):
                self.project_dir = "/workspace"
                from claude_api import ClaudeAPI
                self.api = ClaudeAPI(self.project_dir)

            def delegate_to_subagent(self, subagent_name, prompt, context=None):
                response = self.api.query(prompt, cwd=self.project_dir)
                return {
                    "subagent": subagent_name,
                    "success": response.get("success", False),
                    "response": response.get("response", ""),
                    "error": response.get("error")
                }

        orchestrator = MockOrchestrator()
        agent = DesignAgent(orchestrator)
        result = agent.execute(task.get("requirements", prompt))

    elif agent_name == "implementation":
        from implementation_agent import ImplementationAgent
        class MockOrchestrator:
            def __init__(self):
                self.project_dir = "/workspace"
                from claude_api import ClaudeAPI
                self.api = ClaudeAPI(self.project_dir)

            def delegate_to_subagent(self, subagent_name, prompt, context=None):
                response = self.api.query(prompt, cwd=self.project_dir)
                return {
                    "subagent": subagent_name,
                    "success": response.get("success", False),
                    "response": response.get("response", ""),
                    "error": response.get("error")
                }

        orchestrator = MockOrchestrator()
        agent = ImplementationAgent(orchestrator)
        design_result = task.get("design_result", {})
        result = agent.execute(task.get("requirements", prompt), design_result)

    elif agent_name == "testing":
        from testing_agent import TestingAgent
        class MockOrchestrator:
            def __init__(self):
                self.project_dir = "/workspace"
                from claude_api import ClaudeAPI
                self.api = ClaudeAPI(self.project_dir)

            def delegate_to_subagent(self, subagent_name, prompt, context=None):
                response = self.api.query(prompt, cwd=self.project_dir)
                return {
                    "subagent": subagent_name,
                    "success": response.get("success", False),
                    "response": response.get("response", ""),
                    "error": response.get("error")
                }

        orchestrator = MockOrchestrator()
        agent = TestingAgent(orchestrator)
        impl_result = task.get("implementation_result", {})
        result = agent.execute(task.get("requirements", prompt), impl_result)
    else:
        print(f"❌ Error: Unknown agent: {agent_name}")
        sys.exit(1)

    return result


def write_result(result):
    """Write result to /output/result.json"""
    output_file = "/output/result.json"

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✓ Result written to {output_file}")


def main():
    """Main execution flow"""
    print("="*70)
    print("Docker Agent Executor")
    print("="*70)

    # Setup environment
    setup_bedrock_environment()

    # Read task
    print("\n📥 Reading task definition...")
    task = read_task()
    print(f"  Agent: {task.get('agent')}")
    print(f"  Task type: {task.get('context', {}).get('phase', 'N/A')}")

    # Execute agent
    try:
        result = execute_agent(task)
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        result = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

    # Write result
    print("\n📤 Writing result...")
    write_result(result)

    # Exit with appropriate code
    if result.get("success"):
        print("\n✓ Execution completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
