#!/usr/bin/env python3
"""
Docker Planner Executor
Runs the planner agent inside a Docker container
"""

import json
import os
import sys
from pathlib import Path
from planner_agent import PlannerAgent


def main():
    """Run planner and save results to output directory"""
    # Get configuration from environment
    output_dir = os.environ.get("OUTPUT_DIR", "/output")
    requirements = os.environ.get("REQUIREMENTS", "")
    max_executors = int(os.environ.get("MAX_EXECUTORS", "5"))

    # Check if using Bedrock
    use_bedrock = os.environ.get("USE_BEDROCK", "0") == "1"
    if use_bedrock:
        os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
        bedrock_model = os.environ.get("BEDROCK_MODEL", "global.anthropic.claude-sonnet-4-5-20250929-v1:0")
        bedrock_region = os.environ.get("BEDROCK_REGION", "eu-central-1")
        print(f"Bedrock Mode: Enabled")
        print(f"Bedrock Region: {bedrock_region}")
        print(f"Bedrock Model: {bedrock_model}")

    if not requirements:
        print("Error: REQUIREMENTS environment variable not set")
        sys.exit(1)

    print(f"Docker Planner Executor")
    print(f"Output directory: {output_dir}")
    print(f"Max executors: {max_executors}")
    print(f"Requirements: {requirements[:100]}...")
    print("")

    try:
        # Create planner agent
        planner = PlannerAgent(requirements, output_dir, max_executors)

        # Step 1: Analyze complexity
        print("Step 1: Analyzing complexity...")
        num_tasks = planner.analyze_complexity()
        print(f"  Determined task count: {num_tasks}")

        # Step 2: Create plan
        print("Step 2: Creating execution plan...")
        plan = planner.create_plan(num_tasks)
        print(f"  Plan created with {len(plan['tasks'])} tasks")

        # Save plan to output
        plan_file = Path(output_dir) / "planner_output.json"
        with open(plan_file, 'w') as f:
            json.dump({
                "success": True,
                "num_tasks": num_tasks,
                "plan": plan
            }, f, indent=2)

        print(f"\n✓ Planning complete")
        print(f"  Plan saved to: {plan_file}")

    except Exception as e:
        print(f"\n✗ Planning failed: {e}")

        # Save error to output
        error_file = Path(output_dir) / "planner_output.json"
        with open(error_file, 'w') as f:
            json.dump({
                "success": False,
                "error": str(e)
            }, f, indent=2)

        sys.exit(1)


if __name__ == "__main__":
    main()
