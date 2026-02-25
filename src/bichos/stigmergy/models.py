"""Pydantic schemas for pheromone types in the bichos stigmergy system."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field


class PheromoneType(StrEnum):
    BUG = "bug"
    CURVATURE = "curvature"
    PERFORMANCE = "performance"
    ALERT = "alert"


class Pheromone(BaseModel):
    """Base pheromone deposited on a code path node."""

    key: str = Field(..., description="Cache key: '<type>:<path>:<name>'")
    pheromone_type: PheromoneType
    intensity: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        1.0, description="Current intensity in [0, 100]"
    )
    depositor: str = Field(..., description="Agent ID that deposited this pheromone")

    model_config = {"frozen": False}


class BugPheromone(Pheromone):
    """Pheromone left at a location where a bug was found."""

    pheromone_type: PheromoneType = PheromoneType.BUG
    severity: Annotated[int, Field(ge=1, le=5)] = Field(
        3, description="Bug severity 1 (low) – 5 (critical)"
    )
    file_path: str = Field(..., description="Relative path to the affected file")
    function_name: str = Field(..., description="Name of the affected function/method")
    description: str = Field(..., description="Short human-readable description")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        0.8, description="Model confidence in the bug report"
    )


class CurvaturePheromone(Pheromone):
    """Pheromone encoding the cyclomatic complexity of a code node."""

    pheromone_type: PheromoneType = PheromoneType.CURVATURE
    complexity: Annotated[int, Field(ge=1)] = Field(
        ..., description="Cyclomatic complexity (radon)"
    )
    loc: int = Field(..., ge=0, description="Lines of code in the function/class")
    file_path: str


class PerformancePheromone(Pheromone):
    """Pheromone deposited after a bee scout probes an endpoint."""

    pheromone_type: PheromoneType = PheromoneType.PERFORMANCE
    endpoint: str = Field(..., description="URL or function identifier probed")
    latency_ms: float = Field(
        ..., ge=0.0, description="Observed latency in milliseconds"
    )
    error_rate: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        0.0, description="Fraction of requests that failed"
    )


class AlertPheromone(Pheromone):
    """High-urgency pheromone for security or critical findings."""

    pheromone_type: PheromoneType = PheromoneType.ALERT
    threat_level: Annotated[int, Field(ge=1, le=5)] = Field(
        ..., description="Threat level 1 (info) – 5 (critical)"
    )
    category: str = Field(..., description="e.g. 'security', 'data-loss', 'crash'")
    message: str
