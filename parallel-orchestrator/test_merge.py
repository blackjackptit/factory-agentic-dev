#!/usr/bin/env python3
"""
Test script to verify merge functionality on existing outputs
"""

import json
from pathlib import Path
from orchestrator import ParallelOrchestrator

def test_merge(output_dir: str):
    """Test merge functionality on existing output directory"""
    output_path = Path(output_dir)

    # Check if output directory exists
    if not output_path.exists():
        print(f"Error: Output directory not found: {output_dir}")
        return False

    # Load execution plan
    plan_file = output_path / "execution_plan.json"
    summary_file = output_path / "execution_summary.json"

    if not plan_file.exists() or not summary_file.exists():
        print(f"Error: Missing execution_plan.json or execution_summary.json in {output_dir}")
        return False

    print(f"Testing merge on: {output_dir}")
    print("="*80)

    # Load the plan and summary
    with open(plan_file, "r") as f:
        plan = json.load(f)

    with open(summary_file, "r") as f:
        summary = json.load(f)

    # Create orchestrator instance
    orchestrator = ParallelOrchestrator("Test merge", str(output_path))

    # Set up the orchestrator state from loaded data
    orchestrator.plan = plan
    orchestrator.tasks = plan["tasks"]
    orchestrator.results = summary["results"]

    # Run merge
    try:
        orchestrator.merge_outputs()
        print("\n✓ Merge test completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Merge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        # Default to exam website outputs
        output_dir = "../outputs/parallel-orchestrator"

    success = test_merge(output_dir)
    sys.exit(0 if success else 1)
