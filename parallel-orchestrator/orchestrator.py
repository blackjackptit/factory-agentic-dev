#!/usr/bin/env python3
"""
Parallel Task Orchestrator
Coordinates parallel executor agents using intelligent planning from PlannerAgent
"""

import os
import sys
import json
import time
import shutil
import threading
from typing import List, Dict, Any, Set
from pathlib import Path
from datetime import datetime
from queue import Queue

from planner_agent import PlannerAgent
from executor_agent import ExecutorAgent


class ParallelOrchestrator:
    """
    Main orchestrator that coordinates parallel executors
    Uses PlannerAgent for intelligent complexity analysis and task planning
    """

    def __init__(self, requirements: str, output_dir: str = None, use_real_executors: bool = False):
        self.requirements = requirements
        # Default to centralized outputs directory
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "outputs" / "parallel-orchestrator"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.max_executors = 5
        self.use_real_executors = use_real_executors
        self.plan = None
        self.tasks = []
        self.results = []
        self.executor_threads = []

        # Task queue structures
        self.task_queue = Queue()
        self.completed_tasks: Set[str] = set()
        self.in_progress_tasks: Set[str] = set()
        self.task_lock = threading.Lock()
        self.results_lock = threading.Lock()

        # Log file
        self.log_file = self.output_dir / "orchestrator.log"

        # PlannerAgent will be initialized in run() after max_executors is set
        self.planner = None

    def log(self, message: str):
        """Write log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    def can_execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Check if a task's dependencies are satisfied
        """
        task_id = task["id"]
        dependencies = self.plan.get("dependencies", {}).get(task_id, [])

        # Check if all dependencies are completed
        for dep_id in dependencies:
            if dep_id not in self.completed_tasks:
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
                result = agent.execute(self.requirements)

                self.log(f"[{executor_name}] ✓ Task {task['id']} completed successfully")
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

                self.log(f"[{executor_name}] ✓ Task {task['id']} completed successfully")
                self.log(f"[{executor_name}]   Execution time: {result['execution_time']}")
                self.log(f"[{executor_name}]   Files created: {len(result['output_files'])}")

            with self.results_lock:
                self.results.append(result)

            # Mark task as completed
            with self.task_lock:
                self.completed_tasks.add(task["id"])
                self.in_progress_tasks.discard(task["id"])

        except Exception as e:
            self.log(f"[{executor_name}] ✗ Task {task['id']} failed: {str(e)}")
            result = {
                "task_id": task["id"],
                "executor_id": executor_id,
                "task_name": task["name"],
                "status": "failed",
                "error": str(e)
            }
            with self.results_lock:
                self.results.append(result)

            with self.task_lock:
                self.in_progress_tasks.discard(task["id"])

    def executor_worker(self, executor_id: int):
        """
        Worker function for executor thread - continuously processes tasks from queue
        """
        executor_name = f"Executor-{executor_id}"
        self.log(f"[{executor_name}] Worker started")

        while True:
            # Look for available tasks
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
                self.execute_task(task_to_execute, executor_id)
            else:
                # Check if all tasks are done
                with self.task_lock:
                    total_processed = len(self.completed_tasks) + len([r for r in self.results if r["status"] == "failed"])
                    if total_processed >= len(self.tasks):
                        self.log(f"[{executor_name}] All tasks processed, shutting down")
                        break

                # Wait a bit before checking again (in case dependencies need to complete)
                time.sleep(0.5)

        self.log(f"[{executor_name}] Worker finished")

    def execute_parallel(self):
        """
        Execute all tasks using a task queue model
        M executors work through N tasks dynamically
        """
        self.log("\n" + "="*80)
        self.log("STEP 3: EXECUTING TASKS WITH TASK QUEUE MODEL")
        self.log("="*80)

        num_tasks = len(self.tasks)
        num_executors_needed = min(num_tasks, self.max_executors)

        self.log(f"  Total tasks: {num_tasks}")
        self.log(f"  Executor budget: {self.max_executors}")
        self.log(f"  Executors to spawn: {num_executors_needed}")
        self.log(f"  Execution model: {num_executors_needed} executors working through {num_tasks} tasks")
        self.log(f"  Tasks per executor: ~{num_tasks / num_executors_needed:.1f} average")

        # Initialize task queue and tracking
        self.completed_tasks.clear()
        self.in_progress_tasks.clear()

        # Create and start executor worker threads
        self.log(f"\n  Spawning {num_executors_needed} executor workers...")
        for executor_id in range(1, num_executors_needed + 1):
            thread = threading.Thread(
                target=self.executor_worker,
                args=(executor_id,),
                name=f"Executor-{executor_id}"
            )
            self.executor_threads.append(thread)
            thread.start()
            time.sleep(0.2)  # Stagger starts slightly

        self.log(f"  ✓ All {num_executors_needed} executor workers started")
        self.log("  Executors will dynamically pick tasks from queue...")
        self.log("  Waiting for all tasks to complete...\n")

        # Wait for all executor threads to complete
        for thread in self.executor_threads:
            thread.join()

        self.log(f"\n  ✓ All executor workers finished")
        self.log(f"  ✓ Total tasks completed: {len(self.completed_tasks)}")

    def aggregate_results(self) -> Dict[str, Any]:
        """
        Aggregate results from all executors
        """
        self.log("\n" + "="*80)
        self.log("STEP 4: AGGREGATING RESULTS")
        self.log("="*80)

        completed = sum(1 for r in self.results if r["status"] == "completed")
        failed = sum(1 for r in self.results if r["status"] == "failed")

        total_files = sum(len(r.get("output_files", [])) for r in self.results
                         if r["status"] == "completed")

        total_loc = sum(r.get("metrics", {}).get("lines_of_code", 0)
                       for r in self.results if r["status"] == "completed")

        avg_coverage = (sum(r.get("metrics", {}).get("test_coverage", 0)
                           for r in self.results if r["status"] == "completed") /
                       max(completed, 1))

        summary = {
            "total_tasks": len(self.tasks),
            "completed": completed,
            "failed": failed,
            "success_rate": f"{(completed / len(self.tasks) * 100):.1f}%",
            "total_files_created": total_files,
            "total_lines_of_code": total_loc,
            "average_test_coverage": f"{avg_coverage:.1f}%",
            "results": self.results
        }

        self.log(f"  Total tasks: {summary['total_tasks']}")
        self.log(f"  ✓ Completed: {summary['completed']}")
        self.log(f"  ✗ Failed: {summary['failed']}")
        self.log(f"  Success rate: {summary['success_rate']}")
        self.log(f"  Total files created: {summary['total_files_created']}")
        self.log(f"  Total lines of code: {summary['total_lines_of_code']}")
        self.log(f"  Average test coverage: {summary['average_test_coverage']}")

        # Save summary
        summary_file = self.output_dir / "execution_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.log(f"\n  ✓ Summary saved to {summary_file}")

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

                # Find the task info from results
                task_result = next((r for r in self.results if r["task_id"] == task_id), None)
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
                    self.log(f"      → {target_file.relative_to(self.output_dir)}")

                # Process tests.py
                test_file = task_dir / "tests.py"
                if test_file.exists():
                    target_file = tests_dir / f"test_{task_name}.py"
                    shutil.copy2(test_file, target_file)
                    files_merged += 1
                    self.log(f"      → {target_file.relative_to(self.output_dir)}")

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
            f.write(f"## Components\n\n")
            f.write("\n".join(readme_sections))

        files_merged += 1
        self.log(f"\n  ✓ Created combined README.md")

        # Copy execution summary and plan to docs directory
        summary_file = self.output_dir / "execution_summary.json"
        plan_file = self.output_dir / "execution_plan.json"

        if summary_file.exists():
            shutil.copy2(summary_file, docs_dir / "execution_summary.json")
            files_merged += 1
            self.log(f"  ✓ Copied execution summary to docs/")

        if plan_file.exists():
            shutil.copy2(plan_file, docs_dir / "execution_plan.json")
            files_merged += 1
            self.log(f"  ✓ Copied execution plan to docs/")

        self.log(f"\n  ✓ Consolidation complete!")
        self.log(f"  Total files consolidated: {files_merged}")
        self.log(f"  Project location: {self.output_dir}")
        self.log(f"  Structure:")
        self.log(f"    - src/       : {len(list(src_dir.glob('*.py')))} implementation files")
        self.log(f"    - tests/     : {len(list(tests_dir.glob('*.py')))} test files")
        self.log(f"    - docs/      : {len(list(docs_dir.glob('*')))} documentation files")
        self.log(f"    - README.md  : Combined documentation")

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

        start_time = time.time()

        try:
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

            # Step 3: Execute tasks in parallel
            self.execute_parallel()

            # Step 4: Aggregate results
            summary = self.aggregate_results()

            # Step 5: Merge outputs into unified structure
            self.merge_outputs()

            total_time = time.time() - start_time

            self.log("\n" + "="*80)
            self.log("ORCHESTRATOR COMPLETED SUCCESSFULLY")
            self.log("="*80)
            self.log(f"Total execution time: {total_time:.2f}s")
            self.log(f"Output directory: {self.output_dir}")

            return summary

        except Exception as e:
            self.log(f"\n✗ ORCHESTRATOR FAILED: {str(e)}")
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Parallel Task Orchestrator - Intelligently scales executor agents based on task complexity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Simple task with default settings (max 5 executors)
  python orchestrator.py "Create a calculator function"

  # Complex task with custom executor budget
  python orchestrator.py "Build e-commerce platform" --max-executors 10

  # With custom output directory
  python orchestrator.py "Build chat app" --output-dir my-project --max-executors 3
        '''
    )

    parser.add_argument('requirements', help='Project requirements description')
    parser.add_argument('--output-dir', '-o', default=None,
                       help='Output directory for generated files (default: ../outputs/parallel-orchestrator/)')
    parser.add_argument('--max-executors', '-m', type=int, default=5,
                       help='Maximum number of parallel executors (budget) (default: 5)')
    parser.add_argument('--real', action='store_true',
                       help='Use real Claude API calls to generate actual code (slower but produces working code)')

    args = parser.parse_args()

    # Validate max_executors
    if args.max_executors < 1:
        print("Error: --max-executors must be at least 1")
        sys.exit(1)
    if args.max_executors > 20:
        print("Warning: --max-executors > 20 may cause performance issues")

    print(f"\n{'='*80}")
    print(f"CONFIGURATION")
    print(f"{'='*80}")
    print(f"Requirements: {args.requirements}")
    print(f"Output directory: {args.output_dir}")
    print(f"Executor budget: {args.max_executors} (planner will decide optimal count within this budget)")
    print(f"Execution mode: {'REAL (generates actual code)' if args.real else 'SIMULATED (fast demo)'}")
    print(f"{'='*80}\n")

    orchestrator = ParallelOrchestrator(args.requirements, args.output_dir, use_real_executors=args.real)
    orchestrator.max_executors = args.max_executors
    summary = orchestrator.run()

    print("\n" + "="*80)
    print("EXECUTION COMPLETE")
    print("="*80)
    print(f"Executors used: {summary['total_tasks']} / {args.max_executors} (budget)")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Files Created: {summary['total_files_created']}")
    print(f"Lines of Code: {summary['total_lines_of_code']}")
    print(f"\nCheck output directory: {args.output_dir}")


if __name__ == "__main__":
    main()
