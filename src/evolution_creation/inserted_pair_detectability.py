"""Model 13: population-genetic detectability of a specially inserted pair."""

from __future__ import annotations
import numpy as np


def simulate_private_marker(
    effective_population_size: int = 10_000,
    generations: int = 400,
    initial_copies: int = 2,
    replicates: int = 20_000,
    sample_diploids: int = 1000,
    seed: int | None = None,
) -> dict[str, float]:
    """Neutral Wright-Fisher fate of one private autosomal marker."""
    if effective_population_size < 2:
        raise ValueError("effective_population_size must be at least 2")
    total = 2 * effective_population_size
    if not 0 <= initial_copies <= total:
        raise ValueError("invalid initial_copies")
    if generations < 0 or replicates < 1 or sample_diploids < 1:
        raise ValueError("invalid generations/replicates/sample size")

    rng = np.random.default_rng(seed)
    copies = np.full(replicates, initial_copies, dtype=np.int64)
    for _ in range(generations):
        copies = rng.binomial(total, copies / total)

    freqs = copies / total
    sampling_detection = 1.0 - (1.0 - freqs) ** (2 * sample_diploids)
    return {
        "survival_probability": float(np.mean(copies > 0)),
        "fixation_probability_by_time": float(np.mean(copies == total)),
        "mean_population_frequency": float(np.mean(freqs)),
        "sample_detection_probability": float(np.mean(sampling_detection)),
        "median_frequency_if_surviving": float(
            np.median(freqs[copies > 0]) if np.any(copies > 0) else 0.0
        ),
    }


def at_least_one_marker_detected(
    per_marker_detection_probability: float,
    marker_count: int,
) -> float:
    """Independent-marker approximation for at least one distinctive marker."""
    if not 0.0 <= per_marker_detection_probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    if marker_count < 0:
        raise ValueError("marker_count must be non-negative")
    return float(1.0 - (1.0 - per_marker_detection_probability) ** marker_count)


def initial_pair_genome_fraction(population_size: int) -> float:
    """Fraction of diploid individuals represented by a two-person pair."""
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    return float(2.0 / population_size)


def sample_detection_probability(
    allele_frequency: float,
    sample_diploids: int,
) -> float:
    if not 0.0 <= allele_frequency <= 1.0:
        raise ValueError("allele_frequency must lie in [0, 1]")
    if sample_diploids < 1:
        raise ValueError("sample_diploids must be positive")
    return float(1.0 - (1.0 - allele_frequency) ** (2 * sample_diploids))
