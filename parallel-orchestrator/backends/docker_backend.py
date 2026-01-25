"""
Docker Backend for Parallel Orchestrator

Runs executor agents in local Docker containers for parallel task execution.
"""

import json
import time
import os
import docker
from pathlib import Path
from typing import Dict, List, Set, Any, Callable
from .base import ExecutionBackend

class DockerBackend(ExecutionBackend):
    """
    Backend that runs executors in local Docker containers.

    Features:
    - Parallel execution using Docker containers
    - Volume mounting for file sharing
    - No cloud infrastructure required
    - Similar interface to AWS Batch backend
    """

    def __init__(self, config: Any, output_dir: Path, log_func: Callable[[str], None]):
        """
        Initialize Docker backend.

        Args:
            config: OrchestratorConfig with Docker settings
            output_dir: Directory for outputs
            log_func: Logging function
        """
        super().__init__(config, output_dir, log_func)

        docker_config = config.docker if hasattr(config, 'docker') else None
        self.docker_image = docker_config.image if docker_config else "parallel-orchestrator:latest"
        self.network = docker_config.network if docker_config else None

        # AWS Bedrock configuration
        self.use_bedrock = docker_config.use_bedrock if docker_config else False
        if self.use_bedrock:
            self.aws_access_key_id = (
                docker_config.aws_access_key_id if docker_config
                else os.environ.get("AWS_ACCESS_KEY_ID")
            )
            self.aws_secret_access_key = (
                docker_config.aws_secret_access_key if docker_config
                else os.environ.get("AWS_SECRET_ACCESS_KEY")
            )
            self.aws_session_token = (
                docker_config.aws_session_token if docker_config
                else os.environ.get("AWS_SESSION_TOKEN")
            )
            self.bedrock_region = docker_config.bedrock_region if docker_config else "eu-central-1"
            self.bedrock_model = docker_config.bedrock_model if docker_config else "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
            self.anthropic_api_key = None
        else:
            self.anthropic_api_key = (
                docker_config.anthropic_api_key if docker_config
                else os.environ.get("ANTHROPIC_API_KEY")
            )
            self.aws_access_key_id = None
            self.aws_secret_access_key = None
            self.aws_session_token = None
            self.bedrock_region = None
            self.bedrock_model = None

        try:
            self.client = docker.from_env()
            self.log(f"  Connected to Docker daemon")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")

        self.containers: Dict[str, docker.models.containers.Container] = {}
        self.task_status: Dict[str, str] = {}
        self.task_results: Dict[str, Dict[str, Any]] = {}
        self.executor_tasks: Dict[int, List[Dict]] = {}
        self.use_real = False

    def initialize(self) -> None:
        """Setup Docker environment and build image if needed."""
        self.log("\n  Docker backend initialization...")

        # Check if image exists
        try:
            self.client.images.get(self.docker_image)
            self.log(f"  Docker image '{self.docker_image}' found")
        except docker.errors.ImageNotFound:
            self.log(f"  Docker image '{self.docker_image}' not found")
            self.log(f"  Please build the image first:")
            self.log(f"    cd parallel-orchestrator/docker")
            self.log(f"    docker build -t {self.docker_image} .")
            raise RuntimeError(f"Docker image not found: {self.docker_image}")

        # Create network if specified
        if self.network:
            try:
                self.client.networks.get(self.network)
                self.log(f"  Docker network '{self.network}' exists")
            except docker.errors.NotFound:
                self.log(f"  Creating Docker network '{self.network}'")
                self.client.networks.create(self.network, driver="bridge")

        # Initialize task statuses
        for task in self.tasks:
            self.task_status[task['id']] = 'pending'

    def submit_tasks(
        self,
        tasks: List[Dict[str, Any]],
        plan: Dict[str, Any],
        requirements: str,
        use_real_executors: bool
    ) -> None:
        """
        Submit tasks for execution.

        Args:
            tasks: List of task definitions
            plan: Execution plan with dependencies
            requirements: Original requirements string
            use_real_executors: Whether to use real Claude API
        """
        self.tasks = tasks
        self.plan = plan
        self.requirements = requirements
        self.use_real = use_real_executors

        # Distribute tasks to executors
        num_executors = min(self.config.max_executors, len(tasks))
        self.executor_tasks = {i: [] for i in range(num_executors)}

        # Simple round-robin distribution
        for idx, task in enumerate(tasks):
            executor_id = idx % num_executors
            self.executor_tasks[executor_id].append(task)

        # Remove empty executors
        self.executor_tasks = {k: v for k, v in self.executor_tasks.items() if v}

        self.log(f"  Distributed {len(tasks)} tasks across {len(self.executor_tasks)} executors")

    def wait_for_completion(self, max_executors: int) -> None:
        """
        Wait for all submitted tasks to complete.

        Args:
            max_executors: Maximum number of concurrent executors
        """
        self.log("\n  Starting Docker containers...")

        # Start containers
        for executor_id, task_list in self.executor_tasks.items():
            self._start_executor_container(executor_id, task_list)

        # Monitor containers
        self._monitor_containers()

        # Collect results
        self._collect_results()

    def _start_executor_container(self, executor_id: int, tasks: List[Dict]):
        """Start a Docker container for an executor."""
        container_name = f"po-executor-{executor_id}"

        # Prepare environment variables
        env = {
            "EXECUTOR_ID": str(executor_id),
            "OUTPUT_DIR": "/output",
            "REQUIREMENTS": self.requirements,
            "USE_REAL_EXECUTORS": "1" if self.use_real else "0",
        }

        # Add Bedrock or Anthropic credentials
        if self.use_bedrock:
            env["USE_BEDROCK"] = "1"
            if self.aws_access_key_id:
                env["AWS_ACCESS_KEY_ID"] = self.aws_access_key_id
            if self.aws_secret_access_key:
                env["AWS_SECRET_ACCESS_KEY"] = self.aws_secret_access_key
            if self.aws_session_token:
                env["AWS_SESSION_TOKEN"] = self.aws_session_token
            if self.bedrock_region:
                env["BEDROCK_REGION"] = self.bedrock_region
            if self.bedrock_model:
                env["BEDROCK_MODEL"] = self.bedrock_model
        else:
            if self.anthropic_api_key:
                env["ANTHROPIC_API_KEY"] = self.anthropic_api_key

        # Prepare volumes
        executor_dir = self.output_dir / f"executor_{executor_id}"
        executor_dir.mkdir(parents=True, exist_ok=True)

        # Write tasks to file for container to read
        tasks_file = executor_dir / "tasks.json"
        with open(tasks_file, 'w') as f:
            json.dump({
                "tasks": tasks,
                "plan": self.plan,
                "requirements": self.requirements
            }, f, indent=2)

        volumes = {
            str(executor_dir.absolute()): {
                'bind': '/output',
                'mode': 'rw'
            }
        }

        # Container configuration
        container_config = {
            'image': self.docker_image,
            'name': container_name,
            'environment': env,
            'volumes': volumes,
            'detach': True,
            'remove': False,  # Keep container for logs
            'network': self.network if self.network else None,
            'command': 'python3 /app/docker_executor.py',
        }

        try:
            self.log(f"    Starting {container_name}: {len(tasks)} tasks")

            container = self.client.containers.run(**container_config)
            self.containers[container_name] = container

            # Mark tasks as in progress
            for task in tasks:
                self.task_status[task['id']] = 'in_progress'

            self.log(f"      ✓ Container started: {container.id[:12]}")

        except Exception as e:
            self.log(f"      ✗ Failed to start container: {e}")
            for task in tasks:
                self.task_status[task['id']] = 'failed'
                self.task_results[task['id']] = {
                    'task_id': task['id'],
                    'status': 'failed',
                    'error': str(e)
                }

    def _monitor_containers(self):
        """Monitor running containers until all complete."""
        self.log("\n  Monitoring containers...")

        start_time = time.time()
        check_interval = 5

        while True:
            running = 0
            completed = 0
            failed = 0

            for container_name, container in list(self.containers.items()):
                try:
                    container.reload()
                    status = container.status

                    if status == 'running':
                        running += 1
                    elif status == 'exited':
                        exit_code = container.attrs['State']['ExitCode']
                        if exit_code == 0:
                            completed += 1
                        else:
                            failed += 1
                            self.log(f"    ✗ {container_name} failed with exit code {exit_code}")
                            # Get logs
                            logs = container.logs(tail=50).decode('utf-8')
                            self.log(f"      Last 50 lines of logs:")
                            for line in logs.split('\n')[-50:]:
                                if line.strip():
                                    self.log(f"        {line}")
                except docker.errors.NotFound:
                    completed += 1
                except Exception as e:
                    self.log(f"    Error checking {container_name}: {e}")
                    failed += 1

            elapsed = int(time.time() - start_time)
            self.log(f"    [{elapsed}s] Running: {running}, Completed: {completed}, Failed: {failed}")

            if running == 0:
                break

            time.sleep(check_interval)

        self.log(f"  All containers finished")

    def _collect_results(self):
        """Collect results from executor output directories."""
        self.log("\n  Collecting results...")

        for executor_id in self.executor_tasks.keys():
            executor_dir = self.output_dir / f"executor_{executor_id}"

            if not executor_dir.exists():
                self.log(f"    ✗ Executor {executor_id} output directory not found")
                continue

            # Look for task result directories
            for task_dir in executor_dir.glob("task_*"):
                task_id = task_dir.name

                # Check for result.json
                result_file = task_dir / "result.json"
                if result_file.exists():
                    try:
                        with open(result_file, 'r') as f:
                            result = json.load(f)
                        self.task_results[task_id] = result
                        self.task_status[task_id] = result.get('status', 'completed')
                        self.log(f"    ✓ Collected result for {task_id}")
                    except Exception as e:
                        self.log(f"    ✗ Failed to read result for {task_id}: {e}")
                        self.task_status[task_id] = 'failed'
                else:
                    # No result file - check if task completed
                    if (task_dir / "claude_response.txt").exists():
                        # Task ran but no result.json - mark as completed
                        self.task_status[task_id] = 'completed'
                        self.task_results[task_id] = {
                            'task_id': task_id,
                            'status': 'completed',
                            'output_dir': str(task_dir)
                        }
                        self.log(f"    ⚠ No result.json for {task_id}, but output exists")

    def get_task_status(self, task_id: str) -> str:
        """Get the current status of a task."""
        return self.task_status.get(task_id, 'pending')

    def get_results(self) -> List[Dict[str, Any]]:
        """Get results from all completed tasks."""
        return list(self.task_results.values())

    def mark_task_complete(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark a task as completed with its result."""
        self.task_status[task_id] = 'completed'
        self.task_results[task_id] = result

    def mark_task_failed(self, task_id: str, error: str) -> None:
        """Mark a task as failed with an error message."""
        self.task_status[task_id] = 'failed'
        self.task_results[task_id] = {
            'task_id': task_id,
            'status': 'failed',
            'error': error
        }

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """Check if a task's dependencies are satisfied."""
        task_id = task['id']
        dependencies = self.plan.get('dependencies', {}).get(task_id, [])

        for dep_id in dependencies:
            if self.task_status.get(dep_id) != 'completed':
                return False

        return True

    def get_completed_tasks(self) -> Set[str]:
        """Get set of completed task IDs."""
        return {
            task_id for task_id, status in self.task_status.items()
            if status == 'completed'
        }

    def get_in_progress_tasks(self) -> Set[str]:
        """Get set of in-progress task IDs."""
        return {
            task_id for task_id, status in self.task_status.items()
            if status == 'in_progress'
        }

    def cleanup(self) -> None:
        """Cleanup Docker containers and resources."""
        self.log("\n  Cleaning up Docker resources...")

        # Stop and remove containers
        for container_name, container in self.containers.items():
            try:
                container.reload()
                if container.status == 'running':
                    self.log(f"    Stopping {container_name}")
                    container.stop(timeout=10)

                # Remove container
                container.remove()
                self.log(f"    Removed {container_name}")
            except docker.errors.NotFound:
                pass
            except Exception as e:
                self.log(f"    Error cleaning up {container_name}: {e}")

        self.log("  Docker cleanup complete")

    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the backend."""
        return {
            "backend": "DockerBackend",
            "docker_image": self.docker_image,
            "network": self.network,
            "containers": len(self.containers),
            "output_dir": str(self.output_dir),
        }
