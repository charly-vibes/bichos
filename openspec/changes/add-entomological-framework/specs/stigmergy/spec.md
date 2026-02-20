# Stigmergy System Specification

## ADDED Requirements

### Requirement: Pheromone Data Models
The system SHALL provide type-safe Pydantic models for all pheromone types used in agent coordination.

#### Scenario: Base pheromone model validation
- **WHEN** a pheromone is created with valid intensity value (0.0-100.0)
- **THEN** Pydantic validation passes and timestamps are auto-generated

#### Scenario: Bug pheromone with severity
- **WHEN** a bug pheromone is deposited with severity 9 and location "auth.py:42"
- **THEN** the pheromone type is "bug" and metadata includes severity and location

#### Scenario: Invalid pheromone intensity rejected
- **WHEN** a pheromone is created with intensity 150.0 (exceeds max)
- **THEN** Pydantic ValidationError is raised

### Requirement: Pheromone Cache Storage
The system SHALL use diskcache to store pheromones with automatic TTL-based expiration.

#### Scenario: Store and retrieve pheromone
- **WHEN** a pheromone is deposited with key "bug:path:hash123" and 7-day TTL
- **THEN** it can be retrieved within 7 days
- **AND** it automatically expires after 7 days

#### Scenario: Batch pheromone reads
- **WHEN** wildcard pattern "bug:path:*" is used to query pheromones
- **THEN** all matching pheromones are returned in a single operation

#### Scenario: Concurrent access safety
- **WHEN** multiple agents read/write pheromones simultaneously
- **THEN** no race conditions occur and cache integrity is maintained

### Requirement: Pheromone Decay Mathematics
The system SHALL implement Ant Colony Optimization pheromone update rules with evaporation and reinforcement.

#### Scenario: Evaporation reduces intensity
- **WHEN** a pheromone with intensity 100.0 undergoes decay with ρ=0.1
- **THEN** the new intensity is 90.0 (100.0 * (1 - 0.1))

#### Scenario: Reinforcement increases intensity
- **WHEN** a bug is found and Δτ=50.0 is deposited on existing pheromone (τ=60.0) with ρ=0.1
- **THEN** evaporation gives (1-0.1) × 60.0 = 54.0, plus reinforcement 54.0 + 50.0 = 104.0
- **AND** intensity is capped at max_intensity (100.0), so final value is 100.0

#### Scenario: Configurable evaporation rates per type
- **WHEN** bug pheromones have ρ=0.01 and performance pheromones have ρ=0.5
- **THEN** bug pheromones decay slowly (long memory) and performance pheromones decay quickly (short memory)

### Requirement: Pheromone Grid Operations
The system SHALL provide high-level operations for depositing, reading, and visualizing pheromones.

#### Scenario: Deposit pheromone to grid
- **WHEN** an agent deposits a bug pheromone at "src/auth.py:42"
- **THEN** the pheromone is stored in cache with appropriate TTL
- **AND** structured log entry is created with agent_id and pheromone type

#### Scenario: Read pheromone trail for navigation
- **WHEN** an agent queries pheromones for module "auth"
- **THEN** all related pheromones are returned sorted by intensity (descending)

#### Scenario: Generate pheromone heatmap
- **WHEN** heatmap statistics are requested
- **THEN** a dictionary of {location: intensity} is returned
- **AND** locations are ranked by total pheromone strength

### Requirement: TTL Configuration
The system SHALL use different TTL values for different pheromone types based on biological analogues.

#### Scenario: Bug pheromone long memory
- **WHEN** a bug pheromone is deposited
- **THEN** it has a default TTL of 7 days (604800 seconds)

#### Scenario: Performance pheromone short memory
- **WHEN** a performance pheromone is deposited
- **THEN** it has a default TTL of 1 hour (3600 seconds)

#### Scenario: Architecture pheromone medium memory
- **WHEN** a curvature pheromone is deposited
- **THEN** it has a default TTL of 30 days (2592000 seconds)

#### Scenario: Security alert urgent memory
- **WHEN** an alert pheromone is deposited
- **THEN** it has a default TTL of 24 hours (86400 seconds)

### Requirement: Cache Isolation and Cleanup
The system SHALL isolate pheromone caches per analysis session and provide cleanup utilities.

#### Scenario: Session-specific cache directory
- **WHEN** an analysis is started for repository "myproject"
- **THEN** pheromones are stored in `/tmp/bichos-myproject-{hash}/`
- **AND** cache does not conflict with other concurrent analyses

#### Scenario: Manual cache clearing
- **WHEN** user runs `bichos clear-cache` command
- **THEN** all expired pheromones are removed
- **AND** summary of cleared items is displayed

#### Scenario: Automatic eviction for memory limits
- **WHEN** cache size exceeds configured limit (default 100MB)
- **THEN** least-recently-used pheromones are evicted
- **AND** eviction event is logged

### Requirement: Observability Integration
The system SHALL log all pheromone operations to Loguru with structured metadata for tracing.

#### Scenario: Pheromone deposition logged
- **WHEN** an ant agent deposits a bug pheromone
- **THEN** a log entry is created with fields: agent_id, caste, pheromone_type, location, intensity, timestamp

#### Scenario: Pheromone read logged
- **WHEN** an agent queries pheromones
- **THEN** a log entry is created with fields: agent_id, query_pattern, result_count, timestamp

#### Scenario: Decay operation logged
- **WHEN** background evaporation task runs
- **THEN** a log entry summarizes: pheromones_affected, avg_decay_rate, timestamp

### Requirement: Concurrent Access Safety
The system SHALL ensure thread-safe and process-safe pheromone operations for multi-agent swarms.

#### Scenario: File-level locking for writes
- **WHEN** two agents attempt to write to same pheromone key simultaneously
- **THEN** diskcache file locking ensures writes are serialized
- **AND** no data corruption occurs

#### Scenario: Read-while-write consistency
- **WHEN** agent A reads pheromone while agent B is writing to it
- **THEN** agent A receives either old value or new value (not partial)
- **AND** no torn reads or invalid data structures

#### Scenario: Atomic pheromone updates
- **WHEN** pheromone reinforcement happens (read-modify-write)
- **THEN** operation is atomic (no lost updates)
- **AND** uses diskcache transactional operations

#### Scenario: Multi-process safety
- **WHEN** multiple bichos processes run on same codebase simultaneously
- **THEN** each uses isolated cache directory based on PID or session ID
- **AND** no cross-contamination of pheromones

#### Scenario: Deadlock prevention
- **WHEN** multiple agents acquire locks on different pheromones
- **THEN** locks are acquired in consistent order (sorted by key)
- **AND** no circular wait conditions

### Requirement: Deterministic Mode for Testing
The system SHALL provide deterministic execution mode for reproducible testing and debugging.

#### Scenario: Fixed random seed for ACO
- **WHEN** agent is initialized with `AntDeps(random_seed=42)`
- **THEN** all stochastic decisions (ACO path selection) are reproducible
- **AND** same codebase produces same exploration order

#### Scenario: Deterministic timestamp ordering
- **WHEN** deterministic mode is enabled
- **THEN** pheromone timestamps use monotonic counter instead of wall clock
- **AND** test assertions can verify exact pheromone sequences

#### Scenario: Reproducible bug reports
- **WHEN** bug is found in deterministic mode with seed=42
- **THEN** re-running with same seed finds same bug at same iteration
- **AND** enables debugging of intermittent issues

#### Scenario: Non-deterministic mode by default
- **WHEN** no random_seed is specified
- **THEN** system uses time-based random seed
- **AND** provides natural exploration variance

### Requirement: Pheromone Schema Versioning
The system SHALL version pheromone schemas to handle evolution and backward compatibility.

#### Scenario: Schema version in all pheromones
- **WHEN** a pheromone is created
- **THEN** it includes `schema_version: int = 1` field
- **AND** version is stored in cache alongside data

#### Scenario: Read mixed schema versions
- **WHEN** cache contains pheromones with versions [1, 1, 2, 2]
- **THEN** system reads all versions
- **AND** applies appropriate migrations to normalize to latest version

#### Scenario: Schema migration on read
- **WHEN** v1 pheromone is read and current version is v2
- **THEN** migration function `migrate_v1_to_v2()` is applied
- **AND** migrated pheromone is cached to avoid re-migration

#### Scenario: Reject future schemas
- **WHEN** pheromone has schema_version=5 but system only knows up to v3
- **THEN** pheromone is skipped with warning logged
- **AND** analysis continues with remaining pheromones

#### Scenario: Schema compatibility metadata
- **WHEN** schema version changes
- **THEN** `SCHEMA_CHANGELOG.md` documents breaking vs compatible changes
- **AND** migration functions are unit tested

### Requirement: ACO Algorithm Correctness
The system SHALL validate Ant Colony Optimization mathematics through property-based testing.

#### Scenario: Probability distribution sums to 1.0
- **WHEN** ACO calculates probabilities for N neighbors
- **THEN** sum of all probabilities equals 1.0 (±0.0001 for floating point)
- **AND** property holds for all N ∈ [1, 100]

#### Scenario: Pheromone reinforcement is bounded
- **WHEN** pheromone undergoes repeated reinforcement
- **THEN** intensity never exceeds max_intensity (100.0)
- **AND** intensity never goes negative

#### Scenario: Evaporation converges to zero
- **WHEN** pheromone with intensity=100 undergoes evaporation with ρ=0.1
- **AND** no reinforcement occurs
- **THEN** after sufficient iterations, intensity approaches 0
- **AND** decay follows exponential curve: τ(t) = τ₀ * (1-ρ)^t

#### Scenario: Pheromone influences selection probability
- **WHEN** two paths have equal heuristic (η₁ = η₂) but different pheromones (τ₁ = 90, τ₂ = 10)
- **THEN** path 1 has significantly higher selection probability
- **AND** ratio P₁/P₂ ≈ (90/10)^α = 9 (for α=1.0)

#### Scenario: Heuristic influences selection probability
- **WHEN** two paths have equal pheromone (τ₁ = τ₂ = 50) but different complexity (η₁ = 25, η₂ = 5)
- **THEN** complex path 1 has higher selection probability
- **AND** ratio P₁/P₂ ≈ (25/5)^β = 25 (for β=2.0)

### Requirement: Performance Benchmarking
The system SHALL meet defined performance targets for pheromone operations.

#### Scenario: Pheromone read latency < 10ms
- **WHEN** single pheromone is read from cache
- **THEN** operation completes in < 10 milliseconds (p95)
- **AND** measured via benchmark suite on reference hardware

#### Scenario: Pheromone write latency < 50ms
- **WHEN** single pheromone is written to cache
- **THEN** operation completes in < 50 milliseconds (p95)
- **AND** includes disk sync for durability

#### Scenario: Batch read performance
- **WHEN** 100 pheromones are read via wildcard pattern
- **THEN** batch operation completes in < 200ms
- **AND** is faster than 100 individual reads (which would be ~1000ms)

#### Scenario: Concurrent throughput
- **WHEN** 10 agents perform 10 ops/second each (100 ops/sec total)
- **THEN** all operations complete without timeout
- **AND** p99 latency remains < 100ms
