# Bee Scout Agent Specification

> **Implementation status: Planned.** This capability is gated on the Phase 6 go/no-go decision. The Ant Forager tracer bullet must validate the core ACO thesis before bee agents are built. Configuration values (model, TTL, thresholds) are defined by `HiveConfig` and `StigmergyConfig`; this spec references illustrative defaults that will be reconciled with the canonical config when implemented.

## ADDED Requirements

### Requirement: Waggle Dance Model
The system SHALL use structured Pydantic models to communicate performance analysis data between scout and forager bees.

#### Scenario: Scout reports function performance characteristics
- **WHEN** scout analyzes function "process_data()"
- **THEN** WaggleDance model contains function_name, estimated_complexity (Big-O string), anti_pattern_type, complexity_score (numeric 1-100 derived from Big-O class and function LOC), error (str | None)
- **AND** investigation_priority is calculated as complexity_score * (1 + anti_pattern_count)

#### Scenario: High complexity equals high investigation priority
- **WHEN** function has O(n²) complexity and 2 anti-patterns detected
- **THEN** investigation_priority reflects elevated concern
- **AND** more forager bees are recruited to analyze surrounding module
- **NOTE** Higher priority = worse performance characteristics = needs more investigation (inverted from bee biology where "profitability" means good food; here "priority" means problematic code)

### Requirement: Code Performance Analysis
The system SHALL identify performance anti-patterns and estimate computational complexity through static source code inspection.

#### Scenario: Detect algorithmic complexity
- **WHEN** scout analyzes function with nested loops over input collection
- **THEN** estimated_complexity is reported as O(n²) or higher
- **AND** anti_pattern_type is "nested_iteration"

#### Scenario: Detect N+1 query pattern
- **WHEN** scout finds a database query call inside a loop body
- **THEN** anti_pattern_type is "n_plus_one_query"
- **AND** complexity_score reflects the multiplicative cost

#### Scenario: Detect blocking I/O in async code
- **WHEN** scout finds synchronous I/O calls within an async function
- **THEN** anti_pattern_type is "blocking_io_in_async"
- **AND** performance pheromone with high intensity is deposited

### Requirement: Swarm Recruitment
The system SHALL allocate forager bees proportionally to module investigation_priority.

#### Scenario: Proportional allocation
- **WHEN** 3 modules have investigation_priority [100, 300, 600]
- **AND** total swarm size is 10 bees
- **THEN** allocation is [1, 3, 6] bees respectively
- **AND** module with most anti-patterns gets deepest analysis

#### Scenario: Minimum exploration for clean modules
- **WHEN** module has investigation_priority 0 (no anti-patterns found)
- **THEN** at least 1 bee is still allocated
- **AND** ensures coverage of all modules
- **NOTE** Remaining bees after floored proportional allocation are assigned round-robin to highest-priority modules

#### Scenario: Roulette wheel selection
- **WHEN** bee recruitment uses random.choices() with investigation_priority weights
- **THEN** higher priority increases selection probability
- **AND** maintains stochastic element for exploration

### Requirement: Agent Tool: probe_function
The system SHALL provide a tool for static performance analysis of source code.

#### Scenario: Probe returns WaggleDance
- **WHEN** probe_function("process_order") is called
- **THEN** WaggleDance object is returned with detected anti-patterns and complexity estimate
- **AND** result is validated by Pydantic schema

#### Scenario: Handle analysis failures gracefully
- **WHEN** function source cannot be parsed or analyzed
- **THEN** the `error` field of the WaggleDance result is populated with the failure description
- **AND** exception details are logged

### Requirement: Agent Tool: recruit_foragers
The system SHALL provide a tool for spawning additional bees to perform deeper analysis of hot modules.

#### Scenario: Recruit N foragers for module
- **WHEN** recruit_foragers("src/checkout/", count=5) is called
- **THEN** 5 new bee agents are spawned
- **AND** they analyze different functions within the module for additional anti-patterns

#### Scenario: Foragers deposit performance pheromones
- **WHEN** recruited foragers complete deep analysis
- **THEN** each deposits performance pheromone with anti-pattern data
- **AND** pheromone intensity reflects severity of bottleneck

### Requirement: Agent Tool: aggregate_results
The system SHALL provide a tool for aggregating waggle dance reports into a performance summary.

#### Scenario: Aggregate multiple scout reports
- **WHEN** 5 scouts return WaggleDance objects
- **THEN** aggregate_results() produces PerformanceReport
- **AND** report includes anti-pattern counts by type, complexity distribution, ranked bottlenecks

#### Scenario: Identify top 5 bottlenecks
- **WHEN** performance report is generated
- **THEN** functions are ranked by investigation_priority
- **AND** top 5 most problematic functions are highlighted

### Requirement: Scout Agent Configuration
The system SHALL configure bee agents with fast, cost-effective LLM models.

#### Scenario: Scout uses lightweight model
- **WHEN** scout agent is initialized
- **THEN** it uses `openai:gpt-4o-mini` (fast, cheap)
- **AND** system prompt instructs it to analyze code for performance anti-patterns

#### Scenario: Forager uses similar model
- **WHEN** forager bee is spawned for deep analysis
- **THEN** it uses same or lighter model
- **AND** minimizes cost overhead of LLM calls

### Requirement: False Positive Mitigation
The system SHALL reduce false performance findings through multi-bee confirmation and statistical validation.

#### Scenario: Minimum bee confirmations before reporting
- **WHEN** fewer than 2 bees independently flag the same anti-pattern in a function
- **THEN** no performance pheromone is deposited
- **AND** results are marked as "unconfirmed"

#### Scenario: Cross-bee agreement filter
- **WHEN** 3 out of 4 bees report the same anti_pattern_type for a function
- **THEN** the finding is confirmed with high confidence
- **AND** outlier disagreement is excluded from the report

#### Scenario: Minimum complexity threshold for pheromone deposition
- **WHEN** estimated complexity is O(1) or O(log n) with no anti-patterns
- **THEN** no performance pheromone is deposited
- **AND** function is considered healthy

### Requirement: Performance Pheromone Decay
The system SHALL use short TTL for performance pheromones to reflect changing codebase state.

#### Scenario: Performance pheromone TTL is 1 hour
- **WHEN** performance pheromone is deposited
- **THEN** it expires after 3600 seconds
- **AND** reflects current code state (not historical analysis)

#### Scenario: Rapid evaporation detects fixes
- **WHEN** anti-pattern is fixed in source code
- **THEN** pheromone intensity decays quickly
- **AND** bees reallocate to new bottlenecks within 1 hour

### Requirement: Parallel Execution
The system SHALL execute scout analyses in parallel for efficient coverage.

#### Scenario: 10 scouts analyze 10 modules simultaneously
- **WHEN** hive spawns 10 scout bees
- **THEN** they analyze different modules in parallel
- **AND** results are collected via asyncio.gather()

#### Scenario: Results aggregated at join node
- **WHEN** all scouts complete analysis
- **THEN** waggle dances are passed to join node
- **AND** recruitment decisions are made based on aggregated data
