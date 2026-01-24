#!/usr/bin/env python3
"""
Website Builder CLI
Main entry point for building websites with the orchestrator
"""

import sys
import os
import argparse

# Add orchestrator directory to path
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import WebsiteOrchestrator


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Build a website using AI-powered orchestrator with specialized subagents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build a simple todo app
  python build_website.py "Build a todo list app with add, edit, and delete functionality"

  # Build an e-commerce site
  python build_website.py "Create a product catalog with shopping cart and checkout"

  # Build a dashboard
  python build_website.py "Build an analytics dashboard with charts and data tables"

  # Specify custom project directory
  python build_website.py "Build a blog website" --project-dir ./my-blog

  # Specify custom output directory
  python build_website.py "Build a landing page" --output-dir ./outputs
        """
    )

    parser.add_argument(
        "requirements",
        help="Website requirements and features description"
    )

    parser.add_argument(
        "--project-dir",
        default=None,
        help="Project directory (default: current directory)"
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for results (default: ../outputs/website-orchestrator/)"
    )

    args = parser.parse_args()

    # Print header
    print("\n" + "="*70)
    print("🚀 WEBSITE BUILDER ORCHESTRATOR")
    print("="*70)
    print("\nThis orchestrator will coordinate three specialized subagents:")
    print("  🎨 Design Agent - Creates UI/UX specifications")
    print("  ⚛️  Implementation Agent - Builds React components")
    print("  🧪 Testing Agent - Creates automated test suite")
    print()

    # Setup project directory
    project_dir = args.project_dir or os.getcwd()
    output_dir = args.output_dir

    # Create orchestrator
    orchestrator = WebsiteOrchestrator(
        project_dir=project_dir,
        output_dir=output_dir
    )

    # Check Claude Code CLI availability
    print("Checking Claude Code CLI availability...")
    if not orchestrator.check_claude_available():
        print("\n❌ ERROR: Claude Code CLI is not available!")
        print("\nPlease make sure the 'claude' command is installed and in your PATH.")
        print("You can install it from: https://github.com/anthropics/claude-code")
        print()
        sys.exit(1)

    print("✓ Claude Code CLI is ready\n")

    # Run orchestration
    try:
        result = orchestrator.build_website(args.requirements)

        # Exit with appropriate code
        if result.get("success"):
            print("\n✅ SUCCESS: Website development completed!")
            print(f"\nAll results saved to: {orchestrator.output_dir}")
            print("\nNext steps:")
            print("  1. Review the design specifications")
            print("  2. Examine the React implementation code")
            print("  3. Set up the project using provided instructions")
            print("  4. Run the test suite")
            print()
            sys.exit(0)
        else:
            print("\n❌ FAILED: Website development encountered errors")
            print(f"\nPartial results saved to: {orchestrator.output_dir}")
            print()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Orchestration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
