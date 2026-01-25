"""
Threading-based execution backend
Maintains backward compatibility with existing threading model
"""

import time
import threading
from typing import Dict, Any, List, Set, Callable, Optional
from pathlib import Path
from queue import Queue

from .base import ExecutionBackend


class ThreadingBackend(ExecutionBackend):
    """
    Thread-based execution backend using in-memory state.

    This is the default backend that maintains backward compatibility
    with the original orchestrator implementation.
    """

    def __init__(self, config: Any, output_dir: Path, log_func: Callable[[str], None]):
        super().__init__(config, output_dir, log_func)

        # In-memory state with thread-safe locks
        self.completed_tasks: Set[str] = set()
        self.in_progress_tasks: Set[str] = set()
        self.task_lock = threading.Lock()
        self.results_lock = threading.Lock()

        # Task queue and results
        self.task_queue: Queue = Queue()
        self.results: List[Dict[str, Any]] = []
        self.executor_threads: List[threading.Thread] = []

        # Execution parameters
        self.use_real_executors: bool = False
        self._executor_func: Optional[Callable] = None

    def initialize(self) -> None:
        """Initialize backend state"""
        self.completed_tasks.clear()
        self.in_progress_tasks.clear()
        self.results.clear()
        self.executor_threads.clear()
        self.log("ThreadingBackend initialized")

    def submit_tasks(
        self,
        tasks: List[Dict[str, Any]],
        plan: Dict[str, Any],
        requirements: str,
        use_real_executors: bool
    ) -> None:
        """Store tasks for execution"""
        self.tasks = tasks
        self.plan = plan
        self.requirements = requirements
        self.use_real_executors = use_real_executors
        self.log(f"Submitted {len(tasks)} tasks for execution")

    def set_executor_function(self, executor_func: Callable) -> None:
        """
        Set the function to use for task execution.

        Args:
            executor_func: Function with signature (task, executor_id) -> result
        """
        self._executor_func = executor_func

    def wait_for_completion(self, max_executors: int) -> None:
        """Execute tasks using thread pool and wait for completion"""
        self.log("\n" + "="*80)
        self.log("EXECUTING TASKS WITH THREADING BACKEND")
        self.log("="*80)

        num_tasks = len(self.tasks)
        num_executors_needed = min(num_tasks, max_executors)

        self.log(f"  Total tasks: {num_tasks}")
        self.log(f"  Executor budget: {max_executors}")
        self.log(f"  Executors to spawn: {num_executors_needed}")
        self.log(f"  Tasks per executor: ~{num_tasks / max(num_executors_needed, 1):.1f} average")

        # Create and start executor worker threads
        self.log(f"\n  Spawning {num_executors_needed} executor workers...")
        for executor_id in range(1, num_executors_needed + 1):
            thread = threading.Thread(
                target=self._executor_worker,
                args=(executor_id,),
                name=f"Executor-{executor_id}"
            )
            self.executor_threads.append(thread)
            thread.start()
            time.sleep(0.2)  # Stagger starts slightly

        self.log(f"  All {num_executors_needed} executor workers started")
        self.log("  Executors will dynamically pick tasks from queue...")
        self.log("  Waiting for all tasks to complete...\n")

        # Wait for all executor threads to complete
        for thread in self.executor_threads:
            thread.join()

        self.log(f"\n  All executor workers finished")
        self.log(f"  Total tasks completed: {len(self.completed_tasks)}")

    def _executor_worker(self, executor_id: int) -> None:
        """Worker function for executor thread"""
        executor_name = f"Executor-{executor_id}"
        self.log(f"[{executor_name}] Worker started")

        while True:
            task_to_execute = None

            with self.task_lock:
                # Find a task that:
                # 1. Not completed
                # 2. Not in progress
                # 3. Dependencies satisfied
                for task in self.tasks:
                    task_id = task["id"]
                    if (task_id not in self.completed_tasks and
                        task_id not in self.in_progress_tasks and
                        self.can_execute_task(task)):
                        task_to_execute = task
                        self.in_progress_tasks.add(task_id)
                        break

            if task_to_execute:
                # Execute the task
                if self._executor_func:
                    self._executor_func(task_to_execute, executor_id)
            else:
                # Check if all tasks are done
                with self.task_lock:
                    total_processed = len(self.completed_tasks) + \
                                    len([r for r in self.results if r.get("status") == "failed"])
                    if total_processed >= len(self.tasks):
                        self.log(f"[{executor_name}] All tasks processed, shutting down")
                        break

                # Wait before checking again
                time.sleep(0.5)

        self.log(f"[{executor_name}] Worker finished")

    def get_task_status(self, task_id: str) -> str:
        """Get current status of a task"""
        with self.task_lock:
            if task_id in self.completed_tasks:
                return "completed"
            elif task_id in self.in_progress_tasks:
                return "in_progress"
            else:
                # Check if failed
                for result in self.results:
                    if result.get("task_id") == task_id and result.get("status") == "failed":
                        return "failed"
                return "pending"

    def get_results(self) -> List[Dict[str, Any]]:
        """Get all results"""
        with self.results_lock:
            return list(self.results)

    def mark_task_complete(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark task as completed"""
        with self.results_lock:
            self.results.append(result)
        with self.task_lock:
            self.completed_tasks.add(task_id)
            self.in_progress_tasks.discard(task_id)

    def mark_task_failed(self, task_id: str, error: str) -> None:
        """Mark task as failed"""
        result = {
            "task_id": task_id,
            "status": "failed",
            "error": error
        }
        with self.results_lock:
            self.results.append(result)
        with self.task_lock:
            self.in_progress_tasks.discard(task_id)

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """Check if task dependencies are satisfied"""
        if not self.plan:
            return True

        task_id = task["id"]
        dependencies = self.plan.get("dependencies", {}).get(task_id, [])

        # Check if all dependencies are completed
        for dep_id in dependencies:
            if dep_id not in self.completed_tasks:
                return False

        return True

    def get_completed_tasks(self) -> Set[str]:
        """Get set of completed task IDs"""
        with self.task_lock:
            return set(self.completed_tasks)

    def get_in_progress_tasks(self) -> Set[str]:
        """Get set of in-progress task IDs"""
        with self.task_lock:
            return set(self.in_progress_tasks)

    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information"""
        return {
            "backend": "ThreadingBackend",
            "output_dir": str(self.output_dir),
            "thread_count": len(self.executor_threads),
        }
