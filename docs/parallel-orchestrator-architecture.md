# Parallel Orchestrator Architecture

## System Overview

The Parallel Orchestrator is an intelligent system that uses AI to analyze requirements, creates N tasks, and executes them across multiple backends: Threading (local), Docker (containerized), SLURM (HPC), or AWS ParallelCluster (cloud HPC). The architecture supports horizontal scaling from a single machine to hundreds of compute nodes. All backends support AWS Bedrock for Claude AI inference.

## High-Level Architecture

```mermaid
graph TB
    subgraph Input["Input Phase"]
        REQ["User Requirements<br/>+ Backend Selection<br/>+ Executor Budget (M)"]
    end

    subgraph Orchestrator["Parallel Orchestrator"]
        CONFIG["Configuration<br/>• CLI parsing<br/>• Backend selection<br/>• Resource settings"]
        CA["Complexity Analyzer (AI)<br/>• Analyzes requirements<br/>• Determines N tasks"]
        TP["Task Planner (AI)<br/>• Creates N tasks<br/>• Maps dependencies"]
        BF["Backend Factory<br/>• Creates backend<br/>• Initializes state"]
    end

    subgraph Backends["Execution Backends"]
        TB["ThreadingBackend<br/>• In-memory state<br/>• Thread workers"]
        DB["DockerBackend<br/>• Container isolation<br/>• Parallel containers"]
        SB["SlurmBackend<br/>• File-based state<br/>• sbatch jobs"]
        AB["AWSBackend<br/>• S3-synced state<br/>• ParallelCluster"]
    end

    subgraph Execution["Execution Layer"]
        E1["Executor 1"]
        E2["Executor 2"]
        E3["Executor M"]
    end

    subgraph Output["Output Phase"]
        RA["Results Aggregator"]
        FILES["Generated Files"]
        METRICS["Execution Metrics"]
    end

    REQ --> CONFIG
    CONFIG --> CA
    CA -->|N Tasks| TP
    TP --> BF

    BF -->|threading| TB
    BF -->|docker| DB
    BF -->|slurm| SB
    BF -->|aws| AB

    TB --> E1
    TB --> E2
    TB --> E3

    DB --> E1
    DB --> E2
    DB --> E3

    SB --> E1
    SB --> E2
    SB --> E3

    AB --> E1
    AB --> E2
    AB --> E3

    E1 --> RA
    E2 --> RA
    E3 --> RA

    RA --> FILES
    RA --> METRICS

    classDef inputClass fill:#667eea,stroke:#5568d3,stroke-width:3px,color:#fff
    classDef orchestratorClass fill:#f093fb,stroke:#d678e8,stroke-width:3px,color:#fff
    classDef backendClass fill:#feca57,stroke:#ee5a24,stroke-width:3px,color:#000
    classDef executorClass fill:#4facfe,stroke:#3b8ccc,stroke-width:3px,color:#fff
    classDef outputClass fill:#43e97b,stroke:#38a169,stroke-width:3px,color:#fff

    class REQ inputClass
    class CONFIG,CA,TP,BF orchestratorClass
    class TB,DB,SB,AB backendClass
    class E1,E2,E3 executorClass
    class RA,FILES,METRICS outputClass
```

## Backend Architecture

```mermaid
classDiagram
    class ExecutionBackend {
        <<abstract>>
        +config: OrchestratorConfig
        +output_dir: Path
        +log: Callable
        +tasks: List
        +plan: Dict
        +initialize()
        +submit_tasks()
        +wait_for_completion()
        +get_task_status()
        +get_results()
        +mark_task_complete()
        +mark_task_failed()
        +can_execute_task()
        +get_completed_tasks()
        +get_in_progress_tasks()
        +cleanup()
        +get_backend_info()
    }

    class ThreadingBackend {
        +completed_tasks: Set
        +in_progress_tasks: Set
        +task_lock: Lock
        +results_lock: Lock
        +executor_threads: List
        +_executor_worker()
        +set_executor_function()
    }

    class SlurmBackend {
        +run_id: str
        +state_dir: Path
        +jobs_file: Path
        +tasks_file: Path
        +job_ids: Dict
        +retry_manager: RetryManager
        +slurm_config: SlurmConfig
        +_atomic_write_json()
        +_read_json_with_lock()
        +_submit_slurm_job()
        +_generate_job_script()
        +_monitor_jobs()
        +_check_completed_jobs()
        +_handle_failed_jobs()
    }

    class DockerBackend {
        +docker_image: str
        +network_name: str
        +use_bedrock: bool
        +bedrock_region: str
        +bedrock_model: str
        +planner_in_docker: bool
        +containers: Dict
        +_verify_docker()
        +_build_or_pull_image()
        +_create_network()
        +_start_container()
        +_monitor_containers()
        +_collect_container_results()
        +_run_planner_in_docker()
    }

    class AWSParallelClusterBackend {
        +cluster_name: str
        +region: str
        +s3_bucket: str
        +s3_base_path: str
        +_verify_aws_cli()
        +_verify_s3_access()
        +_s3_upload()
        +_s3_download()
        +_s3_sync_upload()
        +_s3_sync_download()
    }

    class RetryManager {
        +max_retries: int
        +base_delay: float
        +retry_counts: Dict
        +should_retry()
        +record_attempt()
        +get_delay()
    }

    ExecutionBackend <|-- ThreadingBackend
    ExecutionBackend <|-- DockerBackend
    ExecutionBackend <|-- SlurmBackend
    SlurmBackend <|-- AWSParallelClusterBackend
    SlurmBackend *-- RetryManager
```

## Configuration Architecture

```mermaid
classDiagram
    class OrchestratorConfig {
        +requirements: str
        +output_dir: str
        +max_executors: int
        +use_real_executors: bool
        +backend_type: str
        +docker: DockerConfig
        +slurm: SlurmConfig
        +aws: AWSConfig
        +retry: RetryConfig
        +get_output_dir()
    }

    class SlurmConfig {
        +enabled: bool
        +partition: str
        +time_limit: str
        +memory: str
        +cpus_per_task: int
        +gpus_per_task: int
        +gpu_partition: str
        +get_sbatch_args()
    }

    class AWSConfig {
        +enabled: bool
        +cluster_name: str
        +region: str
        +s3_bucket: str
        +s3_prefix: str
        +get_s3_path()
    }

    class DockerConfig {
        +enabled: bool
        +image: str
        +network: str
        +use_bedrock: bool
        +bedrock_region: str
        +bedrock_model: str
        +planner_in_docker: bool
        +aws_access_key_id: str
        +aws_secret_access_key: str
        +aws_session_token: str
    }

    class RetryConfig {
        +max_retries: int
        +retry_delay_seconds: float
        +exponential_backoff: bool
        +backoff_multiplier: float
    }

    OrchestratorConfig *-- DockerConfig
    OrchestratorConfig *-- SlurmConfig
    OrchestratorConfig *-- AWSConfig
    OrchestratorConfig *-- RetryConfig
```

## Threading Backend Flow

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant TB as ThreadingBackend
    participant TQ as Task Queue
    participant W1 as Worker 1
    participant W2 as Worker 2

    Orch->>TB: initialize()
    TB->>TB: Clear state sets

    Orch->>TB: submit_tasks(tasks, plan)
    TB->>TB: Store tasks and plan

    Orch->>TB: wait_for_completion(max_executors)

    TB->>W1: Spawn thread
    TB->>W2: Spawn thread

    par Worker Loop
        W1->>TQ: Check available task
        TQ-->>W1: Task 1 (deps satisfied)
        W1->>W1: Execute task
        W1->>TB: mark_task_complete()

        W2->>TQ: Check available task
        TQ-->>W2: Task 2 (deps satisfied)
        W2->>W2: Execute task
        W2->>TB: mark_task_complete()
    end

    W1->>TQ: Check available task
    TQ-->>W1: No tasks
    W1->>W1: Shutdown

    W2->>TQ: Check available task
    TQ-->>W2: No tasks
    W2->>W2: Shutdown

    TB-->>Orch: Execution complete
```

## Docker Backend Flow

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant DB as DockerBackend
    participant Docker as Docker Engine
    participant PC as Planner Container
    participant C1 as Executor Container 1
    participant C2 as Executor Container 2
    participant EA as ExecutorAgent
    participant Bedrock as AWS Bedrock

    Orch->>DB: initialize()
    DB->>Docker: Verify Docker running
    DB->>Docker: Create network po-network

    alt Planner in Docker
        Orch->>DB: Run planner in Docker
        DB->>Docker: Start planner container
        Docker->>PC: Mount outputs/planner volume
        PC->>PC: PlannerAgent.analyze_complexity()
        PC->>PC: PlannerAgent.create_plan()
        PC->>PC: Write planner_output.json
        PC-->>DB: Plan complete
        DB->>DB: Read plan from volume
    end

    Orch->>DB: submit_tasks(tasks, plan)
    DB->>DB: Store tasks and plan

    Orch->>DB: wait_for_completion(max_executors)

    par Parallel Container Execution
        DB->>Docker: Start container executor_0
        Docker->>C1: Mount volumes, pass env vars
        C1->>EA: Execute docker_executor.py

        DB->>Docker: Start container executor_1
        Docker->>C2: Mount volumes, pass env vars
        C2->>EA: Execute docker_executor.py
    end

    par Task Execution
        EA->>EA: Read task from /input
        EA->>EA: Execute task
        alt Use Bedrock
            EA->>Bedrock: Claude API call
            Bedrock-->>EA: Generated code
        else Use Anthropic API
            EA->>EA: Claude API call (direct)
        end
        EA->>EA: Write result to /output
    end

    loop Monitor Containers
        DB->>Docker: Check container status
        Docker-->>DB: Running/Exited
        DB->>DB: Read output volumes
    end

    C1-->>Docker: Exit
    C2-->>Docker: Exit

    DB->>DB: Collect all results
    DB->>Docker: Cleanup containers
    DB-->>Orch: Execution complete
```

## SLURM Backend Flow

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant SB as SlurmBackend
    participant FS as File System
    participant SLURM as SLURM Scheduler
    participant Node as Compute Node
    participant SE as slurm_executor.py

    Orch->>SB: initialize()
    SB->>FS: Create .slurm_state/
    SB->>FS: Write jobs.json, tasks.json

    Orch->>SB: submit_tasks(tasks, plan)
    SB->>FS: Write task definitions

    Orch->>SB: wait_for_completion()

    loop For each task
        SB->>SB: Generate job script
        SB->>FS: Write script to scripts/
        SB->>SLURM: sbatch script.sh
        SLURM-->>SB: Job ID
        SB->>FS: Update jobs.json
    end

    SLURM->>Node: Schedule job
    Node->>SE: Execute slurm_executor.py
    SE->>FS: Read task definition
    SE->>SE: Execute task
    SE->>FS: Write result to results/
    SE->>FS: Update tasks.json

    loop Monitor loop
        SB->>SLURM: squeue -u $USER
        SLURM-->>SB: Running jobs
        SB->>SLURM: sacct -j job_id
        SLURM-->>SB: Job status
        SB->>FS: Read results/
        SB->>SB: Update internal state
    end

    alt Job failed
        SB->>SB: Check retry count
        SB->>SLURM: Resubmit with backoff
    end

    SB-->>Orch: Execution complete
```

## AWS ParallelCluster Flow

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant AB as AWSBackend
    participant S3 as S3 Bucket
    participant FS as Local FS
    participant SLURM as SLURM
    participant Node as Compute Node

    Orch->>AB: initialize()
    AB->>AB: Verify AWS CLI
    AB->>S3: Verify bucket access
    AB->>FS: Create local state
    AB->>S3: Upload marker.json

    Orch->>AB: submit_tasks(tasks, plan)
    AB->>FS: Write task definitions
    AB->>S3: Sync task_definitions/
    AB->>S3: Sync state/

    Orch->>AB: wait_for_completion()

    loop Submit jobs
        AB->>AB: Generate script with S3 sync
        AB->>SLURM: sbatch script.sh
    end

    SLURM->>Node: Schedule job
    Node->>S3: Sync state from S3
    Node->>Node: Execute task
    Node->>FS: Write result locally
    Node->>S3: Sync results to S3

    loop Monitor loop
        AB->>S3: Sync results from S3
        AB->>S3: Sync state from S3
        AB->>AB: Check job status
    end

    AB->>S3: Final sync (results + output)
    AB-->>Orch: Execution complete
```

## State Management Comparison

```mermaid
graph LR
    subgraph Threading["Threading Backend"]
        TM["In-Memory"]
        TL["Thread Locks"]
        TM --> TL
    end

    subgraph Docker["Docker Backend"]
        DV["Volume Mounts"]
        DC["Container Isolation"]
        DE["Environment Vars"]
        DV --> DC
        DE --> DC
    end

    subgraph SLURM["SLURM Backend"]
        SF["File System"]
        SL["File Locks (fcntl)"]
        SA["Atomic Writes"]
        SF --> SL
        SF --> SA
    end

    subgraph AWS["AWS ParallelCluster"]
        AF["Local Files"]
        AS["S3 Bucket"]
        SYNC["Sync Operations"]
        AF <--> SYNC
        SYNC <--> AS
    end

    style Threading fill:#43e97b,color:#000
    style Docker fill:#feca57,color:#000
    style SLURM fill:#4facfe,color:#fff
    style AWS fill:#f093fb,color:#fff
```

## SLURM Job Script Generation

```mermaid
flowchart TD
    Task["Task Definition"] --> Gen["Generate Script"]

    Gen --> Header["SBATCH Header<br/>--job-name<br/>--partition<br/>--time<br/>--mem"]

    Config{"GPU<br/>Requested?"} --> |Yes| GPU["--gres=gpu:N<br/>--partition=gpu"]
    Config --> |No| NoGPU["CPU only"]

    Header --> Config
    GPU --> Deps
    NoGPU --> Deps

    Deps{"Has<br/>Dependencies?"} --> |Yes| DepFlag["--dependency=afterok:job_ids"]
    Deps --> |No| NoDep["No dependency flag"]

    DepFlag --> Body
    NoDep --> Body

    Body["Script Body<br/>• cd output_dir<br/>• python slurm_executor.py<br/>• --task-id<br/>• --state-dir"]

    AWS{"AWS<br/>Mode?"} --> |Yes| S3Sync["Add S3 sync<br/>• Before execution<br/>• After execution"]
    AWS --> |No| NoS3["Local only"]

    Body --> AWS
    S3Sync --> Script["Final Script"]
    NoS3 --> Script
```

## Retry Logic Flow

```mermaid
flowchart TD
    Start["Job Failed"] --> Check{"Retry Count<br/>< Max?"}

    Check -->|Yes| Record["Record Attempt"]
    Record --> Delay["Calculate Delay<br/>(exponential backoff)"]
    Delay --> Wait["Wait delay seconds"]
    Wait --> Reset["Reset task status"]
    Reset --> Resubmit["Resubmit job"]
    Resubmit --> Monitor["Monitor job"]
    Monitor --> Result{"Job<br/>Result?"}

    Result -->|Success| Done["Task Complete"]
    Result -->|Failed| Start

    Check -->|No| Final["Final Failure"]
    Final --> Log["Log failure details"]

    style Start fill:#ff6b6b,color:#fff
    style Done fill:#43e97b,color:#000
    style Final fill:#ff6b6b,color:#fff
```

## Parallel Execution Timeline

```mermaid
gantt
    title Execution Timeline: 6 Tasks, 3 Workers
    dateFormat X
    axisFormat %L

    section Sequential Baseline
    Task 1 :0, 5
    Task 2 :5, 5
    Task 3 :10, 5
    Task 4 :15, 5
    Task 5 :20, 5
    Task 6 :25, 5

    section Threading (3 Workers)
    Worker 1 - Task 1 :0, 5
    Worker 1 - Task 4 :5, 5
    Worker 2 - Task 2 :0, 5
    Worker 2 - Task 5 :5, 5
    Worker 3 - Task 3 :0, 5
    Worker 3 - Task 6 :5, 5

    section SLURM (3 Jobs)
    Job 1 - Task 1 :0, 5
    Job 1 - Task 4 :5, 5
    Job 2 - Task 2 :0, 5
    Job 2 - Task 5 :5, 5
    Job 3 - Task 3 :0, 5
    Job 3 - Task 6 :5, 5
```

## Component Interaction

```mermaid
graph LR
    subgraph "Orchestrator Core"
        O[Orchestrator<br/>Main Controller]
        C[Config<br/>CLI Parsing]
    end

    subgraph "AI Planning"
        CA[Complexity Analyzer]
        TP[Task Planner]
    end

    subgraph "Backend Layer"
        BF[Backend Factory]
        TB[ThreadingBackend]
        DB[DockerBackend]
        SB[SlurmBackend]
        AB[AWSBackend]
    end

    subgraph "Execution"
        DE[docker_executor.py]
        SE[slurm_executor.py]
        EA[ExecutorAgent]
    end

    subgraph "External Systems"
        DOCKER[Docker Engine]
        SLURM[SLURM Scheduler]
        S3[S3 Bucket]
        BEDROCK[AWS Bedrock]
        CLAUDE[Claude API]
    end

    C --> O
    O --> CA
    CA --> TP
    TP --> BF

    BF --> TB
    BF --> DB
    BF --> SB
    BF --> AB

    DB --> DOCKER
    DOCKER --> DE
    DE --> EA

    SB --> SLURM
    AB --> SLURM
    AB --> S3

    SLURM --> SE
    SE --> EA

    EA --> BEDROCK
    EA --> CLAUDE

    TB --> EA

    style O fill:#764ba2,color:#fff
    style BF fill:#f093fb,color:#fff
    style TB,DB,SB,AB fill:#feca57,color:#000
    style DOCKER,SLURM,S3,BEDROCK,CLAUDE fill:#4facfe,color:#fff
```

## Scaling Strategy

| Backend | Min Scale | Max Scale | State Sync | Best For |
|---------|-----------|-----------|------------|----------|
| **Threading** | 1 thread | ~20 threads | N/A (in-memory) | Local dev, testing |
| **Docker** | 1 container | ~50 containers | Volume mounts | Local parallel, isolation |
| **SLURM** | 1 job | 1000s jobs | File system | HPC clusters |
| **AWS ParallelCluster** | 1 node | 1000s nodes | S3 | Cloud HPC |

## File Structure

```
parallel-orchestrator/
├── orchestrator.py              # Main entry point
├── config.py                    # Configuration classes
├── planner_agent.py             # AI planning agent
├── executor_agent.py            # Task execution agent
├── docker_planner.py            # Docker planner script
├── docker_executor.py           # Docker executor script
├── slurm_executor.py            # SLURM node script
├── docker/                      # Docker image build
│   ├── Dockerfile               # Multi-stage container image
│   ├── build.sh                 # Build automation script
│   └── README.md                # Docker setup guide
└── backends/
    ├── __init__.py              # Exports
    ├── base.py                  # Abstract base
    ├── threading_backend.py     # Local threading
    ├── docker_backend.py        # Docker containers
    ├── slurm_backend.py         # SLURM HPC
    └── aws_parallel_cluster_backend.py  # AWS ParallelCluster
```

## Technology Stack

- **Python 3.9+**: Core implementation
- **Threading**: Local parallel execution
- **Docker**: Container isolation and parallel execution
- **Claude Code CLI**: AI code generation
- **AWS Bedrock**: Cloud AI inference (optional)
- **SLURM**: HPC job scheduling (sbatch, squeue, sacct)
- **AWS CLI**: S3 operations for cloud state
- **fcntl**: File locking for concurrent access
- **JSON**: Configuration and state storage

## Completed Features

1. ✅ Multi-backend architecture (Threading, Docker, SLURM, AWS ParallelCluster)
2. ✅ Docker backend with container isolation
3. ✅ Docker planner mode (planner runs in container)
4. ✅ AWS Bedrock integration (use AWS credentials instead of Anthropic API key)
5. ✅ GPU support with `--gres=gpu:N`
6. ✅ Auto-retry with exponential backoff
7. ✅ File-based state with atomic writes
8. ✅ S3 state synchronization for AWS backends
9. ✅ SLURM job dependency management
10. ✅ Configurable resource limits
11. ✅ Global and regional model support
12. ✅ Production-tested (100% success rate in real projects)

## Future Enhancements

1. **AWS Batch Backend**: Serverless batch job execution (planned)
2. **Kubernetes Backend**: Kubernetes-based execution
3. **Real-time Dashboard**: Web UI for monitoring
4. **Distributed Queue**: Redis/RabbitMQ integration
5. **Checkpoint/Resume**: Long-running job recovery
6. **Resource Estimation**: AI-based resource prediction
7. **Cost Optimization**: AWS Spot instance support

---

## Configuration Defaults

As of version 5.0, the following defaults are used:

- **Region**: `eu-central-1` (all AWS services)
- **Model**: `global.anthropic.claude-sonnet-4-5-20250929-v1:0` (works in all regions)
- **Max Executors**: 5 (configurable via `--max-executors`)
- **Docker Image**: `parallel-orchestrator:latest`
- **Docker Network**: `po-network`

## Real-World Performance

Based on production testing (January 2026):

| Metric | Result |
|--------|--------|
| **Success Rate** | 100% (10/10 tests) |
| **Avg Time per Project** | 3-4 minutes |
| **Files Generated** | 16-24 per project |
| **Lines of Code** | 5,000-10,000 per project |
| **Parallel Efficiency** | 3x speedup with 3 executors |

**Test Projects**:
- Contact form with validation (4 tasks, 16 files, 188s)
- Todo list app with local storage (6 tasks, 24 files, 195s)

## Related Documentation

- **[Main README](../README.md)** - Project overview and quick start
- **[Quick Start Guide](QUICKSTART.md)** - 5-minute setup guide
- **[Docker Backend](docker-backend.md)** - Docker execution details
- **[Docker with Bedrock](docker-bedrock-usage.md)** - AWS Bedrock setup
- **[Docker Planner](docker-planner.md)** - Planner containerization
- **[Bedrock Model Setup](bedrock-model-setup.md)** - Model configuration

---

**Last Updated:** January 2026
**Version:** 5.0 - Docker Backend with Bedrock Integration
