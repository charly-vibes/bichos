# Design: Entomological Codebase Framework

## Context

This framework applies swarm intelligence principles from biology (specifically eusocial insects) to software quality assurance. The core insight is that complex global behaviors can emerge from simple local interactions between specialized agents, avoiding the need for centralized "God-mode" orchestrators.

Key biological concepts being digitalized:
- **Stigmergy**: Indirect coordination via environment modification (pheromone trails)
- **Division of Labor**: Specialized agent castes with distinct tools and prompts
- **Emergent Intelligence**: Global optimization from local interactions
- **Homeostasis**: Self-regulating systems through feedback loops

## Goals / Non-Goals

### Goals
- Implement all four insect-inspired agent patterns (Ant, Bee, Termite, Wasp)
- Create a type-safe, stigmergic coordination system using Pydantic
- Enable autonomous, adaptive codebase analysis without human intervention
- Provide observable swarm behavior through structured logging
- Build a general-purpose framework for analyzing any Python codebase
- Minimize LLM token usage through environment-based coordination

### Non-Goals
- Real-time monitoring (this is batch/CI analysis, not runtime monitoring)
- Distributed multi-machine swarms (single-machine only for v1)
- Non-Python language support (Python-only initially)
- Production code modification (read-only analysis, suggestions only)
- GUI/dashboard (CLI and logs only for v1)

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Hive Orchestrator                  │
│         (pydantic_graph workflow engine)            │
└─────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  Ant Forager  │  │  Bee Scout  │  │   Termite   │
│  (Bug Hunt)   │  │  (Perf Test)│  │  Builder    │
└───────┬───────┘  └──────┬──────┘  └──────┬──────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                ┌─────────▼─────────┐
                │ Stigmergy System  │
                │ (Pheromone Grid)  │
                │   [diskcache]     │
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │    Code Graph     │
                │    [NetworkX]     │
                └───────────────────┘
```

## Execution Model

All agent concurrency uses Python's `asyncio` event loop on a single thread. This is the foundational concurrency decision that affects all other components.

### Agent Execution
- Each agent run is an `asyncio.Task` created via `asyncio.gather()`
- The Hive Orchestrator's `SplitNode.run()` method calls `asyncio.gather(*agent_tasks)` to run all agents concurrently
- This uses the **stable** pydantic_graph API (class-based nodes), not the beta function-based API
- pydantic_graph provides the high-level workflow (Init -> Split -> Join -> Report); parallelism is plain asyncio inside a single node

### Shared State Concurrency
- All agents share a single `diskcache.Cache` instance passed via PydanticAI Deps
- diskcache provides built-in file-level locking for concurrent access (thread-safe and process-safe)
- Pheromone read-modify-write operations (reinforcement) use diskcache's `transact()` context manager for atomicity
- The NetworkX code graph is read-only during agent execution (built once during QueenNode init), so no locking needed

### LLM API Rate Limiting
- An `asyncio.Semaphore(max_concurrent_llm_calls)` gates all LLM API calls across the swarm
- Default: 10 concurrent calls (configurable via `HiveConfig.max_concurrent_llm_calls`)
- Prevents overwhelming provider rate limits when running 23+ agents
- Each agent acquires the semaphore before calling `agent.run()` and releases after

### Error Isolation
- Each agent task is wrapped in try/except within `asyncio.gather(return_exceptions=True)`
- Failed agents are logged with full traceback, marked as `degraded`, and excluded from final metrics
- The swarm continues with remaining agents; the report includes a `degraded_agents` count
- Agent timeout is enforced via `asyncio.wait_for(agent_task, timeout=config.agent_timeout)`

## Key Decisions

### Decision 1: diskcache over Redis for Pheromone Storage

**Rationale**:
- No external server dependency (user requirement)
- Pure Python implementation with TTL support
- Disk persistence for long-running analyses
- Simpler deployment (just `pip install diskcache`)

**Alternatives Considered**:
- Redis: Rejected due to external server requirement
- Plain Python dict: No TTL support, no persistence
- SQLite: More complex than needed, slower than diskcache

**Implementation**:
```python
from diskcache import Cache
cache = Cache('/tmp/bichos-pheromones')
cache.set('bug:path:hash123', {'severity': 9}, expire=604800)  # 7 days TTL
```

### Decision 2: Loguru over Pydantic Logfire for Observability

**Rationale**:
- Lightweight, zero-config structured logging
- No external service dependency
- Sufficient for tracing agent decisions
- Can be extended with OpenTelemetry later if needed

**Alternatives Considered**:
- Pydantic Logfire: Too heavyweight, requires external service
- Standard logging: Less structured, harder to trace swarm behavior
- Custom solution: Reinventing the wheel

**Implementation**:
```python
from loguru import logger
logger.add("bichos_{time}.log", rotation="100 MB",
           serialize=True, enqueue=True)
logger.bind(caste="ant", agent_id=123).info("Depositing pheromone")
```

### Decision 3: Pheromone Data Model

**Rationale**:
Different agent castes need different pheromone types with varying decay rates.

**Schema**:
```python
class Pheromone(BaseModel):
    type: Literal["bug", "curvature", "performance", "alert"]
    intensity: float = Field(ge=0.0, le=100.0)
    metadata: dict[str, Any]
    deposited_at: datetime
    expires_at: datetime

class BugPheromone(Pheromone):
    type: Literal["bug"] = "bug"
    severity: int = Field(ge=1, le=10)
    location: str  # file:line
    description: str
```

### Decision 4: ACO Probability Calculation

**Mathematical Model**:
```
P_ij = (τ_ij^α * η_ij^β) / Σ_k(τ_ik^α * η_ik^β)
```
Where:
- τ_ij = pheromone intensity (from cache)
- η_ij = heuristic visibility (cyclomatic complexity)
- α = 1.0 (pheromone weight)
- β = 2.0 (heuristic weight - favor complex code)

**Rationale**: Standard ACO formula from research literature, proven to converge to optimal paths.

### Decision 5: Agent Tool Architecture

**Rationale**: Each agent caste has specialized tools via PydanticAI's @agent.tool decorator.

**Ant Tools**:
- `choose_next_function(current: str) -> str`: ACO-based navigation
- `report_bug(location: str, severity: int)`: Pheromone deposition
- `analyze_code_path(path: list[str])`: Deep inspection

**Bee Tools**:
- `probe_endpoint(url: str) -> WaggleDance`: Latency measurement
- `recruit_foragers(endpoint: str, count: int)`: Load generation
- `aggregate_results(dances: list[WaggleDance])`: Performance report

**Termite Tools**:
- `measure_curvature(module: str) -> float`: Complexity analysis
- `propose_refactor(violation: ArchViolation)`: Smoothing suggestions
- `verify_structure(before: AST, after: AST)`: Validation

**Wasp Tools**:
- `analyze_hydrocarbon_profile(request: dict) -> SecurityVerdict`: Input validation
- `release_alarm(threat: SecurityVerdict)`: Alert broadcasting
- `block_intruder(ip: str)`: Defensive action (if configured)

### Decision 6: Code Graph Representation

**Rationale**: Use NetworkX directed graph to model call relationships.

**Schema**:
```python
# Nodes: functions/methods
graph.add_node("module.function",
               complexity=15,
               lines=45,
               last_modified="2024-01-01")

# Edges: calls
graph.add_edge("caller", "callee", weight=call_count)
```

**Traversal**: BFS/DFS for path exploration, strongly connected components for cycle detection.

### Decision 7: Hive Orchestrator Workflow

**Rationale**: Use pydantic_graph for stateful, multi-phase workflows.

**Phases**:
1. **Initialization**: Queen node spawns agent castes
2. **Parallel Execution**: Agents run asynchronously
3. **Aggregation**: Join node merges pheromone trails
4. **Decision**: Threshold checks for emergency mode
5. **Report Generation**: Final analysis output

**Graph Structure**:
```python
@dataclass
class InitNode(BaseNode):
    async def run(self, ctx: GraphRunContext) -> SplitNode:
        # Spawn ants, bees, termites, wasps
        return SplitNode()

@dataclass
class SplitNode(BaseNode):
    async def run(self, ctx: GraphRunContext) -> JoinNode:
        # Parallel agent execution
        await asyncio.gather(
            run_ants(), run_bees(), run_termites(), run_wasps()
        )
        return JoinNode()
```

### Decision 8: Scaling Strategy for Large Codebases

**Context**: V1 targets single-machine analysis of up to 100K LOC. Larger codebases (500K+ LOC) require different approaches.

**Rationale**: Design extensibility points for future distributed scaling without over-engineering v1.

#### Horizontal Scaling: Pheromone Grid Partitioning

**Problem**: Single diskcache instance becomes bottleneck at >100 concurrent agents.

**Solution**: Partition pheromone grid by module prefix.
```python
# V1: Single cache
cache = Cache('/tmp/bichos-pheromones')

# V2: Partitioned cache (future)
cache_auth = Cache('/tmp/bichos-pheromones/auth')
cache_api = Cache('/tmp/bichos-pheromones/api')
cache_db = Cache('/tmp/bichos-pheromones/db')

# Routing logic
def get_cache(pheromone_key: str) -> Cache:
    module = extract_module(pheromone_key)
    return partitions[module_hash(module) % num_partitions]
```

**Benefit**: Linear scaling up to N partitions (10x-100x throughput increase).

**Implementation Timeline**: V2 (post-initial release).

#### Vertical Scaling: Code Graph Subgraphs

**Problem**: 1M LOC codebase produces unwieldy graph (100K+ nodes).

**Solution**: Analyze per-module subgraphs independently.
```python
# V1: Full graph
graph = build_code_graph('/repo')  # All files

# V2: Modular analysis
subgraph_auth = build_code_graph('/repo/auth')
subgraph_api = build_code_graph('/repo/api')

# Run independent swarms per subgraph
results = await asyncio.gather(
    analyze_swarm(subgraph_auth),
    analyze_swarm(subgraph_api)
)
```

**Benefit**: Constant memory per module, embarrassingly parallel.

**Trade-off**: Miss cross-module bugs (e.g., auth → api call chain issues).

**Mitigation**: Optional "integration analysis" phase for module boundaries.

#### Distributed Swarm Execution

**Problem**: 100 agents × expensive models = cost/time prohibitive on single machine.

**Solution (V3 exploration)**: Distribute agents across machines.
```python
# Conceptual architecture (not v1)
# Machine 1: Run 50 ants
# Machine 2: Run 20 bees + 20 termites
# Machine 3: Run 10 wasps

# Shared state: Redis Cluster (instead of diskcache)
redis_cluster = RedisCluster(nodes=['host1:6379', 'host2:6379'])

# Agents read/write to distributed pheromone grid
await redis_cluster.set('bug:auth.py:42', pheromone, ex=604800)
```

**Benefit**: Scale to 1000s of agents for massive repos.

**Challenges**:
- Network latency for pheromone operations (10ms local → 50-200ms network)
- Requires infrastructure (Redis cluster, Kubernetes, etc.)
- Violates "no external dependencies" constraint

**Decision**: Defer to v3, only if demand exists.

#### Multi-Language Support Strategy

**Problem**: Python AST parser is language-specific. How to support TypeScript, Java, Go?

**Solution**: Abstract language parsing behind interface.
```python
# V1: Python-specific
from ast import parse as parse_python
tree = parse_python(code)

# V2: Language abstraction (Tree-sitter or LSP)
class LanguageParser(Protocol):
    def parse(self, code: str) -> CodeGraph: ...
    def get_complexity(self, node) -> int: ...
    def get_functions(self, tree) -> List[Function]: ...

# Implementations
python_parser = PythonParser()  # Current AST-based
typescript_parser = TreeSitterParser('typescript')
java_parser = LSPParser('jdtls')

# Select at runtime
parser = get_parser(file_extension)
graph = parser.parse(code)
```

**Benefit**: Language-agnostic agent logic, swappable parsers.

**Complexity**: Each language requires:
- Parser integration (Tree-sitter, LSP)
- Complexity metrics (adapt radon equivalents)
- Call graph extraction (language-specific)

**Implementation Timeline**: V2 (TypeScript support), V3+ (other languages).

#### Adaptive Agent Tuning

**Problem**: Manually tuning α, β, ρ is tedious. Can agents self-optimize?

**Solution (Research Direction)**: Reinforcement learning for parameter tuning.
```python
# Conceptual (not v1)
class AdaptiveACO:
    def __init__(self):
        self.alpha = 1.0
        self.beta = 2.0

    def tune(self, bug_detection_rate: float):
        # If low detection, increase exploration (lower alpha)
        if bug_detection_rate < 0.5:
            self.alpha *= 0.9
        # If high false positives, increase complexity bias (higher beta)
        if false_positive_rate > 0.3:
            self.beta *= 1.1
```

**Benefit**: Self-tuning system, better performance out-of-box.

**Challenges**:
- Requires fitness function (precision/recall on known bugs)
- Risk of overfitting to specific codebase
- Adds complexity to debugging

**Decision**: Exploration only, not v1 commitment.

#### Performance Optimization Roadmap

**Current Bottlenecks (Expected):**
1. LLM API latency: 2-10s per agent iteration
2. Pheromone disk I/O: 10-50ms per write
3. Code graph construction: 1-5s per 10K LOC
4. AST parsing: 0.1-1s per file

**Optimization Strategies:**

| Bottleneck | V1 Mitigation | V2+ Optimization |
|------------|---------------|------------------|
| LLM latency | Use faster models for non-critical agents (Bees = GPT-3.5) | Batch LLM requests, use local Llama models |
| Pheromone I/O | In-memory LRU cache layer | Redis or partitioned diskcache |
| Graph construction | Cache graph between runs (invalidate on file changes) | Incremental graph updates |
| AST parsing | Parallel parsing via multiprocessing | Cache ASTs, use Tree-sitter (faster than Python ast) |

**Target Performance (V2):**
- 100K LOC in < 30 minutes (vs V1: ~90 minutes)
- 1M LOC in < 4 hours (via partitioning)

## False Positive Mitigation Strategy

LLM-powered agents will produce false positives. Without mitigation, false pheromones pollute the grid and waste swarm attention. The framework addresses this at four levels:

### Level 1: Confidence Gating (Per-Agent)
- Each agent finding includes a `confidence` score (0.0-1.0)
- Pheromone deposition requires confidence >= `confidence_threshold` (default 0.5)
- Findings below threshold are logged but don't influence swarm navigation

### Level 2: Severity Threshold (Per-Agent)
- Bug severity < 3 (informational) does not deposit pheromones
- Performance latency below `latency_threshold` (default 100ms) does not deposit pheromones
- Curvature below `deposit_threshold` (default 5.0) does not deposit pheromones

### Level 3: Natural Decay (Stigmergy)
- Unconfirmed findings (deposited once, never reinforced) decay exponentially
- Half-life of ~7 iterations at default ρ=0.1 means isolated false positives vanish naturally
- Only findings confirmed by multiple agents accumulate significant pheromone intensity

### Level 4: Deterministic Validation (Hybrid)
- Termite proposals are validated against deterministic metrics (radon, NetworkX) not just LLM reasoning
- Wasp findings can optionally use quorum sensing (3+ models must agree)
- Bee measurements use statistical outlier rejection (>3σ excluded)

## Risks / Trade-offs

### Risk: Pheromone Parameter Sensitivity
- **Impact**: Wrong evaporation rates could cause convergence to suboptimal paths
- **Mitigation**: Make all parameters configurable, provide sensible defaults from research
- **Monitoring**: Log pheromone heatmaps to Loguru for visualization

### Risk: LLM Hallucination in Bug Detection
- **Impact**: False positives or missed bugs
- **Mitigation**: Quorum sensing (multiple agents must agree), Pydantic validation on outputs
- **Monitoring**: Track precision/recall metrics on known test cases

### Risk: Performance Scalability
- **Impact**: 100-agent swarm might be too slow on single machine
- **Mitigation**: Start with 10-agent default, make configurable
- **Monitoring**: Profile with cProfile, optimize hot paths

### Trade-off: Type Safety vs. Flexibility
- **Decision**: Favor type safety (Pydantic everywhere)
- **Rationale**: Reduces debugging time, prevents hallucinated data
- **Cost**: More boilerplate code for schemas

### Trade-off: In-Memory vs. Persistent Pheromones
- **Decision**: Disk-backed cache with in-memory LRU
- **Rationale**: Balance speed and persistence
- **Cost**: Slightly slower than pure in-memory

## Migration Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Project structure and dependencies
- [ ] Stigmergy system (diskcache + pheromone models)
- [ ] Code graph builder (NetworkX)
- [ ] Loguru configuration

### Phase 2: Ant Pattern Implementation (Week 2)
- [ ] Forager agent with ACO tools
- [ ] Bug pheromone system
- [ ] Sample codebase analysis

### Phase 3: Remaining Patterns (Week 3)
- [ ] Bee scout agent
- [ ] Termite builder agent
- [ ] Wasp guard agent

### Phase 4: Orchestration (Week 4)
- [ ] Hive orchestrator with pydantic_graph
- [ ] Multi-agent coordination
- [ ] Final report generation

### Phase 5: Testing & Dogfooding (Week 5)
- [ ] Unit tests for all components
- [ ] Integration tests on sample repos
- [ ] Dogfood: Analyze bichos itself
- [ ] Documentation and examples

### Rollback Plan
- If critical bugs found, disable specific agent castes via config
- Pheromone cache can be cleared without affecting code
- No production code modification means low rollback risk

## Open Questions

1. **Q**: Should we support multiple simultaneous codebase analyses?
   **A**: No for v1 - single codebase at a time keeps design simple

2. **Q**: How to handle non-Python dependencies in analyzed repos?
   **A**: Ignore for v1 - Python-only analysis

3. **Q**: Should agents be able to propose code changes or just report issues?
   **A**: Report only for v1 - safer, maintains read-only principle

4. **Q**: What's the minimum Python version to support?
   **A**: Python 3.11+ (for PydanticAI compatibility)

5. **Q**: How to distribute the framework?
   **A**: PyPI package with CLI entry point (`bichos analyze <path>`)

## Performance Targets

- Agent startup: < 1s
- Pheromone read: < 10ms
- Pheromone write: < 50ms
- Single agent iteration: < 30s (LLM dependent)
- 10-agent swarm on 10k LOC: < 10 minutes
- Memory usage: < 500MB for medium codebase

## Security Considerations

- No code execution from analyzed repos (AST only)
- LLM API keys stored in environment variables
- Pheromone cache isolated to `/tmp` or user-specified path
- Read-only file system access to analyzed codebase
- Wasp agents validate inputs but don't execute security actions by default
