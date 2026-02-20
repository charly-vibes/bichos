# Implementation Tasks

> **NOTE**: The implementation follows a **tracer-bullet strategy**. See [tracer-bullet.md](./tracer-bullet.md) for the prioritized plan. Phases 0-6 of the tracer bullet (Stigmergy + Code Graph + Ant Forager + Orchestrator + Validation) are implemented first. The tasks below represent the full scope; only those covered by the tracer bullet are worked on initially. Remaining patterns (Bee, Termite, Wasp) are gated on the go/no-go decision at the end of Phase 6.

## 1. Project Foundation

- [ ] 1.1 Create directory structure (`src/bichos/`, `tests/`, `examples/`, `docs/`)
- [ ] 1.2 Create `pyproject.toml` with dependencies (PydanticAI, diskcache, Loguru, NetworkX, radon, Click)
- [ ] 1.3 Set up package `__init__.py` files with version and exports
- [ ] 1.4 Configure Loguru with structured logging and file rotation
- [ ] 1.5 Create `.gitignore` for Python artifacts and pheromone cache
- [ ] 1.6 Write initial `README.md` with quick start guide

## 2. Stigmergy System Implementation

- [ ] 2.1 Create `bichos/stigmergy/models.py` with Pydantic pheromone schemas
  - [ ] Base `Pheromone` model with type, intensity, timestamps
  - [ ] `BugPheromone` with severity and location
  - [ ] `CurvaturePheromone` with complexity score
  - [ ] `PerformancePheromone` with latency data
  - [ ] `AlertPheromone` with threat level
- [ ] 2.2 Create `bichos/stigmergy/cache.py` wrapping diskcache
  - [ ] `PheromoneCache` class with get/set/delete methods
  - [ ] TTL configuration per pheromone type
  - [ ] Decay function implementing `τ(t+1) = (1-ρ)τ(t) + Δτ`
  - [ ] Batch read/write for performance
- [ ] 2.3 Create `bichos/stigmergy/grid.py` for pheromone grid operations
  - [ ] `deposit_pheromone(key, pheromone)` method
  - [ ] `read_pheromones(pattern)` method with wildcard support
  - [ ] `evaporate()` background task for TTL management
  - [ ] Statistics/heatmap generation for observability
- [ ] 2.4 Write unit tests for stigmergy system
  - [ ] Test pheromone CRUD operations
  - [ ] Test TTL expiration
  - [ ] Test decay mathematics
  - [ ] Test concurrent access

## 3. Code Graph Builder

- [ ] 3.1 Create `bichos/graph/builder.py` for AST parsing
  - [ ] Parse Python files to extract functions/classes
  - [ ] Build call graph using AST analysis
  - [ ] Calculate cyclomatic complexity using radon
  - [ ] Store metadata (LOC, last modified, imports)
- [ ] 3.2 Create `bichos/graph/models.py` with NetworkX graph wrapper
  - [ ] `CodeGraph` class wrapping NetworkX DiGraph
  - [ ] Node attributes: name, complexity, lines, path
  - [ ] Edge attributes: call count, call type
  - [ ] Graph traversal methods (BFS, DFS, neighbors)
- [ ] 3.3 Create `bichos/graph/analysis.py` for graph algorithms
  - [ ] Find strongly connected components (circular dependencies)
  - [ ] Calculate betweenness centrality (critical functions)
  - [ ] Detect architectural violations (layer violations)
- [ ] 3.4 Write unit tests for graph builder
  - [ ] Test on sample Python files
  - [ ] Verify complexity calculations
  - [ ] Test cycle detection

## 4. Ant Forager Agent

- [ ] 4.1 Create `bichos/agents/ant/models.py` with ant-specific schemas
  - [ ] `AntDeps` class with cache, code graph, config
  - [ ] `PathExploration` result model
  - [ ] `BugReport` model
- [ ] 4.2 Create `bichos/agents/ant/agent.py` with PydanticAI agent
  - [ ] Define forager agent with system prompt
  - [ ] Set model to `openai:gpt-4o` (configurable)
- [ ] 4.3 Implement ant tools in `bichos/agents/ant/tools.py`
  - [ ] `@agent.tool choose_next_function()` with ACO probability
  - [ ] `@agent.tool analyze_code_path()` for deep inspection
  - [ ] `@agent.tool report_bug()` for pheromone deposition
  - [ ] `@agent.tool get_pheromone_trail()` for reading history
- [ ] 4.4 Create `bichos/agents/ant/aco.py` for ACO mathematics
  - [ ] Probability calculation: `P_ij = (τ^α * η^β) / Σ(τ^α * η^β)`
  - [ ] Pheromone reinforcement function
  - [ ] Stochastic selection with `random.choices()`
- [ ] 4.5 Write unit tests for ant agent
  - [ ] Test ACO probability calculations
  - [ ] Test bug detection on known issues
  - [ ] Test pheromone deposition logic
- [ ] 4.6 Create integration test: ant swarm on sample repo

## 5. Bee Scout Agent

- [ ] 5.1 Create `bichos/agents/bee/models.py` with bee-specific schemas
  - [ ] `BeeDeps` class with cache, HTTP client
  - [ ] `WaggleDance` model with endpoint, latency, throughput, error_rate
  - [ ] `PerformanceReport` aggregate model
- [ ] 5.2 Create `bichos/agents/bee/agent.py` with PydanticAI agent
  - [ ] Define scout agent with system prompt
  - [ ] Set model to `openai:gpt-3.5-turbo` (fast, cheap)
- [ ] 5.3 Implement bee tools in `bichos/agents/bee/tools.py`
  - [ ] `@agent.tool probe_endpoint()` for latency measurement
  - [ ] `@agent.tool recruit_foragers()` for load generation
  - [ ] `@agent.tool aggregate_results()` for waggle dance interpretation
- [ ] 5.4 Create `bichos/agents/bee/recruitment.py` for swarm allocation
  - [ ] Proportional allocation based on profitability
  - [ ] Roulette wheel selection algorithm
- [ ] 5.5 Write unit tests for bee agent
  - [ ] Test waggle dance probability
  - [ ] Test recruitment allocation
- [ ] 5.6 Create integration test: bee swarm on mock API

## 6. Termite Builder Agent

- [ ] 6.1 Create `bichos/agents/termite/models.py` with termite-specific schemas
  - [ ] `TermiteDeps` class with cache, code graph
  - [ ] `ArchitecturalViolation` model with type, severity, location
  - [ ] `TermiteState` model for graph state machine
  - [ ] `RefactoringPlan` model
- [ ] 6.2 Create `bichos/agents/termite/agent.py` with PydanticAI agent
  - [ ] Define builder agent with system prompt
  - [ ] Set model to `anthropic:claude-3-5-sonnet` (reasoning)
- [ ] 6.3 Implement termite tools in `bichos/agents/termite/tools.py`
  - [ ] `@agent.tool measure_curvature()` for complexity analysis
  - [ ] `@agent.tool detect_violations()` for architectural issues
  - [ ] `@agent.tool propose_refactor()` for smoothing suggestions
  - [ ] `@agent.tool verify_structure()` for validation
- [ ] 6.4 Create `bichos/agents/termite/graph.py` for pydantic_graph workflow
  - [ ] `InspectNode` for curvature sensing
  - [ ] `DecisionNode` for threshold checking
  - [ ] `BuildNode` for refactoring proposal
  - [ ] `VerifyNode` for validation
- [ ] 6.5 Write unit tests for termite agent
  - [ ] Test curvature measurement
  - [ ] Test violation detection
  - [ ] Test refactoring suggestions
- [ ] 6.6 Create integration test: termite swarm on messy codebase

## 7. Wasp Guard Agent

- [ ] 7.1 Create `bichos/agents/wasp/models.py` with wasp-specific schemas
  - [ ] `WaspDeps` class with cache, security config
  - [ ] `IncomingRequest` model for input validation
  - [ ] `SecurityVerdict` model with is_safe, threat_level, reasoning
  - [ ] `AlarmPheromone` model
- [ ] 7.2 Create `bichos/agents/wasp/agent.py` with PydanticAI agent
  - [ ] Define guard agent with system prompt
  - [ ] Set model to `google:gemini-1.5-pro` (large context)
- [ ] 7.3 Implement wasp tools in `bichos/agents/wasp/tools.py`
  - [ ] `@agent.tool analyze_hydrocarbon_profile()` for threat detection
  - [ ] `@agent.tool release_alarm_pheromone()` for alerting
  - [ ] `@agent.tool scan_for_vulnerabilities()` for code inspection
- [ ] 7.4 Create `bichos/agents/wasp/quorum.py` for multi-agent consensus
  - [ ] Spawn multiple guard agents with different models
  - [ ] Aggregate verdicts (require 3/5 agreement)
- [ ] 7.5 Write unit tests for wasp agent
  - [ ] Test threat detection on known vulnerabilities
  - [ ] Test alarm pheromone propagation
  - [ ] Test quorum sensing logic
- [ ] 7.6 Create integration test: wasp swarm on vulnerable code

## 8. Hive Orchestrator

- [ ] 8.1 Create `bichos/hive/models.py` with orchestrator schemas
  - [ ] `HiveConfig` model with agent counts, parameters
  - [ ] `SwarmState` model for global state
  - [ ] `AnalysisReport` aggregate result model
- [ ] 8.2 Create `bichos/hive/orchestrator.py` with pydantic_graph workflow
  - [ ] `QueenNode` for initialization
  - [ ] `SplitNode` for caste allocation
  - [ ] `ExecutionNode` for parallel agent spawning
  - [ ] `JoinNode` for result aggregation
  - [ ] `DecisionNode` for feedback loops
  - [ ] `ReportNode` for final output
- [ ] 8.3 Create `bichos/hive/spawner.py` for agent lifecycle
  - [ ] Spawn N agents of each caste
  - [ ] Configure agent Deps with shared resources
  - [ ] Monitor agent health and respawn if needed
- [ ] 8.4 Write unit tests for orchestrator
  - [ ] Test graph workflow execution
  - [ ] Test agent spawning
  - [ ] Test result aggregation
- [ ] 8.5 Create integration test: full hive on sample codebase

## 9. Utilities and Configuration

- [ ] 9.1 Create `bichos/utils/ast_parser.py` for AST utilities
  - [ ] Extract function signatures
  - [ ] Extract class hierarchies
  - [ ] Extract import dependencies
- [ ] 9.2 Create `bichos/utils/complexity.py` wrapping radon
  - [ ] Calculate cyclomatic complexity
  - [ ] Calculate Halstead metrics
  - [ ] Calculate maintainability index
- [ ] 9.3 Create `bichos/config/defaults.yaml` with default parameters
  - [ ] Pheromone evaporation rates (ρ values)
  - [ ] ACO parameters (α, β)
  - [ ] Agent counts per caste
  - [ ] LLM model selections
  - [ ] Logging levels
- [ ] 9.4 Create `bichos/config/loader.py` for YAML config loading
  - [ ] Load and validate configuration
  - [ ] Environment variable overrides
  - [ ] Merge with defaults
- [ ] 9.5 Write unit tests for utilities
  - [ ] Test AST parsing
  - [ ] Test complexity calculations
  - [ ] Test config loading

## 10. CLI Interface

- [ ] 10.1 Create `bichos/cli/main.py` with Click framework
  - [ ] `bichos analyze <path>` command
  - [ ] `bichos config` command to show/edit config
  - [ ] `bichos stats` command for pheromone statistics
  - [ ] `bichos clear-cache` command
- [ ] 10.2 Add progress bars and status updates
- [ ] 10.3 Create rich formatting for analysis reports
- [ ] 10.4 Write tests for CLI commands

## 11. Testing and Quality

- [ ] 11.1 Write unit tests for all modules (target 80% coverage)
  - [ ] Property-based tests for ACO probability calculations
  - [ ] Concurrency tests for pheromone operations
  - [ ] Schema versioning and migration tests
- [ ] 11.2 Create integration tests for each agent pattern
- [ ] 11.3 Create end-to-end test: full analysis pipeline
- [ ] 11.4 Set up pytest with coverage reporting
- [ ] 11.5 Create sample test codebases with known issues
- [ ] 11.6 Create benchmark dataset (10 open-source repos + synthetic bugs)
  - [ ] Download/setup flask, requests, pytest, sqlalchemy, numpy
  - [ ] Create synthetic-bugs-small/medium/large repos
  - [ ] Document known issues in each repo
- [ ] 11.7 Run competitive benchmarking
  - [ ] Baseline: pylint on all benchmark repos
  - [ ] Compare: GPT-4 single-agent on 3 repos
  - [ ] Compare: CrewAI equivalent on 1 repo
  - [ ] Generate comparison report with precision/recall/F1
- [ ] 11.8 Validate performance targets
  - [ ] Measure pheromone operation latencies (p95, p99)
  - [ ] Measure time-to-analysis for each codebase size
  - [ ] Measure token usage and costs
  - [ ] Generate performance report
- [ ] 11.9 Dogfood: Run bichos on itself and fix found issues
- [ ] 11.10 Set up pre-commit hooks (black, ruff, mypy)

## 12. Documentation

- [ ] 12.1 Update main `README.md` with:
  - [ ] Quick start guide
  - [ ] Installation instructions
  - [ ] Basic usage examples
  - [ ] Architecture overview diagram
- [ ] 12.2 Create `docs/CONCEPTS.md` explaining bio-mimetic patterns
- [ ] 12.3 Create `docs/AGENTS.md` documenting each agent caste
- [ ] 12.4 Create `docs/CONFIGURATION.md` for config options
- [ ] 12.5 Create `docs/API.md` for programmatic usage
- [ ] 12.6 Create `docs/TUNING.md` with parameter optimization guide
  - [ ] ACO parameter effects (α, β, ρ)
  - [ ] Swarm sizing recommendations by codebase size
  - [ ] Common tuning scenarios with solutions
  - [ ] Monitoring and iteration guide
  - [ ] Complete configuration file reference
- [ ] 12.7 Create `docs/COST_ANALYSIS.md` from cost-analysis.md
  - [ ] Token usage estimates per agent
  - [ ] Cost comparisons with alternatives
  - [ ] Benchmark strategy and dataset
  - [ ] ROI calculations
- [ ] 12.8 Add docstrings to all public APIs
- [ ] 12.9 Create `examples/` directory with:
  - [ ] Simple analysis example
  - [ ] Custom agent configuration
  - [ ] Pheromone visualization script
  - [ ] Multi-repo batch analysis
  - [ ] Parameter tuning experiment

## 13. Packaging and Distribution

- [ ] 13.1 Configure pyproject.toml for PyPI
  - [ ] Set package metadata (name, version, description)
  - [ ] Define entry points for CLI
  - [ ] Specify dependencies with version constraints
  - [ ] Add development dependencies
- [ ] 13.2 Create `LICENSE` file (choose appropriate license)
- [ ] 13.3 Create `CHANGELOG.md` for version history
- [ ] 13.4 Set up GitHub Actions for CI/CD
  - [ ] Run tests on PRs
  - [ ] Check code formatting
  - [ ] Publish to PyPI on releases
- [ ] 13.5 Test installation in clean environment
- [ ] 13.6 Publish v0.1.0 to PyPI

## Validation Checklist

After implementation, verify:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage ≥ 80%
- [ ] Dogfooding: Bichos analyzes itself without errors
- [ ] CLI works on sample codebases
- [ ] Pheromone decay works correctly over time
- [ ] Multi-agent coordination produces coherent results
- [ ] Documentation is complete and accurate
- [ ] Package installs cleanly via pip
- [ ] Performance meets targets (10k LOC in < 10 min)
