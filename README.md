# 🐜🐝🐛🐝 bichos

**Bio-Mimetic Framework for Agentic Software Quality Assurance**

> *bichos* (Spanish: "bugs/insects") - A swarm intelligence framework for autonomous codebase analysis inspired by eusocial insect colonies.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-Driven-green.svg)](./openspec/)
[![Status: Proposal Stage](https://img.shields.io/badge/status-proposal-orange.svg)](./openspec/changes/add-entomological-framework/)

## 🌟 Overview

**bichos** applies principles from eusocial insect colonies (ants, bees, termites, wasps) to software testing and analysis. Instead of a single "God-mode" agent, bichos deploys specialized agent swarms that coordinate through **stigmergy** (indirect communication via environment modification) to detect bugs, optimize performance, refactor architecture, and audit security.

### Why Bio-Mimetic Agents?

Modern software systems are too complex for traditional deterministic tools to fully comprehend. Bichos addresses this by:

- **Emergent Intelligence**: Complex global behaviors emerge from simple local interactions
- **Stigmergic Coordination**: Agents communicate via "digital pheromones" (80% less token usage than message-passing)
- **Adaptive Focus**: Swarms naturally converge on problematic areas through pheromone reinforcement
- **Fault Tolerance**: Single agent failures don't crash the entire analysis
- **Type Safety**: All agent I/O validated by Pydantic schemas to prevent hallucinations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│          Hive Orchestrator (pydantic_graph)         │
│           Coordinates multi-phase analysis          │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼───────┬────▼────┬───────▼───────┬──────────┐
│  🐜 Ant       │ 🐝 Bee  │  🐛 Termite   │ 🐝 Wasp  │
│  Forager      │ Scout   │  Builder      │  Guard   │
│  (Bug Hunt)   │ (Perf)  │  (Arch)       │ (Sec)    │
└───────┬───────┴────┬────┴───────┬───────┴──────┬───┘
        └────────────┼────────────┘              │
                     │                            │
            ┌────────▼────────┐         ┌────────▼────────┐
            │ Stigmergy System│         │   Code Graph    │
            │ (Pheromone Grid)│         │   (NetworkX)    │
            │   [diskcache]   │         │                 │
            └─────────────────┘         └─────────────────┘
```

### Four Agent Patterns

| Caste | Inspiration | Purpose | Key Technique |
|-------|-------------|---------|---------------|
| 🐜 **Ant (Forager)** | Ant Colony Optimization | Bug detection & edge case discovery | Pheromone-guided path exploration |
| 🐝 **Bee (Scout)** | Waggle Dance recruitment | Performance testing & bottleneck analysis | Proportional load allocation |
| 🐛 **Termite (Builder)** | Stigmergic construction | Architecture refactoring & consistency | Curvature-based smoothing |
| 🐝 **Wasp (Guard)** | Chemical profiling & defense | Security auditing & vulnerability detection | Quorum sensing consensus |

### Digital Pheromones

Agents coordinate via time-decaying "pheromone" signals stored in a shared cache:

```python
# Ant finds bug → deposits pheromone
pheromone = BugPheromone(
    intensity=70.0,  # severity * 10
    severity=7,
    location="auth.py:42",
    ttl=7_days
)

# Other ants smell pheromone → attracted to buggy area
# Pheromone decays: τ(t+1) = (1-ρ) * τ(t) + Δτ
```

## 📋 Project Status

**Current Phase:** Specification / Proposal

The framework design is complete and documented in the [OpenSpec proposal](./openspec/changes/add-entomological-framework/). Implementation will begin after proposal approval.

### Proposal Contents

- **[proposal.md](./openspec/changes/add-entomological-framework/proposal.md)** - Why, what, impact, success criteria
- **[design.md](./openspec/changes/add-entomological-framework/design.md)** - Technical decisions, architecture, trade-offs
- **[tasks.md](./openspec/changes/add-entomological-framework/tasks.md)** - 13 phases, 100+ implementation tasks
- **Specifications:**
  - [stigmergy](./openspec/changes/add-entomological-framework/specs/stigmergy/spec.md) - Pheromone system (8 requirements, 30+ scenarios)
  - [ant-forager](./openspec/changes/add-entomological-framework/specs/ant-forager/spec.md) - Bug detection (9 requirements)
  - [bee-scout](./openspec/changes/add-entomological-framework/specs/bee-scout/spec.md) - Performance testing (9 requirements)
  - [termite-builder](./openspec/changes/add-entomological-framework/specs/termite-builder/spec.md) - Architecture (11 requirements)
  - [wasp-guard](./openspec/changes/add-entomological-framework/specs/wasp-guard/spec.md) - Security (10 requirements)
  - [hive-orchestrator](./openspec/changes/add-entomological-framework/specs/hive-orchestrator/spec.md) - Orchestration (13 requirements)

### Validate Proposal

```bash
# Check proposal is valid
openspec validate add-entomological-framework --strict

# View full proposal
openspec show add-entomological-framework

# View specific capability spec
openspec show add-entomological-framework --type change
```

## 🔬 Research Foundation

This framework is based on peer-reviewed research on swarm intelligence and bio-mimetic systems. See [research.md](./research.md) for:

- Ant Colony Optimization (ACO) mathematics
- Stigmergy mechanisms in insect colonies
- Eusociality and division of labor
- Pheromone-based coordination
- 30+ cited papers from biology and computer science

## 🛠️ Planned Tech Stack

- **Agent Framework:** [PydanticAI](https://ai.pydantic.dev/) - Type-safe agents with graph orchestration
- **State Management:** [diskcache](https://pypi.org/project/diskcache/) - In-memory/disk cache with TTL for pheromones
- **Observability:** [Loguru](https://github.com/Delgan/loguru) - Structured logging and tracing
- **Code Analysis:** Python AST, [radon](https://radon.readthedocs.io/) (complexity), [NetworkX](https://networkx.org/) (graphs)
- **LLM Providers:** OpenAI (GPT-4), Anthropic (Claude), Google (Gemini)

## 🚀 Planned Usage

*Note: Implementation pending. This shows intended API.*

### CLI

```bash
# Install
pip install bichos

# Analyze codebase
bichos analyze /path/to/repo

# Custom configuration
bichos analyze /repo --config swarm.yaml

# View pheromone statistics
bichos stats

# Clear pheromone cache
bichos clear-cache
```

### Programmatic

```python
from bichos import Hive, HiveConfig

# Configure swarm
config = HiveConfig(
    agent_counts={"ants": 20, "bees": 10, "termites": 5, "wasps": 3},
    pheromone_decay_rate=0.1,
    models={"ant": "openai:gpt-4", "bee": "openai:gpt-3.5-turbo"}
)

# Run analysis
hive = Hive(config)
report = await hive.analyze("/path/to/repo")

# Access findings
print(f"Bugs found: {len(report.bugs)}")
print(f"Vulnerabilities: {len(report.security_issues)}")
print(f"Refactorings: {len(report.architecture_suggestions)}")
```

## 📊 Performance Targets

- **Agent Startup:** < 1 second
- **Pheromone Operations:** < 10ms read, < 50ms write
- **Medium Codebase (10k LOC):** < 10 minutes with 23-agent swarm
- **Token Efficiency:** 80% reduction vs. message-passing coordination

## 🤝 Contributing

This project follows OpenSpec-driven development:

1. **Proposals First:** All changes start with OpenSpec proposals in `openspec/changes/`
2. **Validate Strictly:** Use `openspec validate --strict` before submission
3. **Type Safety:** All code uses Pydantic models and type hints
4. **Dogfooding:** The framework will analyze itself

See [openspec/AGENTS.md](./openspec/AGENTS.md) for detailed workflow.

## 📖 Documentation

- **Research:** [research.md](./research.md) - Theoretical foundation and bio-mimetic patterns
- **FAQ:** [docs/FAQ.md](./docs/FAQ.md) - Frequently Asked Questions
- **OpenSpec:** [openspec/](./openspec/) - Specifications and change proposals
- **Project Context:** [openspec/project.md](./openspec/project.md) - Conventions and constraints

## 📜 License

[To be determined - see LICENSE file when added]

## 🙏 Acknowledgments

- Research inspired by pioneering work on swarm intelligence, ACO, and stigmergy
- Built with [PydanticAI](https://ai.pydantic.dev/) from the Pydantic team
- Bio-mimetic patterns from eusocial insect research

---

**Status:** 🟠 Proposal Phase - Implementation starts after approval

**Questions?** Check the [FAQ](./docs/FAQ.md), [research.md](./research.md), or open an issue for discussion.


---

## A note on authorship

All the code in this repository was generated by a large language model. This is not a confession, nor an apology. It's a fact, like the one that says water boils at a hundred degrees at sea level: neutral, technical, and with consequences one discovers later.

What the human did is what tends to happen before and after things come into existence: thinking. Reviewing requirements, arguing about edge cases, understanding what needs to be built and why, deciding how the system should behave when reality —which is capricious and does not read documentation— confronts it with situations nobody anticipated. The hours of planning, of design, of reading specifications until exhaustion dissolves the boundary between understanding and hallucination.

The LLM writes. The human knows what it should say.

There is a distinction, even if looking at the commit history makes it hard to find. The distinction is that a machine can produce correct code without understanding anything, the same way a calculator can solve an integral without knowing what time is. Understanding what that integral is *for*, whether it actually solves the problem, whether the problem was the right problem to begin with — that remains human territory. For now.

*[Leer en español](https://charly-vibes.github.io/charly-vibes/)*
