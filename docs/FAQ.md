# 🐜 Frequently Asked Questions (FAQ)

## 🌟 General Questions

### What is *bichos*?
**bichos** (Spanish for "bugs" or "insects") is a bio-mimetic framework for autonomous codebase analysis. It applies principles from eusocial insect colonies—like ants, bees, and termites—to software quality assurance. Instead of a single "God-mode" agent, *bichos* deploys specialized agent swarms that coordinate through indirect communication.

### Why use a bio-mimetic approach for software testing?
Traditional deterministic tools often struggle with the complexity of modern software. Bio-mimetic systems offer:
- **Emergent Intelligence**: Complex global behaviors emerge from simple local interactions.
- **Resilience**: The swarm continues to function even if individual agents fail.
- **Adaptive Focus**: Agents naturally converge on "interesting" or problematic areas through pheromone reinforcement.
- **Efficiency**: Stigmergic coordination reduces communication overhead and token usage.

### Is *bichos* ready for production?
Currently, the project is in the **Specification/Proposal stage**. The core architecture and ant-based bug hunting are being implemented, while other castes (Bees, Termites, Wasps) are planned. See the [Project Status](../README.md#-project-status) for more details.

---

## 🏗️ Architecture & Core Concepts

### What are "Castes"?
In *bichos*, agents are organized into specialized roles called castes, each inspired by a different insect:
- 🐜 **Ant (Forager)**: Explores the call graph to detect bugs and edge cases.
- 🐝 **Bee (Scout)**: Probes endpoints for performance testing and bottlenecks.
- 🐛 **Termite (Builder)**: Analyzes architecture for refactoring and consistency.
- 🐝 **Wasp (Guard)**: Performs security auditing and vulnerability detection.

### What is "Stigmergy"?
Stigmergy is a mechanism of indirect coordination where agents communicate by modifying their environment. In *bichos*, this is implemented as a **Digital Pheromone Grid**. When an agent finds something interesting (like a bug), it "deposits" a pheromone. Other agents "smell" these pheromones and are attracted to the same area, reinforcing the trail.

### How do Digital Pheromones work?
Pheromones are stored in a persistent cache (`diskcache`). They have:
- **Intensity**: Represents the strength of the signal.
- **Type**: Bug, Curvature (Architecture), Performance, or Alert (Security).
- **Decay**: Over time, pheromones "evaporate" (their intensity decreases). This ensures the swarm doesn't get stuck on stale information and continues to explore new areas.

### What is Ant Colony Optimization (ACO)?
ACO is the mathematical foundation for how ants choose their paths. They balance two factors:
1. **Pheromone Trail (τ - intensity)**: How many other ants found something here.
2. **Heuristic (η - attractiveness)**: A local "guess" of how interesting a node is (e.g., high cyclomatic complexity).

---

## 🛠️ Usage & Configuration

### How do I run an analysis?
Once implemented, you can run an analysis via the CLI:
```bash
bichos analyze /path/to/your/repo
```
Or programmatically:
```python
from pathlib import Path
from bichos import HiveConfig, run_hive

config = HiveConfig()
report = await run_hive(Path("./src"), config)
```

### Which LLM providers are supported?
*bichos* uses [PydanticAI](https://ai.pydantic.dev/), supporting multiple providers:
- **OpenAI** (GPT-4o, etc.)
- **Anthropic** (Claude 3.5 Sonnet, etc.)
- **Ollama** (for local models)
- **OpenRouter**
- *Note: Google Gemini support is planned.*

You can configure the model in your `HiveConfig`:
```python
config = HiveConfig(
    model={"provider": "anthropic", "name": "claude-3-5-sonnet-20241022"}
)
```

### Does it work offline?
Yes! By using local models via **Ollama**, *bichos* can run entirely offline. The pheromone cache is stored locally on disk, and no external database (like Redis) is required.

### How does *bichos* save on token usage?
By using stigmergy instead of direct message-passing between agents, *bichos* avoids sending long chat histories or coordination logs between agents. Agents simply read/write small, structured pheromone data to a shared cache, which can reduce token usage by up to **80%** in large-scale analyses.

---

## 🔬 Technical Details

### How is the codebase represented?
*bichos* builds a **Code Graph** using Python's AST (Abstract Syntax Tree) and `NetworkX`. Nodes represent functions, classes, and modules, while edges represent calls and dependencies.

### What is "Cyclomatic Complexity" and why does it matter?
We use `radon` to calculate the cyclomatic complexity of functions. High complexity often correlates with bugs, so the "Ant" agents use it as a heuristic to decide which functions to prioritize during exploration.

### Where are the pheromones stored?
By default, they are stored in a `.bichos_cache` directory in your project root using `diskcache`. You can clear it at any time with `bichos clear-cache`. Deleting this directory is safe; the swarm will simply restart its exploration without any prior "memory."
