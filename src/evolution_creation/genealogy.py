"""Baseline genealogical ancestry models.

This module intentionally begins with a simple Wright-Fisher-like pedigree model.
It tracks genealogical ancestry only. It does not model DNA, recombination,
selection, geography, or historical demography.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FounderSpreadResult:
    """Output from one founder-spread simulation."""

    fractions: np.ndarray
    population_size: int
    founder_count: int
    generations: int
    seed: int | None

    @property
    def extinct(self) -> bool:
        """Whether all tagged founder lineages disappear by the final generation."""
        return bool(self.fractions[-1] == 0.0)

    @property
    def fixed(self) -> bool:
        """Whether everyone in the final generation descends from a tagged founder."""
        return bool(self.fractions[-1] == 1.0)


def _validate_inputs(population_size: int, generations: int, founder_count: int) -> None:
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 1 <= founder_count <= population_size:
        raise ValueError("founder_count must be between 1 and population_size")


def simulate_founder_spread(
    population_size: int = 1_000,
    generations: int = 50,
    founder_count: int = 1,
    seed: int | None = None,
) -> FounderSpreadResult:
    """Simulate spread of genealogical ancestry from tagged founder(s).

    Each generation contains population_size individuals. Every child samples
    two parents independently and uniformly from the previous generation.
    A child is tagged as a genealogical descendant when either parent is tagged.

    This permits the same individual to be sampled twice as the two parents.
    That choice keeps the baseline model mathematically transparent and will be
    relaxed in later models.
    """
    _validate_inputs(population_size, generations, founder_count)

    rng = np.random.default_rng(seed)

    ancestry = np.zeros(population_size, dtype=bool)
    ancestry[:founder_count] = True

    fractions = np.empty(generations + 1, dtype=float)
    fractions[0] = ancestry.mean()

    for generation in range(1, generations + 1):
        parent_a = rng.integers(0, population_size, size=population_size)
        parent_b = rng.integers(0, population_size, size=population_size)
        ancestry = ancestry[parent_a] | ancestry[parent_b]
        fractions[generation] = ancestry.mean()

    return FounderSpreadResult(
        fractions=fractions,
        population_size=population_size,
        founder_count=founder_count,
        generations=generations,
        seed=seed,
    )


def simulate_replicates(
    population_size: int = 1_000,
    generations: int = 50,
    founder_count: int = 1,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Run independent stochastic replicates and return ancestry-fraction curves."""
    _validate_inputs(population_size, generations, founder_count)
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(0, np.iinfo(np.uint32).max, size=replicates)

    curves = [
        simulate_founder_spread(
            population_size=population_size,
            generations=generations,
            founder_count=founder_count,
            seed=int(child_seed),
        ).fractions
        for child_seed in child_seeds
    ]
    return np.vstack(curves)


def deterministic_random_mating_curve(
    initial_fraction: float,
    generations: int,
) -> np.ndarray:
    """Infinite-population approximation: f[t+1] = 1 - (1 - f[t])**2."""
    if not 0.0 <= initial_fraction <= 1.0:
        raise ValueError("initial_fraction must be between 0 and 1")
    if generations < 0:
        raise ValueError("generations must be non-negative")

    curve = np.empty(generations + 1, dtype=float)
    curve[0] = initial_fraction
    for generation in range(generations):
        curve[generation + 1] = 1.0 - (1.0 - curve[generation]) ** 2
    return curve
