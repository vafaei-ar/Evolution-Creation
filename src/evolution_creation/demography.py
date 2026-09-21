"""Variable-demography models for genealogical ancestry.

This module separates three ideas that are easy to conflate:

1. total population size,
2. the fraction carrying a genealogical ancestry tag, and
3. overlapping descendant sets after intermarriage.

Under random mating, descendants of one founder and descendants of the original
background population are not disjoint subpopulations. A child can belong to
both descendant sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class DemographicSpreadResult:
    """Founder ancestry under a time-varying population-size schedule."""

    population_sizes: np.ndarray
    descendant_counts: np.ndarray
    founder_count: int
    ancestry_parent_weight: float
    seed: int | None

    @property
    def fractions(self) -> np.ndarray:
        return self.descendant_counts / self.population_sizes

    @property
    def extinct(self) -> bool:
        return bool(self.descendant_counts[-1] == 0)

    @property
    def fixed(self) -> bool:
        return bool(self.descendant_counts[-1] == self.population_sizes[-1])


@dataclass(frozen=True)
class OverlapSpreadResult:
    """Two overlapping genealogical descendant sets.

    Category order is:
    0 founder-only
    1 background-only
    2 both
    3 neither
    """

    population_sizes: np.ndarray
    category_counts: np.ndarray
    founder_count: int
    seed: int | None

    @property
    def founder_descendant_fraction(self) -> np.ndarray:
        return (
            self.category_counts[:, 0] + self.category_counts[:, 2]
        ) / self.population_sizes

    @property
    def background_descendant_fraction(self) -> np.ndarray:
        return (
            self.category_counts[:, 1] + self.category_counts[:, 2]
        ) / self.population_sizes

    @property
    def both_fraction(self) -> np.ndarray:
        return self.category_counts[:, 2] / self.population_sizes

    @property
    def founder_only_fraction(self) -> np.ndarray:
        return self.category_counts[:, 0] / self.population_sizes

    @property
    def background_only_fraction(self) -> np.ndarray:
        return self.category_counts[:, 1] / self.population_sizes


def validate_population_schedule(population_sizes: Sequence[int]) -> np.ndarray:
    """Validate a population schedule including generation zero."""
    sizes = np.asarray(population_sizes, dtype=int)
    if sizes.ndim != 1 or sizes.size < 1:
        raise ValueError("population_sizes must be a one-dimensional sequence")
    if np.any(sizes < 2):
        raise ValueError("every generation must contain at least 2 individuals")
    return sizes


def constant_population_schedule(
    population_size: int,
    generations: int,
) -> np.ndarray:
    """Return a fixed population size for generation 0 through generations."""
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    if generations < 0:
        raise ValueError("generations must be non-negative")
    return np.full(generations + 1, population_size, dtype=int)


def exponential_population_schedule(
    initial_population: int,
    growth_rate: float,
    generations: int,
) -> np.ndarray:
    """Deterministic exponential growth schedule.

    growth_rate is the continuous per-generation rate used in
    N(t) = N0 * exp(growth_rate * t).
    """
    if initial_population < 2:
        raise ValueError("initial_population must be at least 2")
    if generations < 0:
        raise ValueError("generations must be non-negative")

    t = np.arange(generations + 1, dtype=float)
    sizes = np.rint(initial_population * np.exp(growth_rate * t)).astype(int)
    return np.maximum(sizes, 2)


def logistic_population_schedule(
    initial_population: int,
    carrying_capacity: int,
    growth_rate: float,
    generations: int,
) -> np.ndarray:
    """Smooth logistic growth schedule approaching carrying_capacity.

    Uses the closed-form logistic curve

    N(t) = K / (1 + ((K - N0) / N0) * exp(-r t)).
    """
    if initial_population < 2:
        raise ValueError("initial_population must be at least 2")
    if carrying_capacity < initial_population:
        raise ValueError(
            "carrying_capacity must be at least initial_population"
        )
    if growth_rate < 0:
        raise ValueError("growth_rate must be non-negative")
    if generations < 0:
        raise ValueError("generations must be non-negative")

    t = np.arange(generations + 1, dtype=float)
    if carrying_capacity == initial_population:
        return constant_population_schedule(initial_population, generations)

    ratio = (carrying_capacity - initial_population) / initial_population
    sizes = carrying_capacity / (1.0 + ratio * np.exp(-growth_rate * t))
    sizes = np.rint(sizes).astype(int)
    sizes[0] = initial_population
    return np.maximum(sizes, 2)


def apply_population_bottleneck(
    population_sizes: Sequence[int],
    start_generation: int,
    duration: int,
    bottleneck_size: int,
) -> np.ndarray:
    """Replace a finite interval of a schedule with a bottleneck size."""
    sizes = validate_population_schedule(population_sizes).copy()
    if not 0 <= start_generation < sizes.size:
        raise ValueError("start_generation is outside the schedule")
    if duration < 1:
        raise ValueError("duration must be at least 1")
    if bottleneck_size < 2:
        raise ValueError("bottleneck_size must be at least 2")

    end = min(start_generation + duration, sizes.size)
    sizes[start_generation:end] = bottleneck_size
    return sizes


def _weighted_parent_tag_probability(
    ancestry_fraction: float,
    ancestry_parent_weight: float,
) -> float:
    if ancestry_parent_weight <= 0:
        raise ValueError("ancestry_parent_weight must be positive")
    numerator = ancestry_parent_weight * ancestry_fraction
    denominator = numerator + (1.0 - ancestry_fraction)
    if denominator == 0.0:
        return 0.0
    return float(numerator / denominator)


def deterministic_ancestry_fraction_curve(
    initial_fraction: float,
    generations: int,
    ancestry_parent_weight: float = 1.0,
) -> np.ndarray:
    """Infinite-population ancestry-fraction recurrence.

    With weight 1, f[t+1] = 1 - (1 - f[t])**2. The recurrence does not depend
    on total population size. Population size matters for counts and finite-
    population stochastic extinction, but not this random-mating expectation.
    """
    if not 0.0 <= initial_fraction <= 1.0:
        raise ValueError("initial_fraction must lie between 0 and 1")
    if generations < 0:
        raise ValueError("generations must be non-negative")

    curve = np.empty(generations + 1, dtype=float)
    curve[0] = initial_fraction

    for generation in range(generations):
        parent_tag_probability = _weighted_parent_tag_probability(
            curve[generation],
            ancestry_parent_weight,
        )
        curve[generation + 1] = 1.0 - (1.0 - parent_tag_probability) ** 2

    return curve


def deterministic_descendant_counts(
    population_sizes: Sequence[int],
    founder_count: int = 1,
    ancestry_parent_weight: float = 1.0,
) -> np.ndarray:
    """Expected founder-descendant counts for a demographic schedule."""
    sizes = validate_population_schedule(population_sizes)
    if not 1 <= founder_count <= sizes[0]:
        raise ValueError("founder_count must fit in generation zero")

    fractions = deterministic_ancestry_fraction_curve(
        initial_fraction=founder_count / sizes[0],
        generations=sizes.size - 1,
        ancestry_parent_weight=ancestry_parent_weight,
    )
    return fractions * sizes


def simulate_demographic_founder_spread(
    population_sizes: Sequence[int],
    founder_count: int = 1,
    ancestry_parent_weight: float = 1.0,
    seed: int | None = None,
) -> DemographicSpreadResult:
    """Simulate founder ancestry with changing total population size.

    Only the count of tagged individuals is required. Conditional on the
    current tagged fraction, the probability a sampled parent is tagged is
    adjusted by ancestry_parent_weight. Each child is tagged if either of two
    independently sampled parents is tagged.
    """
    sizes = validate_population_schedule(population_sizes)
    if not 1 <= founder_count <= sizes[0]:
        raise ValueError("founder_count must fit in generation zero")
    if ancestry_parent_weight <= 0:
        raise ValueError("ancestry_parent_weight must be positive")

    rng = np.random.default_rng(seed)
    counts = np.empty(sizes.size, dtype=int)
    counts[0] = founder_count

    for generation in range(sizes.size - 1):
        if counts[generation] == 0:
            counts[generation + 1 :] = 0
            break

        fraction = counts[generation] / sizes[generation]
        parent_tag_probability = _weighted_parent_tag_probability(
            fraction,
            ancestry_parent_weight,
        )
        child_tag_probability = 1.0 - (1.0 - parent_tag_probability) ** 2
        counts[generation + 1] = rng.binomial(
            sizes[generation + 1],
            child_tag_probability,
        )

    return DemographicSpreadResult(
        population_sizes=sizes,
        descendant_counts=counts,
        founder_count=founder_count,
        ancestry_parent_weight=ancestry_parent_weight,
        seed=seed,
    )


def simulate_demographic_replicates(
    population_sizes: Sequence[int],
    founder_count: int = 1,
    ancestry_parent_weight: float = 1.0,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Return founder-descendant fractions for repeated simulations."""
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    sizes = validate_population_schedule(population_sizes)
    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(
        0,
        np.iinfo(np.uint32).max,
        size=replicates,
    )
    curves = [
        simulate_demographic_founder_spread(
            population_sizes=sizes,
            founder_count=founder_count,
            ancestry_parent_weight=ancestry_parent_weight,
            seed=int(child_seed),
        ).fractions
        for child_seed in child_seeds
    ]
    return np.vstack(curves)


def simulate_overlapping_ancestry_sets(
    population_sizes: Sequence[int],
    founder_count: int = 1,
    seed: int | None = None,
) -> OverlapSpreadResult:
    """Track descendants of founders and background as overlapping sets.

    Generation zero is partitioned into founder-only and background-only
    individuals. Children inherit each ancestry tag independently through their
    two sampled parents. After intermarriage, the "founder descendants" and
    "background descendants" sets overlap.
    """
    sizes = validate_population_schedule(population_sizes)
    if not 1 <= founder_count < sizes[0]:
        raise ValueError(
            "founder_count must be at least 1 and smaller than generation zero"
        )

    rng = np.random.default_rng(seed)
    counts = np.zeros((sizes.size, 4), dtype=int)
    counts[0, 0] = founder_count
    counts[0, 1] = sizes[0] - founder_count

    for generation in range(sizes.size - 1):
        current = counts[generation] / sizes[generation]
        founder_only, background_only, both, neither = current

        no_founder_parent = background_only + neither
        no_background_parent = founder_only + neither

        p_neither = neither**2
        p_founder_only = no_background_parent**2 - p_neither
        p_background_only = no_founder_parent**2 - p_neither
        p_both = 1.0 - p_founder_only - p_background_only - p_neither

        probabilities = np.array(
            [p_founder_only, p_background_only, p_both, p_neither],
            dtype=float,
        )
        probabilities = np.clip(probabilities, 0.0, 1.0)
        probabilities /= probabilities.sum()

        counts[generation + 1] = rng.multinomial(
            sizes[generation + 1],
            probabilities,
        )

    return OverlapSpreadResult(
        population_sizes=sizes,
        category_counts=counts,
        founder_count=founder_count,
        seed=seed,
    )


def deterministic_overlapping_ancestry_fractions(
    initial_population: int,
    founder_count: int,
    generations: int,
) -> np.ndarray:
    """Expected category fractions for the two-tag overlap model."""
    if initial_population < 2:
        raise ValueError("initial_population must be at least 2")
    if not 1 <= founder_count < initial_population:
        raise ValueError(
            "founder_count must be at least 1 and smaller than initial_population"
        )
    if generations < 0:
        raise ValueError("generations must be non-negative")

    fractions = np.zeros((generations + 1, 4), dtype=float)
    fractions[0, 0] = founder_count / initial_population
    fractions[0, 1] = 1.0 - fractions[0, 0]

    for generation in range(generations):
        founder_only, background_only, both, neither = fractions[generation]
        no_founder_parent = background_only + neither
        no_background_parent = founder_only + neither

        p_neither = neither**2
        p_founder_only = no_background_parent**2 - p_neither
        p_background_only = no_founder_parent**2 - p_neither
        p_both = 1.0 - p_founder_only - p_background_only - p_neither

        fractions[generation + 1] = [
            p_founder_only,
            p_background_only,
            p_both,
            p_neither,
        ]

    return fractions
