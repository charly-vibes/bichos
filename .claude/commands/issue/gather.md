---
name: Issue: Gather
description: Stage 1/3 of the Issue Pipeline. Research a topic, save findings as a wai artifact for /issue:create.
category: Issue Pipeline
tags: [issues, research, wai, gather]
---

# Issue: Gather — Stage 1 of 3

Research a topic or feature area before breaking it into issues.
Save findings as a wai artifact so `/issue:create` can read them without re-reading the codebase.

TOPIC TO RESEARCH:
$ARGUMENTS

---

## STEP 1: Orient

Check for existing context to avoid duplicating work:

```bash
wai search "$ARGUMENTS"        # existing artifacts on this topic
bd list --status=open          # existing issues to avoid duplicates
openspec list                  # active change proposals
```

## STEP 2: Codebase Research

Locate relevant code using Glob, Grep, and Read tools:
- Find files related to the topic
- Read the most important files completely — track file:line references
- Check relevant specs: `openspec show <name>` if applicable
- Document what EXISTS, where it lives, and how it works

**You are a documentarian, not an evaluator.**
Describe what IS. Do not suggest improvements or refactors.

## STEP 3: Structure Findings

Produce a structured research summary:

```
## Current state
<what already exists — code, specs, existing issues>

## Gaps
<what's missing, undefined, or ambiguous>

## Scope
<what's in vs out for this feature area>

## Dependencies
<what must exist before this work starts>

## Proposed work units
- <unit 1: one atomic task>
- <unit 2: one atomic task>
- ...
```

## STEP 4: Save to wai

```bash
wai add research "TOPIC: $ARGUMENTS

<paste your structured findings here>"
```

The artifact must contain enough context that `/issue:create` can create issues
WITHOUT re-reading the codebase.

## OUTPUT

Report:
- Wai artifact saved (confirm with `wai search "$ARGUMENTS"`)
- Number of proposed work units
- Any blockers or ambiguities requiring human decision
- Recommended next step: `/issue:create`
