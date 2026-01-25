#!/usr/bin/env python3
"""
Website Development Orchestrator
Coordinates multiple specialized agents to build websites
Supports both local and Docker execution modes
"""

import os
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from claude_api import ClaudeAPI


class WebsiteOrchestrator:
    """
    Orchestrates website development using specialized agents
    - Design Agent: Creates design specifications
    - Implementation Agent: Builds React UI
    - Testing Agent: Creates and runs tests

    Supports both local and Docker execution modes
    """

    def __init__(self,
                 project_dir: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 use_docker: bool = False,
                 docker_image: str = "orchestrator-agents:latest",
                 use_bedrock: bool = False,
                 bedrock_region: str = "eu-central-1",
                 bedrock_model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"):
        """
        Initialize orchestrator

        Args:
            project_dir: Directory for the project being worked on
            output_dir: Directory for orchestrator outputs
            use_docker: Whether to run agents in Docker containers
            docker_image: Docker image to use for agents
            use_bedrock: Whether to use AWS Bedrock instead of Anthropic API
            bedrock_region: AWS region for Bedrock
            bedrock_model: Bedrock model ID
        """
        self.api = ClaudeAPI(project_dir) if not use_docker else None
        self.project_dir = os.path.abspath(project_dir or os.getcwd())
        # Default to centralized outputs directory
        default_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "website-orchestrator")
        self.output_dir = os.path.abspath(output_dir or default_output)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Docker configuration
        self.use_docker = use_docker
        self.docker_image = docker_image
        self.use_bedrock = use_bedrock
        self.bedrock_region = bedrock_region
        self.bedrock_model = bedrock_model

        # Agent results storage
        self.results = {
            "design": None,
            "implementation": None,
            "testing": None
        }

        # Verify Docker if using Docker mode
        if self.use_docker:
            self._verify_docker()

    def _verify_docker(self):
        """Verify Docker is available"""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("Docker is not running")
            print("✓ Docker is available")
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            raise RuntimeError(f"Docker verification failed: {e}")

    def _get_docker_env_vars(self) -> Dict[str, str]:
        """Get environment variables for Docker containers"""
        env_vars = {}

        if self.use_bedrock:
            # AWS Bedrock mode
            env_vars["USE_BEDROCK"] = "1"
            env_vars["BEDROCK_REGION"] = self.bedrock_region
            env_vars["BEDROCK_MODEL"] = self.bedrock_model

            # Get AWS credentials from environment
            aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
            aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

            if not aws_access_key or not aws_secret_key:
                raise ValueError("AWS credentials not found in environment. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")

            env_vars["AWS_ACCESS_KEY_ID"] = aws_access_key
            env_vars["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
            if aws_session_token:
                env_vars["AWS_SESSION_TOKEN"] = aws_session_token
        else:
            # Anthropic API mode
            env_vars["USE_BEDROCK"] = "0"
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")

            env_vars["ANTHROPIC_API_KEY"] = anthropic_key

        return env_vars

    def _execute_agent_in_docker(self,
                                  agent_name: str,
                                  task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent in a Docker container

        Args:
            agent_name: Name of the agent (design, implementation, testing)
            task: Task definition to pass to the agent

        Returns:
            Result from the agent
        """
        print(f"\n🐳 Running {agent_name} agent in Docker...")

        # Create temporary directories for input/output
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(input_dir)
            os.makedirs(output_dir)

            # Write task definition
            task_file = os.path.join(input_dir, "task.json")
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)

            # Build docker command
            docker_cmd = [
                "docker", "run",
                "--rm",
                "-v", f"{input_dir}:/input:ro",
                "-v", f"{output_dir}:/output:rw"
            ]

            # Add environment variables
            env_vars = self._get_docker_env_vars()
            for key, value in env_vars.items():
                docker_cmd.extend(["-e", f"{key}={value}"])

            # Add image
            docker_cmd.append(self.docker_image)

            # Execute container
            print(f"  Starting container...")
            try:
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )

                print(f"  Container output:")
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            print(f"    {line}")

                if result.returncode != 0:
                    print(f"  Container failed with exit code {result.returncode}")
                    if result.stderr:
                        print(f"  Error output:")
                        for line in result.stderr.split('\n'):
                            if line.strip():
                                print(f"    {line}")
                    return {
                        "success": False,
                        "error": f"Container execution failed: {result.stderr}"
                    }

                # Read result
                result_file = os.path.join(output_dir, "result.json")
                if os.path.exists(result_file):
                    with open(result_file, 'r') as f:
                        agent_result = json.load(f)
                    print(f"  ✓ Agent completed successfully")
                    return agent_result
                else:
                    print(f"  ✗ Result file not found")
                    return {
                        "success": False,
                        "error": "Result file not produced by agent"
                    }

            except subprocess.TimeoutExpired:
                print(f"  ✗ Container execution timed out")
                return {
                    "success": False,
                    "error": "Container execution timed out after 10 minutes"
                }
            except Exception as e:
                print(f"  ✗ Error: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    def check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available"""
        if self.use_docker:
            # In Docker mode, we don't need local Claude CLI
            return True
        return self.api.health_check()

    def save_result(self, stage: str, data: Any):
        """Save results from a stage"""
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"{stage}_{timestamp}.json")

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ {stage.capitalize()} results saved to: {output_file}")
        return output_file

    def delegate_to_subagent(self,
                            subagent_name: str,
                            prompt: str,
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Delegate a task to a specialized subagent
        Supports both local and Docker execution

        Args:
            subagent_name: Name of the subagent
            prompt: Task description
            context: Additional context for the task

        Returns:
            Response from the subagent
        """
        print(f"\n{'='*70}")
        print(f"🤖 Delegating to {subagent_name.upper()} Agent")
        print(f"{'='*70}")

        # Build full prompt with context
        full_prompt = f"{prompt}"
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            full_prompt = f"{prompt}\n\nContext:\n{context_str}"

        print(f"\nTask: {prompt[:100]}...")
        print(f"Execution mode: {'Docker' if self.use_docker else 'Local'}")
        print(f"Working...")

        try:
            if self.use_docker:
                # Docker execution
                task = {
                    "agent": subagent_name,
                    "prompt": full_prompt,
                    "context": context or {}
                }
                result = self._execute_agent_in_docker(subagent_name, task)
            else:
                # Local execution
                response = self.api.query(full_prompt, cwd=self.project_dir)

                if response.get("success"):
                    result = {
                        "subagent": subagent_name,
                        "success": True,
                        "response": response.get("response"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    result = {
                        "subagent": subagent_name,
                        "success": False,
                        "error": "Query returned unsuccessful status"
                    }

            if result.get("success"):
                print(f"✓ {subagent_name.capitalize()} completed successfully")
                self.results[subagent_name] = result
                return result
            else:
                print(f"✗ {subagent_name.capitalize()} failed")
                return result

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return {
                "subagent": subagent_name,
                "success": False,
                "error": str(e)
            }

    def build_website(self, requirements: str) -> Dict[str, Any]:
        """
        Main orchestration flow to build a website

        Args:
            requirements: User requirements for the website

        Returns:
            Summary of all stages
        """
        print("\n" + "="*70)
        print("🎯 WEBSITE DEVELOPMENT ORCHESTRATOR")
        print("="*70)
        print(f"\nRequirements: {requirements}")
        print(f"Project Directory: {self.project_dir}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Execution Mode: {'Docker' if self.use_docker else 'Local'}")
        if self.use_docker:
            print(f"Docker Image: {self.docker_image}")
            print(f"AI Mode: {'AWS Bedrock' if self.use_bedrock else 'Anthropic API'}")
            if self.use_bedrock:
                print(f"Bedrock Region: {self.bedrock_region}")
                print(f"Bedrock Model: {self.bedrock_model}")

        # Check availability
        if not self.check_claude_available():
            print("\n✗ Claude Code CLI is not available!")
            print("Please make sure 'claude' command is installed and in your PATH")
            return {"success": False, "error": "Claude Code CLI not available"}

        if self.use_docker:
            print("\n✓ Docker is ready")
        else:
            print("\n✓ Claude Code CLI is ready")

        summary = {
            "requirements": requirements,
            "execution_mode": "docker" if self.use_docker else "local",
            "stages": {},
            "start_time": datetime.now().isoformat()
        }

        # Stage 1: Design
        from design_agent import DesignAgent
        design_agent = DesignAgent(self)
        design_result = design_agent.execute(requirements)
        summary["stages"]["design"] = design_result
        self.save_result("design", design_result)

        if not design_result.get("success"):
            print("\n✗ Design stage failed. Stopping orchestration.")
            return summary

        # Stage 2: Implementation
        from implementation_agent import ImplementationAgent
        impl_agent = ImplementationAgent(self)
        impl_result = impl_agent.execute(requirements, design_result)
        summary["stages"]["implementation"] = impl_result
        self.save_result("implementation", impl_result)

        if not impl_result.get("success"):
            print("\n✗ Implementation stage failed. Stopping orchestration.")
            return summary

        # Stage 3: Testing
        from testing_agent import TestingAgent
        test_agent = TestingAgent(self)
        test_result = test_agent.execute(requirements, impl_result)
        summary["stages"]["testing"] = test_result
        self.save_result("testing", test_result)

        # Final summary
        summary["end_time"] = datetime.now().isoformat()
        summary["success"] = all(
            stage.get("success", False)
            for stage in summary["stages"].values()
        )

        # Save complete summary
        self.save_result("complete_summary", summary)

        print("\n" + "="*70)
        print("🎉 ORCHESTRATION COMPLETE")
        print("="*70)
        print(f"\n✓ Design: {'SUCCESS' if design_result.get('success') else 'FAILED'}")
        print(f"✓ Implementation: {'SUCCESS' if impl_result.get('success') else 'FAILED'}")
        print(f"✓ Testing: {'SUCCESS' if test_result.get('success') else 'FAILED'}")
        print(f"\nResults saved to: {self.output_dir}")

        return summary


if __name__ == "__main__":
    # Simple CLI interface
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Build a website using AI-powered orchestrator"
    )
    parser.add_argument(
        "requirements",
        help="Website requirements description"
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Run agents in Docker containers"
    )
    parser.add_argument(
        "--docker-image",
        default="orchestrator-agents:latest",
        help="Docker image to use (default: orchestrator-agents:latest)"
    )
    parser.add_argument(
        "--docker-use-bedrock",
        action="store_true",
        help="Use AWS Bedrock instead of Anthropic API"
    )
    parser.add_argument(
        "--docker-bedrock-region",
        default="eu-central-1",
        help="AWS region for Bedrock (default: eu-central-1)"
    )
    parser.add_argument(
        "--docker-bedrock-model",
        default="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        help="Bedrock model ID (default: global.anthropic.claude-sonnet-4-5-20250929-v1:0)"
    )

    args = parser.parse_args()

    orchestrator = WebsiteOrchestrator(
        project_dir=os.getcwd(),
        use_docker=args.docker,
        docker_image=args.docker_image,
        use_bedrock=args.docker_use_bedrock,
        bedrock_region=args.docker_bedrock_region,
        bedrock_model=args.docker_bedrock_model
    )
    result = orchestrator.build_website(args.requirements)

    sys.exit(0 if result.get("success") else 1)
