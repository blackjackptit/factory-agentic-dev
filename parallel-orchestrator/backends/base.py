"""
Abstract base class for execution backends
Defines the interface all backends must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set, Callable, Optional
from pathlib import Path


class ExecutionBackend(ABC):
    """
    Abstract base class defining the execution backend interface.

    All backends must implement these methods to provide a consistent
    interface for the ParallelOrchestrator.
    """

    def __init__(self, config: Any, output_dir: Path, log_func: Callable[[str], None]):
        """
        Initialize the backend.

        Args:
            config: Backend-specific configuration
            output_dir: Directory for output files
            log_func: Function to call for logging messages
        """
        self.config = config
        self.output_dir = output_dir
        self.log = log_func
        self.tasks: List[Dict[str, Any]] = []
        self.plan: Optional[Dict[str, Any]] = None
        self.requirements: str = ""

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the backend state.

        Set up any directories, files, or resources needed for execution.
        Called once before task execution begins.
        """
        pass

    @abstractmethod
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
            use_real_executors: Whether to use real Claude API or simulate
        """
        pass

    @abstractmethod
    def wait_for_completion(self, max_executors: int) -> None:
        """
        Wait for all submitted tasks to complete.

        Args:
            max_executors: Maximum number of concurrent executors
        """
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> str:
        """
        Get the current status of a task.

        Args:
            task_id: The task identifier

        Returns:
            Status string: 'pending', 'in_progress', 'completed', or 'failed'
        """
        pass

    @abstractmethod
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get results from all completed tasks.

        Returns:
            List of result dictionaries from completed tasks
        """
        pass

    @abstractmethod
    def mark_task_complete(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Mark a task as completed with its result.

        Args:
            task_id: The task identifier
            result: The task execution result
        """
        pass

    @abstractmethod
    def mark_task_failed(self, task_id: str, error: str) -> None:
        """
        Mark a task as failed with an error message.

        Args:
            task_id: The task identifier
            error: Error message describing the failure
        """
        pass

    @abstractmethod
    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Check if a task's dependencies are satisfied.

        Args:
            task: The task definition

        Returns:
            True if all dependencies are completed, False otherwise
        """
        pass

    @abstractmethod
    def get_completed_tasks(self) -> Set[str]:
        """
        Get set of completed task IDs.

        Returns:
            Set of task IDs that have completed successfully
        """
        pass

    @abstractmethod
    def get_in_progress_tasks(self) -> Set[str]:
        """
        Get set of in-progress task IDs.

        Returns:
            Set of task IDs currently being executed
        """
        pass

    def cleanup(self) -> None:
        """
        Clean up any resources used by the backend.

        Called after all tasks have completed. Override if cleanup is needed.
        """
        pass

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the backend.

        Returns:
            Dictionary with backend name and configuration info
        """
        return {
            "backend": self.__class__.__name__,
            "output_dir": str(self.output_dir),
        }
