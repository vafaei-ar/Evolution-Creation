"""Genealogical versus autosomal genetic ancestry.

The analytic benchmark follows the approximation described by Coop (2013) and
formalized in Agranat-Tamir, Mooney & Rosenberg (2024): for a genealogical
ancestor k generations back, the number of surviving autosomal fragments is
approximated as Poisson with mean

    lambda_k = [q + r (k - 1)] / 2**(k - 1),

where q is the number of autosome pairs and r is the mean number of crossover
breakpoints added across the haploid autosomal genome per meiosis.

The segment simulator is pedagogical. It follows one specified ancestor-
descendant path and models each chromosome in genetic-map units (Morgans).
The lineage-carrying parent has one potentially founder-derived homolog and one
clean homolog. Crossovers follow a Poisson process along each chromosome.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


DEFAULT_AUTOSOME_PAIRS = 22
DEFAULT_CROSSOVERS_PER_HAPLOID_GENOME = 33.0


@dataclass(frozen=True)
class GeneticPathResult:
    generations: np.ndarray
    total_founder_morgans: np.ndarray
    founder_fraction_diploid: np.ndarray
    segment_counts: np.ndarray
    max_segment_cm: np.ndarray
    has_any_founder_dna: np.ndarray
    has_detectable_segment: np.ndarray
    chromosome_lengths_morgans: np.ndarray
    detectable_threshold_cm: float
    seed: int | None


@dataclass(frozen=True)
class GeneticPathReplicateSummary:
    generations: np.ndarray
    any_dna_probability: np.ndarray
    detectable_probability: np.ndarray
    mean_founder_fraction: np.ndarray
    mean_segment_count: np.ndarray
    mean_max_segment_cm: np.ndarray
    replicates: int
    detectable_threshold_cm: float
    seed: int | None


def balanced_autosome_map(
    autosome_pairs: int = DEFAULT_AUTOSOME_PAIRS,
    crossovers_per_haploid_genome: float = DEFAULT_CROSSOVERS_PER_HAPLOID_GENOME,
) -> np.ndarray:
    """Return equal-length chromosome map totaling the chosen Morgan length.

    This is intentionally a transparent approximation, not a chromosome-specific
    reference recombination map.
    """
    if autosome_pairs < 1:
        raise ValueError("autosome_pairs must be at least 1")
    if crossovers_per_haploid_genome <= 0:
        raise ValueError("crossovers_per_haploid_genome must be positive")
    return np.full(
        autosome_pairs,
        crossovers_per_haploid_genome / autosome_pairs,
        dtype=float,
    )


def validate_chromosome_map(
    chromosome_lengths_morgans: Sequence[float],
) -> np.ndarray:
    lengths = np.asarray(chromosome_lengths_morgans, dtype=float)
    if lengths.ndim != 1 or lengths.size < 1:
        raise ValueError(
            "chromosome_lengths_morgans must be one-dimensional"
        )
    if np.any(~np.isfinite(lengths)) or np.any(lengths <= 0):
        raise ValueError(
            "all chromosome lengths must be positive and finite"
        )
    return lengths


def coop_fragment_mean(
    generations_back: int,
    autosome_pairs: int = DEFAULT_AUTOSOME_PAIRS,
    crossovers_per_haploid_genome: float = DEFAULT_CROSSOVERS_PER_HAPLOID_GENOME,
) -> float:
    """Approximate mean number of autosomal fragments from one ancestor."""
    if generations_back < 1:
        raise ValueError("generations_back must be at least 1")
    if autosome_pairs < 1:
        raise ValueError("autosome_pairs must be at least 1")
    if crossovers_per_haploid_genome < 0:
        raise ValueError(
            "crossovers_per_haploid_genome must be non-negative"
        )
    if generations_back == 1:
        return float(autosome_pairs)

    numerator = (
        autosome_pairs
        + crossovers_per_haploid_genome * (generations_back - 1)
    )
    return float(
        numerator / (2 ** (generations_back - 1))
    )


def coop_genetic_ancestor_probability(
    generations_back: int,
    autosome_pairs: int = DEFAULT_AUTOSOME_PAIRS,
    crossovers_per_haploid_genome: float = DEFAULT_CROSSOVERS_PER_HAPLOID_GENOME,
) -> float:
    """Approximate P(a genealogical ancestor contributes >=1 autosomal fragment)."""
    if generations_back == 1:
        return 1.0
    lam = coop_fragment_mean(
        generations_back,
        autosome_pairs,
        crossovers_per_haploid_genome,
    )
    return float(-np.expm1(-lam))


def expected_genetic_ancestor_count(
    generations_back: int,
    autosome_pairs: int = DEFAULT_AUTOSOME_PAIRS,
    crossovers_per_haploid_genome: float = DEFAULT_CROSSOVERS_PER_HAPLOID_GENOME,
) -> float:
    """Expected genetic ancestors among 2**k pedigree slots, ignoring collapse."""
    if generations_back < 1:
        raise ValueError("generations_back must be at least 1")

    return float(
        (2 ** generations_back)
        * coop_genetic_ancestor_probability(
            generations_back,
            autosome_pairs,
            crossovers_per_haploid_genome,
        )
    )


def _intersections(
    intervals: list[tuple[float, float]],
    start: float,
    end: float,
) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for a, b in intervals:
        left = max(a, start)
        right = min(b, end)
        if right > left:
            out.append((left, right))
    return out


def _merge_touching(
    intervals: list[tuple[float, float]],
    tolerance: float = 1e-12,
) -> list[tuple[float, float]]:
    if not intervals:
        return []

    intervals = sorted(intervals)
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + tolerance:
            merged[-1] = (
                last_start,
                max(last_end, end),
            )
        else:
            merged.append((start, end))
    return merged


def _recombine_tagged_with_clean(
    tagged_intervals: list[tuple[float, float]],
    chromosome_length: float,
    rng: np.random.Generator,
) -> list[tuple[float, float]]:
    """Create a gamete from a tagged homolog and a completely clean homolog."""
    if not tagged_intervals:
        return []

    n_crossovers = int(
        rng.poisson(chromosome_length)
    )
    if n_crossovers:
        breakpoints = np.sort(
            rng.uniform(
                0.0,
                chromosome_length,
                n_crossovers,
            )
        )
        bounds = np.concatenate(
            (
                [0.0],
                breakpoints,
                [chromosome_length],
            )
        )
    else:
        bounds = np.array(
            [0.0, chromosome_length]
        )

    use_tagged = bool(
        rng.integers(0, 2)
    )
    transmitted: list[tuple[float, float]] = []

    for left, right in zip(
        bounds[:-1],
        bounds[1:],
    ):
        if use_tagged:
            transmitted.extend(
                _intersections(
                    tagged_intervals,
                    float(left),
                    float(right),
                )
            )
        use_tagged = not use_tagged

    return _merge_touching(transmitted)


def _segment_summary(
    tagged_by_chromosome: list[list[tuple[float, float]]],
    total_haploid_morgans: float,
) -> tuple[float, float, int, float]:
    lengths = [
        end - start
        for chromosome in tagged_by_chromosome
        for start, end in chromosome
    ]
    total = float(sum(lengths))
    fraction_diploid = (
        total / (2.0 * total_haploid_morgans)
    )
    count = len(lengths)
    max_cm = (
        100.0 * max(lengths)
        if lengths else 0.0
    )
    return (
        total,
        fraction_diploid,
        count,
        max_cm,
    )


def simulate_single_path(
    max_generations: int = 20,
    chromosome_lengths_morgans: Sequence[float] | None = None,
    detectable_threshold_cm: float = 0.0,
    seed: int | None = None,
) -> GeneticPathResult:
    """Simulate autosomal transmission along one specified genealogical path.

    Generation 1 is the ancestor's child. That child necessarily receives one
    complete haploid autosomal genome from the ancestor. In each later
    generation, the lineage-carrying individual mates with an unrelated clean
    partner and transmits one recombinant gamete.
    """
    if max_generations < 1:
        raise ValueError(
            "max_generations must be at least 1"
        )
    if detectable_threshold_cm < 0:
        raise ValueError(
            "detectable_threshold_cm must be non-negative"
        )

    if chromosome_lengths_morgans is None:
        lengths = balanced_autosome_map()
    else:
        lengths = validate_chromosome_map(
            chromosome_lengths_morgans
        )

    rng = np.random.default_rng(seed)
    total_haploid = float(lengths.sum())

    tagged: list[list[tuple[float, float]]] = [
        [(0.0, float(length))]
        for length in lengths
    ]

    total_founder = np.empty(
        max_generations,
        dtype=float,
    )
    fractions = np.empty(
        max_generations,
        dtype=float,
    )
    segment_counts = np.empty(
        max_generations,
        dtype=int,
    )
    max_segment_cm = np.empty(
        max_generations,
        dtype=float,
    )

    for generation in range(
        1,
        max_generations + 1,
    ):
        if generation > 1:
            tagged = [
                _recombine_tagged_with_clean(
                    chromosome,
                    float(length),
                    rng,
                )
                for chromosome, length
                in zip(tagged, lengths)
            ]

        (
            total,
            fraction,
            count,
            maximum,
        ) = _segment_summary(
            tagged,
            total_haploid,
        )
        index = generation - 1
        total_founder[index] = total
        fractions[index] = fraction
        segment_counts[index] = count
        max_segment_cm[index] = maximum

    any_dna = total_founder > 0.0
    if detectable_threshold_cm == 0.0:
        detectable = any_dna.copy()
    else:
        detectable = (
            max_segment_cm
            >= detectable_threshold_cm
        )

    return GeneticPathResult(
        generations=np.arange(
            1,
            max_generations + 1,
            dtype=int,
        ),
        total_founder_morgans=total_founder,
        founder_fraction_diploid=fractions,
        segment_counts=segment_counts,
        max_segment_cm=max_segment_cm,
        has_any_founder_dna=any_dna,
        has_detectable_segment=detectable,
        chromosome_lengths_morgans=lengths,
        detectable_threshold_cm=float(
            detectable_threshold_cm
        ),
        seed=seed,
    )


def simulate_path_replicates(
    max_generations: int = 20,
    chromosome_lengths_morgans: Sequence[float] | None = None,
    detectable_threshold_cm: float = 0.0,
    replicates: int = 1_000,
    seed: int | None = None,
) -> GeneticPathReplicateSummary:
    """Estimate single-path transmission probabilities by Monte Carlo."""
    if replicates < 1:
        raise ValueError(
            "replicates must be at least 1"
        )

    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(
        0,
        np.iinfo(np.uint32).max,
        size=replicates,
    )

    any_dna = np.empty(
        (replicates, max_generations),
        dtype=bool,
    )
    detectable = np.empty(
        (replicates, max_generations),
        dtype=bool,
    )
    fractions = np.empty(
        (replicates, max_generations),
        dtype=float,
    )
    segment_counts = np.empty(
        (replicates, max_generations),
        dtype=float,
    )
    max_segment_cm = np.empty(
        (replicates, max_generations),
        dtype=float,
    )

    for index, child_seed in enumerate(
        child_seeds
    ):
        result = simulate_single_path(
            max_generations=max_generations,
            chromosome_lengths_morgans=(
                chromosome_lengths_morgans
            ),
            detectable_threshold_cm=(
                detectable_threshold_cm
            ),
            seed=int(child_seed),
        )
        any_dna[index] = (
            result.has_any_founder_dna
        )
        detectable[index] = (
            result.has_detectable_segment
        )
        fractions[index] = (
            result.founder_fraction_diploid
        )
        segment_counts[index] = (
            result.segment_counts
        )
        max_segment_cm[index] = (
            result.max_segment_cm
        )

    return GeneticPathReplicateSummary(
        generations=np.arange(
            1,
            max_generations + 1,
            dtype=int,
        ),
        any_dna_probability=(
            any_dna.mean(axis=0)
        ),
        detectable_probability=(
            detectable.mean(axis=0)
        ),
        mean_founder_fraction=(
            fractions.mean(axis=0)
        ),
        mean_segment_count=(
            segment_counts.mean(axis=0)
        ),
        mean_max_segment_cm=(
            max_segment_cm.mean(axis=0)
        ),
        replicates=replicates,
        detectable_threshold_cm=float(
            detectable_threshold_cm
        ),
        seed=seed,
    )



@dataclass(frozen=True)
class GeneticSegmentHistory:
    generations: np.ndarray
    segments_by_generation: tuple[
        tuple[tuple[tuple[float, float], ...], ...], ...
    ]
    chromosome_lengths_morgans: np.ndarray
    seed: int | None


def _freeze_segments(
    tagged_by_chromosome: list[list[tuple[float, float]]],
) -> tuple[tuple[tuple[float, float], ...], ...]:
    return tuple(
        tuple(
            (float(start), float(end))
            for start, end in chromosome
        )
        for chromosome in tagged_by_chromosome
    )


def simulate_segment_history(
    max_generations: int = 20,
    chromosome_lengths_morgans: Sequence[float] | None = None,
    seed: int | None = None,
) -> GeneticSegmentHistory:
    """Return founder-derived chromosome intervals along one lineage path."""
    if max_generations < 1:
        raise ValueError(
            "max_generations must be at least 1"
        )

    if chromosome_lengths_morgans is None:
        lengths = balanced_autosome_map()
    else:
        lengths = validate_chromosome_map(
            chromosome_lengths_morgans
        )

    rng = np.random.default_rng(seed)
    tagged: list[list[tuple[float, float]]] = [
        [(0.0, float(length))]
        for length in lengths
    ]
    history = [
        _freeze_segments(tagged)
    ]

    for _generation in range(
        2,
        max_generations + 1,
    ):
        tagged = [
            _recombine_tagged_with_clean(
                chromosome,
                float(length),
                rng,
            )
            for chromosome, length
            in zip(tagged, lengths)
        ]
        history.append(
            _freeze_segments(tagged)
        )

    return GeneticSegmentHistory(
        generations=np.arange(
            1,
            max_generations + 1,
            dtype=int,
        ),
        segments_by_generation=tuple(
            history
        ),
        chromosome_lengths_morgans=lengths,
        seed=seed,
    )
