"""ACO (Ant Colony Optimisation) probability mathematics for bichos."""

from __future__ import annotations

import random


def compute_probabilities(
    candidates: list[str],
    pheromone: dict[str, float],
    heuristic: dict[str, float],
    alpha: float = 1.0,
    beta: float = 2.0,
) -> dict[str, float]:
    """Compute ACO selection probabilities for a set of candidate nodes.

    Implements the standard ACO formula:

        P_ij = (τ_ij^α · η_ij^β) / Σ_k (τ_ik^α · η_ik^β)

    Args:
        candidates: Node identifiers to choose from.
        pheromone:  Mapping node → pheromone intensity τ (defaults to 1.0 if absent).
        heuristic:  Mapping node → heuristic desirability η (defaults to 1.0 if absent).
        alpha:      Pheromone exponent α (controls trail influence).
        beta:       Heuristic exponent β (controls heuristic influence).

    Returns:
        Mapping node → selection probability, summing to 1.0.

    Raises:
        ValueError: If candidates is empty.
    """
    if not candidates:
        raise ValueError("candidates must be non-empty")

    weights: dict[str, float] = {}
    for node in candidates:
        tau = max(pheromone.get(node, 1.0), 1e-9)
        eta = max(heuristic.get(node, 1.0), 1e-9)
        weights[node] = (tau**alpha) * (eta**beta)

    total = sum(weights.values())
    if total == 0.0:
        # Uniform fallback (shouldn't happen given 1e-9 floor)
        uniform = 1.0 / len(candidates)
        return {node: uniform for node in candidates}

    return {node: w / total for node, w in weights.items()}


def stochastic_select(probabilities: dict[str, float]) -> str:
    """Select a node by roulette-wheel (stochastic) selection.

    Args:
        probabilities: Mapping node → probability (must sum ≈ 1.0).

    Returns:
        The selected node identifier.

    Raises:
        ValueError: If probabilities is empty.
    """
    if not probabilities:
        raise ValueError("probabilities must be non-empty")

    nodes = list(probabilities.keys())
    weights = [probabilities[n] for n in nodes]
    return random.choices(nodes, weights=weights, k=1)[0]


def pheromone_deposit(current_intensity: float, delta: float, rho: float) -> float:
    """Apply evaporation then deposit new pheromone.

    Implements: τ(t+1) = (1 - ρ) · τ(t) + Δτ

    Args:
        current_intensity: Current pheromone intensity τ(t).
        delta:             Amount to deposit Δτ.
        rho:               Evaporation rate ρ ∈ [0, 1].

    Returns:
        Updated intensity clamped to [0, 100].
    """
    updated = (1.0 - rho) * current_intensity + delta
    return max(0.0, min(100.0, updated))


def evaporate(current_intensity: float, rho: float) -> float:
    """Apply evaporation only (no deposit).

    Implements: τ(t+1) = (1 - ρ) · τ(t)

    Args:
        current_intensity: Current pheromone intensity τ(t).
        rho:               Evaporation rate ρ ∈ [0, 1].

    Returns:
        Updated intensity (≥ 0.0).
    """
    return max(0.0, (1.0 - rho) * current_intensity)
