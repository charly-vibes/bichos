# Project Context

## Purpose

**bichos** (Spanish for "bugs/insects") is a bio-mimetic framework for agentic software quality assurance inspired by eusocial insect colonies. It implements swarm intelligence patterns using PydanticAI to perform autonomous codebase analysis, bug detection, architectural refactoring, performance optimization, and security auditing.

The framework organizes specialized AI agents into distinct "castes" modeled after ant, bee, termite, and wasp behaviors, coordinating through stigmergy (indirect communication via environment modification) rather than direct message-passing.

## Tech Stack

- **Language**: Python 3.11+
- **Agent Framework**: PydanticAI (type-safe agents with pydantic_graph orchestration)
- **LLM Providers**: OpenAI, Anthropic (Claude), Google (multi-model support)
- **State Management**: diskcache (in-memory/disk cache with TTL for pheromone grid)
- **Observability**: Loguru (structured logging and tracing)
- **Code Analysis**: AST parsing, radon (complexity), pylint/ruff (static analysis)
- **Package Management**: uv/pip, pyproject.toml

## Project Conventions

### Code Style
- Follow PEP 8 with black formatting (line length 100)
- Type hints required for all public APIs
- Use Pydantic models for all data structures
- Docstrings in Google style format

### Architecture Patterns
- **Stigmergic Coordination**: Agents communicate by modifying shared state (pheromone grid), not direct messaging
- **Caste-Based Organization**: Specialized agents (Ant, Bee, Termite, Wasp) with distinct tools and system prompts
- **Graph Orchestration**: Use pydantic_graph for multi-step workflows and state machines
- **Type Safety**: Leverage Pydantic schemas to prevent hallucinated data structures
- **Dependency Injection**: Use PydanticAI Deps for sharing resources (cache, LLM clients, code graphs)

### Testing Strategy
- Unit tests for individual agent tools and pheromone mechanics
- Integration tests for agent swarms on sample codebases
- Property-based testing for ACO (Ant Colony Optimization) algorithms
- Dogfooding: Use bichos agents to analyze the bichos codebase itself

### Git Workflow
- Main branch for stable releases
- Feature branches with descriptive names (e.g., `feat/ant-forager`, `fix/pheromone-decay`)
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- OpenSpec-driven development: proposals before implementation

## Domain Context

### Bio-Mimetic Patterns
The framework implements four primary insect-inspired patterns from the research literature:

1. **Ant Pattern (Foragers)**: Stochastic path exploration using pheromone trails for bug detection
2. **Termite Pattern (Builders)**: Curvature-based construction for architectural alignment
3. **Bee Pattern (Scouts)**: Waggle dance recruitment for performance testing
4. **Wasp Pattern (Guards)**: Chemical profiling and alarm pheromones for security

### Digital Pheromones
Pheromones are implemented as key-value pairs with Time-To-Live (TTL) decay:
- **Bug trails**: `bug:path:{hash}` → Severity, Bug ID (TTL: 7 days)
- **Curvature**: `arch:complexity:{module}` → Complexity Score (TTL: 30 days)
- **Performance**: `perf:endpoint:{url}` → Latency ms (TTL: 1 hour)
- **Security alerts**: `sec:alert:{ip}` → Threat Level (TTL: 24 hours)

### ACO Mathematics
Pheromone update follows standard Ant Colony Optimization:
```
τ_ij(t+1) = (1 - ρ) * τ_ij(t) + Δτ_ij
```
Where ρ is evaporation rate (0-1) and Δτ is reinforcement based on bug severity.

## Important Constraints

- **No External Infrastructure**: Must run without Redis server, Docker, or cloud services
- **Offline Capable**: Should work without internet (LLM API calls optional)
- **Single Machine**: Target deployment is local development environments
- **Token Efficiency**: Minimize LLM token usage through stigmergy (vs. verbose messaging)
- **Type Safety**: All agent inputs/outputs must be Pydantic-validated

## External Dependencies

### Required
- PydanticAI core framework
- diskcache for pheromone storage
- Loguru for observability
- AST parsing (built-in Python ast module)
- radon for cyclomatic complexity
- NetworkX for code graph representation
- Click for CLI entry point and subcommands

### Optional
- ruff/pylint for additional static analysis
- pytest for testing infrastructure
- OpenAI/Anthropic/Google SDKs for LLM access

## Performance Targets

- Agent startup latency: < 1 second
- Pheromone read/write: < 10ms
- Single agent iteration: < 30 seconds (depends on LLM)
- Swarm of 10 agents: Should complete medium codebase (~10k LOC) analysis in < 10 minutes

## Success Metrics

- Bug detection rate: Find issues missed by standard linters
- Architectural improvements: Reduce cyclomatic complexity by 20%
- Performance bottlenecks: Identify top 5 slowest code paths
- Security: Detect injection vulnerabilities and sanitization issues
