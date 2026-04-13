## MODIFIED Requirements

### Requirement: Caste Allocation Strategy
The system SHALL allocate agent counts per caste based on configuration and adaptive feedback.

#### Scenario: Default allocation
- **WHEN** no specific allocation is configured
- **THEN** 5 ant forager agents are spawned (default `ant_count`)
- **AND** bee, termite, and wasp agents are spawned when their castes are implemented
- **NOTE** Current implementation supports ant agents only. Default `ant_count=5`.

#### Scenario: Custom allocation
- **WHEN** config specifies {"ants": 20, "bees": 10, "termites": 5, "wasps": 5}
- **THEN** exactly those counts are spawned
- **AND** enables user to tune for specific analysis types

#### Scenario: Ant count limits total launches
- **WHEN** `HiveConfig.ant_count` is set to `N`
- **THEN** the orchestrator launches exactly `N` ant exploration runs for that analysis phase unless adaptive logic deliberately changes the allocation
- **AND** `N` is not interpreted merely as a semaphore or concurrency cap

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

#### Scenario: Seed propagation reaches ant RNG
- **WHEN** analysis is launched with an explicit seed
- **THEN** the orchestrator derives ant RNG instances from that seed in a deterministic way
- **AND** repeated runs with the same seed produce the same local stochastic choices inside bichos

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

#### Scenario: Report includes accurate execution metrics
- **WHEN** report is generated
- **THEN** it includes: analysis duration, configured agent counts, token usage, coverage percentage
- **AND** token usage is derived from provider usage metadata rather than model-authored fields

#### Scenario: Agent count metadata reflects configured launches
- **WHEN** report metadata includes `agent_count`
- **THEN** the value reflects the number of agents the orchestrator intended to launch for that phase
- **AND** it does not vary only because more function nodes existed in the graph

#### Scenario: Outcome accounting remains explicit
- **WHEN** some launched agents fail, timeout, or complete successfully
- **THEN** the final report includes explicit completed and degraded agent accounting in addition to configured launch counts
- **AND** consumers can distinguish planned swarm size from observed execution outcome

### Requirement: Error Handling and Graceful Degradation
The system SHALL handle failures without crashing the entire analysis.

#### Scenario: Single agent failure doesn't stop swarm
- **WHEN** 1 ant agent crashes
- **THEN** other 9 ants continue working
- **AND** final report notes partial results with degraded_agents count
- **AND** coverage metrics are adjusted to reflect reduced agent count

#### Scenario: LLM API failure retries
- **WHEN** LLM API returns 429 (rate limit)
- **THEN** request is retried with exponential backoff (max 3 retries)
- **AND** agent pauses before retry

#### Scenario: Rate limiting across agent swarm
- **WHEN** multiple agents issue LLM API calls concurrently
- **THEN** an asyncio.Semaphore limits concurrent API calls
- **AND** the semaphore size is configurable independently from total agent count
- **AND** concurrency limiting does not redefine how many agents are launched

#### Scenario: Cache corruption recovery
- **WHEN** pheromone cache file is corrupted
- **THEN** cache is cleared and reinitialized
- **AND** analysis continues with fresh cache
