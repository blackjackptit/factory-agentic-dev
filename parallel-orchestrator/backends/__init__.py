"""
Execution backends for ParallelOrchestrator
Provides different execution strategies: threading, SLURM, AWS ParallelCluster, AWS Batch, Docker
"""

from .base import ExecutionBackend
from .threading_backend import ThreadingBackend
from .slurm_backend import SlurmBackend
from .aws_parallel_cluster_backend import AWSParallelClusterBackend
from .aws_batch_backend import AWSBatchBackend
from .docker_backend import DockerBackend

__all__ = [
    "ExecutionBackend",
    "ThreadingBackend",
    "SlurmBackend",
    "AWSParallelClusterBackend",
    "AWSBatchBackend",
    "DockerBackend",
]
