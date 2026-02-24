# **The Entomological Codebase: A Bio-Mimetic Framework for Agentic Software Assurance Using PydanticAI**

## **1\. Executive Summary**

The escalating complexity of modern software ecosystems—characterized by distributed microservices, asynchronous data flows, and massive codebases—has rendered traditional, deterministic auditing tools increasingly insufficient. While static analysis and unit testing remain foundational, they often fail to capture the emergent properties of system behavior, such as complex race conditions, architectural drift, and latency cascades. This report proposes a paradigm shift in software quality assurance: the application of bio-mimetic agentic architectures inspired by eusocial insects (ants, bees, termites, and wasps). We define a comprehensive framework, **The Entomological Codebase**, which leverages the principles of stigmergy, division of labor, and decentralized self-organization to address critical software quality attributes including robustness, flexibility, reliability, and performance.

Crucially, this framework is architected for practical implementation using **PydanticAI**, a Python-based agent framework that prioritizes type safety, dependency injection, and graph-based control flows. We demonstrate how PydanticAI’s specific features—such as pydantic\_graph for state management, RunContext for dependency injection, and Logfire for observability—map directly to biological mechanisms like pheromone trails, trophallaxis (nutrient exchange), and nest topology.

The analysis is structured around four primary domains of software auditing, each corresponding to a specific insect pattern:

1. **Bug Detection and Path Coverage (The Ant Pattern):** Utilizing stochastic foraging and pheromone reinforcement to explore edge cases, uncovering issues with robustness and reliability through intelligent fuzzing.1
2. **Architectural Alignment and Refactoring (The Termite Pattern):** Employing curvature-based construction rules to detect architectural misalignments and inconsistencies, ensuring system flexibility and structural integrity.3
3. **Performance and Resource Optimization (The Bee Pattern):** Implementing waggle-dance recruitment strategies for load testing, latency analysis, and throughput optimization, directly addressing performance metrics.5
4. **Security and Defense (The Wasp Pattern):** Deploying specialized defense castes for input sanitization and vulnerability scanning, enhancing the system's defensive reliability.7

By replacing monolithic "God-mode" agents with swarms of specialized, Pydantic-typed agents operating via local rules, engineering teams can achieve emergent software reliability that scales with system complexity. This report details the theoretical underpinnings, the mathematical models for digital pheromones, and the concrete implementation strategies required to build this self-healing, autonomic software system.

## ---

**2\. Introduction: The Superorganism Approach to Software Quality**

### **2.1 The Complexity Crisis and the Limitations of Determinism**

Modern software engineering has surpassed the cognitive capacity of individual developers. Systems are no longer static repositories of logic but dynamic, living ecosystems subject to entropy, dependency drift, and emergent failure modes. As systems scale, the interaction between components becomes non-linear; a minor latency spike in a logging service can cascade into a catastrophic failure in a payment gateway. Traditional auditing tools—linters, Static Application Security Testing (SAST), and deterministic unit tests—operate on rigid, predefined rules. They are effective at catching syntax errors and known vulnerability patterns but often fail to detect systemic architectural misalignments, complex race conditions, or "code smells" that arise from the interaction of disparate modules.9

The challenge lies in the distributed nature of the problem. Bugs are rarely isolated incidents; they are often symptoms of deeper architectural entropy or resource contention. Solving these problems requires a distributed problem-solving approach, one that mirrors the most successful distributed systems found in nature: eusocial insect colonies. These biological systems exhibit "Swarm Intelligence," where complex global behavior emerges from simple local interactions, allowing the colony to solve problems—such as finding the shortest path to food or regulating nest temperature—that are far beyond the capabilities of any single individual.11

### **2.2 Biological Inspiration: Eusociality and Stigmergy**

Eusociality represents the highest level of social organization in the animal kingdom, defined by cooperative brood care, overlapping generations, and a division of labor into reproductive and non-reproductive castes.7 The success of ants, bees, and termites is not due to the intelligence of the individual, but the "Superorganism" nature of the colony.

The core mechanism enabling this intelligence is **stigmergy**—a form of indirect coordination where agents communicate by modifying their environment.1 An ant does not tell another ant where the food is; it lays a pheromone trail on the ground. The environment itself becomes the memory and the controller of the system. In the context of software agents, this offers a powerful alternative to complex message-passing architectures. Instead of agents chattering endlessly to each other (consuming tokens and bandwidth), they modify the "environment"—the code, the logs, the shared state—leaving signals for other agents to act upon.14 This decoupling allows for massive scalability; agents can work asynchronously, reacting to the state of the codebase rather than waiting for direct instructions.

### **2.3 The Substrate: PydanticAI**

To translate these biological principles into executable code, a robust framework is required. **PydanticAI** serves as the ideal substrate for this bio-mimetic architecture. Unlike untyped or purely prompt-based frameworks, PydanticAI leverages Python’s type system and dataclasses to enforce rigor, ensuring that the "genetic code" of our agents is type-safe and reliable.16

* **Type Safety as Biological Determinism:** Just as an ant of a specific caste has a specific morphology and function determined by its biology, a PydanticAI agent has strict input/output models defined by Pydantic schemas. This prevents "mutation" errors where agents hallucinate invalid data structures.
* **Dependency Injection (Deps) as Trophallaxis:** Social insects share food and chemical signals directly (trophallaxis). PydanticAI’s dependency injection system allows agents to share database connections, HTTP clients, and global state in a structured, thread-safe manner, facilitating the sharing of "digital nutrients" (data) and "signals" (state).11
* **Pydantic Graph as Nest Topology:** The recent introduction of pydantic\_graph allows for the definition of state machines and complex workflows. This maps perfectly to the structured yet flexible behavior of insect colonies, where individuals transition between roles (states) based on environmental cues.17
* **Logfire as Pheromone Mapping:** Pydantic Logfire provides deep observability, tracing the execution paths of agents. This can be repurposed to visualize "digital pheromones"—identifying where agents have been, where they have found value (bugs), and where the "heat" of the system lies.18

## ---

**3\. Theoretical Framework: The Entomological Codebase**

To organize agentic models effectively, we must first map the biological concepts of eusociality to the domain of software engineering. This mapping provides the "local rules" that govern agent behavior and ensures the system addresses the core requirements of bug detection, architectural consistency, robustness, reliability, and performance.

### **3.1 The Environment as the Medium**

In nature, the medium is the soil, the wood, or the air. In our framework, the **Codebase and Runtime Environment** form the medium.

* **Static Medium:** Source code files, configuration files (YAML/JSON), documentation, and dependency trees.
* **Dynamic Medium:** Running processes, network traffic, logs, database state, and memory profiles.

Stigmergy occurs when an agent modifies this medium. A "ToDo" comment is a weak stigmergic signal. A failing test case is a strong alarm pheromone. A high-latency log entry is a resource signal.1 The framework treats the codebase not as a static text but as a mutable environment where agents leave "digital pheromones" (metadata, tags, annotations) that decay over time.

### **3.2 Caste System and Division of Labor**

Division of labor reduces the cognitive load on any single agent, a critical factor when dealing with limited context windows in LLMs.1 In PydanticAI, this is implemented by defining distinct Agent instances with specialized system prompts, toolsets, and dependency injections.20

| Biological Caste | Software Role | Focus Area | PydanticAI Implementation Mapping |
| :---- | :---- | :---- | :---- |
| **Forager (Ant)** | **Path Explorer / Fuzzer** | Bug detection, edge cases, execution paths, input validation. | Agent with graph traversal tools and stochastic decision logic via Deps. |
| **Builder (Termite)** | **Refactorer / Architect** | Architectural alignment, consistency, refactoring, entropy reduction. | pydantic\_graph state machine for multi-step refactoring (Inspect \-\> Plan \-\> Build). |
| **Scout (Bee)** | **Load Tester / Profiler** | Performance, latency, throughput, bottleneck discovery. | Parallel execution of Agent instances, aggregating results via reducers. |
| **Soldier (Wasp)** | **Security Auditor** | Security, vulnerability scanning, intrusion detection, sanitization. | Agent with specialized validation schemas and "alarm" capabilities via Logfire. |
| **Queen** | **Orchestrator** | Strategy, resource allocation, global reporting. | Graph orchestrator node managing global state and initialization. |

### **3.3 Digital Pheromones: Decay and Reinforcement Mathematics**

A critical aspect of ant colony optimization (ACO) and swarm intelligence is the evaporation of pheromones.2 Without evaporation, the colony converges on suboptimal paths and cannot adapt to changes. In a software context, if "bug pheromones" never evaporated, the swarm would endlessly audit a module that was fixed months ago.

We model the digital pheromone level ![][image1] on a code path (edge between function ![][image2] and ![][image3]) using the standard ACO update rule adapted for software maintenance:

![][image4]
Where:

* ![][image5] (rho) is the **evaporation rate** (![][image6]). This represents the "forgetting curve" of the system. A high ![][image5] makes the system highly reactive to recent bugs but forgetful of long-term history. In our framework, this is implemented via Redis TTL (Time-To-Live) or a decay function in the state manager.22
* ![][image7] is the **reinforcement**, the amount of pheromone deposited by agent ![][image8] if a bug or issue is found.
  * ![][image9] if agent ![][image8] finds a bug, where ![][image10] is a constant (bug severity) and ![][image11] is the path length (complexity).
  * In our software model, finding a critical vulnerability deposits massive pheromone (![][image12]), instantly attracting other agents (Foragers and Soldiers) to that module.

This mathematical foundation ensures that the system is dynamic. It prioritizes "fresh" issues while maintaining a background awareness of historically problematic areas, directly addressing the requirement for **Robustness** and **Reliability** by ensuring continuous, adaptive coverage.

## ---

**4\. Pattern I: The Foraging Ant (Bug Detection & Robustness)**

### **4.1 Biological Basis: Ant Colony Optimization (ACO)**

Ants find the shortest path to food by laying pheromone trails. Shorter paths allow for more frequent trips, resulting in higher pheromone density, which attracts more ants. This positive feedback loop optimizes the route.21 In nature, this is a stochastic process; ants do not follow the trail deterministically but probabilistically. This randomness allows them to explore new paths and avoid getting stuck in local optima.

### **4.2 Software Analog: Execution Path Discovery and Fuzzing**

In the domain of software auditing, "food" corresponds to a bug, an unhandled exception, or a violation of logic. The "path" is the sequence of function calls, API requests, or user interactions leading to that state.

* **Goal:** Maximize code coverage and bug discovery with minimal "energy" (token usage and compute time).
* **The Problem:** Brute-force testing is impossible in large systems due to the combinatorial explosion of states.
* **The Solution:** Agents traverse the Control Flow Graph (CFG) of the application. When an agent triggers a warning, error, or unexpected state, it reinforces that path in the shared environment. Subsequent agents preferentially explore variations of that path, effectively performing "Intelligent Fuzzing."

This pattern directly addresses **Robustness**. By subjecting the code to a swarm of agents that explore edge cases and probabilistic paths, the system uncovers fragile logic that standard unit tests (which usually test the "happy path") miss.

### **4.3 PydanticAI Implementation Strategy**

#### **4.3.1 The Agent Definition and Dependency Injection**

The Forager Agent is designed for exploration. It requires tools to execute code snippets, analyze ASTs, or traverse a graph representation of the codebase. We use PydanticAI’s Deps to inject the "Environment" (the shared state mechanism, e.g., Redis) and the "Map" (the code graph).

Python

from pydantic\_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import List, Optional
import random

\# Define the Shared Environment (Stigmergic State)
class AntDeps:
    redis\_client: 'RedisClient'  \# Represents the Pheromone Grid
    code\_graph: 'NetworkXGraph'  \# Represents the Territory (Codebase)

\# The Forager Agent Definition
forager \= Agent(
    'openai:gpt-4o',  \# Using a high-reasoning model for path analysis
    deps\_type=AntDeps,
    system\_prompt=(
        "You are a Forager Ant in a large software codebase. "
        "Your goal is to traverse the execution graph to find bugs (food). "
        "You must choose your next step based on Pheromone Intensity (historical bugs) "
        "and Heuristic Visibility (code complexity). "
        "If you encounter a potential edge case, explore it deeply."
    )
)

#### **4.3.2 The Stigmergic Navigation Tool**

The core logic of the Forager Ant is its decision-making process. We implement the probabilistic selection rule of ACO 22 within a PydanticAI tool. This tool decides which function to analyze next.

The probability ![][image13] of moving from function ![][image2] to function ![][image3] is given by:

![][image14]
Where:

* ![][image15] is the **Pheromone Level**: Retrieved from Redis, representing how many bugs have been found in function ![][image3] recently.
* ![][image16] is the **Heuristic Information**: A static metric of code quality, such as Cyclomatic Complexity or Halstead Volume. Complex code is more likely to contain bugs, so it has higher "visibility."
* ![][image17] and ![][image18] are control parameters weighting the importance of pheromones vs. heuristics.

Python

@forager.tool
async def choose\_next\_function(ctx: RunContext, current\_function: str) \-\> str:
    """
    Decides the next function to inspect based on ACO probability rules.
    """
    \# 1\. Get neighbors (functions called by or related to current\_function)
    neighbors \= ctx.deps.code\_graph.get\_neighbors(current\_function)

    if not neighbors:
        return "RETURN\_TO\_NEST"

    \# 2\. Calculate probabilities based on Pheromone (Redis) and Complexity (Static Analysis)
    probabilities \=
    weights \=

    for node in neighbors:
        \# Retrieve pheromone level from Redis (Digital Stigmergy)
        \# Default to a small epsilon value if no pheromone exists
        tau \= await ctx.deps.redis\_client.get\_pheromone(node) or 0.1

        \# Retrieve complexity (static analysis pre-calculated in graph)
        \# Higher complexity \= higher attractiveness
        eta \= ctx.deps.code\_graph.get\_complexity(node)

        \# Calculate attraction score (ACO formula)
        \# alpha=1.0, beta=2.0 implies we value complexity twice as much as history initially
        score \= (tau \*\* 1.0) \* (eta \*\* 2.0)
        weights.append(score)

    \# 3\. Select next node stochastically
    \# This randomness is key for coverage; we don't always pick the 'best' path
    selected\_node \= random.choices(neighbors, weights=weights, k=1)

    return selected\_node

#### **4.3.3 Bug Discovery and Pheromone Deposition**

When the agent identifies a potential issue (e.g., a missing None check, a race condition, or a logic error), it must "deposit pheromones" to alert the swarm. This is done by updating the shared state.

Python

@forager.tool
async def report\_bug(ctx: RunContext, function\_name: str, issue\_description: str, severity: int):
    """
    Reports a bug and deposits pheromones on the function to attract more ants.
    """
    \# Reinforce the path\!
    \# Update equation: T\_new \= (1-rho)\*T\_old \+ Delta\_T
    \# We add a value proportional to severity (Severity 1-10)
    pheromone\_amount \= severity \* 10.0

    await ctx.deps.redis\_client.deposit\_pheromone(function\_name, amount=pheromone\_amount)

    \# Log the discovery for observability
    print(f"🐜 BUG FOUND in {function\_name}: {issue\_description}. Pheromone trail reinforced.")

    return "Pheromone deposited. Swarm alerted."

### **4.4 Implications for Robustness and Reliability**

This pattern directly enhances **Robustness** through stochastic coverage. Unlike a human auditor who might follow a logical path, the "Ant Swarm" explores unlikely paths. If a specific module (e.g., UserAuth) is fragile, the first ant to find a bug will deposit pheromones. This attracts more ants, which then explore *adjacent* functions and edge cases within that module. The system naturally focuses its "cognitive energy" on the most unstable parts of the codebase.

**Reliability** is improved because the system is persistent. The "Forager" agents can run continuously in the background (e.g., during CI/CD). Over time, the "Pheromone Map" becomes a heatmap of technical debt and instability, guiding human developers to the areas that need the most attention.

## ---

**5\. Pattern II: The Termite Cathedral (Architectural Consistency)**

### **5.1 Biological Basis: Stigmergic Construction and Curvature**

Termites build massive, cooling-efficient mounds without a centralized blueprint. They follow simple local rules: "If I smell a pheromone on a soil pellet, I deposit my pellet there." Crucially, research shows that construction is driven by **curvature** and **gradients** in the environment.3 Termites react to the "roughness" or shape of the wall; they smooth out irregularities and build arches where curvature is high.4 This results in a homeostatic structure that maintains internal temperature and humidity.

### **5.2 Software Analog: Architectural Alignment and Refactoring**

In software, "curvature" allows for a powerful metaphor for **Architectural Entropy** or **Technical Debt**.

* **Smooth Wall (Low Entropy):** Consistent code style, proper layering (Controller ![][image19] Service ![][image19] Repository), distinct separation of concerns.
* **Rough/High Curvature (High Entropy):** Circular dependencies, massive "God classes," inconsistent naming conventions, mixed abstractions (e.g., SQL queries in the UI layer).

The goal of the Termite Pattern is to detect these inconsistencies and "smooth" them out, aligning the codebase with architectural rules (e.g., SOLID principles) without requiring a single "Architect" agent to rewrite the whole system. This addresses the requirement for **Flexibility** and **Architectural Alignment**.

### **5.3 PydanticAI Implementation Strategy**

#### **5.3.1 The Builder Agent and Local Context**

Termites do not see the whole mound; they only act on their immediate surroundings. Similarly, a Builder Agent operates on a "Local Context" (e.g., a single module and its immediate imports). It does not try to refactor the entire system at once but fixes local "roughness."

We define the agent's state using Pydantic models to track the "curvature" it detects.

Python

from pydantic import BaseModel, Field

class ArchitecturalViolation(BaseModel):
    violation\_type: str \# e.g., "Circular Dependency", "Layer Violation"
    severity: int
    location: str

class TermiteState(BaseModel):
    current\_module\_path: str
    local\_complexity\_score: float
    detected\_violations: List\[ArchitecturalViolation\] \=

builder\_agent \= Agent(
    'anthropic:claude-3-5-sonnet', \# High reasoning capability for structure/refactoring
    result\_type=TermiteState,
    system\_prompt=(
        "You are a Termite Builder. Your task is to maintain Architectural Consistency. "
        "Analyze the local code structure (curvature). "
        "If you detect high entropy (violations), propose a refactor (deposit pellet). "
        "Do not invent new patterns; reinforce existing valid patterns."
    )
)

#### **5.3.2 Implementation via Pydantic Graph**

Refactoring is inherently a stateful, multi-step process: Analysis ![][image19] Planning ![][image19] Modification ![][image19] Verification. This maps perfectly to pydantic\_graph, which allows us to define a directed graph of agentic steps.17

* **Node 1: Inspect (Sense Curvature):** The agent analyzes the Abstract Syntax Tree (AST) for violations.
* **Node 2: Decision (Threshold Check):** If the "curvature" (complexity/violation count) exceeds a threshold, the agent transitions to the Build state. Otherwise, it moves to a new location.
* **Node 3: Build (Deposit Pellet):** The agent generates a refactoring plan or applies a fix (e.g., "Extract Method," "Move Class").
* **Node 4: Verify (Check Stability):** The agent runs local tests to ensure the refactor didn't break functionality.

Python

from pydantic\_graph import BaseNode, Graph, End, GraphRunContext
from dataclasses import dataclass
from typing import Union

@dataclass
class InspectNode(BaseNode):
    async def run(self, ctx: GraphRunContext) \-\> 'DecisionNode':
        \# Analyze "curvature" (complexity and dependency cycles)
        \# This could call an external tool like 'radon' or 'pylint' via the agent
        complexity \= calculate\_cyclomatic\_complexity(ctx.state.current\_module\_path)
        violations \= check\_dependency\_cycles(ctx.state.current\_module\_path)

        ctx.state.local\_complexity\_score \= complexity
        ctx.state.detected\_violations \= violations

        return DecisionNode()

@dataclass
class DecisionNode(BaseNode):
    async def run(self, ctx: GraphRunContext) \-\> Union:
        \# Local Rule: If curvature is high (\> 10\) or violations exist, Build.
        if ctx.state.local\_complexity\_score \> 10 or ctx.state.detected\_violations:
            print(f"High curvature detected in {ctx.state.current\_module\_path}. Transitioning to BUILD.")
            return BuildNode()
        else:
            return MoveNode()

@dataclass
class BuildNode(BaseNode):
    async def run(self, ctx: GraphRunContext) \-\> 'VerifyNode':
        \# The agent generates a refactor plan to reduce entropy
        \# This is the "Stigmergic Action" \- modifying the environment
        print("Applying Refactor (Smoothing Wall)...")
        return VerifyNode()

### **5.4 Implications for Flexibility and Consistency**

The Termite Pattern creates a **Flexible** system. By constantly smoothing out "rough patches" (high coupling), the system prevents the calcification of technical debt. When new features are added, the "Termites" ensure they adhere to the existing structure, maintaining **Architectural Alignment**.

Furthermore, this supports **Emergent Architecture**. Just as termites build complex ventilation shafts without explicitly planning for airflow, Termite Agents can emerge a cleaner architecture (e.g., naturally separating a Monolith into modules) simply by enforcing local rules of low coupling and high cohesion. If a developer introduces a layer violation (e.g., importing a DB model in a UI component), the local curvature spikes. A Termite Agent on its patrol detects this "roughness" and triggers a refactor to move the logic to a service layer, restoring the "smooth wall."

## ---

**6\. Pattern III: The Honeybee Colony (Performance, Latency & Throughput)**

### **6.1 Biological Basis: The Waggle Dance and Recruitment**

Honeybees use the "waggle dance" to communicate the vector (direction and distance) and quality of a resource to the colony.5

* **Scouts:** Fly out to discover food sources.
* **The Dance:** Upon return, they perform a dance where the duration and vigor correlate to the quality of the food.
* **Recruitment:** Onlooker bees watch the dance and are recruited to forage at the best sites. This results in an optimal allocation of the colony's workforce to the most profitable resources.

### **6.2 Software Analog: Load Testing and Bottleneck Analysis**

In the context of software performance, a "resource" is essentially a point of interest, often a negative one: a **Bottleneck**, a **Latency Spike**, or a **Throughput Limit**. We want to recruit agents to "exploit" (stress test) this bottleneck to understand its limits and behavior under load.

* **Scout Bees:** Lightweight agents that ping various API endpoints or functions to measure baseline latency.
* **Waggle Dance:** A structured report containing the endpoint URL (direction) and the latency/error rate (quality/profitability).
* **Forager Bees:** Load generation agents that swarm the endpoint based on the Scout's report.

This pattern directly addresses **Performance (Latency and Throughput)** requirements.

### **6.3 PydanticAI Implementation Strategy**

#### **6.3.1 The Scout Agent and Structured Output**

We use PydanticAI to define a WaggleDance model. This is the **Structured Output** of a Scout Agent, ensuring that the performance data is machine-readable and actionable.

Python

class WaggleDance(BaseModel):
    endpoint\_url: str
    method: str
    average\_latency\_ms: float
    throughput\_rps: float
    error\_rate: float

    @property
    def profitability(self) \-\> float:
        \# In this context, High Latency/Error \= High "Profit" for a debugger/tester bee
        \# We want to investigate the slow endpoints.
        return self.average\_latency\_ms \* (1 \+ self.error\_rate)

scout\_agent \= Agent(
    'openai:gpt-3.5-turbo', \# Use a fast, cheap model for rapid probing
    result\_type=WaggleDance,
    system\_prompt="You are a Scout Bee. Probe the assigned endpoint. Measure latency and throughput. Report back with a Waggle Dance."
)

#### **6.3.2 Swarm Recruitment via Parallel Execution**

Using pydantic\_graph's parallel execution features (currently supported via async gathering and broadcasting patterns) 27, we can simulate the recruitment process.

1. **Phase 1 (Scouting):** The "Hive" launches ![][image20] Scout Agents in parallel to probe different endpoints.
2. **Phase 2 (The Dance Floor / Join):** The results are collected via a **Reducer**. This step aggregates the WaggleDance reports.
3. **Phase 3 (Recruitment):** The reducer allocates "Forager Bees" (Load Generators) proportional to the profitability (latency) of each endpoint.

Python

\# Conceptual Pydantic Graph for Bee Swarm Recruitment

@dataclass
class HiveMindState:
    recruitment\_map: Dict\[str, int\] \# URL \-\> Number of Bees allocated
    total\_bees: int \= 100

async def dance\_floor\_reducer(ctx, scouts\_results: List) \-\> HiveMindState:
    """
    The Waggle Dance Interpreter.
    Allocates more bees to endpoints with higher latency (Profitability).
    """
    total\_profitability \= sum(r.profitability for r in scouts\_results)
    allocation \= {}

    print("🐝 DANCE FLOOR REPORT:")
    for result in scouts\_results:
        \# Proportional allocation (Roulette Wheel Selection)
        if total\_profitability \> 0:
            count \= int((result.profitability / total\_profitability) \* ctx.state.total\_bees)
        else:
            count \= 1 \# Minimum exploration

        allocation\[result.endpoint\_url\] \= count
        print(f"  \- {result.endpoint\_url}: {result.average\_latency\_ms}ms \-\> Recruited {count} Bees")

    return HiveMindState(recruitment\_map=allocation)

\# The graph would define a parallel split to scouts, then a join using this reducer.
\# g.add(g.edge\_from(scout\_node).to(reducer\_node))

### **6.4 Implications for Performance Metrics**

This bio-mimetic approach allows for **Dynamic Performance Analysis**.

* **Auto-Scaling Tests:** Instead of a static load test plan (e.g., "100 users on Login"), the swarm **adapts**. If the "Checkout" service starts slowing down (high latency), the "bees" naturally flock to it, increasing the load until the breaking point is found. This helps identify the true **Throughput** limits of the system components.
* **Latency Arbitrage:** By constantly monitoring latency across the system, the Bee Swarm can detect **Latency Drift**—performance regressions that happen slowly over time—and flag them before they become critical incidents.
* **Resource Optimization:** The system does not waste resources testing stable, fast endpoints. It focuses its "compute" (the agents) on the bottlenecks, maximizing the efficiency of the audit.

## ---

**7\. Pattern IV: The Wasp Nest (Security, Defense & Reliability)**

### **7.1 Biological Basis: Defense Castes and Chemical Profiling**

Wasps and certain ant species have specialized "Soldier" castes designed solely for defense. They guard the nest entrance and inspect incoming individuals. They rely on **Hydrocarbon Profiles** (chemical signatures) to distinguish nestmates from intruders.7 If an intruder is detected, they release an **Alarm Pheromone** that triggers an immediate, aggressive response from the colony.1

### **7.2 Software Analog: Input Validation and Intrusion Detection**

* **Nest Entrance:** API Gateways, Public Interfaces, Login Screens.
* **Hydrocarbon Profile:** JWT Tokens, API Keys, Request Payloads, IP Reputation.
* **Intruder:** Malformed inputs, SQL injection attempts, unauthorized IPs, anomalous traffic patterns.
* **Alarm Pheromone:** Security alerts, log spikes, firewall rules.

This pattern addresses **Security** and **Reliability**. By filtering inputs and aggressively defending the system boundary, the Wasp pattern ensures that the internal components operate in a safe environment.

### **7.3 PydanticAI Implementation Strategy**

#### **7.3.1 The Guard Wasp (Validator Agent)**

This agent sits at the boundary (conceptually or physically in a middleware). It uses Pydantic's powerful validation engine combined with LLM reasoning to detect "mimicry" (sophisticated attacks that pass regex checks but contain malicious intent).

Python

from pydantic import BaseModel, Field, validator

class IncomingRequest(BaseModel):
    headers: Dict\[str, str\]
    payload: str
    source\_ip: str

class SecurityVerdict(BaseModel):
    is\_safe: bool
    threat\_level: int \= Field(..., ge=0, le=10)
    threat\_type: str
    reasoning: str

guard\_wasp \= Agent(
    'google:gemini-1.5-pro', \# Large context window for pattern recognition
    result\_type=SecurityVerdict,
    system\_prompt=(
        "You are a Guard Wasp. Analyze the hydrocarbon profile (request signature). "
        "Look for anomalies, mimetic attacks, or payload obfuscation (e.g., prompt injection). "
        "Strictly categorize the threat level."
    )
)

#### **7.3.2 The Stigmergic Alarm System via Logfire**

When a Guard Wasp detects an intruder, it must alert the hive. In PydanticAI, we use **Logfire** as the alarm pheromone channel.18 A high-severity log entry acts as a signal that can trigger other automated systems (e.g., a firewall update).

Python

import logfire

@guard\_wasp.tool
async def release\_alarm\_pheromone(ctx: RunContext, verdict: SecurityVerdict, source\_ip: str):
    """
    Releases an alarm signal if a threat is detected.
    """
    if verdict.threat\_level \> 7:
        \# 1\. Physical Defense: Block IP (Environment Modification)
        \# This assumes the agent has access to a Firewall tool via Deps
        \# await ctx.deps.firewall.block\_ip(source\_ip)

        \# 2\. Alert the Hive (Logfire Pheromone)
        \# We use structured logging to make this machine-readable
        logfire.error(
            "🚨 INTRUDER DETECTED: WASP ALARM TRIGGERED",
            tags=\["security", "wasp\_alarm", "defcon\_1"\],
            threat\_level=verdict.threat\_level,
            source\_ip=source\_ip,
            reasoning=verdict.reasoning
        )

        \# 3\. Update Stigmergic State (Global Alert Level)
        \# This puts the whole colony (other agents) into a defensive posture
        await ctx.deps.redis\_client.set("hive\_state", "ALERT\_MODE")

        return "Alarm released. Colony alerted."

    return "Threat level low. Monitoring."

### **7.4 Reliability via Redundancy and Quorum Sensing**

Biological defense is robust because it is redundant. If one guard is tricked, another may not be. In this framework, we can implement **Quorum Sensing**.29 Instead of relying on a single agent, the request is analyzed by a "squad" of Guard Wasps (using different LLMs—e.g., one GPT-4, one Claude, one Llama). The request is only admitted if a quorum (e.g., 3 out of 5\) agrees it is safe. This drastically reduces false negatives and enhances the **Reliability** of the security layer.

## ---

**8\. Implementation Architecture: The "Hive" Operating System**

To orchestrate these diverse patterns, we propose a unified "Hive" architecture. This is the operating system that manages the agents, the shared state, and the lifecycle of the digital insects.

### **8.1 The Graph Topology**

The system is not a linear pipeline but a cyclic, parallel graph implemented using pydantic\_graph.

1. **Start Node (The Queen):** Initializes the run, checks global configuration, and determines the "Season" (e.g., Audit Season, Performance Season).
2. **Split Node (Caste Allocation):** Based on the query or trigger (e.g., "Full System Audit"), allocates resources.
   * *Branch A (Ants):* Spawns parallel foraging agents for code path analysis.
   * *Branch B (Termites):* Spawns builder agents for architectural checks.
   * *Branch C (Bees):* Spawns scout agents for performance baselining.
3. **Execution Phase (The Field):** Agents run asynchronously. They interact with the "Environment" (Code/Dependencies) and write to "Shared State" (Redis Pheromones).
4. **Join Node (The Trophallaxis Hub):** Aggregates results. Reducers merge bug reports, de-duplicating them based on stack traces or signatures.
5. **Decision Node (Swarm Intelligence):**
   * *Feedback Loop:* If critical\_bug\_count \> threshold, trigger "Emergency Mode" (spawn more Wasps).
   * *Coverage Check:* If coverage \< target, re-spawn Foragers with higher "temperature" (volatility) to explore new paths.
6. **End Node:** Generate Final Report.

### **8.2 Handling State: The Digital Pheromone Grid**

The GraphRunContext in PydanticAI acts as the short-term working memory. However, for true stigmergy, we need persistent state. **Redis** is the ideal candidate for the "Pheromone Grid" due to its speed and support for TTL (Time-To-Live).

| Pheromone Type | Redis Key Structure | Value Data | Decay (TTL) | Used By |
| :---- | :---- | :---- | :---- | :---- |
| **Food Trail** | bug:path:{hash} | Severity, Bug ID | 7 Days | Ants (Foragers) |
| **Curvature** | arch:complexity:{module} | Complexity Score | 30 Days | Termites (Builders) |
| **Waggle** | perf:endpoint:{url} | Latency (ms) | 1 Hour | Bees (Scouts) |
| **Alarm** | sec:alert:{ip} | Threat Level | 24 Hours | Wasps (Guards) |

### **8.3 Observability and Metrics**

This framework generates massive concurrency. Debugging a swarm of 100 agents is non-trivial. **Pydantic Logfire** is essential here. By tagging spans with biological roles (e.g., caste:ant), we can visualize the swarm's behavior in real-time.

* **Heatmaps:** Visualize which parts of the code are attracting the most "Ants" (bugs).
* **Flow Diagrams:** Trace the "Waggle Dance" recruitment process.
* **Alerts:** Immediate notification of "Wasp Alarms."

## ---

**9\. Conclusion: The Autonomic Future**

The **Entomological Codebase** framework represents a radical departure from linear, human-centric software testing. By organizing Agentic Models using PydanticAI into distinct biological castes—Ants (Explorers), Termites (Builders), Bees (Optimizers), and Wasps (Defenders)—we create a system that is not just automated, but **autonomic**. It is capable of self-management, self-repair, and emergent intelligence.

PydanticAI provides the necessary engineering rigor to make this biological metaphor a reality. Its type-safe agents, graph-based orchestration, and deep observability allow us to harness the chaotic power of swarm intelligence and channel it into the disciplined structure required for high-reliability software engineering. This approach promises to uncover deep, structural inconsistencies and robustness issues that evade the deterministic gaze of traditional tools, paving the way for software systems that evolve and adapt as organically as the superorganisms that inspired them. The future of software assurance is not a single smart auditor, but a billion smart interactions.

#### **Works cited**

1. Emergence of cooperation and division of labor in the primitively eusocial wasp Ropalidia marginata \- PMC, accessed February 14, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5789922/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5789922/)
2. Pheromone-Focused Ant Colony Optimization algorithm for path planning \- arXiv, accessed February 14, 2026, [https://arxiv.org/html/2601.07597v1](https://arxiv.org/html/2601.07597v1)
3. Nesting strategy reflects individual worker movement in termites \- PMC, accessed February 14, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12751460/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12751460/)
4. Termite mound architecture and climate control: a review of X-ray tomography and flow field simulation approaches \- PMC, accessed February 14, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12539963/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12539963/)
5. Test Case Optimization Using Artificial Bee Colony Algorithm \- ResearchGate, accessed February 14, 2026, [https://www.researchgate.net/publication/220790134\_Test\_Case\_Optimization\_Using\_Artificial\_Bee\_Colony\_Algorithm](https://www.researchgate.net/publication/220790134_Test_Case_Optimization_Using_Artificial_Bee_Colony_Algorithm)
6. A bee colony optimization algorithm for efficient resource allocation in e-government systems \- Emerald Publishing, accessed February 14, 2026, [https://www.emerald.com/jidt/article/2/2/196/1253239/A-bee-colony-optimization-algorithm-for-efficient](https://www.emerald.com/jidt/article/2/2/196/1253239/A-bee-colony-optimization-algorithm-for-efficient)
7. Eusociality \- Wikipedia, accessed February 14, 2026, [https://en.wikipedia.org/wiki/Eusociality](https://en.wikipedia.org/wiki/Eusociality)
8. Phylogeny and evolution of eusocial insects a comparison of origins and losses in ants and bees \- SICB, accessed February 14, 2026, [https://sicb.org/abstracts/phylogeny-and-evolution-of-eusocial-insects-a-comparison-of-origins-and-losses-in-ants-and-bees/](https://sicb.org/abstracts/phylogeny-and-evolution-of-eusocial-insects-a-comparison-of-origins-and-losses-in-ants-and-bees/)
9. Formal Software Architecture Rule Learning: A Comparative Investigation between Large Language Models and Inductive Techniques \- MDPI, accessed February 14, 2026, [https://www.mdpi.com/2079-9292/13/5/816](https://www.mdpi.com/2079-9292/13/5/816)
10. 12 Software Architecture Pitfalls and How to Avoid Them \- InfoQ, accessed February 14, 2026, [https://www.infoq.com/articles/avoid-architecture-pitfalls/](https://www.infoq.com/articles/avoid-architecture-pitfalls/)
11. (PDF) Distributed problem solving in social insects \- ResearchGate, accessed February 14, 2026, [https://www.researchgate.net/publication/220642562\_Distributed\_problem\_solving\_in\_social\_insects](https://www.researchgate.net/publication/220642562_Distributed_problem_solving_in_social_insects)
12. A test bed for insect-inspired robotic control \- PubMed, accessed February 14, 2026, [https://pubmed.ncbi.nlm.nih.gov/14599319/](https://pubmed.ncbi.nlm.nih.gov/14599319/)
13. \[P\] Stigmergy pattern for multi-agent LLM orchestration \- 80% token reduction \- Reddit, accessed February 14, 2026, [https://www.reddit.com/r/LocalLLaMA/comments/1qv3o3o/p\_stigmergy\_pattern\_for\_multiagent\_llm/](https://www.reddit.com/r/LocalLLaMA/comments/1qv3o3o/p_stigmergy_pattern_for_multiagent_llm/)
14. Built a production multi-agent system with stigmergy coordination (80% token reduction) · community · Discussion \#186260 \- GitHub, accessed February 14, 2026, [https://github.com/orgs/community/discussions/186260](https://github.com/orgs/community/discussions/186260)
15. Stigmergy Mechanism as a Form of Architectural Space Programming, accessed February 14, 2026, [https://www.hrpub.org/download/20220830/CEA4-14827486.pdf](https://www.hrpub.org/download/20220830/CEA4-14827486.pdf)
16. Dependencies \- Pydantic AI, accessed February 14, 2026, [https://ai.pydantic.dev/dependencies/](https://ai.pydantic.dev/dependencies/)
17. Overview \- Pydantic AI, accessed February 14, 2026, [https://ai.pydantic.dev/graph/](https://ai.pydantic.dev/graph/)
18. Debugging & Monitoring with Pydantic Logfire \- Pydantic AI, accessed February 14, 2026, [https://ai.pydantic.dev/logfire/](https://ai.pydantic.dev/logfire/)
19. Logfire Redis Integration & Setup Guide, accessed February 14, 2026, [https://logfire.pydantic.dev/docs/integrations/databases/redis/](https://logfire.pydantic.dev/docs/integrations/databases/redis/)
20. Agents \- Pydantic AI, accessed February 14, 2026, [https://ai.pydantic.dev/agent/](https://ai.pydantic.dev/agent/)
21. Ant Colony Optimization for Accelerated Pathway Identification in Connection Element Method Reservoir Models: A Fast-Track Solution for Large-Scale Simulations \- MDPI, accessed February 14, 2026, [https://www.mdpi.com/2227-9717/13/2/404](https://www.mdpi.com/2227-9717/13/2/404)
22. Introduction to Ant Colony Optimization \- GeeksforGeeks, accessed February 14, 2026, [https://www.geeksforgeeks.org/machine-learning/introduction-to-ant-colony-optimization/](https://www.geeksforgeeks.org/machine-learning/introduction-to-ant-colony-optimization/)
23. Stigmergic interaction in robotic multi-agent systems using virtual pheromones \- Diva-portal.org, accessed February 14, 2026, [http://www.diva-portal.org/smash/get/diva2:1887312/FULLTEXT01.pdf](http://www.diva-portal.org/smash/get/diva2:1887312/FULLTEXT01.pdf)
24. Ant Colony Optimization Explained: A Nature-Inspired Solution for Complex Problems, accessed February 14, 2026, [https://yugensys.com/2024/08/07/ant-colony-optimization/](https://yugensys.com/2024/08/07/ant-colony-optimization/)
25. Self-organized biotectonics of termite nests \- PNAS, accessed February 14, 2026, [https://www.pnas.org/doi/10.1073/pnas.2006985118](https://www.pnas.org/doi/10.1073/pnas.2006985118)
26. Stigmergy Mechanism as a Form of Architectural Space Programming \- ResearchGate, accessed February 14, 2026, [https://www.researchgate.net/publication/400601213\_Stigmergy\_Mechanism\_as\_a\_Form\_of\_Architectural\_Space\_Programming](https://www.researchgate.net/publication/400601213_Stigmergy_Mechanism_as_a_Form_of_Architectural_Space_Programming)
27. Parallel Execution \- Pydantic AI, accessed February 14, 2026, [https://ai.pydantic.dev/graph/beta/parallel/](https://ai.pydantic.dev/graph/beta/parallel/)
28. Joins & Reducers \- Pydantic AI, accessed February 14, 2026, [https://ai.pydantic.dev/graph/beta/joins/](https://ai.pydantic.dev/graph/beta/joins/)
29. A quorum sensing pattern for multi-agent self-organizing security systems \- ResearchGate, accessed February 14, 2026, [https://www.researchgate.net/publication/261416808\_A\_quorum\_sensing\_pattern\_for\_multi-agent\_self-organizing\_security\_systems](https://www.researchgate.net/publication/261416808_A_quorum_sensing_pattern_for_multi-agent_self-organizing_security_systems)
30. Collective Multi-Agent Navigation Model Based on Bacterial Quorum Sensing, accessed February 14, 2026, [http://www.scielo.org.co/scielo.php?script=sci\_arttext\&pid=S0123-921X2016000100002](http://www.scielo.org.co/scielo.php?script=sci_arttext&pid=S0123-921X2016000100002)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAZCAYAAABHLbxYAAACm0lEQVR4XrWWT6hPQRTHzyiEXlH+FiVCQooNFjxlgaRXkrUsJKVsZKXE8vVShLKxsJEoYiMLKc9CYiOlrClFCEV6vufO3Jk5Z2buffP+fOr77p3vmTlz7r3nd+8jmiDGKXVz/mQpZSz5TBTrmpZhnjbiDO5sA7TEm9NLtvyf2ujgFrQwm2WqMbLY3dDR2OhhLvRcm930XVZfnMwj/BlL3HDKsdVh6HkFrRT5e/eK6JpbiHEhh7UZkVyEYwbZ2BYdmBpktQug39BM4QYGoDGxxA+aEy70mo9FLIIGrYw7eu2wU6q4CQ1rM8p9g2wxe9xYYGwsueN8Cf9coKRa3kJHtEmcyyS5c/k/UMb/hlqXu/PNOD/oI4XmyyLn8ibrhBPih8jGt3sn5R6pQpfGA/BGjVtmQ0+0CeZDt7UJuP8yL/mG15TcreSOXKZkjsQH1dKt0H1pNeyHrmqzebyGZmnbUXrcMcOuT4t0BitIHn104Rzr+1rdpY5ajkGftIkNLpFqCWNf1NwK72M/4i8m7dUm2VbjAs668Qj0MoQ9qj3ki+wB/jyOHbKvjjtke4b7seUFtAq6Ai2L/JZR6JQ2ybYQF7DPjfltsyuEPT8oLjSqc40LHAhWw3p31I+h7b8/3pFNvRP6KJzAd+gr9Jn0qobG4v34xlWxGGsf4riW0l+yuAC1K8fOS2tc8MfnHSXp+jB0muw3m1/inCTmlxoHTHPHvmgzh3IvQCfbQX5FHv4AXKfwuFuGyJgzYZik5O/8U2iF8vvgvlU/n3jQzSZtkP3FbrOnxUz8z8mzNl6cFRiCTmjTMY7lEu694+6YR6bcSOkXsEHtfA66KK3JMQjNkZbcsvrS+6hOWFhQsCdOOWE5Mn1U71m9oGpFzdwS/wHIc3LsVlK/UwAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAZCAYAAAD9jjQ4AAAAxUlEQVR4XpVRuRECMQyUh6EGQjJaIL4iiCCEGogogCG8Bsiog6ELGiAmIWNgZflZPwTsnSRrtZZ8PhHAqevEvIi5C0xd8GCyaOX0dRu4SaaN1OQA/0G25T0FYhdOLbRajxXsWJNQuz38A/aGzeoOO6/xh5F1YkEsSKZFhhXg59IWDSjeEM5JSkNPWOsuvZkR9CVVgKtoSxM/EYc8TWQJe8HusKnpI+ibfl5RH0FMYyJBx/6rY0T42WGdVkrbU6A7oiXpUIQv38oS/iFzsowAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAZCAYAAADjRwSLAAAA3klEQVR4XoVPIQ5CMQztDBoFd4Bb4Al3wBAcGsEVAI8g4SI4EFwBFBr7QxCft7Xb79Yl/yVdX19fu40owHHy2dAoFFA+jYpsF+TXSJ7gHEulkcaPiBbVVslqU9IMoolzbtJVxy+gO2T/prIXsEEcoLVoPPMW44ORhVz3I28MyNdMFfeGiilyzt7wKp5CemAW3kS0tKYIR1ec71JWCLNfxMnKGQlXjeSX3MhNbiimThLMEWtRVsjJxOBNXjwjHsR8oNqJ3JDuiAaxj7r00qmVkpqKBaPV0O/rc4Rm7TWO/pK5HZxAzzitAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAaCAYAAACO5M0mAAAA/UlEQVR4Xn1SIQ5CMQzdHAoEjgTDDfAIBHfAowgX4BY4NA7BDdAIwnUggQTzeeu6rt3feEn/2te39mX5zgl8Tg1aPBrSSkmpLWuDapNJOrzZkRrESmXOlo0K/kn0BsqsOHnKLtTeKCdij/igeQBzBXVLegFf7NC8yEyPmtOEKeIFZpa90Y4gXLGG2LeLZIkOmxaUsbcg6nqPG62MVO2D8JQenS9sSSgS5yZMbISMfh6Is95xRDwRX67HLl68h8ksjP5geMfPs+RQyDOD4bmmU2RRPIPQEDUMXP39LGB1iM9aD6K18iMwIav0xmxQo89YlBNaF3yzU4Gx0k9M+QOHzh8LoD6uvAAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAZCAYAAABJhMI3AAADDUlEQVR4XuWWy6tOYRTG10YSA8XMNbdIGSgTpY4kDImOpOQvoFwGUmYGJow5A0VISYmJlCSJMlCMSEqUIsJAlHjWXmfv793rve9vf8d3+HWec877rPXe1r69RP8YhTZa0s04kVEi4Wz6Ha/f/u35ezMLA5+/5QTtutW95kGXoL3QrDo8WXBt3uX5MHID3U5pw+Q3dHH8/4XQM2hzcDiLnNwBEJneCB8m2e+jnhXkMUl+JSc3oDHHKrwdWrAYOqrNJtb8JW43hUbPOdA36DM03wyYRObiu9BbEw4c0yYFOmSyCPoJ3deBCWIu9Ak6Ds1WsRyiRdyjTRJ/nTYTmQE9hX5Ba3t25FrbTIUuQNehBSpW4xn1Cslrid/xXRAt4i5tkvhbtZkAf5TeQuegpSqWy2sU6Cr+nqHABirGi4l3OT2E7pixDogWcXvVMK4q+wd6zSi8US7eodrx3CIJbIB+QMsNj9/dt412E5mL71jOWdWIdUO0iDu1SeLHHoWVJI/sA0oqWUIKU5RzfzXa/POcZE3Tat/PGpLcER3IQa02WsTdDUd6pzzOR6BX0BYdSCyXiykkc/M7zYS9F8oLsZ7KC1zc1YGWRIt4sPxPrrhZxJlVkuAuTSFfwDfQPkq7U3xDMXwU4rmXKZ+9UeWlwvvj9blOIakEi3gTuqxNCnQIwKXZAb2j9seJL1SeWxuMFsnr8V8dkrucD89cTD475hAsIt89vGk+TlTwo8CH0yCB5W6EPkInpRnIJCvKC31i2Eug99D+KqEkMGQgVHEL+q7NCk//RhFVTtm8R5JwmuRg+sFI6Jez0Hlodc/yLFPgdWwjuYgvoWtUnzXd/dxuZ/B6XGp7hjbIX/n08ne43yYKPDJDg3MPTtNDTm4W5cAnaDIUMZdmzdJbbssyTPirzgdsPrS3ZQXJ+zhFI9SC4A406cnpmRH4HcN3IX/UBkZnq3Uz4OEnAO8OvIFEvP2tgGV0gntUt5tOv/0DDG7o/JFzenhzvQFyxhwW+dz/hMTNW2mFbYXISh4W9KJ12zaGmj9u+4P9PNynCwAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAZCAYAAACPQVaOAAADU0lEQVR4XuWYy48NQRTGTxHjnYi3CJkQLCRCPFbIeCywIFj4DyQiQmywIggrxCMWYoNEbIi9JRYWnrMQCXZILDxjNhMZ5+uq6qo6far7zmhD4pd8c/t+px6nHl3dd4gkRhp/g38iiT9JPEB1sGOlobBaGgVqc1X6WIsTR6uoee1xmPUVFx10M5F1hzVCBgpCA2pTA6yb0rSo5WsYbPmSn6yd0qzhO+uCNPPYvC6y3pEd8K04PBy4qbnHWp8EAivJ5jZH+NPI7kh9dRUwM5gh3CdoEBoSfj2HuK7Zfrm9x5SPd7PeplY+A8zMKXftB7swhKmublvMYH2TZkTTItTFSqZSGCg4QrZif+RpjGP1ZDSqKNFEOoE3WKcTh2g8hTb9YDeSPZgcZSPlYCvrEhnHyQ7YM4H1kepnCgfIJwoJSO0ORTvmFWuH8LZRtW0I968cFPwpqVUF96oEM4fK52WAWcM6w1rivmNiToZwM5WZJ1pFtr95SgzsIhtfIQMR/Vx3izQDhg7x31nSdul8JtvBuTRGa8V3LmNmCw9gx7yWJjOJdU14m8n2lTtRX7Du+i+ZCXnJ2osLLY6TF6tSoBQ4RjaBPi0I2B5J9nElfYBtjq0p2co6K7xNVD9YxA5KU+T1nHVAC4D3rKvSjDHhHonv6bgpbN8T4euQmU9uG8uAA7HqCFKyLyNY1evSVLjEfQxwN5lHgkESi6RLdkWfUnpgLCA7OW8iLwan/wZpMtPdpHsuR9cxKNOdOMZO0D7WM7JvLHXyD/K4sxht6+Fww4mOWHxgPHKfV1iTI99hEN8jXQpvTh6soEYuR8Jq+UE4FatUUbSVj/rKEVoHc1kzWbeF32XsROSe3+tYH6Tp+EF24sszRkHLxW3+8Cf126GX2xpDdtAx2MZJUr5P96kn3Mx2yv0YUMbZClGTNmlTORceEH6+5fv+wuqSZnOy5iElh1tT+XbBdrvPks9fTMJ+4RW49EYb+5QIO0LNOzGfUH77/w5qzxr4GVa+H6NWtE2Xez8DTnIcjp2CN8Bl0izpOOVBkW21lzBIU7zd9IhYrtpSUk/sCvIQzKP346gN1lGpiBO4x2j/U6oUJd0bLnzf0Vb8P9AGq3n/Ai3k1dBEQ7h95H5LE/gF/feqU1Rb34oAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAYCAYAAAAs7gcTAAABDklEQVR4XmNgAANGCIUGwKKYUoyYMjAmpmIwMAPKOADpWCAuxKYPGfxHws+QJdAUw7niDBDFRQg5DMVwMB2IPwMxE7oEuhYZoMB/oFg5iigmAIdGDFgxA4MlkkQ1EK+HmIlq8j0GkHsRYheB2AmILwBxDVwUDBjhIdEHxKchljE0gsSBNB+6yTDF24BYGC4K0YQCVBkgCqcA8U4wm5HBGSYJdzNU1wIg4w0DKMggAt5QZ8GUucEYIACNCLjuRCD+CZUrhFAIx4AUG8N5DAy6UDFlIL6FJA4GthAKySuMDAZAUh0hhO5NTAGsQlCA8DF+gK4InU8IYKjHEIABmItwKkAGGM7HpgvJOCJNxq4YADTMJrVeYF8oAAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG0AAAAZCAYAAAA7S6CBAAAE7ElEQVR4Xu2ZWahVVRjHv20pzXOQpQ2S2gARRBTRcKlHrYjegsDUVNDoQdRooIGERpoIeuilTJDwrXmgrkJlIAblSxNIiDSRDWSIhH3//a119tr/vdbeZ9jn3FP5g//de39rnTUP31pXxJH5l25p+kE6/D7Vs2zsmXT6hxgCq1UH2fgfY1b+d4oG1qlsaIE/VZ+xMafFSg6Y1GmqDar3VI9QWBMLVAci+aMjL5Vymx6lOiX4boV9mvkFbBwQzLKn3PscsQbqiUiDtMlNYmV8RbVe9YNqm+q8MFING1WvsVH5Vixd1qIgjgxau9mCRDP5W+o6rvc8UNATVW+oPnHf0k9CLXOLCnV9gOzgdS0fynkuB0T4UePOYGMA0vmOjV3R0EQzVftVa8QyQWVaILtO//ysmgxsxWuE+tDBCNJeJvX7LDoB7VEXB2A2Xs1GAmksHUa9nlH9oTpGimncI9FiPai6S/WE2NIzDpyt+k31OdmZSWlqh0weZVOZ7HCxNOZzSEG03apEov0uxQap0z3P6MUiOMrRqomEpquOUP0lBb4BtgS2qcAPSjRoHU9LXadZI2I7qRgD7pG6NAYAnRXOgrvFMsLyEEWLdrM+fpGiAQpl+XOp6hpn8+D9IlXD6LSqV6rfFla+bhryHWmOt5UNxNtie2OfpFthLxuUe8UKfDoHKFepnhTrAPCT2DLIHKa6MPg+M3ivxRX1OKnO4CZVKKqdv60Vq9c3HXOc86UYiCluUx3PxoArxH6/nQO6Id1dtoc9XjZ1oiPDfWJOSpgIb7yIl8f5F/C9WHlXhcZIA+FciXibOMCBwdzkrL0llsb1HOC4NXi/QyzuY4EtCZyESoO7SmAGIiHMqtAegtm0m41NRNJpDZ92Io89brnCgbgOP8vO4QAHZuxXbCTg2CGNkzjAwbP4oJb5RrJVgHuf3LfEzlZNSwT2wtjSCB6S+DKEdF9iY5uUO6z09ZxYfTBYiU68y8XifFqEVcg7NDEwPHVth4mCc6IHTlH81og4oJrLxpCsOKuk3HWEdQ6gVAkc0MuHTovQUNcOcHZ8xcsqnAlWU+Ini8Xb475xhsQytst9+yNPaoaB6ZrJ7WwkIkenTsmWlO05uFRf6N7fFfO6Kz7AkWJ3bU28IJZBzFkBnHmShsYcJWFjLnfPOWKjH7MLXmMJKvsNqhPKJkcREcsc8uCz4HyNgmWQ2+19sRUIV2rw5hEOR8Zw6e5yAb0Io4fhzD1fik13jGwPZvXDYndyU808sbJ/JHZBjP1nUsorT+yOFJ0Vnj0ZHNq53WLiS2nYJlVnkX1kLHZPLK3hJow9FOwQO3yPGdnXYrfwABfG1waBnq1S8bZT9LS2eN/iedWVYksjLicSRNMOjNHwWpAhRulmsqOjjpVmV3n4xOuE0Y5V4FXVhxTmQZyL2Tgg6JwP8rdM7hdbFreI3TiNlC/EnBBeYuDQoOJDIt4bdQS/CJevGIi6go19US7mStUl7h3LNnwN+Bwjx1f85ZJV5GPVr2Trgt47ow/eFLtM8M4Jg0uFuAMS0ntRcdYNuYy+h0G0lLh0xvp/BtnRmXeSzRFNZ5xYx4YxJxukTfHvdpxrpql2UtjA9F+sOvpJNfWblB1wGH9H6SpSl6TSyrC/YYZh7Z4oh42GVMlAXdgYMrLiwmOckCnaXA9RYWQd/7/mHwuaCmhcVC0AAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAZCAYAAADuWXTMAAABeUlEQVR4XqVUu0oEQRDsOQUNLjEyNTU11Mj7BRMRzDwFLxTR6HIDH6CCoR+hJn6BqJEgmF1qIqigiMha3dM7710Ei6vdnqqe7p0HR/QnmFTw8JaJ4gyBFLkyqBX/XkB4iega7KsaJJQxBZ7iO77xPgYPwB9wD9PGosyk4QX4CM6r7GHMBx5VKjMmwQfwKzUCbKJBhS53qbEPVjDXUyPAHPFkS4bhH3flivEnZfti+Dh47VHeqgrPkhI6DqLOkuvss15VXHOKQ1TqiGzejY7FZOGlzjDF1i6P2dOaTsx2MIccU3JURsRP4gsg+1fEOdlNHQSapG7zTiMaqjgiu743HS9q12Jllth8R7SEd1eTDsEV2HxxturEGKwY6uC5QbbICaQzjXfAcc2cIHvvA+TlavTh7Uok94NuwU5LvncQDXStV+A9uOxMj8ZS0+TPduTS7DJD8GeZVOThE9nJM2I19qmRV/4vor0oIzMyIZAKXgPaMvONaoH9i/4FQtlD7fiNPJIAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAZCAYAAAA14t7uAAABgUlEQVR4Xq2SsS5FQRCG/yWhIBqJiIZEq3Mr1dVoRCWiUvAECnQknkBEJ0rvQK1QaRS8A4VGFAph9sydu3Nm5+w5wpfMvTv/7MzO7hngnwgFT+EFRHNiSnKiQ5bJFslGldYvpziYK4zRz7dvhY47UeWFPXBBG/gzz8gKS2n/gOzjOdtmwUU/bKALeb2kXCAWDjhKwXbygkKKPII77g2VGnLN7PKtxAnI3rcNKdxwQCXLiHlMqNQeLd/pP1or0+Cib9Gxp5O/b9RP8m8GMYXNBM7BhY91jJdhk36+kloR964aLWMOwzEL4yY2MojtKG2SrOqWuCJ7oA4O2ZUPzOyCk29FULE78FxPKXWd7ATx+QLWwLlnEhTkgxUsbJiXuyd7IX2rLreRv79GOowsgZ8iPt98Oc3gbD5FmvUZskuyA7LttKVGNgp2KbySeq38J7IV5TdRL+UUXgBPhdBXa42TiiZV4dyqIcfpNFhV+I0asRHr50IJdRFpszOd9vqb1LGd+QH1uz87kjMYuQAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAZCAYAAABdEVzWAAACh0lEQVR4Xr2WTahNURTH1xEiyogBLxMjZcaI5PrI4I1kLB9lIkRCPjIwUSbCM9KbUFI+Bgy8YoZIUQplYkaY+HozEv//Wfucu84+63zd6/rVv7v3f+291zr77HPOFclI8lYrOg4floZ0DeFakuGmx6yDpqAH0PYoZhgk5SBzRBZBk5j6E7/noEvQH+hYYdR/5j70ClrpXNNvYYFOwLH+Bemy86C30I9irMBp0Z27lfZGVE3MhGjSbXFASasYFx3DnavHKdqxGpkrmtC9TYbFko1rRf1ibdglabLkfRyI2Cha1K84UKS+oDxqhlXN+C6acEcciLghOu5m0a5adniY7FPWKaYp9LLbuNyatZRqTo2t0KYo4MJkj2NTcQsbgoQr3kVjjTH58u6Zfg6TTTuXZ+EXgOeQVxvhzHOsShL5EFsZR0WL45t9BvRO9I3/JcS3hHgVj0TP3QtoM3QQ+gZdRdKH+KVmix6Ba9DnUPnFMJdr87N3lqaFoxj8Krqtc4J/BdoTYjuDF3MB6oUNYjFPRG8Vikk4b6bo/DHoHrQ09C1VT3m6LHdqr+gkJrsc2vtDjCyQftGEX4tp08+gz7n8xlqWQC+R7aPxVojenU4cgXaHNoubig7PSei4NQwsjBcSQ38V1sme7NvQQtGX/Fjbo3lC9PNzB3oNrS6G5YCUb/EG0Yt4mhkm2SzoeWifER3H40P2QYdDu/HhWSb9V8SbisGMnYKuQ+uDx3PKAmN43vjv5ZnxDkHnofnGM/hJQcInlMm53cHKW4QL9sTG+2fSY62Ui+gVuzaBU5hjVaJju8xoRdJtTTO2cZozwLEGI1/IWdGxFCfgWCOilKlkuNaI6JKpOLauF/MXxU5v+rj9Q94AAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAZCAYAAAArK+5dAAABvUlEQVR4XqWVzysFURTHz41Y+JH/QGykbNhR9ChrWyU29hbKUvkHLBRbpRRK9nq2noX8BVK2LMTSQs/3zLkzc+6dM/eZfPLtzv1+zz13Zt59D5GjelwidNlfOdEklqVDleWXqfI6hqEJaAbLlyCMNAmNhmVN8Lfhh25FzovoCTqQMk3YII0U5c0Lw7MA/UDf2ixo8N7UBoJa06YoE6Qi0buMcNVlqTCnD/ogM0u0jtgmaXAaB+CCJLuMgyackTTZigMqX91YHPQgeDxuwB/iNcmJuYI67KNql3yxq7ySeM5YnmywFzj26ViDXgKHcbRp+greYDY2meh+bqCv0Mq4J9vP2CF/QuyHo0QgpH6++Ah+knkEKzxD71Ar8s9JXs945GcskjR/5btM3AhncyS1h8re8CP7J8ovzFjHQUVJ/qOHJ3ADyp/yI5+2ZeXbpJ4AHEHzkN6AGYTaPdamKJa++bH4MvpkFdrnWbgJz/60bVHUweUDZis6BY9QP1/UtPM2n7WaCg//UxrRhi/3J7B2sR1YrvLWoVtoCOZdaUeYTSyzguO6FoZps8m/aP7Z6er82uoSz4XMtSNFz4Jm/AImE0p5kEUZVwAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAZCAYAAAAxFw7TAAABWElEQVR4XrVRvS6EQRS9I0QiW6lo6CRsIlERRDaUOi+h20TjRRTbiEKh8AJUXmIbnUqholMo1pnfO3Nn5vvJcpLz3bnn/s58RP8GFT4ZMjUTOqJcp2oBi6bYHGiZOheixvb4h5PSVt4rDyipa+AopmK7G7I6YgGcearojNn+zDDrpA8iN/wC1935DNznkEzNHjmFsldlj+g98Rgr4FMhcAy+JoqAvnIJRySvbjHBgB8pxu9SKuqLsNMVjtPChjfI0fqd8TjhGfwAT4Ii8AI+CO3UabqZ3d423AGXyL65rsuwR7bg0Hi8xbazOnYZVKItlzODHRduVYPSdRuwj05YTsJEnyT/O6Om0zV4Di6Cg0hfBf2gdkTtL8Bb+PcsGUxIX70R1SVpmIaMN028bvCpwW7i8+2cN2cd4rayrhkj8ECKBrZeNTQyfznxew5n9MkPue1FtYzyrX4BedMrn9oQKqEAAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAZCAYAAAA14t7uAAABqElEQVR4XsVTPS9EQRS90ymwdDqbEAWRSEQpWaVOqVFLlCKEhIjeD2ATdAqJSqVRKrZUoGGjotEoJBSc++brzrx5s7uJxEnO3Dfnnndm5u0s0X9CZWadEfvtXOilBareKTUYcWBlcIhcL43sLv4E+eDqbnUn16LktxYYAS/BHaFtgGfgitB6xgN4C/5gdV5/GzwFnwstu6cQsXGN9M445A6siVvxhnHXGqsQBzLqprZIB0ssGK3hJdVOphA9gaNuJjwcYIK1inGPNdQ+4Xy1DxrO+4IyJDULDv0KFKJPo1NsTqJsUf0QEaD2E4t9m+dH8ByeadfV3kPwAhxwug9Ri6RD5qMG35KWOewUhklw0zaBVegH8MzheV3oDidoNiOtQTp4CXUQVFjgnqs41bipx2DdqQy/aakWuCa+Kd7QVPpU4sgO+ncoZwj45gfx91NOegdvwC3nKFB0+ebkELTj3fE9vwJnQ1sx4T9Vhx176F34T1Gj4se1gqtjGI7MxGqJReL30lgmfaJhsB22ukCYHa+kZjBMRGInxCESuV4KXfsTxoTUE3p5/xdOYjz32XHqHgAAAABJRU5ErkJggg==>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAaCAYAAACD+r1hAAABA0lEQVR4XpVROw7CMAy1JSbExBEAcQdGjsCGYIMFMbGzMbGzwREYuBEj4gZISAjsOE2cxC3qA6fx+9RNC1AAjTbjGlF4C+Iv2ifaw5pRchWDSlSuJFCmLeSuvBdsqF5URzLcEOGutJhA94Mrbb9UgyBIP/amheJhRwyLM00SLlRvqh7VJ7AodzqEPg7fgmj8qBMRxcDkNNgqAXAFLoDPRBNSQcy8zL225lafOg1E+AmwzIUTpfiAXd/vqR5UfZDAGeQFMGQQrR1aR5C+1grDuDU+oEHl0JYwMYM/tZbjWtptzsEQPOUu+QOU9pKpR+XVmTSP/t800YOFWhHSmxiQSWGvrj97Gx1BP4tDhQAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAZCAYAAAAFbs/PAAABNklEQVR4Xn1SPUtDQRDcgxQiWASs/AFJoYV2Qaxtg/gfAiktLPwB6dPYSEgt2NpZCmJhEbCJjVjZpAhaGkKcvb3PzSYD83Znbu92771HVMHVEpqd2l13tkPOMPc04I4QmT1jvcIliqeI1+AtuAD365KMPbCrvEPwyxjDOz9FHuMVOAlGAXkBd9oGnsAbbTL6Ie6CR9h/QNLxO5fUc92HuCo4B1upQuB3HZMUBJlO+gVnxoXpAUVD7UOPKR5UmMwZwkV2UngGV/EDB3j5brUlX4wOrryu49+APnNNQhtcgqci85YOcp7zLDmCN5KPFhDbOPcY0gGeH0j+EF9hNetBMritAftS7L/IUvlMazrxFz5PykKsdZKcgDtRRLDaNJDAaB3VumNZCsrLckOjAON0G+pP2gZd+g93WCi7dYwBlwAAAABJRU5ErkJggg==>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAYCAYAAAAYl8YPAAAA+0lEQVR4Xq2TsRHCMAxFbXoaRmALlmAX9mAAJqBjAehSUnF0DMACWQBk4yiypO/kcrw7Eet/SfaZJIQWEQm/p7EdJSNlUAJ1ZcCyNqgN6ex4BTGpntGEunSPziXay7mzL+famCZ15K6DMmYwnMTueueV9SYoDeKeTpRdOJsN3nlPsUsLXDKH8dZ7Om4aWnGluNmIU9qT4kNxTkN8zLnz22iJ4UW/nVE9arUauKF4UKxAa0GYjbojuW/49WTNMxSlpKdYD+Xm08Jwi3xsTX8SWFSLsdi0tdDFIleWrmTsiQSV5hUs4V9zNMNNLpzvtck/B91tLDm4SG+sJYYvFbwWbBuSppcAAAAASUVORK5CYII=>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAYCAYAAAD3Va0xAAABNklEQVR4XrWTMUpEQQyGk1uItVh4BkELwULQwkNsZyfqJSwFsRMLO1sRW7sVC8ELWNgL1msmk3mTTCY7suAHeZn8ySTz5u0CGFA9qw+ZCnTlcDeanC3rNQJYI9sh2yVbtymONuNhNrNgQ/bvOiF8kS1Q6si/tgWa1OiFfQ+EA3oetrKDptyLT40uO3f64KUSFgVhm5ZbEn1CbnYicWE6qW9UuVDrc8ibPjiqw9I99agVxLdKJC1ffo1T0azGBnOi9DpKwme5qysRzkw6BOG2UY4hN/qR+FHlQvbJNqzEs08hN9sTPzzRfFr5ynJX1z6nBYQbyD/EiCfIjdJfKALvgIv4C7V3VDgie2vFP+EO54T/YNUhvM9v9sqIYEeRe+meJixJrYjr6ISQcSW2RcteWzFIh7TDfgH1tjA7d5syCAAAAABJRU5ErkJggg==>
