# Ant Forager Agent Specification

## ADDED Requirements

### Requirement: ACO-Based Path Navigation
The system SHALL implement Ant Colony Optimization probability-based navigation for exploring code paths.

#### Scenario: Probabilistic function selection
- **WHEN** ant agent is at function "login()" with neighbors ["validate()", "encrypt()", "log()"]
- **AND** "validate()" has high pheromone (τ=80) and high complexity (η=25)
- **THEN** "validate()" has highest selection probability
- **AND** selection is stochastic (not deterministic)

#### Scenario: Unexplored path has baseline probability
- **WHEN** function "new_feature()" has no pheromone trail (τ=0.1 default)
- **AND** has moderate complexity (η=10)
- **THEN** it still has non-zero probability of selection
- **AND** enables exploration of new code paths

#### Scenario: ACO parameters affect exploration vs exploitation
- **WHEN** α (pheromone weight) is set to 1.0 and β (heuristic weight) is set to 2.0
- **THEN** heuristic information (complexity) is weighted twice as much as pheromone history
- **AND** favors exploring complex code over following known trails

### Requirement: Bug Detection and Reporting
The system SHALL detect potential bugs through code analysis and report them via pheromone deposition.

#### Scenario: Detect missing None check
- **WHEN** ant analyzes code path with potential None dereference
- **THEN** bug report is created with severity 7, location, and description
- **AND** pheromone is deposited with intensity = severity * 5

#### Scenario: Detect race condition
- **WHEN** ant finds unsynchronized access to shared state
- **THEN** bug report is created with severity 8
- **AND** alarm is logged to Loguru with caste="ant"

#### Scenario: False positive validation
- **WHEN** bug is detected with confidence < 70%
- **THEN** severity is reduced by 50%
- **AND** report is marked as "potential_issue" rather than "confirmed_bug"

### Requirement: Code Path Traversal
The system SHALL traverse the code graph using BFS/DFS strategies guided by pheromones.

#### Scenario: Start traversal from entry point
- **WHEN** analysis begins on module "main.py"
- **THEN** ant spawns at main() function
- **AND** begins exploration of call graph

#### Scenario: Depth-limited search
- **WHEN** ant has explored 50 functions (max depth reached)
- **THEN** ant returns to nest (reports findings)
- **AND** resets for new exploration path

#### Scenario: Avoid infinite loops in circular dependencies
- **WHEN** ant encounters already-visited function in current path
- **THEN** circular dependency is flagged as architectural issue
- **AND** ant backtracks to explore alternative path

### Requirement: Agent Tool: choose_next_function
The system SHALL provide a tool for ACO-based function selection.

#### Scenario: Tool returns valid neighbor
- **WHEN** choose_next_function("current_func") is called
- **THEN** one neighbor function from code graph is returned
- **AND** selection probability is based on ACO formula

#### Scenario: Tool returns RETURN_TO_NEST when no neighbors
- **WHEN** choose_next_function() is called on leaf function (no callees)
- **THEN** special value "RETURN_TO_NEST" is returned
- **AND** signals end of exploration path

#### Scenario: Tool accesses pheromone cache via Deps
- **WHEN** tool retrieves pheromone levels for neighbors
- **THEN** it uses ctx.deps.pheromone_cache.get_pheromone()
- **AND** defaults to 0.1 if no pheromone exists

### Requirement: Agent Tool: analyze_code_path
The system SHALL provide a tool for deep inspection of code execution paths.

#### Scenario: Analyze path for edge cases
- **WHEN** agent analyzes path ["login", "validate", "check_password"]
- **THEN** AST is parsed for each function
- **AND** edge cases like empty strings, None values are tested

#### Scenario: Detect unhandled exceptions
- **WHEN** code path contains operations that may raise exceptions
- **AND** no try-except block is present
- **THEN** potential bug is flagged with severity 6

### Requirement: Agent Tool: report_bug
The system SHALL provide a tool for depositing bug pheromones.

#### Scenario: Deposit bug pheromone with severity
- **WHEN** report_bug("auth.py:42", "Missing None check", severity=7) is called
- **THEN** pheromone with intensity 35.0 is deposited
- **AND** structured log entry is created

#### Scenario: Attract more ants to buggy area
- **WHEN** bug pheromone is deposited in module "auth"
- **THEN** other ants' probability of exploring "auth" increases
- **AND** swarm focuses on high-bug-density areas

### Requirement: Forager Agent Configuration
The system SHALL configure ant agents with appropriate LLM models and system prompts.

#### Scenario: Agent uses high-reasoning model
- **WHEN** forager agent is initialized
- **THEN** it uses `openai:gpt-4o` (or configured equivalent)
- **AND** system prompt instructs it to find bugs via path exploration

#### Scenario: Agent has access to code graph
- **WHEN** agent is spawned
- **THEN** Deps includes code_graph (NetworkX) and pheromone_cache (diskcache)
- **AND** agent can navigate and deposit pheromones

### Requirement: Swarm Coordination
The system SHALL spawn multiple ant agents that coordinate via pheromones without direct communication.

#### Scenario: 10 ants explore in parallel
- **WHEN** hive spawns 10 forager ants
- **THEN** they run asynchronously
- **AND** each ant deposits pheromones that influence other ants' navigation

#### Scenario: Emergent convergence on bugs
- **WHEN** multiple ants find bugs in same module
- **THEN** pheromone intensity accumulates
- **AND** later ants are attracted to high-pheromone areas

#### Scenario: Exploration vs exploitation balance
- **WHEN** some code paths have high pheromones (known bugs)
- **AND** some paths have no pheromones (unexplored)
- **THEN** probabilistic selection ensures both are visited
- **AND** system avoids local optima

### Requirement: False Positive Mitigation
The system SHALL reduce false positive bug reports through confidence thresholds and pheromone gating.

#### Scenario: Confidence threshold gates pheromone deposition
- **WHEN** bug is detected with confidence < 50%
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
- **WHEN** user sets `ant.confidence_threshold: 0.8` in config
- **THEN** only findings with >= 80% confidence deposit pheromones
- **AND** default is 0.5 (50%)

### Requirement: Performance Optimization
The system SHALL minimize LLM token usage through efficient context management.

#### Scenario: Token usage per iteration < 2000
- **WHEN** ant completes one iteration (choose + analyze + report)
- **THEN** total tokens consumed is less than 2000
- **AND** enables cost-effective swarm analysis

#### Scenario: Cache code complexity metrics
- **WHEN** cyclomatic complexity is calculated for a function
- **THEN** result is cached in code graph metadata
- **AND** not recalculated on subsequent ant visits
