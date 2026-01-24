#!/usr/bin/env python3
"""
Demo script showing different scenarios with the Parallel Orchestrator
"""

from orchestrator import ParallelOrchestrator
import time


def demo_simple_task():
    """Demo: Simple task requiring 1 executor"""
    print("\n" + "="*80)
    print("DEMO 1: SIMPLE TASK (1 Executor Expected)")
    print("="*80)

    orchestrator = ParallelOrchestrator(
        requirements="Create a simple calculator function that adds two numbers",
        output_dir="../outputs/parallel-orchestrator/demo/simple_task"
    )

    summary = orchestrator.run()
    print(f"\n✓ Demo 1 completed: {summary['total_tasks']} executor(s) used")


def demo_medium_task():
    """Demo: Medium complexity task requiring 2-3 executors"""
    print("\n" + "="*80)
    print("DEMO 2: MEDIUM TASK (2-3 Executors Expected)")
    print("="*80)

    orchestrator = ParallelOrchestrator(
        requirements="""
        Build a todo list application with the following features:
        - Add, edit, and delete tasks
        - Mark tasks as complete
        - Filter by status (all, active, completed)
        - Local storage persistence
        """,
        output_dir="../outputs/parallel-orchestrator/demo/medium_task"
    )

    summary = orchestrator.run()
    print(f"\n✓ Demo 2 completed: {summary['total_tasks']} executor(s) used")


def demo_complex_task():
    """Demo: Complex task requiring 4-5 executors"""
    print("\n" + "="*80)
    print("DEMO 3: COMPLEX TASK (4-5 Executors Expected)")
    print("="*80)

    orchestrator = ParallelOrchestrator(
        requirements="""
        Create a full-stack e-commerce platform with the following features:
        - User authentication with JWT tokens
        - Product catalog with search and filtering
        - Shopping cart functionality
        - Payment processing integration with Stripe
        - Order management system
        - Admin dashboard for inventory management
        - Real-time notifications for order updates
        - PostgreSQL database with proper indexing
        - REST API with comprehensive documentation
        - React frontend with responsive design
        - Automated testing suite with 80%+ coverage
        - Docker containerization
        """,
        output_dir="../outputs/parallel-orchestrator/demo/complex_task"
    )

    summary = orchestrator.run()
    print(f"\n✓ Demo 3 completed: {summary['total_tasks']} executor(s) used")


def demo_custom_scenario():
    """Demo: Custom user-defined scenario"""
    print("\n" + "="*80)
    print("DEMO 4: CUSTOM SCENARIO")
    print("="*80)

    requirements = input("\nEnter your requirements: ")

    orchestrator = ParallelOrchestrator(
        requirements=requirements,
        output_dir="../outputs/parallel-orchestrator/demo/custom_task"
    )

    summary = orchestrator.run()
    print(f"\n✓ Custom demo completed: {summary['total_tasks']} executor(s) used")
    print(f"  Success rate: {summary['success_rate']}")
    print(f"  Files created: {summary['total_files_created']}")
    print(f"  Total LOC: {summary['total_lines_of_code']}")


def compare_scenarios():
    """Compare different complexity scenarios"""
    print("\n" + "="*80)
    print("SCENARIO COMPARISON")
    print("="*80)

    scenarios = [
        {
            "name": "Simple",
            "requirements": "Create a hello world function",
            "expected_executors": 1
        },
        {
            "name": "Medium",
            "requirements": "Build a contact form with validation and email notification",
            "expected_executors": 2
        },
        {
            "name": "Complex",
            "requirements": "Create a blogging platform with authentication, comments, and admin panel",
            "expected_executors": 3
        },
        {
            "name": "Advanced",
            "requirements": "Build a real-time collaborative document editor with authentication, "
                          "websockets, rich text editing, and version history",
            "expected_executors": 4
        },
        {
            "name": "Enterprise",
            "requirements": "Create a complete project management system with authentication, "
                          "role-based access control, real-time updates, file attachments, "
                          "reporting dashboard, third-party integrations, and API",
            "expected_executors": 5
        }
    ]

    results = []

    for scenario in scenarios:
        print(f"\n--- Testing {scenario['name']} Scenario ---")
        print(f"Requirements: {scenario['requirements'][:100]}...")

        orchestrator = ParallelOrchestrator(
            requirements=scenario['requirements'],
            output_dir=f"../outputs/parallel-orchestrator/demo/comparison_{scenario['name'].lower()}"
        )

        num_executors = orchestrator.analyze_complexity()

        results.append({
            "name": scenario['name'],
            "expected": scenario['expected_executors'],
            "actual": num_executors,
            "match": "✓" if num_executors == scenario['expected_executors'] else "✗"
        })

        print(f"Expected: {scenario['expected_executors']} | Actual: {num_executors} | {results[-1]['match']}")

    # Summary table
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    print(f"{'Scenario':<15} {'Expected':<12} {'Actual':<12} {'Match':<8}")
    print("-" * 80)

    for result in results:
        print(f"{result['name']:<15} {result['expected']:<12} {result['actual']:<12} {result['match']:<8}")

    accuracy = sum(1 for r in results if r['match'] == '✓') / len(results) * 100
    print(f"\nComplexity Analysis Accuracy: {accuracy:.1f}%")


def main():
    """Main demo menu"""
    while True:
        print("\n" + "="*80)
        print("PARALLEL ORCHESTRATOR - DEMO MENU")
        print("="*80)
        print("1. Demo 1: Simple Task (1 executor)")
        print("2. Demo 2: Medium Task (2-3 executors)")
        print("3. Demo 3: Complex Task (4-5 executors)")
        print("4. Demo 4: Custom Scenario")
        print("5. Compare All Scenarios")
        print("6. Exit")
        print("="*80)

        choice = input("\nSelect demo (1-6): ").strip()

        if choice == "1":
            demo_simple_task()
        elif choice == "2":
            demo_medium_task()
        elif choice == "3":
            demo_complex_task()
        elif choice == "4":
            demo_custom_scenario()
        elif choice == "5":
            compare_scenarios()
        elif choice == "6":
            print("\n✓ Exiting demo. Thank you!")
            break
        else:
            print("\n✗ Invalid choice. Please select 1-6.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("="*80)
    print("PARALLEL ORCHESTRATOR DEMONSTRATION")
    print("="*80)
    print("\nThis demo showcases the orchestrator's ability to:")
    print("  • Analyze requirement complexity")
    print("  • Determine optimal number of executors (1-5)")
    print("  • Execute tasks in parallel")
    print("  • Aggregate results efficiently")
    print("\nNote: This is a simulation. Executors will create sample files.")
    print("      In production, executors would call Claude API for actual code generation.")

    input("\nPress Enter to start demo...")

    main()
