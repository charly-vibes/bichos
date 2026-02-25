"""Tests for ACO probability mathematics."""

from __future__ import annotations

import pytest

from bichos.agents.ant.aco import (
    compute_probabilities,
    evaporate,
    pheromone_deposit,
    stochastic_select,
)

# ── compute_probabilities ─────────────────────────────────────────────────────


def test_probabilities_sum_to_one() -> None:
    candidates = ["a", "b", "c"]
    probs = compute_probabilities(candidates, {}, {})
    assert abs(sum(probs.values()) - 1.0) < 1e-9


def test_uniform_when_no_pheromone_or_heuristic() -> None:
    candidates = ["x", "y", "z"]
    probs = compute_probabilities(candidates, {}, {})
    for p in probs.values():
        assert abs(p - 1 / 3) < 1e-6


def test_higher_pheromone_gets_higher_probability() -> None:
    candidates = ["low", "high"]
    pheromone = {"low": 1.0, "high": 10.0}
    probs = compute_probabilities(candidates, pheromone, {})
    assert probs["high"] > probs["low"]


def test_higher_heuristic_gets_higher_probability() -> None:
    candidates = ["dull", "sharp"]
    heuristic = {"dull": 1.0, "sharp": 5.0}
    probs = compute_probabilities(candidates, {}, heuristic)
    assert probs["sharp"] > probs["dull"]


def test_alpha_zero_ignores_pheromone() -> None:
    candidates = ["a", "b"]
    pheromone = {"a": 100.0, "b": 1.0}
    heuristic = {"a": 1.0, "b": 1.0}
    probs = compute_probabilities(candidates, pheromone, heuristic, alpha=0.0, beta=1.0)
    assert abs(probs["a"] - probs["b"]) < 1e-6


def test_beta_zero_ignores_heuristic() -> None:
    candidates = ["a", "b"]
    pheromone = {"a": 1.0, "b": 1.0}
    heuristic = {"a": 100.0, "b": 1.0}
    probs = compute_probabilities(candidates, pheromone, heuristic, alpha=1.0, beta=0.0)
    assert abs(probs["a"] - probs["b"]) < 1e-6


def test_empty_candidates_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        compute_probabilities([], {}, {})


def test_single_candidate_probability_is_one() -> None:
    probs = compute_probabilities(["only"], {}, {})
    assert abs(probs["only"] - 1.0) < 1e-9


# ── stochastic_select ─────────────────────────────────────────────────────────


def test_stochastic_select_returns_valid_node() -> None:
    probs = {"a": 0.2, "b": 0.5, "c": 0.3}
    result = stochastic_select(probs)
    assert result in probs


def test_stochastic_select_respects_weights() -> None:
    """With probability 1.0 on one node, it must always be selected."""
    probs = {"always": 1.0, "never": 0.0}
    for _ in range(20):
        assert stochastic_select(probs) == "always"


def test_stochastic_select_empty_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        stochastic_select({})


# ── pheromone_deposit ─────────────────────────────────────────────────────────


def test_deposit_increases_intensity() -> None:
    result = pheromone_deposit(current_intensity=10.0, delta=5.0, rho=0.1)
    # τ(t+1) = 0.9 * 10 + 5 = 14
    assert abs(result - 14.0) < 1e-9


def test_deposit_clamps_to_max() -> None:
    result = pheromone_deposit(current_intensity=99.0, delta=50.0, rho=0.0)
    assert result == 100.0


def test_deposit_clamps_to_zero() -> None:
    result = pheromone_deposit(current_intensity=0.0, delta=0.0, rho=1.0)
    assert result == 0.0


# ── evaporate ─────────────────────────────────────────────────────────────────


def test_evaporate_reduces_intensity() -> None:
    result = evaporate(current_intensity=10.0, rho=0.1)
    assert abs(result - 9.0) < 1e-9


def test_evaporate_full_rho_gives_zero() -> None:
    result = evaporate(current_intensity=50.0, rho=1.0)
    assert result == 0.0


def test_evaporate_zero_rho_unchanged() -> None:
    result = evaporate(current_intensity=42.0, rho=0.0)
    assert abs(result - 42.0) < 1e-9


def test_evaporate_never_negative() -> None:
    result = evaporate(current_intensity=0.001, rho=0.99)
    assert result >= 0.0
