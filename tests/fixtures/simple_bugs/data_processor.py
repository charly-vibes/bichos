"""Data processing utilities — clean module (no planted bugs)."""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


def flatten(nested: list[list[T]]) -> list[T]:
    """Flatten one level of nesting."""
    result: list[T] = []
    for sublist in nested:
        result.extend(sublist)
    return result


def chunk(items: list[T], size: int) -> list[list[T]]:
    """Split a list into fixed-size chunks."""
    if size <= 0:
        raise ValueError(f"Chunk size must be positive, got {size}")
    return [items[i : i + size] for i in range(0, len(items), size)]


def deduplicate(items: list[T]) -> list[T]:
    """Return unique items preserving insertion order."""
    seen: set[object] = set()
    out: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide with a safe fallback for zero denominator."""
    if denominator == 0:
        return default
    return numerator / denominator
