# Hive Orchestrator Specification

## ADDED Requirements

### Requirement: Graph-Based Workflow Orchestration
The system SHALL use pydantic_graph to coordinate multi-phase analysis workflows.

#### Scenario: Sequential phase execution
- **WHEN** analysis is initiated on codebase
- **THEN** QueenNode initializes resources
- **AND** transitions to SplitNode
- **AND** SplitNode spawns agents in parallel
- **AND** transitions to JoinNode
- **AND** JoinNode aggregates results
- **AND** transitions to ReportNode

#### Scenario: Parallel agent execution
- **WHEN** SplitNode is executed
- **THEN** ant, bee, termite, wasp agents run concurrently
- **AND** each operates independently via asyncio
- **AND** all complete before transition to JoinNode

### Requirement: Queen Node Initialization
The system SHALL initialize analysis resources and configuration via Queen node.

#### Scenario: Load configuration
- **WHEN** QueenNode runs
- **THEN** HiveConfig is loaded from YAML or defaults
- **AND** contains agent counts, pheromone parameters, LLM models

#### Scenario: Initialize code graph
- **WHEN** codebase path is provided
- **THEN** code graph is built from AST parsing
- **AND** stored in SwarmState for agent access

#### Scenario: Initialize pheromone cache
- **WHEN** analysis session starts
- **THEN** diskcache instance is created at configured path
- **AND** previous pheromones are loaded (if persistent)
- **OR** fresh cache is created (if new analysis)

### Requirement: Caste Allocation Strategy
The system SHALL allocate agent counts per caste based on configuration and adaptive feedback.

#### Scenario: Default allocation
- **WHEN** no specific allocation is configured
- **THEN** 10 ants, 5 bees, 5 termites, 3 wasps are spawned
- **AND** total swarm size is 23 agents

#### Scenario: Custom allocation
- **WHEN** config specifies {"ants": 20, "bees": 10, "termites": 5, "wasps": 5}
- **THEN** exactly those counts are spawned
- **AND** enables user to tune for specific analysis types

#### Scenario: Adaptive allocation based on findings
- **WHEN** many bugs are found early (high bug pheromones)
- **THEN** DecisionNode spawns additional ants
- **AND** swarm focuses on bug detection

### Requirement: Agent Spawning and Lifecycle
The system SHALL spawn agents with proper Deps injection and monitor health.

#### Scenario: Spawn agent with Deps
- **WHEN** ant agent is spawned
- **THEN** AntDeps is injected with code_graph, pheromone_cache, config
- **AND** agent has access to all required resources

#### Scenario: Agent failure recovery
- **WHEN** agent crashes with exception
- **THEN** exception is logged with agent_id and caste
- **AND** agent is marked as failed
- **AND** swarm continues with remaining agents

#### Scenario: Agent timeout handling
- **WHEN** agent exceeds timeout (default 5 minutes)
- **THEN** agent task is cancelled
- **AND** partial results are collected
- **AND** warning is logged

### Requirement: Result Aggregation
The system SHALL collect and merge results from all agent castes via Join node.

#### Scenario: Aggregate bug reports
- **WHEN** multiple ants report bugs
- **THEN** reports are deduplicated by location
- **AND** severity is averaged if multiple ants found same bug

#### Scenario: Aggregate performance metrics
- **WHEN** bees return WaggleDance objects
- **THEN** PerformanceReport is generated with ranked bottlenecks
- **AND** min/max/avg latencies are calculated

#### Scenario: Aggregate refactoring suggestions
- **WHEN** termites propose refactorings
- **THEN** suggestions are grouped by module
- **AND** ordered by curvature score (descending)

#### Scenario: Aggregate security findings
- **WHEN** wasps report vulnerabilities
- **THEN** findings are ranked by threat_level
- **AND** critical issues are highlighted

### Requirement: Feedback Loop and Adaptive Behavior
The system SHALL adjust swarm behavior based on intermediate findings via Decision node.

#### Scenario: Emergency mode for critical bugs
- **WHEN** critical_bug_count > 10
- **THEN** DecisionNode triggers "EMERGENCY_MODE"
- **AND** spawns 20 additional ants
- **AND** focuses swarm on high-pheromone areas

#### Scenario: Coverage check triggers re-exploration
- **WHEN** code coverage < 70%
- **THEN** DecisionNode spawns more ants with higher exploration parameter
- **AND** ensures broader code path coverage

#### Scenario: Performance bottleneck triggers bee recruitment
- **WHEN** > 5 endpoints have latency > 1000ms
- **THEN** DecisionNode spawns additional bees
- **AND** intensifies load testing

### Requirement: Final Report Generation
The system SHALL produce comprehensive AnalysisReport combining all findings.

#### Scenario: Report structure
- **WHEN** ReportNode executes
- **THEN** AnalysisReport contains:
  - **AND** summary statistics (total bugs, vulnerabilities, bottlenecks, refactorings)
  - **AND** detailed findings per caste
  - **AND** pheromone heatmap visualization
  - **AND** recommendations prioritized by severity

#### Scenario: Report output formats
- **WHEN** report is generated
- **THEN** it is available as JSON (machine-readable)
- **AND** as Markdown (human-readable)
- **AND** as HTML (web viewable)

#### Scenario: Report includes metrics
- **WHEN** report is generated
- **THEN** it includes: analysis duration, agent counts, token usage, coverage percentage
- **AND** enables performance tracking

### Requirement: Hive Configuration Model
The system SHALL use typed configuration for all hive parameters.

#### Scenario: HiveConfig validation
- **WHEN** config is loaded from YAML
- **THEN** Pydantic validates all fields
- **AND** raises ValidationError for invalid values

#### Scenario: Config includes all parameters
- **WHEN** HiveConfig is instantiated
- **THEN** it contains: agent_counts (dict), pheromone_params (evaporation rates), llm_models (per caste), analysis_timeout (seconds)

### Requirement: Swarm State Management
The system SHALL maintain global state accessible to all agents via GraphRunContext.

#### Scenario: SwarmState includes shared resources
- **WHEN** graph workflow accesses ctx.state
- **THEN** SwarmState contains: code_graph, pheromone_cache, hive_config, global_metrics

#### Scenario: State updates are thread-safe
- **WHEN** multiple agents update global metrics concurrently
- **THEN** no race conditions occur
- **AND** final metrics are accurate

### Requirement: Observability and Logging
The system SHALL log all orchestration events to Loguru with structured metadata.

#### Scenario: Log phase transitions
- **WHEN** graph transitions from SplitNode to JoinNode
- **THEN** log entry includes: phase_from, phase_to, timestamp, agent_counts

#### Scenario: Log agent spawns
- **WHEN** agent is spawned
- **THEN** log entry includes: caste, agent_id, model, timestamp

#### Scenario: Log aggregation results
- **WHEN** JoinNode aggregates results
- **THEN** log entry includes: total_bugs, total_vulnerabilities, total_bottlenecks, timestamp

### Requirement: Error Handling and Graceful Degradation
The system SHALL handle failures without crashing the entire analysis.

#### Scenario: Single agent failure doesn't stop swarm
- **WHEN** 1 ant agent crashes
- **THEN** other 9 ants continue working
- **AND** final report notes partial results

#### Scenario: LLM API failure retries
- **WHEN** LLM API returns 429 (rate limit)
- **THEN** request is retried with exponential backoff
- **AND** agent pauses before retry

#### Scenario: Cache corruption recovery
- **WHEN** pheromone cache file is corrupted
- **THEN** cache is cleared and reinitialized
- **AND** analysis continues with fresh cache

### Requirement: Performance Targets
The system SHALL meet defined performance benchmarks for analysis speed.

#### Scenario: Medium codebase (10k LOC) in < 10 minutes
- **WHEN** analysis is run on 10k LOC Python codebase
- **THEN** total duration is less than 600 seconds
- **AND** includes all agent castes

#### Scenario: Agent startup latency < 1 second
- **WHEN** single agent is spawned
- **THEN** time from spawn to first tool call is < 1 second

#### Scenario: Pheromone operations < 50ms
- **WHEN** pheromone read or write is performed
- **THEN** operation completes in < 50 milliseconds
- **AND** doesn't block agent iteration

### Requirement: CLI Integration
The system SHALL provide command-line interface for initiating hive analysis.

#### Scenario: Run analysis via CLI
- **WHEN** user runs `bichos analyze /path/to/repo`
- **THEN** hive orchestrator is initialized
- **AND** analysis begins with progress bar
- **AND** report is saved to `bichos-report.md`

#### Scenario: Custom config via CLI
- **WHEN** user runs `bichos analyze /repo --config custom.yaml`
- **THEN** custom config overrides defaults
- **AND** analysis runs with specified parameters

#### Scenario: View pheromone heatmap
- **WHEN** user runs `bichos stats`
- **THEN** pheromone statistics are displayed
- **AND** top 10 high-pheromone locations are shown
