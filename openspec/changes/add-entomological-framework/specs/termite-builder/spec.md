# Termite Builder Agent Specification

## ADDED Requirements

### Requirement: Curvature-Based Architecture Analysis
The system SHALL detect architectural entropy ("roughness") by measuring code complexity and structural violations.

#### Scenario: Low curvature indicates clean architecture
- **WHEN** module has cyclomatic complexity < 10 and no circular dependencies
- **THEN** curvature score is low (< 5.0)
- **AND** no refactoring action is triggered

#### Scenario: High curvature indicates technical debt
- **WHEN** module has complexity > 20 or circular dependencies
- **THEN** curvature score is high (> 15.0)
- **AND** builder agent proposes refactoring

#### Scenario: Curvature pheromone deposited
- **WHEN** high curvature is detected in module "legacy_auth"
- **THEN** curvature pheromone with intensity = curvature_score is deposited
- **AND** attracts more termite builders to smooth the roughness

### Requirement: Architectural Violation Detection
The system SHALL detect common architectural anti-patterns and violations.

#### Scenario: Detect circular dependency
- **WHEN** module A imports B and B imports A
- **THEN** ArchitecturalViolation with type="circular_dependency" is created
- **AND** severity is set to 8 (high)

#### Scenario: Detect layer violation
- **WHEN** UI component directly imports database model
- **THEN** ArchitecturalViolation with type="layer_violation" is created
- **AND** violation includes expected layer (service) and actual layer (database)

#### Scenario: Detect God class
- **WHEN** class has > 500 lines or > 30 methods
- **THEN** ArchitecturalViolation with type="god_class" is created
- **AND** refactoring suggestion is to split by responsibility

### Requirement: State Machine for Refactoring Workflow
The system SHALL use pydantic_graph to implement a multi-step refactoring process.

#### Scenario: Inspect → Decision → Build → Verify flow
- **WHEN** termite agent is spawned on module "messy_code"
- **THEN** InspectNode analyzes curvature
- **AND** DecisionNode checks if curvature > threshold (10.0)
- **AND** if yes, transitions to BuildNode
- **AND** BuildNode proposes refactor
- **AND** VerifyNode validates proposed changes

#### Scenario: Low curvature transitions to Move
- **WHEN** DecisionNode finds curvature < 10.0
- **THEN** transitions to MoveNode (explore different module)
- **AND** no refactoring is proposed

### Requirement: Agent Tool: measure_curvature
The system SHALL provide a tool for calculating architectural entropy.

#### Scenario: Calculate curvature from complexity
- **WHEN** measure_curvature("auth.py") is called
- **THEN** cyclomatic complexity is calculated using radon
- **AND** circular dependencies are checked using NetworkX
- **AND** curvature score is returned as float

#### Scenario: Curvature includes multiple metrics
- **WHEN** curvature is measured
- **THEN** it combines: complexity + (circular_deps * 5) + (layer_violations * 3)
- **AND** provides holistic measure of architectural health

### Requirement: Agent Tool: detect_violations
The system SHALL provide a tool for finding architectural anti-patterns.

#### Scenario: Detect multiple violations in module
- **WHEN** detect_violations("legacy_auth.py") is called
- **THEN** list of ArchitecturalViolation objects is returned
- **AND** each includes type, severity, location, description

#### Scenario: Violations trigger pheromone deposition
- **WHEN** violations are detected
- **THEN** curvature pheromone is deposited for each
- **AND** intensity is proportional to violation severity

### Requirement: Agent Tool: propose_refactor
The system SHALL provide a tool for generating refactoring suggestions.

#### Scenario: Extract method refactoring
- **WHEN** function has complexity > 15
- **THEN** propose_refactor suggests "Extract Method" pattern
- **AND** identifies code blocks that can be extracted

#### Scenario: Move class refactoring
- **WHEN** layer violation is detected
- **THEN** propose_refactor suggests moving class to correct layer
- **AND** provides destination module path

#### Scenario: Refactoring plan includes validation
- **WHEN** refactoring is proposed
- **THEN** RefactoringPlan includes before/after AST comparison
- **AND** list of affected files and tests to run

### Requirement: Agent Tool: verify_structure
The system SHALL provide a tool for validating refactoring proposals against simulated ASTs. Since the system is read-only, the "after" AST is a hypothetical AST constructed from the proposed refactoring plan, not from actual code modification. The tool generates the after-AST by applying proposed transformations (extract method, move class) to a copy of the original AST in memory.

#### Scenario: Verify refactoring reduces complexity
- **WHEN** verify_structure(before_ast, simulated_after_ast) is called
- **THEN** complexity of simulated_after_ast is lower than before_ast
- **AND** verification passes

#### Scenario: Verify refactoring maintains structural integrity
- **WHEN** simulated after-AST is verified
- **THEN** all existing imports still resolve in the simulated structure
- **AND** no new syntax errors are introduced in the simulated AST
- **AND** no actual source files are modified (read-only)

#### Scenario: Verification failure aborts refactoring
- **WHEN** verification fails (complexity increased or structural errors)
- **THEN** refactoring proposal is rejected with reason
- **AND** agent backtracks to explore different module

### Requirement: Builder Agent Configuration
The system SHALL configure termite agents with high-reasoning LLM models.

#### Scenario: Agent uses reasoning model
- **WHEN** builder agent is initialized
- **THEN** it uses `anthropic:claude-3-5-sonnet` (high reasoning)
- **AND** system prompt instructs it to maintain architectural consistency

#### Scenario: Agent has access to code graph
- **WHEN** agent analyzes structure
- **THEN** Deps includes code_graph for dependency analysis
- **AND** pheromone_cache for curvature history

### Requirement: Emergent Architecture Improvement
The system SHALL enable multiple termite agents to collectively smooth architectural roughness.

#### Scenario: Termites converge on high-curvature modules
- **WHEN** multiple termites explore codebase
- **AND** some modules have high curvature pheromones
- **THEN** termites probabilistically visit high-curvature areas more often
- **AND** propose multiple refactorings for complex modules

#### Scenario: Local smoothing leads to global consistency
- **WHEN** termites apply local refactorings (fix circular deps)
- **AND** enforce local rules (low coupling, high cohesion)
- **THEN** overall architectural consistency improves
- **AND** curvature pheromones decay as issues are resolved

### Requirement: False Positive Mitigation
The system SHALL reduce false architectural findings through deterministic validation and threshold gating.

#### Scenario: Curvature threshold gates pheromone deposition
- **WHEN** measured curvature is below deposit_threshold (default 5.0)
- **THEN** no curvature pheromone is deposited
- **AND** module is considered architecturally healthy

#### Scenario: Deterministic metrics validate LLM suggestions
- **WHEN** termite proposes a refactoring based on LLM reasoning
- **THEN** the proposal is validated against deterministic metrics (radon complexity, NetworkX cycle detection)
- **AND** proposals not supported by metric evidence are downgraded to "suggestion" severity

#### Scenario: Duplicate detection across termites
- **WHEN** two termites propose the same refactoring for the same module
- **THEN** proposals are deduplicated at aggregation time
- **AND** confidence is increased for independently confirmed findings

### Requirement: Read-Only Analysis
The system SHALL only propose refactorings without modifying code.

#### Scenario: Refactoring suggestions are output only
- **WHEN** termite proposes refactoring
- **THEN** suggestion is written to report file
- **AND** no source code files are modified

#### Scenario: User reviews and applies refactorings
- **WHEN** analysis completes
- **THEN** all refactoring proposals are in AnalysisReport
- **AND** user can manually apply or use automated tools

### Requirement: Curvature Pheromone TTL
The system SHALL use medium-length TTL for curvature pheromones to reflect stable architectural properties.

#### Scenario: Curvature pheromone TTL is 30 days
- **WHEN** curvature pheromone is deposited
- **THEN** it expires after 2592000 seconds (30 days)
- **AND** reflects relatively stable architectural debt

#### Scenario: Long TTL enables trend analysis
- **WHEN** curvature is measured over multiple runs
- **THEN** pheromone history shows improvement or degradation trends
- **AND** helps prioritize refactoring efforts
