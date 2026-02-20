# Tracer-Bullet Implementation Plan

> **Goal**: Build a thin, end-to-end vertical slice that proves the core architecture works. One pattern (Ant Forager), one coordination mechanism (stigmergy), one orchestration flow (spawn → explore → report). If the tracer bullet hits the target, we build out the remaining patterns. If it misses, we know before investing months.

## What Is a Tracer Bullet?

A tracer bullet is not a prototype (throwaway code) or a spike (research). It is **production-quality code for a narrow slice** of the system. Every layer is real, tested, and extensible. The remaining patterns (Bee, Termite, Wasp) plug into the same infrastructure.

## Architecture Slice

```
CLI: `bichos analyze /path/to/repo`
         │
         ▼
┌─────────────────────────┐
│  Hive Orchestrator      │  ← Minimal: Init → Split → Join → Report
│  (pydantic_graph)       │     Only spawns Ant agents
└────────────┬────────────┘
             │
    ┌────────▼────────┐
    │  Ant Forager    │  ← N agents via asyncio.gather()
    │  (PydanticAI)   │     ACO navigation + bug detection
    └────────┬────────┘
             │
    ┌────────▼────────┐    ┌──────────────────┐
    │ Stigmergy System│    │   Code Graph      │
    │ (diskcache)     │    │   (NetworkX)      │
    └─────────────────┘    └──────────────────┘
             ▲ read/write          ▲ read-only
             └──── Ant accesses ───┘
```

## What the Tracer Bullet Validates

| Question | How We Answer It |
|----------|-----------------|
| Does ACO-guided exploration find more bugs than heuristics alone? | Compare bug count: ACO vs complexity-only vs random baselines |
| Does pheromone reinforcement cause convergence? | Measure: do later ants visit buggy modules more? |
| Is diskcache fast enough for concurrent agents? | Benchmark: p95 read/write latency under 10 agents |
| Does PydanticAI + asyncio.gather() work for parallel agents? | Run 10 agents concurrently, no crashes |
| Are false positives manageable with confidence gating? | Measure precision on synthetic bugs |
| Is the token cost acceptable? | Track total tokens for a 5K LOC analysis |

## Phases

### Phase 0: Project Skeleton (Day 1)

**Deliverable**: Running `pip install -e .` works, `bichos --help` prints usage.

```
bichos/
├── pyproject.toml
├── src/
│   └── bichos/
│       ├── __init__.py
│       ├── cli.py                  # Click CLI entry point
│       ├── config.py               # HiveConfig Pydantic model
│       ├── stigmergy/
│       │   ├── __init__.py
│       │   ├── models.py           # Pheromone Pydantic schemas
│       │   └── cache.py            # PheromoneCache wrapping diskcache
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── builder.py          # AST → NetworkX code graph
│       │   └── models.py           # CodeGraph wrapper
│       ├── agents/
│       │   ├── __init__.py
│       │   └── ant/
│       │       ├── __init__.py
│       │       ├── agent.py        # PydanticAI Agent definition
│       │       ├── tools.py        # choose_next_function, report_bug
│       │       ├── aco.py          # ACO probability math
│       │       └── models.py       # AntDeps, BugReport
│       └── hive/
│           ├── __init__.py
│           ├── orchestrator.py     # pydantic_graph workflow
│           └── models.py           # SwarmState, AnalysisReport
└── tests/
    ├── conftest.py
    ├── fixtures/                    # Sample Python repos with known bugs
    │   ├── simple_bugs/            # 5 files, 3 known bugs
    │   └── medium_bugs/            # 20 files, 10 known bugs
    ├── test_stigmergy.py
    ├── test_graph.py
    ├── test_ant_aco.py
    ├── test_ant_agent.py
    └── test_orchestrator.py
```

Tasks:
- [ ] 0.1 Create directory structure
- [ ] 0.2 Write `pyproject.toml` with deps: pydantic-ai, diskcache, loguru, networkx, radon, click
- [ ] 0.3 Write minimal `cli.py` with Click: `bichos analyze <path>` and `bichos --version`
- [ ] 0.4 Write `config.py` with HiveConfig Pydantic model (agent_counts, aco params, model names)
- [ ] 0.5 Create test fixtures: `simple_bugs/` with 5 Python files containing 3 planted bugs
- [ ] 0.6 Configure Loguru with structured JSON logging

### Phase 1: Stigmergy System (Days 2-3)

**Deliverable**: Pheromone CRUD with TTL decay, fully tested.

Tasks:
- [ ] 1.1 Write `stigmergy/models.py`:
  - `Pheromone` base model (type, intensity 0-100, deposited_at, expires_at, schema_version, confidence)
  - `BugPheromone(Pheromone)` with severity, location, description
  - Validators: intensity capped at 100.0, severity 1-10
- [ ] 1.2 Write `stigmergy/cache.py`:
  - `PheromoneCache` class wrapping `diskcache.Cache`
  - `deposit(key, pheromone)` — stores with TTL
  - `read(key)` → `Pheromone | None`
  - `read_pattern(prefix)` → `list[Pheromone]` — iterate matching keys
  - `reinforce(key, delta_tau, rho)` — atomic read-modify-write via `transact()`
  - `evaporate_all(rho)` — apply decay to all pheromones
  - `heatmap()` → `dict[str, float]` — location → intensity
  - `clear()` — remove all entries
  - Session-isolated paths: `/tmp/bichos-{repo_hash}/`
- [ ] 1.3 Write `test_stigmergy.py`:
  - Test CRUD operations
  - Test TTL expiration (use short TTL + sleep)
  - Test reinforcement math: τ_new = (1-ρ)*τ_old + Δτ, capped at 100
  - Test concurrent access (spawn 10 asyncio tasks writing simultaneously)
  - Test heatmap generation
  - Property-based test: intensity always in [0, 100] after any sequence of operations

### Phase 2: Code Graph Builder (Days 3-4)

**Deliverable**: Parse Python repo into NetworkX graph with complexity metrics.

Tasks:
- [ ] 2.1 Write `graph/builder.py`:
  - `build_code_graph(repo_path: Path) -> CodeGraph` — walk .py files, parse AST
  - Extract functions and classes as nodes
  - Extract call relationships as edges (using AST Name/Attribute visitor)
  - Calculate cyclomatic complexity per function via `radon.complexity`
  - Store node metadata: name, file_path, line_number, complexity, loc
- [ ] 2.2 Write `graph/models.py`:
  - `CodeGraph` class wrapping `nx.DiGraph`
  - `get_neighbors(func_name) -> list[str]`
  - `get_complexity(func_name) -> float`
  - `get_entry_points() -> list[str]` — functions with no callers
  - `node_count` and `edge_count` properties
- [ ] 2.3 Write `test_graph.py`:
  - Test on `fixtures/simple_bugs/` — verify expected nodes and edges
  - Test complexity calculation matches radon directly
  - Test entry point detection
  - Test handling of empty/malformed files

### Phase 3: ACO Mathematics (Day 4)

**Deliverable**: Standalone ACO module with proven convergence properties.

Tasks:
- [ ] 3.1 Write `agents/ant/aco.py`:
  - `calculate_probabilities(neighbors, pheromones, complexities, alpha, beta) -> list[float]`
    - Implements: P_ij = (τ^α * η^β) / Σ(τ^α * η^β)
    - Returns normalized probability distribution
  - `select_next(neighbors, probabilities, rng) -> str`
    - Stochastic selection via `rng.choices()`
  - `calculate_reinforcement(severity: int) -> float`
    - Returns Δτ = severity * 5.0 (leaves headroom below intensity cap of 100 for multi-agent reinforcement)
- [ ] 3.2 Write `test_ant_aco.py`:
  - Property: probabilities sum to 1.0 (±0.0001) for any valid inputs
  - Property: intensity never exceeds 100.0 after reinforcement
  - Property: intensity never goes negative after evaporation
  - Test: higher pheromone → higher probability (with equal complexity)
  - Test: higher complexity → higher probability (with equal pheromone)
  - Test: deterministic with fixed seed
  - Test: edge case — single neighbor always selected

### Phase 4: Ant Forager Agent (Days 5-8)

**Deliverable**: Working PydanticAI agent that navigates code graph and reports bugs.

Tasks:
- [ ] 4.1 Write `agents/ant/models.py`:
  - `AntDeps` dataclass: pheromone_cache, code_graph, config, rng, llm_semaphore
  - `BugReport` Pydantic model: location, description, severity, confidence
  - `ExplorationResult` model: path_visited, bugs_found, tokens_used
- [ ] 4.2 Write `agents/ant/agent.py`:
  - Create `forager` PydanticAI Agent with:
    - `deps_type=AntDeps`
    - `output_type=ExplorationResult`
    - System prompt: "You are a Forager Ant..." (focused on finding bugs)
    - Model: configurable, default `openai:gpt-4o`
  - Function `run_ant(deps: AntDeps) -> ExplorationResult` — wraps agent.run()
- [ ] 4.3 Write `agents/ant/tools.py`:
  - `@forager.tool choose_next_function(ctx, current_function)` — ACO probability selection
  - `@forager.tool analyze_code(ctx, function_name)` — reads source, returns code snippet
  - `@forager.tool report_bug(ctx, location, description, severity, confidence)`:
    - If confidence >= threshold: deposit pheromone
    - If severity >= 3: deposit pheromone
    - Otherwise: log only
  - `@forager.tool get_pheromone_trail(ctx, module)` — read nearby pheromones
- [ ] 4.4 Write `test_ant_agent.py`:
  - Mock LLM responses (use PydanticAI test mode / `agent.override()`)
  - Test: agent calls choose_next_function and navigates graph
  - Test: agent deposits pheromone when bug found with sufficient confidence
  - Test: agent does NOT deposit pheromone when confidence < threshold
  - Test: agent respects max_path_depth limit
  - Integration test: run real agent on `fixtures/simple_bugs/` (requires API key, mark as slow)

### Phase 5: Minimal Hive Orchestrator (Days 9-10)

**Deliverable**: End-to-end flow: CLI → orchestrator → N ants → report.

Tasks:
- [ ] 5.1 Write `hive/models.py`:
  - `SwarmState` dataclass: code_graph, pheromone_cache, config, results, degraded_agents
  - `AnalysisReport` Pydantic model: bugs, summary_stats, pheromone_heatmap, metadata
- [ ] 5.2 Write `hive/orchestrator.py` using pydantic_graph stable API:
  - `InitNode(BaseNode)`: load config, build code graph, create cache → SplitNode
  - `SplitNode(BaseNode)`: spawn N ant agents via asyncio.gather(), semaphore-gated → JoinNode
  - `JoinNode(BaseNode)`: deduplicate bugs, aggregate stats → ReportNode
  - `ReportNode(BaseNode)`: generate AnalysisReport → End
  - Error handling: `asyncio.gather(return_exceptions=True)`, log failures, continue
  - Timeout: `asyncio.wait_for()` per agent
- [ ] 5.3 Wire `cli.py`:
  - `bichos analyze <path>` → creates graph, runs orchestrator, prints report
  - `bichos stats` → reads pheromone cache, prints heatmap
  - `--config` flag for custom YAML
  - `--agents N` override for ant count
  - `--seed N` for deterministic mode
- [ ] 5.4 Write `test_orchestrator.py`:
  - Test: InitNode builds graph and cache
  - Test: SplitNode spawns correct number of agents (mock)
  - Test: JoinNode deduplicates bugs with same location
  - Test: full pipeline on `fixtures/simple_bugs/` with mocked LLM
  - Test: agent failure doesn't crash swarm
  - Test: timeout is enforced

### Phase 6: Validation & Benchmark (Days 11-13)

**Deliverable**: Empirical evidence that ACO-guided exploration outperforms random.

**Prerequisites**: Phases 4-6 integration tests and all of Phase 6 require live LLM API calls. Ensure `OPENAI_API_KEY` is set. Tests requiring API keys MUST be marked `@pytest.mark.slow` and skipped gracefully when keys are absent.

Tasks:
- [ ] 6.1 Create `fixtures/medium_bugs/`: 20 Python files, 10 planted bugs of varying severity
  - Missing None checks (sev 6-7)
  - Unhandled exceptions (sev 5-6)
  - SQL injection patterns (sev 9)
  - Hardcoded credentials (sev 9)
  - Race condition patterns (sev 8)
  - Unused imports / dead code (sev 2-3, should NOT trigger pheromones)
- [ ] 6.2 Validate fixtures: peer-review planted bugs, verify no accidental real bugs in "clean" files, document ground truth in `fixtures/MANIFEST.md`
- [ ] 6.3 Create benchmark runner: `bichos benchmark` CLI command (or pytest suite) that automates all Phase 6 benchmarks with configurable seeds, modes, and output format
- [ ] 6.4 Run benchmark: ACO mode vs complexity-only vs random
  - ACO mode: normal operation (α=1.0, β=2.0) — pheromone memory + complexity heuristic
  - Complexity-only mode: α=0, β=2.0 — follow complexity heuristic, no pheromone memory
  - Random mode: α=0, β=0 — uniform random selection, no pheromone influence
  - Metrics: bugs found, iterations to first bug, precision, recall, token usage
  - Run each mode 10 times with different seeds, report mean ± std
  - Note: LLM non-determinism adds variance; N=10 provides better statistical power
- [ ] 6.5 Run benchmark: pheromone convergence
  - Track pheromone intensity over iterations
  - Verify: buggy modules accumulate pheromone, clean modules don't
  - Verify: later ants visit buggy modules more often than early ants
- [ ] 6.6 Run benchmark: cost analysis
  - Measure: total tokens, total cost for 5K LOC analysis
  - Compare: 5 ants vs 10 ants vs 20 ants (diminishing returns?)
- [ ] 6.7 Run benchmark: diskcache performance
  - Measure: p95 read/write latency under 10 concurrent agents
  - Verify: meets spec targets (read <10ms, write <50ms)
- [ ] 6.8 Write benchmark report with go/no-go criteria:
  - GO if: ACO finds ≥ 20% more bugs than complexity-only baseline on same token budget
  - GO if: precision > 50% (majority of reported bugs are real)
  - GO if: cost < $5 for 5K LOC analysis (tracer-bullet scope: ants only, not full swarm)
  - GO if: p95 latency meets targets
  - NO-GO otherwise: revisit architecture before building remaining patterns

## Go/No-Go Decision Point

After Phase 6, we have empirical data. Three outcomes:

### Green: ACO > Complexity-Only Baseline, Precision > 50%, Cost < $5/5K LOC
→ Proceed to build Bee, Termite, Wasp patterns using the same infrastructure.

### Yellow: Mixed results (some metrics pass, some fail)
→ Investigate. Tune ACO parameters. Consider if the biological metaphor needs simplification.

### Red: ACO ≈ Complexity-Only or Precision < 30%
→ Stop. The core thesis (pheromone memory adds value) is not validated.
→ **Rollback**: Archive tracer-bullet code as `experiments/tracer-bullet-v1/` for reference. Do not delete — the stigmergy, code graph, and agent infrastructure may be reusable even if ACO navigation is replaced with simpler multi-agent coordination (direct message-passing, round-robin, etc.).

## What Comes After (If Green)

The tracer bullet created all the infrastructure. Adding new patterns is incremental:

| Phase | What | Reuses | New Code |
|-------|------|--------|----------|
| Phase 7 | Bee Scout | stigmergy, orchestrator, CLI | bee agent, probe tools, WaggleDance model |
| Phase 8 | Termite Builder | stigmergy, code graph, orchestrator | termite agent, curvature tools, state machine |
| Phase 9 | Wasp Guard | stigmergy, orchestrator | wasp agent, security tools, quorum sensing |
| Phase 10 | Full Hive | all infrastructure | multi-caste SplitNode, combined reporting |
| Phase 11 | Polish | all | tuning CLI, config validation, docs |

## Timeline Summary

| Phase | Days | Cumulative | Deliverable |
|-------|------|-----------|-------------|
| 0: Skeleton | 1 | 1 | `pip install -e .` works |
| 1: Stigmergy | 2 | 3 | Pheromone CRUD tested |
| 2: Code Graph | 1.5 | 4.5 | AST → NetworkX tested |
| 3: ACO Math | 1 | 5.5 | Probability calculations proven |
| 4: Ant Agent | 3.5 | 8.5 | Working PydanticAI agent (extra day for prompt tuning) |
| 5: Orchestrator | 1.5 | 10 | End-to-end CLI → report |
| 6: Validation | 3 | 13 | Go/No-Go with data |
| **Total** | **~13 working days** | | **Validated or invalidated core thesis** |

> **Note on Phase 1/2/3 parallelism**: Phases 1, 2, and 3 can run concurrently after Phase 0, potentially reducing the critical path by ~2 days. The cumulative column assumes sequential execution as a conservative estimate.

## Dependencies

```
Phase 0 (Skeleton)
    ├── Phase 1 (Stigmergy) ────┐
    ├── Phase 2 (Code Graph) ───┼── Phase 4 (Ant Agent)
    └── Phase 3 (ACO Math) ─────┘         │
                                    Phase 5 (Orchestrator)
                                           │
                                    Phase 6 (Validation)
```

Phases 1, 2, and 3 can all run in parallel after Phase 0. Phase 3 (ACO math) is pure computation — its unit tests need no external dependencies. Only Phase 4 integrates all three. Phases 5 and 6 are sequential.
