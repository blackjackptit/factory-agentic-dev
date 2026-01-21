#!/usr/bin/env python3
"""
Simple orchestrator test
Tests a minimal website build to verify the system works
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import WebsiteOrchestrator

def main():
    print("="*70)
    print("SIMPLE ORCHESTRATOR TEST")
    print("="*70)

    # Simple requirements
    requirements = "Build a simple landing page with a hero section that has a title and subtitle."

    print(f"\nRequirements: {requirements}")
    print("\nNote: This is a simplified test. Full dashboard builds take 3-5 minutes.")
    print()

    # Create orchestrator
    orchestrator = WebsiteOrchestrator(
        project_dir=os.getcwd(),
        output_dir="/tmp/orchestrator-test-simple"
    )

    # Check availability
    if not orchestrator.check_claude_available():
        print("✗ Claude CLI not available")
        return 1

    print("✓ Claude CLI is available\n")

    # Build website
    print("Starting build process...")
    print("(This will take a few minutes as each agent processes the requirements)\n")

    result = orchestrator.build_website(requirements)

    # Show results
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)

    if result.get("success"):
        print("\n✅ Orchestrator test PASSED")
        print(f"\nResults saved to: {orchestrator.output_dir}")

        # Show what each agent produced
        if "stages" in result:
            for stage_name, stage_result in result["stages"].items():
                status = "✓" if stage_result.get("success") else "✗"
                print(f"  {status} {stage_name.capitalize()}: {'SUCCESS' if stage_result.get('success') else 'FAILED'}")

        return 0
    else:
        print("\n❌ Orchestrator test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
