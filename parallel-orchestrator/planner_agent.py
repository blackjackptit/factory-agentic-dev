#!/usr/bin/env python3
"""
Planner Agent
Uses Claude Code to analyze requirements and create intelligent execution plans
"""

import json
import subprocess
import re
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class PlannerAgent:
    """
    Intelligent planner that uses Claude Code to analyze complexity and create execution plans
    """

    def __init__(self, requirements: str, output_dir: str = "output", max_executors: int = 5):
        self.requirements = requirements
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_executors = max_executors
        self.log_file = self.output_dir / "orchestrator.log"

    def log(self, message: str):
        """Write log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    def call_claude_for_analysis(self) -> Dict[str, Any]:
        """
        Call Claude Code to analyze requirement complexity
        """
        self.log("  Calling Claude Code for complexity analysis...")

        prompt = f"""
You are an expert project planner analyzing software requirements to determine optimal task parallelization.

REQUIREMENTS TO ANALYZE:
{self.requirements}

EXECUTOR BUDGET:
Maximum executors available: {self.max_executors}

YOUR TASK:
Analyze the complexity of these requirements and determine how to best utilize the executor budget.

IMPORTANT EXECUTION MODEL:
- The user has a budget of {self.max_executors} parallel executors
- You should break work into TASKS (not limited by executor count)
- All {self.max_executors} executors will work in parallel on the task queue
- When an executor finishes a task, it picks up the next task from the queue
- This means you can create MORE tasks than executors for better parallelization

EXAMPLES:
- Budget of 5 executors, 10 tasks → All 5 executors work through 10 tasks in parallel
- Budget of 10 executors, 3 tasks → Only 3 executors needed (others idle)
- Budget of 3 executors, 15 tasks → All 3 executors continuously work through 15 tasks

YOUR DECISION:
Determine the optimal number of tasks to create, considering:
1. Can work be broken into more fine-grained tasks for better parallelization?
2. Are there enough distinct components to keep all executors busy?
3. What's the right balance between task granularity and coordination overhead?

COMPLEXITY FACTORS TO CONSIDER:
1. Scope: How many words/features/components are mentioned?
2. Technical complexity: What technologies, algorithms, or systems are involved?
3. Multiple domains: Does it span different areas (data, ML, UI, backend, mobile, etc)?
4. Integration needs: Are there multiple systems or components that need to work together?
5. Specialized knowledge: Does it require domain expertise (ML, game dev, data science, etc)?

TASK CREATION GUIDELINES (Domain-Agnostic):

REMEMBER: You're creating TASKS, not executors. Tasks will be executed by {self.max_executors} parallel executors.

**Simple Projects** (Few distinct components):
- Create 1-3 tasks if work is inherently sequential or has few separable parts
- Examples: Single utility, basic script, proof of concept

**Moderate Projects** (Several components):
- Create 3-8 tasks if work can be broken into distinct parallel components
- Examples:
  • Web: Database schema, API routes (multiple), Frontend components (multiple), Testing
  • ML: Data loading, Data preprocessing, Model architecture, Training loop, Evaluation metrics
  • Game: Core engine, Physics system, Rendering, Audio system, Game logic
  • Mobile: Backend API, iOS UI, Android UI, Shared business logic, Testing

**Complex Projects** (Many components):
- Create 8-15+ tasks if work has many fine-grained parallelizable components
- Break large components into smaller tasks for better parallelization
- Examples:
  • Web: DB schema, User API, Product API, Order API, Auth middleware, Frontend layout, Frontend components (multiple), E2E tests, Unit tests
  • ML: Data collection, Data cleaning, Feature engineering, Model architecture, Training pipeline, Hyperparameter tuning, Evaluation, Deployment script
  • Game: Core engine, Physics, Collision detection, Rendering pipeline, Shader system, Audio engine, Sound effects, UI system, Game logic, AI behaviors
  • Multi-service: Service 1, Service 2, Service 3, API Gateway, Auth service, Database setup, Frontend, Mobile app, Testing, Documentation

**Key Considerations**:
1. **Task Granularity**: Smaller tasks = better parallelization, but don't make them too small (minimum 30min-1hr of work)
2. **Dependencies**: Some tasks may depend on others - that's OK, executors will wait or pick other tasks
3. **Executor Budget**: With {self.max_executors} executors, all will work in parallel through your task queue
4. **Optimal Utilization**: Create enough tasks to keep all executors busy throughout execution

OUTPUT REQUIRED:
Respond with a JSON object in this exact format:
```json
{{
  "num_tasks": <number of tasks to create (can be more than {self.max_executors})>,
  "reasoning": "<brief explanation of task breakdown strategy>",
  "key_features_detected": ["feature1", "feature2", ...],
  "technical_components": ["component1", "component2", ...]
}}
```

IMPORTANT:
- "num_tasks" is the number of TASKS you'll create in the execution plan
- This can be MORE than {self.max_executors} (the executor budget)
- All {self.max_executors} executors will work through these tasks in parallel
- Example: num_tasks=10 with budget of 5 executors is perfectly fine!

Provide ONLY the JSON object, no additional text.
"""

        try:
            result = subprocess.run(
                [
                    "claude",
                    "--dangerously-skip-permissions",
                    "--print",
                    "-p", prompt
                ],
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": result.stdout,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "response": None,
                    "error": f"Claude CLI error: {result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "response": None,
                "error": "Claude API timeout (60 seconds)"
            }
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }

    def parse_complexity_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Claude's complexity analysis response
        """
        try:
            # Extract JSON from response
            json_pattern = r'```json\s*\n(.*?)\n```'
            match = re.search(json_pattern, response, re.DOTALL)

            if match:
                json_str = match.group(1)
                analysis = json.loads(json_str)
                return analysis
            else:
                # Try to find JSON without code blocks
                json_pattern = r'\{.*?\}'
                match = re.search(json_pattern, response, re.DOTALL)
                if match:
                    analysis = json.loads(match.group(0))
                    return analysis

                raise ValueError("No JSON found in response")

        except Exception as e:
            self.log(f"  Error: Failed to parse Claude response: {str(e)}")
            raise ValueError(f"Failed to parse complexity analysis from Claude Code response: {str(e)}")

    def analyze_complexity(self) -> int:
        """
        Analyze requirement complexity and determine number of executors needed
        Returns: number of executors (1 to max_executors)
        """
        self.log("\n" + "="*80)
        self.log("STEP 1: ANALYZING REQUIREMENT COMPLEXITY (via Claude Code)")
        self.log("="*80)
        self.log(f"  Executor budget: {self.max_executors} (planner will decide optimal count)")

        # Call Claude for intelligent analysis
        api_response = self.call_claude_for_analysis()

        if not api_response["success"]:
            error_msg = f"Claude API failed: {api_response['error']}"
            self.log(f"  ✗ Error: {error_msg}")
            raise RuntimeError(error_msg)

        analysis = self.parse_complexity_response(api_response["response"])

        # Get number of tasks (can be more than max_executors)
        num_tasks = analysis.get("num_tasks", analysis.get("complexity_score", 1))
        num_tasks = max(num_tasks, 1)  # Ensure at least 1 task

        self.log(f"  Requirements length: {len(self.requirements.split())} words")
        self.log(f"  Number of tasks to create: {num_tasks}")
        self.log(f"  Executor budget: {self.max_executors}")
        self.log(f"  Task queue model: {self.max_executors} executors will work through {num_tasks} tasks")
        self.log(f"  Reasoning: {analysis.get('reasoning', 'N/A')}")
        if analysis.get('key_features_detected'):
            self.log(f"  Key features: {', '.join(analysis['key_features_detected'])}")
        if analysis.get('technical_components'):
            self.log(f"  Technical components: {', '.join(analysis['technical_components'])}")

        return num_tasks

    def call_claude_for_plan(self, num_tasks: int) -> Dict[str, Any]:
        """
        Call Claude Code to create execution plan
        """
        self.log("  Calling Claude Code for execution plan generation...")

        prompt = f"""
You are an expert project planner creating an execution plan for parallel development.

REQUIREMENTS:
{self.requirements}

EXECUTION MODEL:
- Number of tasks to create: {num_tasks}
- Executor budget: {self.max_executors} parallel executors
- Execution strategy: All {self.max_executors} executors will work through {num_tasks} tasks in parallel
- When an executor finishes a task, it picks up the next task from the queue

YOUR TASK:
Create a detailed execution plan with exactly {num_tasks} tasks.
These tasks will be executed by {self.max_executors} parallel executors working through a task queue.

TASK BREAKDOWN STRATEGIES (Domain-Agnostic):

REMEMBER: You're creating {num_tasks} TASKS that will be executed by {self.max_executors} parallel executors.

**Task Granularity Guidelines**:
- Each task should represent 30min-2hrs of work
- Tasks can have dependencies (executors will handle the queue intelligently)
- Create enough tasks to keep all {self.max_executors} executors busy
- Break large components into smaller tasks for better parallelization

**Examples by Project Type**:

**Web Application** ({num_tasks} tasks):
- Database schema design
- User authentication API
- Product API endpoints
- Order management API
- Payment integration
- Frontend routing setup
- UI component library
- Page components (multiple tasks)
- Form validation
- API integration layer
- Unit tests
- Integration tests
- Deployment configuration

**Machine Learning** ({num_tasks} tasks):
- Data collection scripts
- Data cleaning pipeline
- Exploratory data analysis
- Feature engineering
- Data augmentation
- Model architecture design
- Training loop implementation
- Hyperparameter tuning setup
- Evaluation metrics
- Visualization scripts
- Model serialization
- Inference API
- Testing suite

**Game Development** ({num_tasks} tasks):
- Core engine setup
- Physics engine
- Collision detection
- Rendering pipeline
- Shader system
- Texture loading
- Audio engine
- Sound effect integration
- Input handling
- UI system
- Game state management
- Level design tools
- AI behaviors
- Multiplayer networking

**Multi-Service System** ({num_tasks} tasks):
- Service 1 implementation
- Service 2 implementation
- Service 3 implementation
- API Gateway
- Authentication service
- Database schema
- Message queue setup
- Service communication
- Frontend application
- Admin dashboard
- Monitoring setup
- Testing framework
- Documentation
- CI/CD pipeline

IMPORTANT:
- Analyze the ACTUAL requirements to determine appropriate task breakdown
- Don't force patterns - adapt to the domain (ML, game dev, mobile, data, web, etc.)
- Tasks should be parallelizable where possible
- Dependencies are OK - executors will handle task queue intelligently
- Focus on creating meaningful, substantial tasks

GUIDELINES:
1. Create exactly {num_tasks} tasks (not limited by executor count)
2. Each task should be substantial (30min-2hrs of work)
3. Tasks should be as parallel as possible, but dependencies are OK
4. Tasks will be executed by {self.max_executors} executors working through the queue
5. When an executor finishes, it picks up the next available task
6. Balance tasks to keep all executors busy throughout execution

OUTPUT REQUIRED:
Respond with a JSON object in this exact format:
```json
{{
  "tasks": [
    {{
      "id": "task_1",
      "name": "<concise task name>",
      "description": "<detailed description of what needs to be implemented>",
      "priority": <1-5, where 1 is highest priority>,
      "estimated_effort": "<low/medium/high>",
      "estimated_duration": "<e.g., 30min, 1hr, 2hrs>"
    }},
    {{
      "id": "task_2",
      "name": "...",
      ...
    }},
    ...create all {num_tasks} tasks
  ],
  "dependencies": {{
    "task_2": ["task_1"],
    "task_5": ["task_2", "task_3"],
    ...map out which tasks depend on others
  }},
  "execution_strategy": "<brief description of how tasks will be executed>",
  "notes": "<important notes about the plan, coordination needs, etc.>"
}}
```

IMPORTANT:
- Create exactly {num_tasks} tasks in the tasks array
- Number tasks sequentially (task_1, task_2, ..., task_{num_tasks})
- NO executor_id field (executors will pick tasks from queue dynamically)
- Dependencies show which tasks must wait for others to complete
- All {self.max_executors} executors will work through these tasks in parallel

Provide ONLY the JSON object, no additional text.
"""

        try:
            result = subprocess.run(
                [
                    "claude",
                    "--dangerously-skip-permissions",
                    "--print",
                    "-p", prompt
                ],
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": result.stdout,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "response": None,
                    "error": f"Claude CLI error: {result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "response": None,
                "error": "Claude API timeout (60 seconds)"
            }
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }

    def parse_plan_response(self, response: str, num_executors: int) -> Dict[str, Any]:
        """
        Parse Claude's plan generation response
        """
        try:
            # Extract JSON from response
            json_pattern = r'```json\s*\n(.*?)\n```'
            match = re.search(json_pattern, response, re.DOTALL)

            if match:
                json_str = match.group(1)
                plan_data = json.loads(json_str)
                return plan_data
            else:
                # Try to find JSON without code blocks
                json_pattern = r'\{.*?\}'
                match = re.search(json_pattern, response, re.DOTALL)
                if match:
                    plan_data = json.loads(match.group(0))
                    return plan_data

                raise ValueError("No JSON found in response")

        except Exception as e:
            self.log(f"  Error: Failed to parse Claude response: {str(e)}")
            raise ValueError(f"Failed to parse plan from Claude Code response: {str(e)}")

    def create_plan(self, num_tasks: int) -> Dict[str, Any]:
        """
        Create execution plan and break down into tasks using Claude Code
        """
        self.log("\n" + "="*80)
        self.log("STEP 2: CREATING EXECUTION PLAN (via Claude Code)")
        self.log("="*80)

        self.log(f"  Analyzing requirements: {self.requirements[:100]}...")
        self.log(f"  Creating {num_tasks} tasks for {self.max_executors} parallel executors...")
        self.log(f"  Execution model: Task queue with dynamic allocation")

        # Call Claude for intelligent plan generation
        api_response = self.call_claude_for_plan(num_tasks)

        if not api_response["success"]:
            error_msg = f"Claude API failed: {api_response['error']}"
            self.log(f"  ✗ Error: {error_msg}")
            raise RuntimeError(error_msg)

        plan_data = self.parse_plan_response(api_response["response"], num_tasks)

        # Build final plan
        plan = {
            "num_tasks": num_tasks,
            "executor_budget": self.max_executors,
            "execution_model": "task_queue",
            "tasks": plan_data.get("tasks", []),
            "dependencies": plan_data.get("dependencies", {}),
            "execution_strategy": plan_data.get("execution_strategy", "Parallel execution with task queue"),
            "notes": plan_data.get("notes", "")
        }

        self.log(f"  ✓ Created execution plan with {len(plan['tasks'])} tasks")
        self.log(f"  ✓ Executor budget: {self.max_executors} parallel executors")
        self.log(f"  ✓ Tasks per executor: ~{len(plan['tasks']) / self.max_executors:.1f} average")
        for i, task in enumerate(plan["tasks"], 1):
            self.log(f"    - Task {i}: {task['name']}")

        # Save plan to file
        plan_file = self.output_dir / "execution_plan.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)
        self.log(f"  ✓ Plan saved to {plan_file}")

        return plan
