"""
AWS ParallelCluster execution backend
Extends SLURM backend with S3 state synchronization for cross-node execution
"""

import json
import subprocess
from typing import Dict, Any, List, Callable
from pathlib import Path
from datetime import datetime

from .slurm_backend import SlurmBackend


class AWSParallelClusterBackend(SlurmBackend):
    """
    AWS ParallelCluster execution backend.

    Extends SlurmBackend with:
    - S3 state synchronization for distributed execution
    - ParallelCluster-specific environment setup
    - Cross-node result collection via S3
    """

    def __init__(self, config: Any, output_dir: Path, log_func: Callable[[str], None]):
        super().__init__(config, output_dir, log_func)

        # AWS configuration
        self.aws_config = getattr(config, 'aws', None)
        if not self.aws_config:
            raise ValueError("AWS configuration required for AWSParallelClusterBackend")

        self.cluster_name = self.aws_config.cluster_name
        self.region = self.aws_config.region
        self.s3_bucket = self.aws_config.s3_bucket
        self.s3_prefix = self.aws_config.s3_prefix

        # S3 paths
        self.s3_base_path = f"s3://{self.s3_bucket}/{self.s3_prefix}/{self.run_id}"
        self.s3_state_path = f"{self.s3_base_path}/state"
        self.s3_tasks_path = f"{self.s3_base_path}/tasks"
        self.s3_results_path = f"{self.s3_base_path}/results"

    def initialize(self) -> None:
        """Initialize backend with S3 setup"""
        # Initialize local state (from parent)
        super().initialize()

        self.log("Initializing AWS ParallelCluster backend...")
        self.log(f"  Cluster: {self.cluster_name}")
        self.log(f"  Region: {self.region}")
        self.log(f"  S3 base path: {self.s3_base_path}")

        # Verify AWS CLI is available
        if not self._verify_aws_cli():
            raise RuntimeError("AWS CLI not available or not configured")

        # Verify S3 bucket access
        if not self._verify_s3_access():
            raise RuntimeError(f"Cannot access S3 bucket: {self.s3_bucket}")

        # Create initial S3 structure
        self._init_s3_structure()

        self.log("  AWS ParallelCluster backend initialized")

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
        """Create initial S3 directory structure"""
        # Create marker files to establish paths
        marker_content = json.dumps({
            "run_id": self.run_id,
            "created": datetime.now().isoformat(),
            "cluster": self.cluster_name
        })

        marker_file = self.state_dir / "s3_marker.json"
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

    def _s3_sync_upload(self, local_dir: str, s3_path: str) -> bool:
        """Sync local directory to S3"""
        try:
            result = subprocess.run(
                ["aws", "s3", "sync", local_dir, s3_path,
                 "--region", self.region],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"    S3 sync upload failed: {e}")
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
        """Submit tasks and sync to S3"""
        # Submit tasks locally (parent method)
        super().submit_tasks(tasks, plan, requirements, use_real_executors)

        # Sync task definitions to S3
        self.log("  Syncing task definitions to S3...")
        self._s3_sync_upload(str(self.task_defs_dir), self.s3_tasks_path)
        self._s3_sync_upload(str(self.state_dir), self.s3_state_path)

    def _generate_job_script(self, task: Dict[str, Any], task_id: str, task_name: str) -> Path:
        """Generate SLURM job script with S3 sync for AWS"""
        script_path = self.scripts_dir / f"{task_id}.sh"

        # Get Python path
        python_path = subprocess.run(
            ["which", "python3"],
            capture_output=True,
            text=True
        ).stdout.strip() or "python3"

        script_content = f'''#!/bin/bash
#SBATCH --job-name=po_{task_name}_{task_id}

# ParallelOrchestrator AWS ParallelCluster job script
# Task: {task['name']}
# Generated: {datetime.now().isoformat()}

echo "Starting task {task_id}: {task['name']}"
echo "Node: $(hostname)"
echo "Cluster: {self.cluster_name}"
echo "Time: $(date)"

# Set AWS region
export AWS_DEFAULT_REGION={self.region}

# Sync state from S3 before execution
echo "Syncing state from S3..."
aws s3 sync {self.s3_state_path}/ {self.state_dir}/ --region {self.region}
aws s3 sync {self.s3_tasks_path}/ {self.task_defs_dir}/ --region {self.region}

# Change to output directory
cd {self.output_dir}

# Run the executor with AWS mode
{python_path} {self.executor_script} \\
    --task-id "{task_id}" \\
    --state-dir "{self.state_dir}" \\
    --output-dir "{self.output_dir}" \\
    --aws-mode \\
    --s3-bucket "{self.s3_bucket}" \\
    --s3-prefix "{self.s3_prefix}/{self.run_id}" \\
    --aws-region "{self.region}"

EXIT_CODE=$?

# Sync results back to S3
echo "Syncing results to S3..."
aws s3 sync {self.results_dir}/ {self.s3_results_path}/ --region {self.region}
aws s3 sync {self.state_dir}/ {self.s3_state_path}/ --region {self.region}

echo "Task {task_id} finished with exit code $EXIT_CODE"
echo "Time: $(date)"

exit $EXIT_CODE
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        script_path.chmod(0o755)

        return script_path

    def _check_completed_jobs(self) -> None:
        """Check for completed jobs and sync results from S3"""
        # Sync results from S3
        self._s3_sync_download(self.s3_results_path, str(self.results_dir))
        self._s3_sync_download(self.s3_state_path, str(self.state_dir))

        # Call parent method to process results
        super()._check_completed_jobs()

    def get_results(self) -> List[Dict[str, Any]]:
        """Get results, syncing from S3 first"""
        # Sync results from S3
        self._s3_sync_download(self.s3_results_path, str(self.results_dir))

        # Call parent method
        return super().get_results()

    def cleanup(self) -> None:
        """Cleanup including S3 state sync"""
        # Final sync
        self.log("  Final S3 sync...")
        self._s3_sync_upload(str(self.results_dir), self.s3_results_path)
        self._s3_sync_upload(str(self.state_dir), self.s3_state_path)

        # Also sync output directory
        self._s3_sync_upload(str(self.output_dir), f"{self.s3_base_path}/output")

        self.log(f"  Results available at: {self.s3_base_path}")
        super().cleanup()

    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information including AWS details"""
        info = super().get_backend_info()
        info.update({
            "backend": "AWSParallelClusterBackend",
            "cluster_name": self.cluster_name,
            "region": self.region,
            "s3_bucket": self.s3_bucket,
            "s3_base_path": self.s3_base_path,
        })
        return info
