#!/usr/bin/env python3
"""
Executor Agent
Handles individual task execution with Claude API integration
"""

import os
import time
import subprocess
from typing import Dict, Any
from pathlib import Path


class ExecutorAgent:
    """
    Individual executor agent that performs specific tasks
    """

    def __init__(self, executor_id: int, task: Dict[str, Any], output_dir: str):
        self.executor_id = executor_id
        self.task = task
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.name = f"Executor-{executor_id}"
        self.status = "initialized"
        self.result = None

    def log(self, message: str):
        """Log executor activity"""
        print(f"[{self.name}] {message}")

    def call_claude_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call Claude API to execute the task
        Uses the Claude CLI interface
        """
        self.log("Calling Claude API...")

        try:
            # Build the prompt with task context
            full_prompt = f"""
You are an expert software developer working on a specific task.

TASK ASSIGNMENT:
- Task Name: {self.task['name']}
- Description: {self.task['description']}
- Priority: {self.task['priority']}

INSTRUCTIONS:
1. Implement the complete solution for this task
2. Create all necessary files with proper structure
3. Include error handling and edge cases
4. Write clean, maintainable, and well-documented code
5. Provide implementation details and file contents

OUTPUT FORMAT (CRITICAL):
You MUST output the actual complete file contents in code blocks, NOT descriptions.
For each file, use EXACTLY this format:
```html
# filename: index.html
<!DOCTYPE html>
<html>
<!-- COMPLETE FILE CONTENT HERE -->
</html>
```

DO NOT output summaries, descriptions, or plans. Output the ACTUAL CODE that will be saved to files.

REQUIREMENTS:
{prompt}

Implement this completely with full file contents in code blocks.
"""

            # Use Claude CLI (in production, replace with actual API call)
            # Get Bedrock model from environment or use default
            bedrock_model = os.environ.get("BEDROCK_MODEL", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
            use_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK", "0") == "1"

            cmd = [
                "claude",
                "--dangerously-skip-permissions",
                "--print",
            ]

            # If using Bedrock, specify the model explicitly
            if use_bedrock:
                cmd.extend(["--model", bedrock_model])

            cmd.extend(["-p", full_prompt])

            result = subprocess.run(
                cmd,
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": result.stdout,
                    "error": None
                }
            else:
                # Capture both stdout and stderr for debugging
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return {
                    "success": False,
                    "response": None,
                    "error": f"Claude CLI error (exit {result.returncode}): {error_msg[:500]}"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "response": None,
                "error": "Claude API timeout (5 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }

    def parse_and_create_files(self, response: str) -> list:
        """
        Parse Claude response and create files
        """
        import re

        created_files = []

        # First, save the raw response for debugging
        response_file = self.output_dir / "claude_response.txt"
        with open(response_file, 'w') as f:
            f.write(response)
        created_files.append(str(response_file))

        # Try multiple patterns to extract files

        # Pattern 1: # filename: path/to/file
        pattern1 = r'```(?:\w+)?\s*\n#\s*filename:\s*([^\n]+)\n(.*?)```'
        matches = list(re.finditer(pattern1, response, re.DOTALL | re.IGNORECASE))

        # Pattern 2: <!-- filename: path/to/file -->
        pattern2 = r'```(?:\w+)?\s*\n<!--\s*filename:\s*([^\n]+)\s*-->\n(.*?)```'
        matches.extend(re.finditer(pattern2, response, re.DOTALL | re.IGNORECASE))

        # Pattern 3: For single-file responses, save as index.html
        if not matches and '<!DOCTYPE' in response.upper():
            # Extract HTML content
            html_match = re.search(r'```html\s*(.*?)```', response, re.DOTALL | re.IGNORECASE)
            if html_match:
                filepath = "index.html"
                content = html_match.group(1).strip()
                full_path = self.output_dir / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
                created_files.append(str(full_path))
                self.log(f"Created file: {filepath}")
            return created_files

        for match in matches:
            filepath = match.group(1).strip()
            content = match.group(2).strip()

            # Create file
            full_path = self.output_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(content)

            created_files.append(str(full_path))
            self.log(f"Created file: {filepath}")

        return created_files

    def execute(self, requirements: str) -> Dict[str, Any]:
        """
        Execute the assigned task
        """
        self.log(f"Starting execution of task: {self.task['name']}")
        self.status = "running"

        start_time = time.time()

        try:
            # Call Claude API
            api_response = self.call_claude_api(requirements)

            if not api_response["success"]:
                raise Exception(api_response["error"])

            # Parse response and create files
            created_files = self.parse_and_create_files(api_response["response"])

            # Calculate metrics
            total_lines = 0
            for file_path in created_files:
                with open(file_path, 'r') as f:
                    total_lines += len(f.readlines())

            execution_time = time.time() - start_time

            self.result = {
                "task_id": self.task["id"],
                "executor_id": self.executor_id,
                "task_name": self.task["name"],
                "status": "completed",
                "execution_time": f"{execution_time:.2f}s",
                "output_files": created_files,
                "metrics": {
                    "lines_of_code": total_lines,
                    "files_created": len(created_files),
                    "response_length": len(api_response["response"])
                }
            }

            self.status = "completed"
            self.log(f"✓ Task completed in {execution_time:.2f}s")
            self.log(f"  Files created: {len(created_files)}")
            self.log(f"  Total lines: {total_lines}")

            return self.result

        except Exception as e:
            execution_time = time.time() - start_time

            self.result = {
                "task_id": self.task["id"],
                "executor_id": self.executor_id,
                "task_name": self.task["name"],
                "status": "failed",
                "execution_time": f"{execution_time:.2f}s",
                "error": str(e)
            }

            self.status = "failed"
            self.log(f"✗ Task failed: {str(e)}")

            return self.result

    def get_status(self) -> Dict[str, Any]:
        """Get current executor status"""
        return {
            "executor_id": self.executor_id,
            "task_name": self.task["name"],
            "status": self.status,
            "result": self.result
        }
