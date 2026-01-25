#!/usr/bin/env python3
"""
Parallel Task Orchestrator
Coordinates parallel executor agents using intelligent planning from PlannerAgent
Supports multiple execution backends: Threading, SLURM, AWS ParallelCluster
"""

import json
import os
import time
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from planner_agent import PlannerAgent
from executor_agent import ExecutorAgent
from config import OrchestratorConfig, parse_args, print_config
from backends import (
    ExecutionBackend,
    ThreadingBackend,
    SlurmBackend,
    AWSParallelClusterBackend,
    AWSBatchBackend,
    DockerBackend,
)


class ParallelOrchestrator:
    """
    Main orchestrator that coordinates parallel executors
    Uses PlannerAgent for intelligent complexity analysis and task planning
    Supports multiple execution backends: Threading, SLURM, AWS ParallelCluster
    """

    def __init__(
        self,
        requirements: str,
        output_dir: str = None,
        use_real_executors: bool = False,
        config: OrchestratorConfig = None
    ):
        self.requirements = requirements
        self.config = config

        # Default to centralized outputs directory
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "outputs" / "parallel-orchestrator"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.max_executors = config.max_executors if config else 5
        self.use_real_executors = use_real_executors
        self.plan = None
        self.tasks = []
        self.results = []

        # Log file
        self.log_file = self.output_dir / "orchestrator.log"

        # PlannerAgent will be initialized in run() after max_executors is set
        self.planner = None

        # Backend will be created based on config
        self.backend: Optional[ExecutionBackend] = None

    def log(self, message: str):
        """Write log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    def _create_backend(self) -> ExecutionBackend:
        """Create the appropriate execution backend based on configuration"""
        backend_type = self.config.backend_type if self.config else "threading"

        self.log(f"Creating {backend_type} execution backend...")

        if backend_type == "docker":
            return DockerBackend(self.config, self.output_dir, self.log)
        elif backend_type == "batch":
            return AWSBatchBackend(self.config, self.output_dir, self.log)
        elif backend_type == "aws":
            return AWSParallelClusterBackend(self.config, self.output_dir, self.log)
        elif backend_type == "slurm":
            return SlurmBackend(self.config, self.output_dir, self.log)
        else:
            return ThreadingBackend(self.config, self.output_dir, self.log)

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Check if a task's dependencies are satisfied
        """
        if self.backend:
            return self.backend.can_execute_task(task)

        task_id = task["id"]
        dependencies = self.plan.get("dependencies", {}).get(task_id, [])

        # Check if all dependencies are completed
        completed_tasks = self.backend.get_completed_tasks() if self.backend else set()
        for dep_id in dependencies:
            if dep_id not in completed_tasks:
                return False

        return True

    def execute_task(self, task: Dict[str, Any], executor_id: int):
        """
        Execute a single task using real or simulated executor
        """
        executor_name = f"Executor-{executor_id}"
        task_output_dir = self.output_dir / f"executor_{executor_id}" / task["id"]
        task_output_dir.mkdir(parents=True, exist_ok=True)

        self.log(f"\n[{executor_name}] Starting task: {task['name']}")
        self.log(f"[{executor_name}]   Task ID: {task['id']}")
        self.log(f"[{executor_name}]   Description: {task['description']}")
        self.log(f"[{executor_name}]   Priority: {task['priority']}")
        if task.get('estimated_duration'):
            self.log(f"[{executor_name}]   Estimated duration: {task['estimated_duration']}")

        start_time = time.time()

        try:
            if self.use_real_executors:
                # Use real ExecutorAgent with Claude API
                agent = ExecutorAgent(executor_id, task, str(task_output_dir))
                # Execute the specific task description, with overall requirements as context
                task_prompt = f"{task['description']}\n\nOverall project context: {self.requirements}"
                result = agent.execute(task_prompt)

                self.log(f"[{executor_name}] Task {task['id']} completed successfully")
                self.log(f"[{executor_name}]   Execution time: {result['execution_time']}")
                self.log(f"[{executor_name}]   Files created: {len(result.get('output_files', []))}")
            else:
                # Simulate task execution with progress updates
                steps = 5
                for step in range(1, steps + 1):
                    time.sleep(1)  # Simulate work
                    progress = (step / steps) * 100
                    self.log(f"[{executor_name}]   Progress: {progress:.0f}% - Step {step}/{steps}")

                # Create result
                result = {
                    "task_id": task["id"],
                    "executor_id": executor_id,
                    "task_name": task["name"],
                    "status": "completed",
                    "execution_time": f"{time.time() - start_time:.2f}s",
                    "output_files": [
                        f"{task_output_dir}/implementation.py",
                        f"{task_output_dir}/tests.py",
                        f"{task_output_dir}/README.md"
                    ],
                    "metrics": {
                        "lines_of_code": 150 + (executor_id * 50),
                        "test_coverage": 85 + (executor_id * 2),
                        "complexity_score": 3 + executor_id
                    }
                }

                # Simulate file creation
                for file_path in result["output_files"]:
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, "w") as f:
                        f.write(f"# {task['name']}\n\n")
                        f.write(f"# Generated by {executor_name}\n")
                        f.write(f"# Task ID: {task['id']}\n")
                        f.write(f"# Task: {task['description']}\n\n")
                        f.write(f"# Implementation code would go here\n")

                self.log(f"[{executor_name}] Task {task['id']} completed successfully")
                self.log(f"[{executor_name}]   Execution time: {result['execution_time']}")
                self.log(f"[{executor_name}]   Files created: {len(result['output_files'])}")

            # Mark task complete via backend
            if self.backend:
                self.backend.mark_task_complete(task["id"], result)
            else:
                self.results.append(result)

        except Exception as e:
            self.log(f"[{executor_name}] Task {task['id']} failed: {str(e)}")
            error_msg = str(e)

            if self.backend:
                self.backend.mark_task_failed(task["id"], error_msg)
            else:
                result = {
                    "task_id": task["id"],
                    "executor_id": executor_id,
                    "task_name": task["name"],
                    "status": "failed",
                    "error": error_msg
                }
                self.results.append(result)

    def execute_parallel(self):
        """
        Execute all tasks using the configured backend
        """
        self.log("\n" + "="*80)
        self.log("STEP 3: EXECUTING TASKS WITH BACKEND")
        self.log("="*80)

        # Create and initialize backend
        self.backend = self._create_backend()
        self.backend.initialize()

        # Log backend info
        backend_info = self.backend.get_backend_info()
        self.log(f"  Backend: {backend_info['backend']}")
        for key, value in backend_info.items():
            if key != 'backend':
                self.log(f"    {key}: {value}")

        num_tasks = len(self.tasks)
        self.log(f"\n  Total tasks: {num_tasks}")
        self.log(f"  Executor budget: {self.max_executors}")

        # Submit tasks to backend
        self.backend.submit_tasks(
            self.tasks,
            self.plan,
            self.requirements,
            self.use_real_executors
        )

        # For threading backend, set the executor function
        if isinstance(self.backend, ThreadingBackend):
            self.backend.set_executor_function(self.execute_task)

        # Wait for all tasks to complete
        self.backend.wait_for_completion(self.max_executors)

        # Collect results
        self.results = self.backend.get_results()

    def aggregate_results(self) -> Dict[str, Any]:
        """
        Aggregate results from all executors
        """
        self.log("\n" + "="*80)
        self.log("STEP 4: AGGREGATING RESULTS")
        self.log("="*80)

        completed = sum(1 for r in self.results if r.get("status") == "completed")
        failed = sum(1 for r in self.results if r.get("status") == "failed")

        total_files = sum(len(r.get("output_files", [])) for r in self.results
                         if r.get("status") == "completed")

        total_loc = sum(r.get("metrics", {}).get("lines_of_code", 0)
                       for r in self.results if r.get("status") == "completed")

        avg_coverage = (sum(r.get("metrics", {}).get("test_coverage", 0)
                           for r in self.results if r.get("status") == "completed") /
                       max(completed, 1))

        summary = {
            "total_tasks": len(self.tasks),
            "completed": completed,
            "failed": failed,
            "success_rate": f"{(completed / max(len(self.tasks), 1) * 100):.1f}%",
            "total_files_created": total_files,
            "total_lines_of_code": total_loc,
            "average_test_coverage": f"{avg_coverage:.1f}%",
            "backend": self.backend.get_backend_info() if self.backend else {"backend": "threading"},
            "results": self.results
        }

        self.log(f"  Total tasks: {summary['total_tasks']}")
        self.log(f"  Completed: {summary['completed']}")
        self.log(f"  Failed: {summary['failed']}")
        self.log(f"  Success rate: {summary['success_rate']}")
        self.log(f"  Total files created: {summary['total_files_created']}")
        self.log(f"  Total lines of code: {summary['total_lines_of_code']}")
        self.log(f"  Average test coverage: {summary['average_test_coverage']}")

        # Save summary
        summary_file = self.output_dir / "execution_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.log(f"\n  Summary saved to {summary_file}")

        return summary

    def merge_outputs(self):
        """
        Merge all executor outputs into a unified project structure
        Organizes implementation files, tests, and documentation at project root
        """
        self.log("\n" + "="*80)
        self.log("STEP 5: MERGING EXECUTOR OUTPUTS")
        self.log("="*80)

        # Place consolidated files at the root of the project directory
        src_dir = self.output_dir / "src"
        tests_dir = self.output_dir / "tests"
        docs_dir = self.output_dir / "docs"

        # Create directory structure
        for directory in [src_dir, tests_dir, docs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.log(f"  Consolidating files at project root: {self.output_dir}")

        # Track files and README content
        readme_sections = []
        files_merged = 0

        # Iterate through all executor directories
        executor_dirs = sorted([d for d in self.output_dir.iterdir()
                               if d.is_dir() and d.name.startswith("executor_")])

        self.log(f"  Found {len(executor_dirs)} executor directories to merge")

        for executor_dir in executor_dirs:
            executor_name = executor_dir.name
            self.log(f"\n  Processing {executor_name}...")

            # Iterate through task directories
            task_dirs = sorted([d for d in executor_dir.iterdir() if d.is_dir()])

            for task_dir in task_dirs:
                task_id = task_dir.name
                self.log(f"    - Merging {task_id}")

                # Find the task info
                task_info = next((t for t in self.tasks if t["id"] == task_id), None)

                if not task_info:
                    continue

                task_name = task_info["name"].lower().replace(" ", "_").replace("-", "_")

                # Process implementation.py
                impl_file = task_dir / "implementation.py"
                if impl_file.exists():
                    target_file = src_dir / f"{task_name}.py"
                    shutil.copy2(impl_file, target_file)
                    files_merged += 1
                    self.log(f"      -> {target_file.relative_to(self.output_dir)}")

                # Process tests.py
                test_file = task_dir / "tests.py"
                if test_file.exists():
                    target_file = tests_dir / f"test_{task_name}.py"
                    shutil.copy2(test_file, target_file)
                    files_merged += 1
                    self.log(f"      -> {target_file.relative_to(self.output_dir)}")

                # Process README.md
                readme_file = task_dir / "README.md"
                if readme_file.exists():
                    with open(readme_file, "r") as f:
                        content = f.read()
                    readme_sections.append(f"## {task_info['name']}\n\n{content}\n")

        # Create combined README
        combined_readme = self.output_dir / "README.md"
        with open(combined_readme, "w") as f:
            f.write(f"# {self.requirements}\n\n")
            f.write(f"Generated by Parallel Task Orchestrator\n\n")
            f.write(f"## Overview\n\n")
            f.write(f"This project was generated from {len(self.tasks)} tasks executed by ")
            f.write(f"{len(executor_dirs)} parallel executors.\n\n")
            if self.backend:
                backend_info = self.backend.get_backend_info()
                f.write(f"Backend: {backend_info['backend']}\n\n")
            f.write(f"## Components\n\n")
            f.write("\n".join(readme_sections))

        files_merged += 1
        self.log(f"\n  Created combined README.md")

        # Copy execution summary and plan to docs directory
        summary_file = self.output_dir / "execution_summary.json"
        plan_file = self.output_dir / "execution_plan.json"

        if summary_file.exists():
            shutil.copy2(summary_file, docs_dir / "execution_summary.json")
            files_merged += 1
            self.log(f"  Copied execution summary to docs/")

        if plan_file.exists():
            shutil.copy2(plan_file, docs_dir / "execution_plan.json")
            files_merged += 1
            self.log(f"  Copied execution plan to docs/")

        self.log(f"\n  Consolidation complete!")
        self.log(f"  Total files consolidated: {files_merged}")
        self.log(f"  Project location: {self.output_dir}")
        self.log(f"  Structure:")
        self.log(f"    - src/       : {len(list(src_dir.glob('*.py')))} implementation files")
        self.log(f"    - tests/     : {len(list(tests_dir.glob('*.py')))} test files")
        self.log(f"    - docs/      : {len(list(docs_dir.glob('*')))} documentation files")
        self.log(f"    - README.md  : Combined documentation")

    def _run_planner_in_docker(self) -> Tuple[int, Dict[str, Any]]:
        """
        Run the planner agent in a Docker container.

        Returns:
            tuple: (num_tasks, plan) - number of tasks and the execution plan
        """
        import docker

        self.log("\n  Running planner in Docker container...")

        # Get Docker configuration
        docker_config = self.config.docker if hasattr(self.config, 'docker') else None
        docker_image = docker_config.image if docker_config else "parallel-orchestrator:latest"

        # Setup planner output directory
        planner_dir = self.output_dir / "planner"
        planner_dir.mkdir(parents=True, exist_ok=True)

        # Prepare environment variables
        env = {
            "OUTPUT_DIR": "/output",
            "REQUIREMENTS": self.requirements,
            "MAX_EXECUTORS": str(self.max_executors),
        }

        # Add Bedrock or Anthropic credentials if available
        if docker_config and docker_config.use_bedrock:
            env["USE_BEDROCK"] = "1"
            if docker_config.aws_access_key_id:
                env["AWS_ACCESS_KEY_ID"] = docker_config.aws_access_key_id
            elif os.environ.get("AWS_ACCESS_KEY_ID"):
                env["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")

            if docker_config.aws_secret_access_key:
                env["AWS_SECRET_ACCESS_KEY"] = docker_config.aws_secret_access_key
            elif os.environ.get("AWS_SECRET_ACCESS_KEY"):
                env["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")

            if docker_config.aws_session_token:
                env["AWS_SESSION_TOKEN"] = docker_config.aws_session_token
            elif os.environ.get("AWS_SESSION_TOKEN"):
                env["AWS_SESSION_TOKEN"] = os.environ.get("AWS_SESSION_TOKEN")

            if docker_config.bedrock_region:
                env["BEDROCK_REGION"] = docker_config.bedrock_region
            if docker_config.bedrock_model:
                env["BEDROCK_MODEL"] = docker_config.bedrock_model
        else:
            # Use Anthropic API key
            if docker_config and docker_config.anthropic_api_key:
                env["ANTHROPIC_API_KEY"] = docker_config.anthropic_api_key
            elif os.environ.get("ANTHROPIC_API_KEY"):
                env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY")

        # Prepare volumes
        volumes = {
            str(planner_dir.absolute()): {
                'bind': '/output',
                'mode': 'rw'
            }
        }

        # Connect to Docker
        try:
            client = docker.from_env()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")

        # Start planner container
        container_name = "po-planner"
        self.log(f"    Starting planner container: {container_name}")

        try:
            # Remove existing container if exists
            try:
                old_container = client.containers.get(container_name)
                old_container.remove(force=True)
            except docker.errors.NotFound:
                pass

            # Run container
            container = client.containers.run(
                image=docker_image,
                name=container_name,
                environment=env,
                volumes=volumes,
                detach=True,
                remove=False,
                command='python3 /app/docker_planner.py'
            )

            self.log(f"      Container started: {container.id[:12]}")
            self.log(f"      Waiting for planner to complete...")

            # Wait for container to finish
            result = container.wait()
            exit_code = result['StatusCode']

            # Get logs
            logs = container.logs().decode('utf-8')
            self.log(f"      Planner logs:")
            for line in logs.split('\n'):
                if line.strip():
                    self.log(f"        {line}")

            # Clean up container
            container.remove()

            if exit_code != 0:
                raise RuntimeError(f"Planner container failed with exit code {exit_code}")

            # Read planner output
            output_file = planner_dir / "planner_output.json"
            if not output_file.exists():
                raise RuntimeError("Planner did not produce output file")

            with open(output_file, 'r') as f:
                output_data = json.load(f)

            if not output_data.get("success", False):
                error = output_data.get("error", "Unknown error")
                raise RuntimeError(f"Planner failed: {error}")

            num_tasks = output_data["num_tasks"]
            plan = output_data["plan"]

            self.log(f"    ✓ Planner completed successfully")
            self.log(f"      Tasks: {num_tasks}")
            self.log(f"      Plan tasks: {len(plan['tasks'])}")

            return num_tasks, plan

        except Exception as e:
            self.log(f"    ✗ Failed to run planner in Docker: {e}")
            raise

    def run(self) -> Dict[str, Any]:
        """
        Main orchestrator workflow
        Delegates planning to PlannerAgent, handles execution coordination
        """
        self.log("\n" + "="*80)
        self.log("PARALLEL ORCHESTRATOR STARTING")
        self.log("="*80)
        self.log(f"Requirements: {self.requirements}")
        self.log(f"Output directory: {self.output_dir}")
        if self.config:
            self.log(f"Backend type: {self.config.backend_type}")

        start_time = time.time()

        try:
            # Check if we should run planner in Docker
            use_docker_planner = (
                self.config and
                hasattr(self.config, 'docker') and
                self.config.docker and
                self.config.docker.planner_in_docker
            )

            if use_docker_planner:
                # Run planner in Docker container
                num_tasks, plan = self._run_planner_in_docker()
            else:
                # Run planner locally (default behavior)
                # Initialize PlannerAgent with current max_executors setting
                if self.planner is None:
                    self.planner = PlannerAgent(self.requirements, str(self.output_dir), self.max_executors)

                # Step 1: Analyze complexity (delegated to PlannerAgent)
                # Returns number of tasks to create (can be more than max_executors)
                num_tasks = self.planner.analyze_complexity()

                # Step 2: Create execution plan (delegated to PlannerAgent)
                # Creates num_tasks tasks that will be executed by max_executors workers
                plan = self.planner.create_plan(num_tasks)
            self.plan = plan
            self.tasks = plan["tasks"]

            # Step 3: Execute tasks using the configured backend
            self.execute_parallel()

            # Step 4: Aggregate results
            summary = self.aggregate_results()

            # Step 5: Merge outputs into unified structure
            self.merge_outputs()

            # Cleanup backend
            if self.backend:
                self.backend.cleanup()

            total_time = time.time() - start_time

            self.log("\n" + "="*80)
            self.log("ORCHESTRATOR COMPLETED SUCCESSFULLY")
            self.log("="*80)
            self.log(f"Total execution time: {total_time:.2f}s")
            self.log(f"Output directory: {self.output_dir}")

            return summary

        except Exception as e:
            self.log(f"\n ORCHESTRATOR FAILED: {str(e)}")
            raise


def main():
    """Main entry point"""
    # Parse arguments using new config module
    config = parse_args()

    # Print configuration
    print_config(config)

    # Create orchestrator with config
    orchestrator = ParallelOrchestrator(
        config.requirements,
        config.output_dir,
        use_real_executors=config.use_real_executors,
        config=config
    )

    # Run orchestration
    summary = orchestrator.run()

    print("\n" + "="*80)
    print("EXECUTION COMPLETE")
    print("="*80)
    print(f"Backend: {config.backend_type.upper()}")
    print(f"Tasks completed: {summary['completed']} / {summary['total_tasks']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Files Created: {summary['total_files_created']}")
    print(f"Lines of Code: {summary['total_lines_of_code']}")
    print(f"\nCheck output directory: {config.output_dir or '(default)'}")

if __name__ == "__main__":
    main()
