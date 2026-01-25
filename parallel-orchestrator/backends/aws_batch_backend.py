"""
AWS Batch execution backend
Executes tasks as AWS Batch jobs with S3 state management
"""

import json
import subprocess
import time
from typing import Dict, Any, List, Set, Callable, Optional
from pathlib import Path
from datetime import datetime
from uuid import uuid4

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


class AWSBatchBackend(ExecutionBackend):
    """
    AWS Batch execution backend.

    Executes tasks as AWS Batch jobs with S3-based state management.
    Jobs run in containers that download task definitions from S3,
    execute them, and upload results back to S3.
    """

    # Batch job terminal states
    TERMINAL_STATES = {"SUCCEEDED", "FAILED"}
    RUNNING_STATES = {"SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"}

    def __init__(self, config: Any, output_dir: Path, log_func: Callable[[str], None]):
        super().__init__(config, output_dir, log_func)

        # AWS Batch configuration
        self.batch_config = getattr(config, 'batch', None)
        if not self.batch_config:
            raise ValueError("Batch configuration required for AWSBatchBackend")

        self.job_queue = self.batch_config.job_queue
        self.job_definition = self.batch_config.job_definition
        self.region = self.batch_config.region
        self.s3_bucket = self.batch_config.s3_bucket
        self.s3_prefix = self.batch_config.s3_prefix
        self.vcpus = self.batch_config.vcpus
        self.memory = self.batch_config.memory
        self.timeout = self.batch_config.timeout

        # Run identifier
        self.run_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:8]}"

        # S3 paths
        self.s3_base = f"s3://{self.s3_bucket}/{self.s3_prefix}/{self.run_id}"
        self.s3_tasks_path = f"{self.s3_base}/tasks"
        self.s3_state_path = f"{self.s3_base}/state"
        self.s3_results_path = f"{self.s3_base}/results"

        # Local state directory
        self.state_dir = output_dir / ".batch_state"
        self.results_dir = self.state_dir / "results"
        self.tasks_dir = self.state_dir / "tasks"

        # Job tracking
        self.job_mapping: Dict[str, str] = {}  # task_id -> batch_job_id
        self.task_status: Dict[str, str] = {}  # task_id -> status
        self.task_results: Dict[str, Dict[str, Any]] = {}  # task_id -> result

        # Retry manager
        self.retry_manager: Optional[RetryManager] = None
        self.retry_config = getattr(config, 'retry', None)

        # Task metadata for resubmission
        self.use_real_executors = False

    def initialize(self) -> None:
        """Initialize backend with AWS validation and S3 setup"""
        self.log("Initializing AWS Batch backend...")

        # Create local state directories
        for directory in [self.state_dir, self.results_dir, self.tasks_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Verify AWS CLI
        if not self._verify_aws_cli():
            raise RuntimeError("AWS CLI not available or not configured")

        # Verify Batch resources
        if not self._verify_batch_resources():
            raise RuntimeError(f"Cannot access Batch job queue or definition")

        # Verify S3 access
        if not self._verify_s3_access():
            raise RuntimeError(f"Cannot access S3 bucket: {self.s3_bucket}")

        # Initialize S3 structure
        self._init_s3_structure()

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

        self.log(f"  Job queue: {self.job_queue}")
        self.log(f"  Job definition: {self.job_definition}")
        self.log(f"  Region: {self.region}")
        self.log(f"  S3 base path: {self.s3_base}")
        self.log(f"  Run ID: {self.run_id}")
        self.log("  AWS Batch backend initialized")

    def _verify_aws_cli(self) -> bool:
        """Verify AWS CLI is installed and configured"""
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _verify_batch_resources(self) -> bool:
        """Verify Batch job queue and job definition exist"""
        try:
            # Verify job queue
            result = subprocess.run(
                ["aws", "batch", "describe-job-queues",
                 "--job-queues", self.job_queue,
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.log(f"  Warning: Cannot verify job queue: {result.stderr}")
                return False

            queues = json.loads(result.stdout).get("jobQueues", [])
            if not queues:
                self.log(f"  Warning: Job queue '{self.job_queue}' not found")
                return False

            # Verify job definition
            result = subprocess.run(
                ["aws", "batch", "describe-job-definitions",
                 "--job-definition-name", self.job_definition,
                 "--status", "ACTIVE",
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.log(f"  Warning: Cannot verify job definition: {result.stderr}")
                return False

            definitions = json.loads(result.stdout).get("jobDefinitions", [])
            if not definitions:
                self.log(f"  Warning: Job definition '{self.job_definition}' not found or not active")
                return False

            return True
        except Exception as e:
            self.log(f"  Warning: Error verifying Batch resources: {e}")
            return False

    def _verify_s3_access(self) -> bool:
        """Verify we can access the S3 bucket"""
        try:
            result = subprocess.run(
                ["aws", "s3", "ls", f"s3://{self.s3_bucket}/",
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

    def _init_s3_structure(self) -> None:
        """Create initial S3 directory structure with marker file"""
        marker_content = json.dumps({
            "run_id": self.run_id,
            "created": datetime.now().isoformat(),
            "job_queue": self.job_queue,
            "job_definition": self.job_definition,
            "region": self.region
        }, indent=2)

        marker_file = self.state_dir / "marker.json"
        with open(marker_file, 'w') as f:
            f.write(marker_content)

        # Upload marker to S3
        self._s3_upload(str(marker_file), f"{self.s3_state_path}/marker.json")

    def _s3_upload(self, local_path: str, s3_path: str) -> bool:
        """Upload file to S3"""
        try:
            result = subprocess.run(
                ["aws", "s3", "cp", local_path, s3_path,
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"    S3 upload failed: {e}")
            return False

    def _s3_download(self, s3_path: str, local_path: str) -> bool:
        """Download file from S3"""
        try:
            result = subprocess.run(
                ["aws", "s3", "cp", s3_path, local_path,
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception:
            return False

    def _s3_sync_download(self, s3_path: str, local_dir: str) -> bool:
        """Sync S3 path to local directory"""
        try:
            result = subprocess.run(
                ["aws", "s3", "sync", s3_path, local_dir,
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"    S3 sync download failed: {e}")
            return False

    def submit_tasks(
        self,
        tasks: List[Dict[str, Any]],
        plan: Dict[str, Any],
        requirements: str,
        use_real_executors: bool
    ) -> None:
        """Upload task definitions to S3"""
        self.tasks = tasks
        self.plan = plan
        self.requirements = requirements
        self.use_real_executors = use_real_executors

        self.log("  Uploading task definitions to S3...")

        for task in tasks:
            task_id = task["id"]

            # Create task definition
            task_def = {
                "task": task,
                "requirements": requirements,
                "use_real_executors": use_real_executors,
                "output_dir": str(self.output_dir),
                "plan": plan,
                "run_id": self.run_id
            }

            # Write locally
            task_def_file = self.tasks_dir / f"{task_id}.json"
            with open(task_def_file, 'w') as f:
                json.dump(task_def, f, indent=2)

            # Upload to S3
            s3_task_path = f"{self.s3_tasks_path}/{task_id}.json"
            self._s3_upload(str(task_def_file), s3_task_path)

            # Initialize task status
            self.task_status[task_id] = "pending"

        # Upload state file
        self._save_state()

        self.log(f"  Uploaded {len(tasks)} task definitions to S3")

    def _save_state(self) -> None:
        """Save current state to S3"""
        state = {
            "run_id": self.run_id,
            "task_status": self.task_status,
            "job_mapping": self.job_mapping,
            "updated": datetime.now().isoformat()
        }

        state_file = self.state_dir / "tasks.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        self._s3_upload(str(state_file), f"{self.s3_state_path}/tasks.json")

        # Also save job mapping
        jobs_file = self.state_dir / "jobs.json"
        with open(jobs_file, 'w') as f:
            json.dump({"jobs": self.job_mapping, "run_id": self.run_id}, f, indent=2)

        self._s3_upload(str(jobs_file), f"{self.s3_state_path}/jobs.json")

    def wait_for_completion(self, max_executors: int) -> None:
        """Submit jobs to AWS Batch and wait for completion"""
        self.log("\n" + "=" * 80)
        self.log("EXECUTING TASKS WITH AWS BATCH BACKEND")
        self.log("=" * 80)

        num_tasks = len(self.tasks)
        self.log(f"  Total tasks: {num_tasks}")
        self.log(f"  Max concurrent jobs: {max_executors}")

        # Get dependencies
        dependencies = self.plan.get("dependencies", {})

        # Submit all jobs with dependencies
        self._submit_all_jobs(dependencies)

        # Monitor jobs until completion
        self._monitor_jobs()

        # Handle any failed jobs with retry
        self._handle_failed_jobs(dependencies)

        # Collect final results
        self._collect_all_results()

        completed = len(self.get_completed_tasks())
        failed = len([t for t, s in self.task_status.items() if s == "failed"])
        self.log(f"\n  All AWS Batch jobs finished")
        self.log(f"  Completed: {completed}, Failed: {failed}")

    def _submit_all_jobs(self, dependencies: Dict[str, List[str]]) -> None:
        """Submit all tasks as AWS Batch jobs with dependencies"""
        self.log("\n  Submitting jobs to AWS Batch...")

        # Sort tasks by dependencies (topological-like ordering)
        submitted = set()
        pending = list(self.tasks)

        while pending:
            ready = []
            for task in pending:
                task_id = task["id"]
                task_deps = dependencies.get(task_id, [])
                # Can submit if all dependencies have been submitted
                if all(dep in submitted for dep in task_deps):
                    ready.append(task)

            if not ready:
                self.log(f"  Warning: Cannot submit remaining tasks - possible circular dependency")
                break

            for task in ready:
                task_id = task["id"]
                task_deps = dependencies.get(task_id, [])

                # Get Batch job IDs for dependencies
                dep_job_ids = [self.job_mapping[dep] for dep in task_deps if dep in self.job_mapping]

                # Submit job
                job_id = self._submit_batch_job(task, dep_job_ids)
                if job_id:
                    self.job_mapping[task_id] = job_id
                    self.task_status[task_id] = "submitted"
                    submitted.add(task_id)
                else:
                    self.task_status[task_id] = "failed"

                pending.remove(task)

        # Save state with job mappings
        self._save_state()

        self.log(f"  Submitted {len(submitted)} jobs to AWS Batch")

    def _submit_batch_job(self, task: Dict[str, Any], dependency_job_ids: List[str]) -> Optional[str]:
        """Submit a single task as AWS Batch job"""
        task_id = task["id"]
        job_name = f"po_{task_id}"

        self.log(f"    Submitting task {task_id}: {task['name'][:40]}...")

        # Build submit-job command
        cmd = [
            "aws", "batch", "submit-job",
            "--job-name", job_name,
            "--job-queue", self.job_queue,
            "--job-definition", self.job_definition,
            "--region", self.region,
        ]

        # Add dependencies if any
        if dependency_job_ids:
            depends_on = [{"jobId": jid, "type": "SEQUENTIAL"} for jid in dependency_job_ids]
            cmd.extend(["--depends-on", json.dumps(depends_on)])

        # Container overrides with environment variables
        # Note: For Fargate, use resourceRequirements instead of vcpus/memory
        overrides = {
            "resourceRequirements": [
                {"type": "VCPU", "value": str(self.vcpus)},
                {"type": "MEMORY", "value": str(self.memory)}
            ],
            "environment": [
                {"name": "TASK_ID", "value": task_id},
                {"name": "S3_BUCKET", "value": self.s3_bucket},
                {"name": "S3_PREFIX", "value": f"{self.s3_prefix}/{self.run_id}"},
                {"name": "AWS_REGION", "value": self.region},
                {"name": "AWS_DEFAULT_REGION", "value": self.region},
                {"name": "OUTPUT_DIR", "value": "/output"},
                {"name": "USE_REAL_EXECUTORS", "value": str(self.use_real_executors).lower()},
                {"name": "CLAUDE_CODE_USE_BEDROCK", "value": "1"},
                {"name": "BEDROCK_MODEL", "value": "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"},
            ]
        }
        cmd.extend(["--container-overrides", json.dumps(overrides)])

        # Add timeout if specified
        if self.timeout > 0:
            cmd.extend(["--timeout", json.dumps({"attemptDurationSeconds": self.timeout})])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                response = json.loads(result.stdout)
                job_id = response.get("jobId")
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

    def _monitor_jobs(self) -> None:
        """Poll AWS Batch for job status updates"""
        self.log("\n  Monitoring job status...")

        poll_interval = 15  # seconds
        max_wait = 7200  # 2 hours max
        elapsed = 0

        while elapsed < max_wait:
            # Get all job IDs that aren't in terminal state
            active_jobs = [
                job_id for task_id, job_id in self.job_mapping.items()
                if self.task_status.get(task_id) not in {"completed", "failed"}
            ]

            if not active_jobs:
                break

            # Query job status in batches of 100
            for i in range(0, len(active_jobs), 100):
                batch_jobs = active_jobs[i:i + 100]
                self._check_job_status(batch_jobs)

            # Log progress
            completed = len([t for t, s in self.task_status.items() if s == "completed"])
            failed = len([t for t, s in self.task_status.items() if s == "failed"])
            in_progress = len([t for t, s in self.task_status.items() if s in {"submitted", "running"}])

            self.log(f"    Jobs - Running: {in_progress}, Completed: {completed}, Failed: {failed}")

            # Check if all done
            if completed + failed >= len(self.tasks):
                break

            time.sleep(poll_interval)
            elapsed += poll_interval

        if elapsed >= max_wait:
            self.log("  Warning: Timeout waiting for jobs")

    def _check_job_status(self, job_ids: List[str]) -> None:
        """Check status of jobs via describe-jobs"""
        try:
            result = subprocess.run(
                ["aws", "batch", "describe-jobs",
                 "--jobs"] + job_ids +
                ["--region", self.region],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.log(f"    Warning: Failed to describe jobs: {result.stderr}")
                return

            response = json.loads(result.stdout)
            jobs = response.get("jobs", [])

            for job in jobs:
                job_id = job["jobId"]
                status = job["status"]
                task_id = self._get_task_id_for_job(job_id)

                if not task_id:
                    continue

                if status == "SUCCEEDED":
                    self.task_status[task_id] = "completed"
                elif status == "FAILED":
                    reason = job.get("statusReason", "Unknown error")
                    self.log(f"    Task {task_id} failed: {reason}")
                    self.task_status[task_id] = "failed"
                elif status == "RUNNING":
                    self.task_status[task_id] = "running"

        except Exception as e:
            self.log(f"    Warning: Error checking job status: {e}")

    def _get_task_id_for_job(self, job_id: str) -> Optional[str]:
        """Get task ID for a given job ID"""
        for task_id, jid in self.job_mapping.items():
            if jid == job_id:
                return task_id
        return None

    def _handle_failed_jobs(self, dependencies: Dict[str, List[str]]) -> None:
        """Retry failed jobs if retries remain"""
        failed_tasks = [t for t, s in self.task_status.items() if s == "failed"]

        if not failed_tasks:
            return

        self.log(f"\n  Checking {len(failed_tasks)} failed tasks for retry...")

        retried = False
        for task_id in failed_tasks:
            if self.retry_manager and self.retry_manager.should_retry(task_id):
                retry_count = self.retry_manager.record_attempt(task_id)
                delay = self.retry_manager.get_delay(task_id)

                self.log(f"    Retrying task {task_id} (attempt {retry_count}/{self.retry_manager.max_retries})")
                time.sleep(delay)

                # Find task and resubmit
                task = next((t for t in self.tasks if t["id"] == task_id), None)
                if task:
                    task_deps = dependencies.get(task_id, [])
                    dep_job_ids = [self.job_mapping[dep] for dep in task_deps if dep in self.job_mapping]
                    job_id = self._submit_batch_job(task, dep_job_ids)
                    if job_id:
                        self.job_mapping[task_id] = job_id
                        self.task_status[task_id] = "submitted"
                        retried = True

        # Monitor retried jobs
        if retried:
            self._save_state()
            self._monitor_jobs()

    def _collect_all_results(self) -> None:
        """Download and collect all results from S3"""
        self.log("\n  Collecting results from S3...")

        # Sync results directory from S3
        self._s3_sync_download(self.s3_results_path, str(self.results_dir))

        # Sync generated files directory from S3
        s3_files_path = f"{self.s3_base}/files"
        files_dir = self.output_dir / "generated_files"
        files_dir.mkdir(exist_ok=True)
        self._s3_sync_download(s3_files_path, str(files_dir))

        # Load results
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                task_id = result.get("task_id")
                if task_id:
                    self.task_results[task_id] = result
            except Exception as e:
                self.log(f"    Warning: Failed to load result {result_file}: {e}")

        self.log(f"  Collected {len(self.task_results)} results")

        # Copy generated files to output directory
        if files_dir.exists() and any(files_dir.iterdir()):
            self.log(f"  Copying generated files to output directory...")
            import shutil
            for item in files_dir.glob("**/*"):
                if item.is_file():
                    # Get relative path from files_dir
                    rel_path = item.relative_to(files_dir)
                    # Skip task_id prefix if present
                    parts = list(rel_path.parts)
                    if parts and parts[0].startswith("task_"):
                        rel_path = Path(*parts[1:]) if len(parts) > 1 else rel_path
                    dest = self.output_dir / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
                    self.log(f"    ✓ Copied {rel_path}")

    def get_task_status(self, task_id: str) -> str:
        """Get current status of a task"""
        return self.task_status.get(task_id, "unknown")

    def get_results(self) -> List[Dict[str, Any]]:
        """Get results from all tasks"""
        results = []

        for task in self.tasks:
            task_id = task["id"]
            if task_id in self.task_results:
                results.append(self.task_results[task_id])
            elif self.task_status.get(task_id) == "failed":
                # Create failure result
                results.append({
                    "task_id": task_id,
                    "task_name": task.get("name", "unknown"),
                    "status": "failed",
                    "error": "Job failed or result not available"
                })

        return results

    def mark_task_complete(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark task as completed with its result"""
        self.task_status[task_id] = "completed"
        self.task_results[task_id] = result

        # Save result locally
        result_file = self.results_dir / f"{task_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)

    def mark_task_failed(self, task_id: str, error: str) -> None:
        """Mark task as failed"""
        self.task_status[task_id] = "failed"
        self.task_results[task_id] = {
            "task_id": task_id,
            "status": "failed",
            "error": error
        }

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
        return {t for t, s in self.task_status.items() if s == "completed"}

    def get_in_progress_tasks(self) -> Set[str]:
        """Get set of in-progress task IDs"""
        return {t for t, s in self.task_status.items() if s in {"submitted", "running"}}

    def cleanup(self) -> None:
        """Clean up and final S3 sync"""
        self.log("  Final state sync to S3...")
        self._save_state()

        # Sync local results to S3
        for result_file in self.results_dir.glob("*.json"):
            self._s3_upload(str(result_file), f"{self.s3_results_path}/{result_file.name}")

        self.log(f"  Results available at: {self.s3_base}")
        self.log("AWS Batch backend cleanup complete")

    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information"""
        return {
            "backend": "AWSBatchBackend",
            "output_dir": str(self.output_dir),
            "run_id": self.run_id,
            "job_queue": self.job_queue,
            "job_definition": self.job_definition,
            "region": self.region,
            "s3_bucket": self.s3_bucket,
            "s3_base_path": self.s3_base,
            "vcpus": self.vcpus,
            "memory": self.memory,
        }
