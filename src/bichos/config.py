"""HiveConfig — centralised configuration for a bichos analysis run."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, model_validator


class ACOConfig(BaseModel):
    """Ant Colony Optimisation hyperparameters."""

    alpha: float = Field(1.0, ge=0.0, description="Pheromone trail weight (τ^α)")
    beta: float = Field(2.0, ge=0.0, description="Heuristic weight (η^β)")
    rho: float = Field(0.1, ge=0.0, le=1.0, description="Evaporation rate ρ ∈ [0, 1]")
    q: float = Field(1.0, gt=0.0, description="Pheromone deposit constant Q")


class StigmergyConfig(BaseModel):
    """Pheromone cache settings."""

    cache_dir: Path = Field(
        Path(".bichos_cache"), description="Directory for diskcache storage"
    )
    default_ttl: int = Field(3600, gt=0, description="Default TTL in seconds")
    bug_ttl: int = Field(86400, gt=0, description="Bug pheromone TTL in seconds")
    max_intensity: float = Field(
        100.0, gt=0.0, description="Maximum pheromone intensity"
    )
    min_intensity: float = Field(
        0.01, ge=0.0, description="Minimum intensity before pruning"
    )


class HiveConfig(BaseModel):
    """Top-level configuration for a bichos swarm analysis."""

    # Agent counts
    ant_count: int = Field(5, ge=1, le=50, description="Number of Ant Forager agents")

    # Model selection
    ant_model: str = Field(
        "openai:gpt-4o", description="PydanticAI model string for Ant agents"
    )

    # ACO parameters
    aco: ACOConfig = Field(default_factory=ACOConfig)

    # Stigmergy / cache
    stigmergy: StigmergyConfig = Field(default_factory=StigmergyConfig)

    # Analysis limits
    max_files: int = Field(
        500, ge=1, description="Maximum files to include in code graph"
    )
    max_tokens_per_ant: int = Field(
        4096, ge=256, description="Token budget per ant agent run"
    )

    # Confidence threshold for reporting bugs
    min_confidence: float = Field(
        0.7, ge=0.0, le=1.0, description="Minimum bug confidence to include in report"
    )

    @model_validator(mode="after")
    def _validate_intensity_range(self) -> HiveConfig:
        if self.stigmergy.min_intensity >= self.stigmergy.max_intensity:
            raise ValueError(
                "stigmergy.min_intensity must be less than stigmergy.max_intensity"
            )
        return self

    @classmethod
    def default(cls) -> HiveConfig:
        """Return a HiveConfig with sensible defaults."""
        return cls()
