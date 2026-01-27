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
  # Build a simple todo app (local execution)
  python build_website.py "Build a todo list app with add, edit, and delete functionality"

  # Build with Docker execution
  python build_website.py "Build a blog website" --docker

  # Build with Docker and AWS Bedrock
  python build_website.py "Create a dashboard" --docker --docker-use-bedrock

  # Build with custom Docker image
  python build_website.py "Build an e-commerce site" --docker --docker-image my-image:latest

  # Build with custom AWS Bedrock settings
  python build_website.py "Build a landing page" --docker --docker-use-bedrock --docker-bedrock-region us-east-1

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

    # Docker execution options
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Run agents in Docker containers"
    )

    parser.add_argument(
        "--docker-image",
        default="orchestrator-agents:latest",
        help="Docker image to use (default: orchestrator-agents:latest)"
    )

    # AWS Bedrock options
    parser.add_argument(
        "--docker-use-bedrock",
        action="store_true",
        help="Use AWS Bedrock instead of Anthropic API"
    )

    parser.add_argument(
        "--docker-bedrock-region",
        default="eu-central-1",
        help="AWS region for Bedrock (default: eu-central-1)"
    )

    parser.add_argument(
        "--docker-bedrock-model",
        default="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        help="Bedrock model ID (default: global.anthropic.claude-sonnet-4-5-20250929-v1:0)"
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
    print(f"Execution Mode: {'Docker' if args.docker else 'Local'}")
    if args.docker:
        print(f"Docker Image: {args.docker_image}")
        print(f"AI Mode: {'AWS Bedrock' if args.docker_use_bedrock else 'Anthropic API'}")
        if args.docker_use_bedrock:
            print(f"Bedrock Region: {args.docker_bedrock_region}")
            print(f"Bedrock Model: {args.docker_bedrock_model}")
    else:
        # Show API mode for local execution
        from claude_api import ClaudeAPI
        import os
        use_bedrock = os.environ.get("USE_BEDROCK", "0") == "1" or \
                     os.environ.get("CLAUDE_CODE_USE_BEDROCK", "0") == "1"
        if use_bedrock:
            bedrock_model = os.environ.get("BEDROCK_MODEL", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
            print(f"AI Mode: Claude CLI with Bedrock ({bedrock_model})")
        else:
            print(f"AI Mode: Claude CLI (Anthropic)")
    print()

    # Setup project directory
    project_dir = args.project_dir or os.getcwd()
    output_dir = args.output_dir

    # Create orchestrator
    orchestrator = WebsiteOrchestrator(
        project_dir=project_dir,
        output_dir=output_dir,
        use_docker=args.docker,
        docker_image=args.docker_image,
        use_bedrock=args.docker_use_bedrock,
        bedrock_region=args.docker_bedrock_region,
        bedrock_model=args.docker_bedrock_model
    )

    # Check Claude Code CLI availability
    if args.docker:
        print("Checking Docker availability...")
    else:
        print("Checking Claude Code CLI availability...")

    if not orchestrator.check_claude_available():
        if args.docker:
            print("\n❌ ERROR: Docker is not available!")
            print("\nPlease make sure Docker is installed and running.")
            print("You can install it from: https://www.docker.com/get-started")
        else:
            print("\n❌ ERROR: Claude Code CLI is not available!")
            print("\nPlease make sure the 'claude' command is installed and in your PATH.")
            print("You can install it from: https://github.com/anthropics/claude-code")
        print()
        sys.exit(1)

    if args.docker:
        print("✓ Docker is ready\n")
    else:
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
