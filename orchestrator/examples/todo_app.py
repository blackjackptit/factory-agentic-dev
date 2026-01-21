#!/usr/bin/env python3
"""
Example: Building a Todo App
Demonstrates orchestrator usage for a simple todo list application
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from orchestrator import WebsiteOrchestrator


def main():
    """Build a todo app using the orchestrator"""

    requirements = """
Build a Todo List Application with the following features:

CORE FEATURES:
- Add new todos with a text input and button
- Display list of todos
- Mark todos as complete/incomplete with checkbox
- Delete todos with a delete button
- Edit existing todos inline

UI REQUIREMENTS:
- Clean, modern design
- Responsive layout that works on mobile and desktop
- Pleasant color scheme (blues and greens)
- Smooth animations for adding/removing items
- Clear visual feedback for completed items

TECHNICAL REQUIREMENTS:
- Use React with functional components and hooks
- State management with useState or useReducer
- Local storage persistence (todos saved between sessions)
- Input validation (don't allow empty todos)
- Accessibility features (ARIA labels, keyboard navigation)

ADDITIONAL FEATURES:
- Filter todos by: All, Active, Completed
- Show count of active todos
- "Clear completed" button to remove all completed todos
- Simple animations for list operations
    """

    print("Building Todo Application...")
    print("=" * 70)

    # Create orchestrator
    orchestrator = WebsiteOrchestrator(
        project_dir=os.getcwd(),
        output_dir=os.path.join(os.path.dirname(__file__), "../output/todo_app")
    )

    # Build the website
    result = orchestrator.build_website(requirements)

    # Print summary
    print("\n" + "=" * 70)
    print("BUILD SUMMARY")
    print("=" * 70)

    if result.get("success"):
        print("\n✅ Todo app successfully created!")
        print(f"\nResults location: {orchestrator.output_dir}")
        print("\nWhat was created:")
        print("  ✓ Complete design specifications")
        print("  ✓ React component implementation")
        print("  ✓ Comprehensive test suite")
        print("\nNext steps:")
        print("  1. Review design specs in output directory")
        print("  2. Create React project: npx create-react-app todo-app")
        print("  3. Copy component code into your project")
        print("  4. Install dependencies from implementation")
        print("  5. Run tests to verify functionality")
    else:
        print("\n❌ Build failed. Check output for details.")
        print(f"\nPartial results: {orchestrator.output_dir}")

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
