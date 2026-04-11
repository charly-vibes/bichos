## MODIFIED Requirements

### Requirement: Agent Tool: choose_next_function
The system SHALL provide a tool for ACO-based function selection.

#### Scenario: Tool returns valid neighbor
- **WHEN** choose_next_function("current_func") is called
- **THEN** one neighbor function from code graph is returned
- **AND** selection probability is based on ACO formula

#### Scenario: Tool handles leaf function with no neighbors
- **WHEN** choose_next_function() is called on leaf function (no callees)
- **THEN** the current function is returned unchanged
- **AND** signals end of exploration path (no further traversal possible)

#### Scenario: Tool accesses pheromone cache via Deps
- **WHEN** tool retrieves pheromone levels for neighbors
- **THEN** it uses pheromone data from `ctx.deps.pheromone_cache`
- **AND** defaults to a non-zero baseline when no pheromone exists

### Requirement: Agent Tool: report_bug
The system SHALL provide a tool for depositing bug pheromones.

#### Scenario: Deposit bug pheromone with severity
- **WHEN** report_bug("auth.py:42", "Missing None check", severity=7) is called
- **THEN** pheromone is deposited with intensity proportional to severity and confidence
- **AND** structured log entry is created

#### Scenario: Confidence threshold gates deposition
- **WHEN** a finding is below the configured confidence threshold
- **THEN** the finding may still be returned in the exploration result
- **AND** no pheromone is deposited

### Requirement: False Positive Mitigation
The system SHALL reduce false positive bug reports through confidence thresholds and pheromone gating.

#### Scenario: Confidence threshold gates pheromone deposition
- **WHEN** bug is detected with confidence < confidence_threshold (default 0.7)
- **THEN** no pheromone is deposited
- **AND** finding is logged as "low_confidence" for review but does not attract other agents

#### Scenario: Minimum severity for pheromone deposition
- **WHEN** bug severity is < 3 (informational)
- **THEN** pheromone intensity is set to 0 (no deposition)
- **AND** finding is included in report but does not influence swarm navigation

#### Scenario: Pheromone decay naturally cleans false positives
- **WHEN** a false bug pheromone is deposited
- **AND** no other agents confirm the finding (no reinforcement)
- **THEN** pheromone decays to near-zero within half-life iterations
- **AND** swarm attention naturally moves away

#### Scenario: Configurable confidence threshold
- **WHEN** user sets `min_confidence: 0.8` in config
- **THEN** only findings with >= 80% confidence deposit pheromones
- **AND** default is 0.7 (70%)

### Requirement: Performance Optimization
The system SHALL minimize LLM token usage through efficient context management.

#### Scenario: Token usage per iteration < 2000
- **WHEN** ant completes one iteration (choose + analyze + report)
- **THEN** total tokens consumed is less than 2000
- **AND** enables cost-effective swarm analysis

#### Scenario: Exploration result records provider usage
- **WHEN** an ant run completes
- **THEN** `ExplorationResult.tokens_used` is populated from provider usage metadata associated with that run
- **AND** the value does not depend on the model inventing a token count in its structured output

#### Scenario: Cache code complexity metrics
- **WHEN** cyclomatic complexity is calculated for a function
- **THEN** result is cached in code graph metadata
- **AND** not recalculated on subsequent ant visits
