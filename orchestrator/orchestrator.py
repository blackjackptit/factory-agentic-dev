#!/usr/bin/env python3
"""
Website Development Orchestrator
Coordinates multiple specialized subagents to build websites
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from claude_api import ClaudeAPI


class WebsiteOrchestrator:
    """
    Orchestrates website development using specialized subagents
    - Design Subagent: Creates design specifications
    - Implementation Subagent: Builds React UI
    - Testing Subagent: Creates and runs tests
    """

    def __init__(self,
                 project_dir: Optional[str] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize orchestrator

        Args:
            project_dir: Directory for the project being worked on
            output_dir: Directory for orchestrator outputs
        """
        self.api = ClaudeAPI(project_dir)
        self.project_dir = os.path.abspath(project_dir or os.getcwd())
        self.output_dir = os.path.abspath(output_dir or os.path.join(os.path.dirname(__file__), "output"))
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Subagent results storage
        self.results = {
            "design": None,
            "implementation": None,
            "testing": None
        }

    def check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available"""
        return self.api.health_check()

    def save_result(self, stage: str, data: Any):
        """Save results from a stage"""
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"{stage}_{timestamp}.json")

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ {stage.capitalize()} results saved to: {output_file}")
        return output_file

    def delegate_to_subagent(self,
                            subagent_name: str,
                            prompt: str,
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Delegate a task to a specialized subagent

        Args:
            subagent_name: Name of the subagent
            prompt: Task description
            context: Additional context for the task

        Returns:
            Response from the subagent
        """
        print(f"\n{'='*70}")
        print(f"🤖 Delegating to {subagent_name.upper()} Subagent")
        print(f"{'='*70}")

        # Build full prompt with context
        full_prompt = f"{prompt}"
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            full_prompt = f"{prompt}\n\nContext:\n{context_str}"

        print(f"\nTask: {prompt[:100]}...")
        print(f"Working...")

        try:
            response = self.api.query(full_prompt, cwd=self.project_dir)

            if response.get("success"):
                print(f"✓ {subagent_name.capitalize()} completed successfully")
                result = {
                    "subagent": subagent_name,
                    "success": True,
                    "response": response.get("response"),
                    "timestamp": datetime.now().isoformat()
                }
                self.results[subagent_name] = result
                return result
            else:
                print(f"✗ {subagent_name.capitalize()} failed")
                return {
                    "subagent": subagent_name,
                    "success": False,
                    "error": "Query returned unsuccessful status"
                }

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return {
                "subagent": subagent_name,
                "success": False,
                "error": str(e)
            }

    def build_website(self, requirements: str) -> Dict[str, Any]:
        """
        Main orchestration flow to build a website

        Args:
            requirements: User requirements for the website

        Returns:
            Summary of all stages
        """
        print("\n" + "="*70)
        print("🎯 WEBSITE DEVELOPMENT ORCHESTRATOR")
        print("="*70)
        print(f"\nRequirements: {requirements}")
        print(f"Project Directory: {self.project_dir}")
        print(f"Output Directory: {self.output_dir}")

        # Check Claude Code CLI availability
        if not self.check_claude_available():
            print("\n✗ Claude Code CLI is not available!")
            print("Please make sure 'claude' command is installed and in your PATH")
            return {"success": False, "error": "Claude Code CLI not available"}

        print("\n✓ Claude Code CLI is ready")

        summary = {
            "requirements": requirements,
            "stages": {},
            "start_time": datetime.now().isoformat()
        }

        # Stage 1: Design
        from subagents.design_agent import DesignAgent
        design_agent = DesignAgent(self)
        design_result = design_agent.execute(requirements)
        summary["stages"]["design"] = design_result
        self.save_result("design", design_result)

        if not design_result.get("success"):
            print("\n✗ Design stage failed. Stopping orchestration.")
            return summary

        # Stage 2: Implementation
        from subagents.implementation_agent import ImplementationAgent
        impl_agent = ImplementationAgent(self)
        impl_result = impl_agent.execute(requirements, design_result)
        summary["stages"]["implementation"] = impl_result
        self.save_result("implementation", impl_result)

        if not impl_result.get("success"):
            print("\n✗ Implementation stage failed. Stopping orchestration.")
            return summary

        # Stage 3: Testing
        from subagents.testing_agent import TestingAgent
        test_agent = TestingAgent(self)
        test_result = test_agent.execute(requirements, impl_result)
        summary["stages"]["testing"] = test_result
        self.save_result("testing", test_result)

        # Final summary
        summary["end_time"] = datetime.now().isoformat()
        summary["success"] = all(
            stage.get("success", False)
            for stage in summary["stages"].values()
        )

        # Save complete summary
        self.save_result("complete_summary", summary)

        print("\n" + "="*70)
        print("🎉 ORCHESTRATION COMPLETE")
        print("="*70)
        print(f"\n✓ Design: {'SUCCESS' if design_result.get('success') else 'FAILED'}")
        print(f"✓ Implementation: {'SUCCESS' if impl_result.get('success') else 'FAILED'}")
        print(f"✓ Testing: {'SUCCESS' if test_result.get('success') else 'FAILED'}")
        print(f"\nResults saved to: {self.output_dir}")

        return summary


if __name__ == "__main__":
    # Simple CLI interface
    import sys

    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py '<website requirements>'")
        print("\nExample:")
        print("  python orchestrator.py 'Build a todo list app with add, edit, delete features'")
        sys.exit(1)

    requirements = sys.argv[1]
    orchestrator = WebsiteOrchestrator(project_dir=os.getcwd())
    result = orchestrator.build_website(requirements)

    sys.exit(0 if result.get("success") else 1)
