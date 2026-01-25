"""
SLURM execution backend for local HPC clusters
Uses file-based state management and sbatch for job submission
"""

import os
import json
import time
import fcntl
import subprocess
from typing import Dict, Any, List, Set, Callable, Optional
from pathlib import Path
from datetime import datetime
import uuid

from .base import ExecutionBackend


class RetryManager:
    """Manages retry attempts for failed jobs"""

    def __init__(self, max_retries: int = 3, base_delay: float = 5.0,
                 exponential_backoff: bool = True, backoff_multiplier: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential_backoff = exponential_backoff
        self.backoff_multiplier = backoff_multiplier
        self.retry_counts: Dict[str, int] = {}

    def should_retry(self, task_id: str) -> bool:
        """Check if task should be retried"""
        return self.retry_counts.get(task_id, 0) < self.max_retries

    def record_attempt(self, task_id: str) -> int:
        """Record a retry attempt and return current count"""
        self.retry_counts[task_id] = self.retry_counts.get(task_id, 0) + 1
        return self.retry_counts[task_id]

    def get_delay(self, task_id: str) -> float:
        """Get delay before next retry"""
        attempts = self.retry_counts.get(task_id, 0)
        if self.exponential_backoff:
            return self.base_delay * (self.backoff_multiplier ** attempts)
        return self.base_delay

    def get_retry_count(self, task_id: str) -> int:
        """Get number of retries for a task"""
        return self.retry_counts.get(task_id, 0)


class SlurmBackend(ExecutionBackend):
    """
    SLURM-based execution backend for HPC clusters.

    Uses file-based state management with atomic writes to coordinate
    across SLURM compute nodes.
    """

    def __init__(self, config: Any, output_dir: Path, log_func: Callable[[str], None]):
        super().__init__(config, output_dir, log_func)

        # Run identifier
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]

        # State directory structure
        self.state_dir = output_dir / ".slurm_state"
        self.jobs_file = self.state_dir / "jobs.json"
        self.tasks_file = self.state_dir / "tasks.json"
        self.results_dir = self.state_dir / "results"
        self.scripts_dir = self.state_dir / "scripts"
        self.logs_dir = self.state_dir / "logs"
        self.task_defs_dir = self.state_dir / "task_definitions"

        # Job tracking
        self.job_ids: Dict[str, str] = {}  # task_id -> slurm_job_id
        self.retry_manager: Optional[RetryManager] = None

        # SLURM configuration from config
        self.slurm_config = getattr(config, 'slurm', None)
        self.retry_config = getattr(config, 'retry', None)

        # Path to slurm_executor.py
        self.executor_script = Path(__file__).parent.parent / "slurm_executor.py"

    def initialize(self) -> None:
        """Initialize state directories and files"""
        self.log("Initializing SLURM backend...")

        # Create directory structure
        for directory in [self.state_dir, self.results_dir, self.scripts_dir,
                         self.logs_dir, self.task_defs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Initialize state files
        self._atomic_write_json(self.jobs_file, {"jobs": {}, "run_id": self.run_id})
        self._atomic_write_json(self.tasks_file, {
            "tasks": {},
            "completed": [],
            "in_progress": [],
            "failed": [],
            "pending": []
        })

        # Initialize retry manager
        if self.retry_config:
            self.retry_manager = RetryManager(
                max_retries=self.retry_config.max_retries,
                base_delay=self.retry_config.retry_delay_seconds,
                exponential_backoff=self.retry_config.exponential_backoff,
                backoff_multiplier=self.retry_config.backoff_multiplier
            )
        else:
            self.retry_manager = RetryManager(max_retries=3)

        self.log(f"  State directory: {self.state_dir}")
        self.log(f"  Run ID: {self.run_id}")
        self.log("  SLURM backend initialized")

    def _atomic_write_json(self, filepath: Path, data: Dict) -> None:
        """Write JSON file atomically using a temporary file"""
        temp_path = filepath.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        temp_path.rename(filepath)

    def _read_json_with_lock(self, filepath: Path) -> Dict:
        """Read JSON file with file locking"""
        if not filepath.exists():
            return {}
        with open(filepath, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _write_json_with_lock(self, filepath: Path, data: Dict) -> None:
        """Write JSON file with file locking"""
        with open(filepath, 'r+' if filepath.exists() else 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def submit_tasks(
        self,
        tasks: List[Dict[str, Any]],
        plan: Dict[str, Any],
        requirements: str,
        use_real_executors: bool
    ) -> None:
        """Store tasks and prepare for SLURM submission"""
        self.tasks = tasks
        self.plan = plan
        self.requirements = requirements
        self.use_real_executors = use_real_executors

        # Write task definitions to files
        tasks_state = self._read_json_with_lock(self.tasks_file)

        for task in tasks:
            task_id = task["id"]

            # Write task definition
            task_def = {
                "task": task,
                "requirements": requirements,
                "use_real_executors": use_real_executors,
                "output_dir": str(self.output_dir),
                "plan": plan
            }
            task_def_file = self.task_defs_dir / f"{task_id}.json"
            self._atomic_write_json(task_def_file, task_def)

            # Update tasks state
            tasks_state["tasks"][task_id] = "pending"
            if task_id not in tasks_state["pending"]:
                tasks_state["pending"].append(task_id)

        self._write_json_with_lock(self.tasks_file, tasks_state)
        self.log(f"Submitted {len(tasks)} tasks to SLURM backend")

    def wait_for_completion(self, max_executors: int) -> None:
        """Submit jobs to SLURM and wait for completion"""
        self.log("\n" + "="*80)
        self.log("EXECUTING TASKS WITH SLURM BACKEND")
        self.log("="*80)

        num_tasks = len(self.tasks)
        self.log(f"  Total tasks: {num_tasks}")
        self.log(f"  Max concurrent jobs: {max_executors}")

        # Build dependency map for SLURM jobs
        dependencies = self.plan.get("dependencies", {})

        # Submit all jobs with dependencies
        self._submit_all_jobs(dependencies, max_executors)

        # Monitor jobs until completion
        self._monitor_jobs()

        # Handle any failed jobs with retry
        self._handle_failed_jobs(dependencies, max_executors)

        completed = len(self.get_completed_tasks())
        self.log(f"\n  All SLURM jobs finished")
        self.log(f"  Total tasks completed: {completed}")

    def _submit_all_jobs(self, dependencies: Dict[str, List[str]], max_executors: int) -> None:
        """Submit all tasks as SLURM jobs"""
        self.log("\n  Submitting jobs to SLURM...")

        # Sort tasks by dependencies (topological-like ordering)
        submitted = set()
        pending = list(self.tasks)

        while pending:
            # Find tasks that can be submitted
            ready = []
            for task in pending:
                task_id = task["id"]
                task_deps = dependencies.get(task_id, [])
                # Can submit if all dependencies have been submitted
                if all(dep in submitted for dep in task_deps):
                    ready.append(task)

            if not ready:
                # No progress - circular dependency or error
                self.log(f"  Warning: Cannot submit remaining tasks - possible circular dependency")
                break

            for task in ready:
                task_id = task["id"]
                task_deps = dependencies.get(task_id, [])

                # Get SLURM job IDs for dependencies
                dep_job_ids = [self.job_ids[dep] for dep in task_deps if dep in self.job_ids]

                # Generate and submit job
                job_id = self._submit_slurm_job(task, dep_job_ids)
                if job_id:
                    self.job_ids[task_id] = job_id
                    submitted.add(task_id)
                    self._update_task_status(task_id, "in_progress")

                pending.remove(task)

        # Save job mapping
        jobs_data = self._read_json_with_lock(self.jobs_file)
        jobs_data["jobs"] = self.job_ids
        self._write_json_with_lock(self.jobs_file, jobs_data)

        self.log(f"  Submitted {len(submitted)} jobs to SLURM")

    def _submit_slurm_job(self, task: Dict[str, Any], dependency_job_ids: List[str]) -> Optional[str]:
        """Generate and submit a single SLURM job"""
        task_id = task["id"]
        task_name = task["name"].replace(" ", "_")[:20]

        # Generate job script
        script_path = self._generate_job_script(task, task_id, task_name)

        # Build sbatch command
        sbatch_cmd = ["sbatch"]

        # Add SLURM configuration
        if self.slurm_config:
            sbatch_cmd.extend(self.slurm_config.get_sbatch_args())

        # Add job name
        sbatch_cmd.extend(["--job-name", f"po_{task_name}_{task_id}"])

        # Add output/error file paths
        sbatch_cmd.extend([
            "--output", str(self.logs_dir / f"{task_id}.out"),
            "--error", str(self.logs_dir / f"{task_id}.err")
        ])

        # Add dependencies if any
        if dependency_job_ids:
            dep_str = ":".join(dependency_job_ids)
            sbatch_cmd.extend(["--dependency", f"afterok:{dep_str}"])

        # Add script path
        sbatch_cmd.append(str(script_path))

        try:
            self.log(f"    Submitting task {task_id}: {task['name'][:40]}...")
            result = subprocess.run(
                sbatch_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse job ID from output (format: "Submitted batch job 12345")
                job_id = result.stdout.strip().split()[-1]
                self.log(f"      -> Job {job_id} submitted")
                return job_id
            else:
                self.log(f"      -> Failed to submit: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.log(f"      -> Timeout submitting job")
            return None
        except Exception as e:
            self.log(f"      -> Error: {str(e)}")
            return None

    def _generate_job_script(self, task: Dict[str, Any], task_id: str, task_name: str) -> Path:
        """Generate SLURM job script"""
        script_path = self.scripts_dir / f"{task_id}.sh"

        # Get Python path
        python_path = subprocess.run(
            ["which", "python3"],
            capture_output=True,
            text=True
        ).stdout.strip() or "python3"

        script_content = f'''#!/bin/bash
#SBATCH --job-name=po_{task_name}_{task_id}

# ParallelOrchestrator SLURM job script
# Task: {task['name']}
# Generated: {datetime.now().isoformat()}

echo "Starting task {task_id}: {task['name']}"
echo "Node: $(hostname)"
echo "Time: $(date)"

# Change to output directory
cd {self.output_dir}

# Run the executor
{python_path} {self.executor_script} \\
    --task-id "{task_id}" \\
    --state-dir "{self.state_dir}" \\
    --output-dir "{self.output_dir}"

EXIT_CODE=$?

echo "Task {task_id} finished with exit code $EXIT_CODE"
echo "Time: $(date)"

exit $EXIT_CODE
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make executable
        script_path.chmod(0o755)

        return script_path

    def _monitor_jobs(self) -> None:
        """Monitor SLURM jobs until all complete"""
        self.log("\n  Monitoring job status...")

        poll_interval = 10  # seconds
        max_wait = 7200  # 2 hours max
        elapsed = 0

        while elapsed < max_wait:
            # Get job statuses via squeue
            running_jobs = self._get_running_jobs()

            # Check for completed jobs via sacct
            self._check_completed_jobs()

            # Get current state
            tasks_state = self._read_json_with_lock(self.tasks_file)
            completed = len(tasks_state.get("completed", []))
            failed = len(tasks_state.get("failed", []))
            in_progress = len(tasks_state.get("in_progress", []))

            self.log(f"    Jobs - Running: {len(running_jobs)}, "
                    f"Completed: {completed}, Failed: {failed}")

            # Check if all done
            if completed + failed >= len(self.tasks):
                break

            time.sleep(poll_interval)
            elapsed += poll_interval

        if elapsed >= max_wait:
            self.log("  Warning: Timeout waiting for jobs")

    def _get_running_jobs(self) -> Set[str]:
        """Get set of currently running SLURM job IDs"""
        try:
            result = subprocess.run(
                ["squeue", "-u", os.environ.get("USER", ""), "-h", "-o", "%A"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return set(result.stdout.strip().split())
        except Exception:
            pass
        return set()

    def _check_completed_jobs(self) -> None:
        """Check for completed jobs via sacct and update state"""
        for task_id, job_id in list(self.job_ids.items()):
            try:
                result = subprocess.run(
                    ["sacct", "-j", job_id, "-n", "-o", "State", "-P"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    states = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
                    if not states:
                        continue

                    # Get the main job state (first line usually)
                    main_state = states[0].split('|')[0] if '|' in states[0] else states[0]

                    if main_state in ["COMPLETED"]:
                        self._collect_task_result(task_id)
                    elif main_state in ["FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL"]:
                        self._handle_job_failure(task_id, f"SLURM job {main_state}")

            except Exception as e:
                self.log(f"    Warning: Could not check job {job_id}: {e}")

    def _collect_task_result(self, task_id: str) -> None:
        """Collect result from completed task"""
        result_file = self.results_dir / f"{task_id}.json"

        if result_file.exists():
            result = self._read_json_with_lock(result_file)
            if result.get("status") == "completed":
                self._update_task_status(task_id, "completed")
                return

        # If no result file, mark as failed
        self._handle_job_failure(task_id, "No result file found")

    def _handle_job_failure(self, task_id: str, reason: str) -> None:
        """Handle a failed job"""
        self.log(f"    Task {task_id} failed: {reason}")
        self._update_task_status(task_id, "failed")

    def _handle_failed_jobs(self, dependencies: Dict[str, List[str]], max_executors: int) -> None:
        """Retry failed jobs if retries remain"""
        tasks_state = self._read_json_with_lock(self.tasks_file)
        failed_tasks = tasks_state.get("failed", [])

        if not failed_tasks:
            return

        self.log(f"\n  Checking {len(failed_tasks)} failed tasks for retry...")

        for task_id in list(failed_tasks):
            if self.retry_manager and self.retry_manager.should_retry(task_id):
                retry_count = self.retry_manager.record_attempt(task_id)
                delay = self.retry_manager.get_delay(task_id)

                self.log(f"    Retrying task {task_id} (attempt {retry_count}/{self.retry_manager.max_retries})")
                time.sleep(delay)

                # Reset task status to pending
                self._update_task_status(task_id, "pending")

                # Find task and resubmit
                task = next((t for t in self.tasks if t["id"] == task_id), None)
                if task:
                    task_deps = dependencies.get(task_id, [])
                    dep_job_ids = [self.job_ids[dep] for dep in task_deps if dep in self.job_ids]
                    job_id = self._submit_slurm_job(task, dep_job_ids)
                    if job_id:
                        self.job_ids[task_id] = job_id
                        self._update_task_status(task_id, "in_progress")

        # Monitor retried jobs
        if any(self.retry_manager.get_retry_count(t) > 0 for t in failed_tasks):
            self._monitor_jobs()

    def _update_task_status(self, task_id: str, status: str) -> None:
        """Update task status in state file"""
        tasks_state = self._read_json_with_lock(self.tasks_file)

        # Remove from all status lists
        for status_list in ["pending", "in_progress", "completed", "failed"]:
            if task_id in tasks_state.get(status_list, []):
                tasks_state[status_list].remove(task_id)

        # Add to new status list
        if status not in tasks_state:
            tasks_state[status] = []
        if task_id not in tasks_state[status]:
            tasks_state[status].append(task_id)

        tasks_state["tasks"][task_id] = status

        self._write_json_with_lock(self.tasks_file, tasks_state)

    def get_task_status(self, task_id: str) -> str:
        """Get current status of a task"""
        tasks_state = self._read_json_with_lock(self.tasks_file)
        return tasks_state.get("tasks", {}).get(task_id, "unknown")

    def get_results(self) -> List[Dict[str, Any]]:
        """Get results from all completed tasks"""
        results = []
        for result_file in self.results_dir.glob("*.json"):
            try:
                result = self._read_json_with_lock(result_file)
                results.append(result)
            except Exception:
                pass
        return results

    def mark_task_complete(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark task as completed (called by slurm_executor)"""
        result_file = self.results_dir / f"{task_id}.json"
        self._atomic_write_json(result_file, result)
        self._update_task_status(task_id, "completed")

    def mark_task_failed(self, task_id: str, error: str) -> None:
        """Mark task as failed"""
        result = {
            "task_id": task_id,
            "status": "failed",
            "error": error
        }
        result_file = self.results_dir / f"{task_id}.json"
        self._atomic_write_json(result_file, result)
        self._update_task_status(task_id, "failed")

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """Check if task dependencies are satisfied"""
        if not self.plan:
            return True

        task_id = task["id"]
        dependencies = self.plan.get("dependencies", {}).get(task_id, [])

        completed = self.get_completed_tasks()
        return all(dep in completed for dep in dependencies)

    def get_completed_tasks(self) -> Set[str]:
        """Get set of completed task IDs"""
        tasks_state = self._read_json_with_lock(self.tasks_file)
        return set(tasks_state.get("completed", []))

    def get_in_progress_tasks(self) -> Set[str]:
        """Get set of in-progress task IDs"""
        tasks_state = self._read_json_with_lock(self.tasks_file)
        return set(tasks_state.get("in_progress", []))

    def cleanup(self) -> None:
        """Clean up SLURM state (optional)"""
        self.log("SLURM backend cleanup complete")

    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information"""
        info = {
            "backend": "SlurmBackend",
            "output_dir": str(self.output_dir),
            "run_id": self.run_id,
            "state_dir": str(self.state_dir),
        }
        if self.slurm_config:
            info["slurm_partition"] = self.slurm_config.partition
            info["slurm_time_limit"] = self.slurm_config.time_limit
            if self.slurm_config.gpus_per_task > 0:
                info["slurm_gpus"] = self.slurm_config.gpus_per_task
        return info
