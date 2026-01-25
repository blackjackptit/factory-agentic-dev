"""
Configuration module for ParallelOrchestrator
Defines configuration dataclasses and CLI argument parsing
"""

import argparse
import sys
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class SlurmConfig:
    """Configuration for SLURM-based execution"""
    enabled: bool = False
    partition: str = "default"
    time_limit: str = "01:00:00"
    memory: str = "4G"
    cpus_per_task: int = 1
    gpus_per_task: int = 0
    gpu_partition: Optional[str] = None

    def get_sbatch_args(self) -> list:
        """Generate sbatch command line arguments"""
        args = [
            f"--partition={self.partition}",
            f"--time={self.time_limit}",
            f"--mem={self.memory}",
            f"--cpus-per-task={self.cpus_per_task}",
        ]

        if self.gpus_per_task > 0:
            args.append(f"--gres=gpu:{self.gpus_per_task}")
            if self.gpu_partition:
                args[0] = f"--partition={self.gpu_partition}"

        return args


@dataclass
class AWSConfig:
    """Configuration for AWS ParallelCluster execution"""
    enabled: bool = False
    cluster_name: Optional[str] = None
    region: str = "eu-central-1"
    s3_bucket: Optional[str] = None
    s3_prefix: str = "parallel-orchestrator"

    def get_s3_path(self, run_id: str) -> str:
        """Get S3 path for a specific run"""
        if not self.s3_bucket:
            raise ValueError("S3 bucket not configured")
        return f"s3://{self.s3_bucket}/{self.s3_prefix}/{run_id}"


@dataclass
class BatchConfig:
    """Configuration for AWS Batch execution"""
    enabled: bool = False
    job_queue: str = ""              # Required: Batch job queue name
    job_definition: str = ""          # Required: Batch job definition name
    region: str = "eu-central-1"
    s3_bucket: str = ""               # Required: S3 bucket for state
    s3_prefix: str = "parallel-orchestrator"
    vcpus: int = 1                    # vCPUs per job
    memory: int = 2048                # Memory in MB
    timeout: int = 3600               # Job timeout in seconds


@dataclass
class DockerConfig:
    """Configuration for Docker execution"""
    enabled: bool = False
    image: str = "parallel-orchestrator:latest"
    network: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    use_bedrock: bool = False
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    bedrock_region: str = "eu-central-1"
    bedrock_model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    planner_in_docker: bool = False  # Run planner agent in Docker container


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0


@dataclass
class OrchestratorConfig:
    """Main configuration for the ParallelOrchestrator"""
    requirements: str = ""
    output_dir: Optional[str] = None
    max_executors: int = 5
    use_real_executors: bool = False

    # Backend selection
    backend_type: str = "threading"  # "threading", "slurm", "aws", "batch", "docker"

    # Backend-specific configs
    slurm: SlurmConfig = field(default_factory=SlurmConfig)
    aws: AWSConfig = field(default_factory=AWSConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    docker: DockerConfig = field(default_factory=DockerConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)

    def get_output_dir(self, base_dir: Path) -> Path:
        """Get the output directory, using default if not specified"""
        if self.output_dir:
            return Path(self.output_dir)
        return base_dir / "outputs" / "parallel-orchestrator"


def parse_args(args: list = None) -> OrchestratorConfig:
    """
    Parse command line arguments and return configuration.

    Args:
        args: Optional list of arguments (defaults to sys.argv)

    Returns:
        OrchestratorConfig with parsed values
    """
    parser = argparse.ArgumentParser(
        description='Parallel Task Orchestrator - Scales executor agents with SLURM/AWS support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Threading mode (default, unchanged)
  python orchestrator.py "Build app" --max-executors 5

  # Local SLURM cluster (CPU)
  python orchestrator.py "Build ML pipeline" \\
      --slurm \\
      --slurm-partition=compute \\
      --slurm-time=02:00:00 \\
      --max-executors 10

  # Local SLURM with GPU
  python orchestrator.py "Train ML models" \\
      --slurm \\
      --slurm-partition=gpu \\
      --slurm-gpus=1 \\
      --slurm-mem=16G \\
      --max-executors 4

  # AWS ParallelCluster
  python orchestrator.py "Build platform" \\
      --aws \\
      --aws-cluster-name=my-cluster \\
      --aws-s3-bucket=my-bucket \\
      --max-executors 20

  # AWS ParallelCluster with GPU
  python orchestrator.py "Train deep learning" \\
      --aws \\
      --aws-cluster-name=gpu-cluster \\
      --aws-s3-bucket=ml-bucket \\
      --slurm-partition=gpu \\
      --slurm-gpus=1 \\
      --max-executors 8

  # AWS Batch execution
  python orchestrator.py "Build a website" \\
      --batch \\
      --batch-job-queue=my-queue \\
      --batch-job-definition=parallel-orchestrator-job \\
      --batch-s3-bucket=my-bucket \\
      --max-executors 10

  # AWS Batch with custom resources
  python orchestrator.py "Train ML model" \\
      --batch \\
      --batch-job-queue=gpu-queue \\
      --batch-job-definition=ml-job-def \\
      --batch-s3-bucket=ml-bucket \\
      --batch-vcpus=4 \\
      --batch-memory=16384 \\
      --batch-timeout=7200 \\
      --max-executors 8

  # Docker execution (local containers)
  python orchestrator.py "Build a task management app" \\
      --docker \\
      --max-executors 4 \\
      --real

  # Docker with AWS Bedrock (no Anthropic API key needed)
  python orchestrator.py "Build a full-stack app" \\
      --docker \\
      --docker-use-bedrock \\
      --docker-bedrock-region=eu-central-1 \\
      --docker-bedrock-model=global.anthropic.claude-sonnet-4-5-20250929-v1:0 \\
      --max-executors 4 \\
      --real

  # Docker with custom image and network
  python orchestrator.py "Build microservices" \\
      --docker \\
      --docker-image=my-orchestrator:v1 \\
      --docker-network=orchestrator-net \\
      --max-executors 6
        '''
    )

    # Required argument
    parser.add_argument('requirements', help='Project requirements description')

    # General options
    parser.add_argument('--output-dir', '-o', default=None,
                       help='Output directory for generated files')
    parser.add_argument('--max-executors', '-m', type=int, default=5,
                       help='Maximum number of parallel executors (default: 5)')
    parser.add_argument('--real', action='store_true',
                       help='Use real Claude API calls (slower but produces working code)')

    # Backend selection
    backend_group = parser.add_mutually_exclusive_group()
    backend_group.add_argument('--slurm', action='store_true',
                               help='Enable local SLURM backend')
    backend_group.add_argument('--aws', action='store_true',
                               help='Enable AWS ParallelCluster backend')
    backend_group.add_argument('--batch', action='store_true',
                               help='Enable AWS Batch backend')
    backend_group.add_argument('--docker', action='store_true',
                               help='Enable local Docker backend')

    # SLURM options
    slurm_group = parser.add_argument_group('SLURM Options')
    slurm_group.add_argument('--slurm-partition', default='default',
                            help='SLURM partition name (default: default)')
    slurm_group.add_argument('--slurm-time', default='01:00:00',
                            help='Job time limit (default: 01:00:00)')
    slurm_group.add_argument('--slurm-mem', default='4G',
                            help='Memory per job (default: 4G)')
    slurm_group.add_argument('--slurm-cpus', type=int, default=1,
                            help='CPUs per task (default: 1)')
    slurm_group.add_argument('--slurm-gpus', type=int, default=0,
                            help='GPUs per task (default: 0)')
    slurm_group.add_argument('--slurm-gpu-partition', default=None,
                            help='GPU-specific partition name')

    # AWS options
    aws_group = parser.add_argument_group('AWS ParallelCluster Options')
    aws_group.add_argument('--aws-cluster-name', default=None,
                          help='ParallelCluster name')
    aws_group.add_argument('--aws-region', default='eu-central-1',
                          help='AWS region (default: eu-central-1)')
    aws_group.add_argument('--aws-s3-bucket', default=None,
                          help='S3 bucket for state synchronization')

    # AWS Batch options
    batch_group = parser.add_argument_group('AWS Batch Options')
    batch_group.add_argument('--batch-job-queue', default=None,
                            help='AWS Batch job queue name (required for --batch)')
    batch_group.add_argument('--batch-job-definition', default=None,
                            help='AWS Batch job definition name (required for --batch)')
    batch_group.add_argument('--batch-region', default='eu-central-1',
                            help='AWS region for Batch (default: eu-central-1)')
    batch_group.add_argument('--batch-s3-bucket', default=None,
                            help='S3 bucket for state (required for --batch)')
    batch_group.add_argument('--batch-s3-prefix', default='parallel-orchestrator',
                            help='S3 prefix for state (default: parallel-orchestrator)')
    batch_group.add_argument('--batch-vcpus', type=int, default=1,
                            help='vCPUs per job (default: 1)')
    batch_group.add_argument('--batch-memory', type=int, default=2048,
                            help='Memory per job in MB (default: 2048)')
    batch_group.add_argument('--batch-timeout', type=int, default=3600,
                            help='Job timeout in seconds (default: 3600)')

    # Docker options
    docker_group = parser.add_argument_group('Docker Options')
    docker_group.add_argument('--docker-image', default='parallel-orchestrator:latest',
                             help='Docker image to use (default: parallel-orchestrator:latest)')
    docker_group.add_argument('--docker-network', default=None,
                             help='Docker network name (optional)')
    docker_group.add_argument('--docker-api-key', default=None,
                             help='Anthropic API key (or use ANTHROPIC_API_KEY env var)')
    docker_group.add_argument('--docker-use-bedrock', action='store_true',
                             help='Use AWS Bedrock instead of Anthropic API')
    docker_group.add_argument('--docker-aws-access-key-id', default=None,
                             help='AWS Access Key ID (or use AWS_ACCESS_KEY_ID env var)')
    docker_group.add_argument('--docker-aws-secret-access-key', default=None,
                             help='AWS Secret Access Key (or use AWS_SECRET_ACCESS_KEY env var)')
    docker_group.add_argument('--docker-aws-session-token', default=None,
                             help='AWS Session Token (optional, or use AWS_SESSION_TOKEN env var)')
    docker_group.add_argument('--docker-bedrock-region', default='eu-central-1',
                             help='AWS region for Bedrock (default: eu-central-1)')
    docker_group.add_argument('--docker-bedrock-model', default='global.anthropic.claude-sonnet-4-5-20250929-v1:0',
                             help='Bedrock model ID (default: global.anthropic.claude-sonnet-4-5-20250929-v1:0)')
    docker_group.add_argument('--docker-planner-in-docker', action='store_true',
                             help='Run planner agent in Docker container instead of locally')

    # Retry options
    retry_group = parser.add_argument_group('Retry Options')
    retry_group.add_argument('--max-retries', type=int, default=3,
                            help='Max retry attempts for failed jobs (default: 3)')

    parsed = parser.parse_args(args)

    # Validate arguments
    if parsed.max_executors < 1:
        print("Error: --max-executors must be at least 1")
        sys.exit(1)
    if parsed.max_executors > 100:
        print("Warning: --max-executors > 100 may cause performance issues")

    # AWS validation
    if parsed.aws:
        if not parsed.aws_cluster_name:
            print("Error: --aws-cluster-name is required when using --aws")
            sys.exit(1)
        if not parsed.aws_s3_bucket:
            print("Error: --aws-s3-bucket is required when using --aws")
            sys.exit(1)

    # AWS Batch validation
    if parsed.batch:
        if not parsed.batch_job_queue:
            print("Error: --batch-job-queue is required when using --batch")
            sys.exit(1)
        if not parsed.batch_job_definition:
            print("Error: --batch-job-definition is required when using --batch")
            sys.exit(1)
        if not parsed.batch_s3_bucket:
            print("Error: --batch-s3-bucket is required when using --batch")
            sys.exit(1)

    # Docker validation
    if parsed.docker:
        import os
        # Get API key or AWS credentials from args or environment
        if parsed.docker_use_bedrock:
            aws_key = parsed.docker_aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
            aws_secret = parsed.docker_aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
            if parsed.real and (not aws_key or not aws_secret):
                print("Warning: Using Bedrock but AWS credentials not provided.")
                print("  Set --docker-aws-access-key-id and --docker-aws-secret-access-key")
                print("  Or use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars")
        else:
            api_key = parsed.docker_api_key or os.environ.get("ANTHROPIC_API_KEY")
            if parsed.real and not api_key:
                print("Warning: No Anthropic API key provided. Set --docker-api-key or ANTHROPIC_API_KEY env var")

    # Determine backend type
    if parsed.docker:
        backend_type = "docker"
    elif parsed.batch:
        backend_type = "batch"
    elif parsed.aws:
        backend_type = "aws"
    elif parsed.slurm:
        backend_type = "slurm"
    else:
        backend_type = "threading"

    # Build config
    config = OrchestratorConfig(
        requirements=parsed.requirements,
        output_dir=parsed.output_dir,
        max_executors=parsed.max_executors,
        use_real_executors=parsed.real,
        backend_type=backend_type,
        slurm=SlurmConfig(
            enabled=parsed.slurm or parsed.aws,  # AWS uses SLURM too
            partition=parsed.slurm_partition,
            time_limit=parsed.slurm_time,
            memory=parsed.slurm_mem,
            cpus_per_task=parsed.slurm_cpus,
            gpus_per_task=parsed.slurm_gpus,
            gpu_partition=parsed.slurm_gpu_partition,
        ),
        aws=AWSConfig(
            enabled=parsed.aws,
            cluster_name=parsed.aws_cluster_name,
            region=parsed.aws_region,
            s3_bucket=parsed.aws_s3_bucket,
        ),
        batch=BatchConfig(
            enabled=parsed.batch,
            job_queue=parsed.batch_job_queue or "",
            job_definition=parsed.batch_job_definition or "",
            region=parsed.batch_region,
            s3_bucket=parsed.batch_s3_bucket or "",
            s3_prefix=parsed.batch_s3_prefix,
            vcpus=parsed.batch_vcpus,
            memory=parsed.batch_memory,
            timeout=parsed.batch_timeout,
        ),
        docker=DockerConfig(
            enabled=parsed.docker,
            image=parsed.docker_image,
            network=parsed.docker_network,
            anthropic_api_key=parsed.docker_api_key,
            use_bedrock=parsed.docker_use_bedrock,
            aws_access_key_id=parsed.docker_aws_access_key_id,
            aws_secret_access_key=parsed.docker_aws_secret_access_key,
            aws_session_token=parsed.docker_aws_session_token,
            bedrock_region=parsed.docker_bedrock_region,
            bedrock_model=parsed.docker_bedrock_model,
            planner_in_docker=parsed.docker_planner_in_docker,
        ),
        retry=RetryConfig(
            max_retries=parsed.max_retries,
        ),
    )

    return config


def print_config(config: OrchestratorConfig) -> None:
    """Print configuration summary to console"""
    print(f"\n{'='*80}")
    print("CONFIGURATION")
    print(f"{'='*80}")
    print(f"Requirements: {config.requirements}")
    print(f"Output directory: {config.output_dir or '(default)'}")
    print(f"Executor budget: {config.max_executors}")
    print(f"Execution mode: {'REAL' if config.use_real_executors else 'SIMULATED'}")
    print(f"Backend: {config.backend_type.upper()}")

    if config.backend_type == "slurm":
        print(f"\nSLURM Configuration:")
        print(f"  Partition: {config.slurm.partition}")
        print(f"  Time limit: {config.slurm.time_limit}")
        print(f"  Memory: {config.slurm.memory}")
        print(f"  CPUs per task: {config.slurm.cpus_per_task}")
        if config.slurm.gpus_per_task > 0:
            print(f"  GPUs per task: {config.slurm.gpus_per_task}")
            if config.slurm.gpu_partition:
                print(f"  GPU partition: {config.slurm.gpu_partition}")

    elif config.backend_type == "aws":
        print(f"\nAWS ParallelCluster Configuration:")
        print(f"  Cluster: {config.aws.cluster_name}")
        print(f"  Region: {config.aws.region}")
        print(f"  S3 bucket: {config.aws.s3_bucket}")
        print(f"\nSLURM Configuration (on cluster):")
        print(f"  Partition: {config.slurm.partition}")
        print(f"  Time limit: {config.slurm.time_limit}")
        print(f"  Memory: {config.slurm.memory}")
        if config.slurm.gpus_per_task > 0:
            print(f"  GPUs per task: {config.slurm.gpus_per_task}")

    elif config.backend_type == "batch":
        print(f"\nAWS Batch Configuration:")
        print(f"  Job queue: {config.batch.job_queue}")
        print(f"  Job definition: {config.batch.job_definition}")
        print(f"  Region: {config.batch.region}")
        print(f"  S3 bucket: {config.batch.s3_bucket}")
        print(f"  S3 prefix: {config.batch.s3_prefix}")
        print(f"  vCPUs per job: {config.batch.vcpus}")
        print(f"  Memory per job: {config.batch.memory} MB")
        print(f"  Job timeout: {config.batch.timeout}s")

    elif config.backend_type == "docker":
        print(f"\nDocker Configuration:")
        print(f"  Image: {config.docker.image}")
        if config.docker.network:
            print(f"  Network: {config.docker.network}")
        print(f"  Planner: {'Docker container' if config.docker.planner_in_docker else 'Local'}")
        if config.docker.use_bedrock:
            print(f"  Mode: AWS Bedrock")
            print(f"  Region: {config.docker.bedrock_region}")
            print(f"  Model: {config.docker.bedrock_model}")
            print(f"  AWS Credentials: {'***' if config.docker.aws_access_key_id else '(from environment)'}")
        else:
            print(f"  Mode: Anthropic API")
            print(f"  API Key: {'***' if config.docker.anthropic_api_key else '(from environment)'}")

    print(f"\nRetry Configuration:")
    print(f"  Max retries: {config.retry.max_retries}")
    print(f"{'='*80}\n")
