# Bee Scout Agent Specification

## ADDED Requirements

### Requirement: Waggle Dance Model
The system SHALL use structured Pydantic models to communicate performance data between scout and forager bees.

#### Scenario: Scout reports endpoint performance
- **WHEN** scout probes endpoint "/api/users"
- **THEN** WaggleDance model contains endpoint_url, average_latency_ms, throughput_rps, error_rate
- **AND** profitability is calculated as latency * (1 + error_rate)

#### Scenario: High latency equals high profitability
- **WHEN** endpoint has 500ms latency and 0.1 error rate
- **THEN** profitability is 550.0 (500 * 1.1)
- **AND** more forager bees are recruited to stress test this endpoint

### Requirement: Endpoint Probing
The system SHALL measure latency and throughput of code execution paths or API endpoints.

#### Scenario: Measure function execution time
- **WHEN** scout probes function "process_data()"
- **THEN** function is called 10 times
- **AND** average, min, max latencies are recorded

#### Scenario: Measure throughput under load
- **WHEN** scout generates 100 requests per second
- **THEN** actual throughput (successful requests) is measured
- **AND** error rate (failed requests / total) is calculated

#### Scenario: Detect latency spike
- **WHEN** endpoint latency exceeds 1000ms
- **THEN** performance pheromone with high intensity is deposited
- **AND** alarm is logged for investigation

### Requirement: Swarm Recruitment
The system SHALL allocate forager bees proportionally to endpoint profitability (latency).

#### Scenario: Proportional allocation
- **WHEN** 3 endpoints have profitability [100, 300, 600]
- **AND** total swarm size is 10 bees
- **THEN** allocation is [1, 3, 6] bees respectively
- **AND** slowest endpoint gets most load testing

#### Scenario: Minimum exploration for stable endpoints
- **WHEN** endpoint has profitability 0 (perfect performance)
- **THEN** at least 1 bee is still allocated
- **AND** ensures monitoring of all endpoints

#### Scenario: Roulette wheel selection
- **WHEN** bee recruitment uses random.choices() with profitability weights
- **THEN** higher profitability increases selection probability
- **AND** maintains stochastic element for exploration

### Requirement: Agent Tool: probe_endpoint
The system SHALL provide a tool for measuring endpoint performance.

#### Scenario: Probe returns WaggleDance
- **WHEN** probe_endpoint("process_order") is called
- **THEN** WaggleDance object is returned with measured metrics
- **AND** result is validated by Pydantic schema

#### Scenario: Handle probe failures gracefully
- **WHEN** endpoint raises exception during probe
- **THEN** error_rate is increased
- **AND** exception details are logged

### Requirement: Agent Tool: recruit_foragers
The system SHALL provide a tool for spawning additional load-testing bees.

#### Scenario: Recruit N foragers for endpoint
- **WHEN** recruit_foragers("/api/checkout", count=5) is called
- **THEN** 5 new bee agents are spawned
- **AND** they generate concurrent load on the endpoint

#### Scenario: Foragers deposit performance pheromones
- **WHEN** recruited foragers complete load test
- **THEN** each deposits performance pheromone with latency data
- **AND** pheromone intensity reflects severity of bottleneck

### Requirement: Agent Tool: aggregate_results
The system SHALL provide a tool for aggregating waggle dance reports into performance summary.

#### Scenario: Aggregate multiple scout reports
- **WHEN** 5 scouts return WaggleDance objects
- **THEN** aggregate_results() produces PerformanceReport
- **AND** report includes min/max/avg latencies, total throughput, ranked bottlenecks

#### Scenario: Identify top 5 bottlenecks
- **WHEN** performance report is generated
- **THEN** endpoints are ranked by profitability
- **AND** top 5 slowest endpoints are highlighted

### Requirement: Scout Agent Configuration
The system SHALL configure bee agents with fast, cost-effective LLM models.

#### Scenario: Scout uses lightweight model
- **WHEN** scout agent is initialized
- **THEN** it uses `openai:gpt-3.5-turbo` (fast, cheap)
- **AND** system prompt instructs it to measure performance

#### Scenario: Forager uses similar model
- **WHEN** forager bee is spawned for load testing
- **THEN** it uses same or faster model
- **AND** minimizes latency overhead of LLM calls

### Requirement: Performance Pheromone Decay
The system SHALL use short TTL for performance pheromones to reflect transient nature of latency.

#### Scenario: Performance pheromone TTL is 1 hour
- **WHEN** performance pheromone is deposited
- **THEN** it expires after 3600 seconds
- **AND** reflects real-time performance (not historical)

#### Scenario: Rapid evaporation detects improvements
- **WHEN** bottleneck is fixed
- **THEN** pheromone intensity decays quickly
- **AND** bees reallocate to new bottlenecks within 1 hour

### Requirement: Parallel Execution
The system SHALL execute scout probes in parallel for efficient coverage.

#### Scenario: 10 scouts probe 10 endpoints simultaneously
- **WHEN** hive spawns 10 scout bees
- **THEN** they probe different endpoints in parallel
- **AND** results are collected via asyncio.gather()

#### Scenario: Results aggregated at join node
- **WHEN** all scouts complete probing
- **THEN** waggle dances are passed to join node
- **AND** recruitment decisions are made based on aggregated data
