"""Model 11: convert genetic admixture histories into genealogical consequences.

The key distinction is between mean source-DNA proportion and pedigree
descendant status. Under neutral random mating, a source ancestry proportion can
remain small while genealogical descent from that source spreads rapidly.
"""

from __future__ import annotations

import numpy as np


def genetic_ancestry_after_continuous_admixture(
    external_parent_rate: float,
    generations: int,
    initial_ancestry: float = 0.0,
) -> float:
    """Expected source-DNA fraction after constant external parental input."""
    if not 0.0 <= external_parent_rate <= 1.0:
        raise ValueError("external_parent_rate must lie in [0, 1]")
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 0.0 <= initial_ancestry <= 1.0:
        raise ValueError("initial_ancestry must lie in [0, 1]")
    return float(
        1.0
        - (1.0 - initial_ancestry)
        * (1.0 - external_parent_rate) ** generations
    )


def genealogical_fraction_after_continuous_admixture(
    external_parent_rate: float,
    generations: int,
    initial_fraction: float = 0.0,
) -> float:
    """Fraction descended from a source whose external parents are all tagged."""
    if not 0.0 <= external_parent_rate <= 1.0:
        raise ValueError("external_parent_rate must lie in [0, 1]")
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 0.0 <= initial_fraction <= 1.0:
        raise ValueError("initial_fraction must lie in [0, 1]")
    f = float(initial_fraction)
    for _ in range(generations):
        f = 1.0 - ((1.0 - external_parent_rate) * (1.0 - f)) ** 2
    return float(f)


def constant_rate_from_observed_admixture(
    observed_ancestry: float,
    generations: int,
    initial_ancestry: float = 0.0,
) -> float:
    """Infer the constant external-parent rate matching an expected DNA fraction.

    This is a demographic conversion under a specified model, not a direct
    measurement of historical parentage.
    """
    if not 0.0 <= observed_ancestry <= 1.0:
        raise ValueError("observed_ancestry must lie in [0, 1]")
    if generations < 1:
        raise ValueError("generations must be at least 1")
    if not 0.0 <= initial_ancestry < 1.0:
        raise ValueError("initial_ancestry must lie in [0, 1)")
    remaining = (1.0 - observed_ancestry) / (1.0 - initial_ancestry)
    if remaining < 0.0 or remaining > 1.0:
        raise ValueError("observed ancestry is incompatible with initial ancestry")
    return float(1.0 - remaining ** (1.0 / generations))


def pulse_genealogical_fraction(
    pulse_ancestry: float,
    generations_since_pulse: int,
) -> float:
    """Genealogical descendant fraction after a single source-admixture pulse.

    pulse_ancestry is the expected source-DNA proportion immediately after the
    pulse. With independent parental-source draws, the fraction with >=1 source
    parent is 1-(1-a)^2. Subsequent generations have no further source input and
    mate randomly.
    """
    if not 0.0 <= pulse_ancestry <= 1.0:
        raise ValueError("pulse_ancestry must lie in [0, 1]")
    if generations_since_pulse < 1:
        raise ValueError("generations_since_pulse must be at least 1")
    f = 1.0 - (1.0 - pulse_ancestry) ** 2
    for _ in range(generations_since_pulse - 1):
        f = 1.0 - (1.0 - f) ** 2
    return float(f)


def independent_fixation_probability(
    descendant_fraction: float,
    population_size: int,
) -> float:
    """Approximate probability every individual is a descendant.

    Final descendant indicators are treated as independent; a finite pedigree
    creates correlations, so this is an approximation rather than an exact
    population probability.
    """
    if not 0.0 <= descendant_fraction <= 1.0:
        raise ValueError("descendant_fraction must lie in [0, 1]")
    if population_size < 1:
        raise ValueError("population_size must be positive")
    if descendant_fraction == 0.0:
        return 0.0
    if descendant_fraction == 1.0:
        return 1.0
    return float(np.exp(population_size * np.log(descendant_fraction)))


def simulate_pulse_fixation(
    pulse_ancestry: float,
    generations_since_pulse: int,
    population_size: int = 1000,
    replicates: int = 5000,
    seed: int | None = None,
) -> dict[str, float]:
    """Finite-population Monte Carlo after a single admixture pulse."""
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    if replicates < 1:
        raise ValueError("replicates must be positive")
    if not 0.0 <= pulse_ancestry <= 1.0:
        raise ValueError("pulse_ancestry must lie in [0, 1]")
    if generations_since_pulse < 1:
        raise ValueError("generations_since_pulse must be at least 1")

    rng = np.random.default_rng(seed)
    first_p = 1.0 - (1.0 - pulse_ancestry) ** 2
    counts = rng.binomial(population_size, first_p, size=replicates)

    for _ in range(generations_since_pulse - 1):
        f = counts / population_size
        child_p = 1.0 - (1.0 - f) ** 2
        counts = rng.binomial(population_size, child_p)

    fractions = counts / population_size
    return {
        "mean_final_fraction": float(np.mean(fractions)),
        "fixation_probability": float(np.mean(counts == population_size)),
        "q05": float(np.quantile(fractions, 0.05)),
        "median": float(np.quantile(fractions, 0.50)),
        "q95": float(np.quantile(fractions, 0.95)),
    }
