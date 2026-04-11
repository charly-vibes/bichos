# Bichos Tuning Guide

> **Purpose**: This guide helps users optimize bichos performance for their specific use case by adjusting ACO parameters, swarm sizing, and pheromone decay rates.

## 🎯 Quick Decision Tree

```
What do you want to optimize?

├─ Finding More Bugs
│  └─ Increase ant count (10 → 20)
│  └─ Increase α (pheromone weight: 1.0 → 1.5)
│  └─ Decrease ρ (slower decay: 0.1 → 0.05)
│
├─ Faster Analysis
│  └─ Decrease total agents (23 → 10-15)
│  └─ Increase ρ (faster decay: 0.1 → 0.3)
│  └─ Enable early stopping (no new bugs → terminate)
│
├─ Better Architecture Suggestions
│  └─ Increase termite count (5 → 10)
│  └─ Decrease curvature threshold (10 → 7)
│  └─ Increase termite model quality (GPT-4o-mini → GPT-4o)
│
├─ More Security Coverage
│  └─ Increase wasp count (3 → 7)
│  └─ Enable quorum sensing (1 wasp → 5 wasps per check)
│  └─ Decrease threat threshold (7 → 5)
│
└─ Lower Cost
   └─ Reduce agent counts (23 → 10)
   └─ Use cheaper models (GPT-4o → GPT-4o-mini)
   └─ Partition large repos (analyze incrementally)
```

## 📊 Swarm Sizing Recommendations

### By Codebase Size

| Codebase Size | Recommended Swarm | Minimal Swarm | Maximum Swarm |
|---------------|-------------------|---------------|---------------|
| **< 5K LOC** | 5 ants, 2 bees, 2 termites, 1 wasp | 3 ants, 1 bee, 1 termite, 1 wasp | 10 ants, 3 bees, 3 termites, 2 wasps |
| **5K-10K LOC** | 10 ants, 5 bees, 5 termites, 3 wasps *(default)* | 5 ants, 2 bees, 2 termites, 1 wasp | 20 ants, 10 bees, 10 termites, 5 wasps |
| **10K-50K LOC** | 20 ants, 10 bees, 10 termites, 5 wasps | 10 ants, 5 bees, 5 termites, 3 wasps | 50 ants, 20 bees, 20 termites, 10 wasps |
| **50K-100K LOC** | 50 ants, 20 bees, 20 termites, 10 wasps | 20 ants, 10 bees, 10 termites, 5 wasps | 100 ants, 40 bees, 40 termites, 20 wasps |
| **> 100K LOC** | Use partitioning (analyze modules separately) | - | - |

### By Analysis Focus

| Goal | Ant % | Bee % | Termite % | Wasp % | Example Swarm (20 total) |
|------|-------|-------|-----------|--------|---------------------------|
| **Bug Hunting** | 60% | 15% | 15% | 10% | 12 ants, 3 bees, 3 termites, 2 wasps |
| **Performance** | 20% | 50% | 20% | 10% | 4 ants, 10 bees, 4 termites, 2 wasps |
| **Architecture** | 20% | 15% | 55% | 10% | 4 ants, 3 bees, 11 termites, 2 wasps |
| **Security** | 20% | 15% | 15% | 50% | 4 ants, 3 bees, 3 termites, 10 wasps |
| **Balanced** *(default)* | 45% | 20% | 20% | 15% | 9 ants, 4 bees, 4 termites, 3 wasps |

## 🧮 ACO Parameter Tuning

### The Three Core Parameters

**α (Alpha) - Pheromone Weight**
- Controls how much agents follow historical trails
- Range: 0.5 - 3.0
- Default: 1.0

**β (Beta) - Heuristic Weight**
- Controls how much agents favor complex/interesting code
- Range: 0.5 - 5.0
- Default: 2.0

**ρ (Rho) - Evaporation Rate**
- Controls how quickly pheromones decay
- Range: 0.01 - 0.9
- Global default: 0.1 (overridden by per-type defaults below)
- Per-type defaults: bug=0.1, performance=0.5, curvature=0.05, alert=0.3

### Parameter Effects

#### α (Pheromone Weight) Effects

| α Value | Behavior | Use When | Example |
|---------|----------|----------|---------|
| **0.5** (Low) | Agents ignore pheromones, explore randomly | Codebase has many false positives from previous runs | Fresh start, clear cache |
| **1.0** (Default) | Balanced exploration/exploitation | Normal operation | Most codebases |
| **2.0** (High) | Agents strongly follow trails | Known problematic modules need deep analysis | Security-critical module |
| **3.0** (Very High) | Agents almost always follow strongest trail | Focused analysis on specific area | Bug cluster investigation |

**Example Configuration:**
```yaml
# config.yaml
aco:
  alpha: 1.5  # Slightly favor following trails
```

#### β (Heuristic Weight) Effects

| β Value | Behavior | Use When | Example |
|---------|----------|----------|---------|
| **0.5** (Low) | Agents ignore complexity, explore uniformly | Simple codebase, want full coverage | Tutorial/example code |
| **2.0** (Default) | Agents favor complex code 4x more (2² = 4) | Normal operation | Most codebases |
| **3.0** (High) | Agents favor complex code 27x more (3³ = 27) | Legacy code with complexity hotspots | Refactoring project |
| **5.0** (Very High) | Agents almost exclusively visit complex code | Want to find worst offenders | Complexity audit |

**Example Configuration:**
```yaml
# config.yaml
aco:
  beta: 3.0  # Strongly favor complex code
```

#### ρ (Evaporation Rate) Effects

| ρ Value | Half-Life | Behavior | Use When |
|---------|-----------|----------|----------|
| **0.01** (Very Slow) | ~69 iterations | Long memory, convergence | Stable codebase, long-term patterns |
| **0.05** (Slow) | ~14 iterations | Balanced memory | Default for bug detection |
| **0.1** (Default) | ~7 iterations | Moderate memory | Most use cases |
| **0.3** (Fast) | ~2 iterations | Short memory, high exploration | Rapidly changing codebase |
| **0.5** (Very Fast) | ~1 iteration | Minimal memory, almost random | Fresh exploration |

**Evaporation Math:**
```
Intensity after N iterations: I(N) = I₀ × (1 - ρ)^N
Half-life (intensity = 50%): N = ln(0.5) / ln(1 - ρ)

Example: ρ = 0.1
Half-life = ln(0.5) / ln(0.9) = 6.6 iterations
```

**Example Configuration:**
```yaml
# config.yaml
pheromone_decay:
  bug: 0.01      # Slow decay - remember bugs for ~70 iterations
  performance: 0.5  # Fast decay - performance is transient
  curvature: 0.05   # Moderate - architecture is stable
  alert: 0.3        # Fast - security alerts are urgent
```

### Parameter Combinations

#### Exploration-Heavy (Find New Issues)
```yaml
aco:
  alpha: 0.7   # Low - don't follow trails too much
  beta: 1.5    # Moderate - balance complexity and coverage
pheromone_decay:
  bug: 0.2     # Fast decay - don't get stuck on old bugs
```
**Effect:** Agents explore broadly, less influenced by history

#### Exploitation-Heavy (Deep Dive Known Areas)
```yaml
aco:
  alpha: 2.0   # High - follow pheromone trails
  beta: 3.0    # High - focus on complex areas
pheromone_decay:
  bug: 0.02    # Slow decay - remember issues longer
```
**Effect:** Agents converge on problematic areas

#### Balanced (Default)
```yaml
aco:
  alpha: 1.0
  beta: 2.0
pheromone_decay:
  bug: 0.1
```

## 🎚️ Common Tuning Scenarios

### Scenario 1: "Agents Keep Finding Same Bugs"

**Problem:** High pheromone trails cause agents to repeatedly visit same locations

**Solution:**
```yaml
pheromone_decay:
  bug: 0.3      # Increase decay rate (default 0.1)
aco:
  alpha: 0.5    # Reduce pheromone influence (default 1.0)
```

**Or:** Clear pheromone cache between runs
```bash
bichos clear-cache
bichos analyze /repo
```

### Scenario 2: "Missing Obvious Bugs"

**Problem:** Agents exploring too randomly, not following productive trails

**Solution:**
```yaml
aco:
  alpha: 1.5    # Increase pheromone influence (default 1.0)
  beta: 2.5     # Increase complexity preference (default 2.0)
swarm:
  ants: 20      # More agents (default 10)
```

### Scenario 3: "Analysis Takes Too Long"

**Problem:** Too many agents or too many iterations

**Solution:**
```yaml
swarm:
  ants: 5       # Reduce agents (default 10)
  bees: 2       # (default 5)
  termites: 2   # (default 5)
  wasps: 1      # (default 3)

performance:
  max_iterations: 20  # Stop after N cycles (default unlimited)
  early_stopping: true  # Stop if no new findings in 5 cycles
```

### Scenario 4: "Too Many False Positives"

**Problem:** Agents reporting non-issues

**Solution:**
```yaml
detection:
  confidence_threshold: 0.8  # Increase threshold (default 0.5)

wasp:
  quorum_size: 5       # Require more agents to agree (default 1)
  quorum_threshold: 3  # 3 out of 5 must agree (default majority)
```

### Scenario 5: "Want Deeper Analysis of Specific Module"

**Problem:** Need focused exploration of one area

**Solution:**
```yaml
scope:
  focus_modules:
    - "src/auth/**"
    - "src/payment/**"

aco:
  alpha: 2.0    # Strong trail following
  beta: 1.0     # Don't just focus on complex parts

swarm:
  ants: 30      # More agents for focused area
```

**Or:** Pre-seed pheromones
```bash
bichos seed-pheromone --module "src/auth" --intensity 50
bichos analyze /repo
```

## 🔬 Advanced: Per-Agent-Type Configuration

### Ant-Specific Tuning

```yaml
ant:
  model: "openai:gpt-4o"        # Model for reasoning
  max_path_depth: 50            # Max functions to explore per path
  bug_severity_threshold: 5     # Only report bugs >= severity 5
  aco:
    alpha: 1.2   # Ants follow trails slightly more
    beta: 2.0
```

### Bee-Specific Tuning

```yaml
bee:
  model: "openai:gpt-4o-mini"  # Faster, cheaper for analysis
  probe_iterations: 10            # How many times to measure
  recruitment_strategy: "proportional"  # or "threshold"
  latency_threshold: 1000         # Only flag if > 1000ms
```

### Termite-Specific Tuning

```yaml
termite:
  model: "anthropic:claude-3-5-sonnet"
  curvature_threshold: 10        # Trigger refactoring if > 10
  max_complexity: 20              # Flag functions > 20 complexity
  check_layer_violations: true
  check_circular_deps: true
```

### Wasp-Specific Tuning

```yaml
wasp:
  model: "openai:gpt-4o"  # Large context for pattern matching
  quorum_sensing: true             # Use multiple agents
  quorum_size: 5
  threat_threshold: 7              # Only alert if >= 7/10
  scan_for_secrets: true
  scan_for_injection: true
```

## 📈 Monitoring and Iteration

### What to Monitor

**After Each Run, Check:**
1. **Coverage**: What % of codebase was visited?
   ```bash
   bichos stats --coverage
   ```
   - Target: > 80% for thorough analysis
   - If low: Increase agents or decrease α (more exploration)

2. **Pheromone Distribution**: Are trails concentrated or spread?
   ```bash
   bichos stats --heatmap
   ```
   - Concentrated: Good (found problem areas)
   - Too spread: Increase β (focus on complexity)
   - Too concentrated: Increase ρ (faster decay)

3. **Findings per Agent**: Are all agents contributing?
   ```bash
   bichos stats --agent-efficiency
   ```
   - Some idle: Reduce swarm size
   - All busy but no findings: Increase iterations or adjust thresholds

4. **Cost per Finding**:
   ```bash
   bichos stats --cost-analysis
   ```
   - High cost/finding: Reduce agents or use cheaper models
   - Low findings: Increase agent quality or count

### Iterative Tuning Process

**Week 1: Baseline**
```yaml
# Use defaults, measure results
swarm: {ants: 10, bees: 5, termites: 5, wasps: 3}
aco: {alpha: 1.0, beta: 2.0}
pheromone_decay: {bug: 0.1}
```

**Week 2: Optimize for Your Codebase**
- Adjust based on Week 1 findings
- Change ONE parameter at a time
- Measure impact

**Week 3: Fine-Tune**
- Dial in optimal swarm size
- Tune ACO parameters for best F1 score
- Set cost limits

**Week 4: Lock Configuration**
- Document chosen parameters
- Add to CI/CD pipeline
- Review quarterly

## 🔧 Configuration File Reference

### Complete Example

```yaml
# bichos-config.yaml
version: 1

# Swarm sizing
swarm:
  ants: 10
  bees: 5
  termites: 5
  wasps: 3

# ACO parameters
aco:
  alpha: 1.0      # Pheromone weight
  beta: 2.0       # Heuristic weight

# Pheromone decay rates
pheromone_decay:
  bug: 0.1
  performance: 0.5
  curvature: 0.05
  alert: 0.3

# LLM models
models:
  ant: "openai:gpt-4o"
  bee: "openai:gpt-4o-mini"
  termite: "anthropic:claude-3-5-sonnet"
  wasp: "openai:gpt-4o"

# Detection thresholds
thresholds:
  bug_severity: 5
  performance_latency: 1000  # ms
  curvature: 10
  security_threat: 7

# Performance settings
performance:
  max_iterations: 0  # 0 = unlimited
  early_stopping: false
  timeout: 3600      # seconds

# Cost controls
cost:
  max_per_analysis: 50  # USD
  warn_threshold: 30    # USD

# Scope
scope:
  include:
    - "src/**/*.py"
  exclude:
    - "tests/**"
    - "venv/**"
  focus_modules: []  # Empty = analyze all
```

### Usage

```bash
# Use custom config
bichos analyze /repo --config bichos-config.yaml

# Override specific params
bichos analyze /repo --config bichos-config.yaml \
  --ants 20 \
  --alpha 1.5
```

## 🎓 Learning Resources

**Understanding ACO:**
- Read: `research.md` section on Ant Colony Optimization
- Experiment: Visualize pheromone trails with `bichos viz --pheromones`

**Parameter Sensitivity:**
- Run: `bichos benchmark-params --vary alpha --range 0.5:3.0`
- Generates: Report showing F1 score vs α

**Community Configs:**
- Share: `bichos share-config` (anonymizes repo details)
- Browse: `bichos config-gallery`
