"""Integrated population pedigree and autosomal founder-DNA simulation.

Model 08 combines the pedigree logic from the earlier founder-spread models with
explicit chromosome-segment inheritance. The population is finite and
panmictic. A small founder set is placed in generation 0. Pedigree ancestry is
tracked separately for each founder, while autosomal DNA from the founder set is
tracked collectively as tagged chromosome intervals.

The default chromosome model is the same transparent 22-autosome, 33-Morgan
aggregate map used in Model 07. It is not a high-resolution historical human
recombination map.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .genetic_ancestry import (
    balanced_autosome_map,
    validate_chromosome_map,
)


Interval = tuple[float, float]
Chromosome = tuple[list[Interval], list[Interval]]
Genome = list[Chromosome]


@dataclass(frozen=True)
class PedigreeGenomeResult:
    population_size: int
    founder_count: int
    generations: np.ndarray
    any_founder_descendant_fraction: np.ndarray
    all_founders_descendant_fraction: np.ndarray
    genetic_carrier_fraction: np.ndarray
    detectable_carrier_fraction: np.ndarray
    mean_founder_dna_fraction: np.ndarray
    max_founder_dna_fraction: np.ndarray
    not_all_founders_fraction: np.ndarray
    all_founders_no_dna_fraction: np.ndarray
    all_founders_subdetectable_fraction: np.ndarray
    all_founders_detectable_fraction: np.ndarray
    any_founder_fixation_generation: int | None
    all_founders_universal_generation: int | None
    genetic_extinction_generation: int | None
    ghost_generation: int | None
    chromosome_lengths_morgans: np.ndarray
    detectable_threshold_cm: float
    distinct_parents: bool
    seed: int | None


@dataclass(frozen=True)
class PedigreeGenomeReplicateSummary:
    generations: np.ndarray
    mean_any_founder_descendant_fraction: np.ndarray
    mean_all_founders_descendant_fraction: np.ndarray
    mean_genetic_carrier_fraction: np.ndarray
    mean_detectable_carrier_fraction: np.ndarray
    mean_founder_dna_fraction: np.ndarray
    all_founders_universal_generations: np.ndarray
    ghost_generations: np.ndarray
    final_genetic_carrier_fraction: np.ndarray
    final_detectable_carrier_fraction: np.ndarray
    population_size: int
    founder_count: int
    max_generations: int
    replicates: int
    detectable_threshold_cm: float
    seed: int | None

    @property
    def all_founders_universal_probability(self) -> float:
        return float(
            np.mean(
                np.isfinite(
                    self.all_founders_universal_generations
                )
            )
        )

    @property
    def ghost_probability_by_final(self) -> float:
        return float(
            np.mean(
                np.isfinite(
                    self.ghost_generations
                )
            )
        )

    @property
    def median_all_founders_universal_generation(self) -> float:
        finite = self.all_founders_universal_generations[
            np.isfinite(
                self.all_founders_universal_generations
            )
        ]
        return (
            float(np.median(finite))
            if finite.size
            else float("nan")
        )


def _intersections(
    intervals: list[Interval],
    start: float,
    end: float,
) -> list[Interval]:
    out: list[Interval] = []
    for a, b in intervals:
        left = max(a, start)
        right = min(b, end)
        if right > left:
            out.append((left, right))
    return out


def _merge_touching(
    intervals: list[Interval],
    tolerance: float = 1e-12,
) -> list[Interval]:
    if not intervals:
        return []

    ordered = sorted(intervals)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + tolerance:
            merged[-1] = (
                last_start,
                max(last_end, end),
            )
        else:
            merged.append((start, end))
    return merged


def _make_gamete(
    homolog_a: list[Interval],
    homolog_b: list[Interval],
    chromosome_length: float,
    rng: np.random.Generator,
) -> list[Interval]:
    """Return tagged founder intervals in one recombinant parental gamete."""
    if not homolog_a and not homolog_b:
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

    use_a = bool(
        rng.integers(0, 2)
    )
    transmitted: list[Interval] = []

    for left, right in zip(
        bounds[:-1],
        bounds[1:],
    ):
        source = (
            homolog_a
            if use_a
            else homolog_b
        )
        if source:
            transmitted.extend(
                _intersections(
                    source,
                    float(left),
                    float(right),
                )
            )
        use_a = not use_a

    return _merge_touching(
        transmitted
    )


def _sample_parents(
    population_size: int,
    rng: np.random.Generator,
    distinct_parents: bool,
) -> tuple[np.ndarray, np.ndarray]:
    first = rng.integers(
        0,
        population_size,
        size=population_size,
    )
    if not distinct_parents:
        second = rng.integers(
            0,
            population_size,
            size=population_size,
        )
        return first, second

    raw = rng.integers(
        0,
        population_size - 1,
        size=population_size,
    )
    second = raw + (
        raw >= first
    )
    return first, second


def _summarize_genomes(
    population: list[Genome],
    total_haploid_morgans: float,
    detectable_threshold_cm: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    population_size = len(
        population
    )
    genetic = np.zeros(
        population_size,
        dtype=bool,
    )
    detectable = np.zeros(
        population_size,
        dtype=bool,
    )
    fractions = np.zeros(
        population_size,
        dtype=float,
    )

    for person_index, genome in enumerate(
        population
    ):
        total = 0.0
        maximum_segment_morgans = 0.0

        for homolog_a, homolog_b in genome:
            for homolog in (
                homolog_a,
                homolog_b,
            ):
                for start, end in homolog:
                    length = end - start
                    total += length
                    maximum_segment_morgans = max(
                        maximum_segment_morgans,
                        length,
                    )

        fractions[person_index] = (
            total
            / (
                2.0
                * total_haploid_morgans
            )
        )
        genetic[person_index] = (
            total > 0.0
        )
        if detectable_threshold_cm == 0.0:
            detectable[person_index] = (
                genetic[person_index]
            )
        else:
            detectable[person_index] = (
                100.0
                * maximum_segment_morgans
                >= detectable_threshold_cm
            )

    return (
        genetic,
        detectable,
        fractions,
    )


def simulate_pedigree_genome(
    population_size: int = 200,
    max_generations: int = 25,
    founder_count: int = 2,
    chromosome_lengths_morgans: Sequence[float] | None = None,
    detectable_threshold_cm: float = 6.0,
    distinct_parents: bool = True,
    seed: int | None = None,
) -> PedigreeGenomeResult:
    """Simulate pedigree spread and founder-set autosomal DNA jointly.

    Pedigree ancestry is tracked separately for each founder using a bit mask.
    Autosomal segments are tagged only as belonging to the founder set, not to a
    particular founder. Therefore, genetic_carrier_fraction means carrying DNA
    from at least one member of the founder set.
    """
    if population_size < 2:
        raise ValueError(
            "population_size must be at least 2"
        )
    if founder_count < 1:
        raise ValueError(
            "founder_count must be at least 1"
        )
    if founder_count > population_size:
        raise ValueError(
            "founder_count cannot exceed population_size"
        )
    if max_generations < 0:
        raise ValueError(
            "max_generations must be non-negative"
        )
    if detectable_threshold_cm < 0:
        raise ValueError(
            "detectable_threshold_cm must be non-negative"
        )

    if chromosome_lengths_morgans is None:
        chromosome_lengths = (
            balanced_autosome_map()
        )
    else:
        chromosome_lengths = (
            validate_chromosome_map(
                chromosome_lengths_morgans
            )
        )

    rng = np.random.default_rng(
        seed
    )
    total_haploid_morgans = float(
        chromosome_lengths.sum()
    )

    population: list[Genome] = []
    ancestry_masks = [
        0
        for _ in range(
            population_size
        )
    ]

    for person_index in range(
        population_size
    ):
        if person_index < founder_count:
            genome: Genome = [
                (
                    [
                        (
                            0.0,
                            float(length),
                        )
                    ],
                    [
                        (
                            0.0,
                            float(length),
                        )
                    ],
                )
                for length
                in chromosome_lengths
            ]
            ancestry_masks[
                person_index
            ] = (
                1 << person_index
            )
        else:
            genome = [
                (
                    [],
                    [],
                )
                for _length
                in chromosome_lengths
            ]
        population.append(
            genome
        )

    complete_founder_mask = (
        (1 << founder_count)
        - 1
    )

    generations = np.arange(
        max_generations + 1,
        dtype=int,
    )
    any_descendant = np.empty(
        max_generations + 1,
        dtype=float,
    )
    all_descendant = np.empty(
        max_generations + 1,
        dtype=float,
    )
    genetic_fraction = np.empty(
        max_generations + 1,
        dtype=float,
    )
    detectable_fraction = np.empty(
        max_generations + 1,
        dtype=float,
    )
    mean_founder_fraction = np.empty(
        max_generations + 1,
        dtype=float,
    )
    max_founder_fraction = np.empty(
        max_generations + 1,
        dtype=float,
    )
    not_all_founders = np.empty(
        max_generations + 1,
        dtype=float,
    )
    all_no_dna = np.empty(
        max_generations + 1,
        dtype=float,
    )
    all_subdetectable = np.empty(
        max_generations + 1,
        dtype=float,
    )
    all_detectable = np.empty(
        max_generations + 1,
        dtype=float,
    )

    any_fixation_generation: (
        int | None
    ) = None
    all_universal_generation: (
        int | None
    ) = None
    genetic_extinction_generation: (
        int | None
    ) = None
    ghost_generation: (
        int | None
    ) = None

    for generation in generations:
        (
            genetic,
            detectable,
            founder_fractions,
        ) = _summarize_genomes(
            population,
            total_haploid_morgans,
            detectable_threshold_cm,
        )

        masks = np.asarray(
            ancestry_masks,
            dtype=object,
        )
        any_mask = masks != 0
        all_mask = (
            masks
            == complete_founder_mask
        )

        any_descendant[
            generation
        ] = float(
            np.mean(any_mask)
        )
        all_descendant[
            generation
        ] = float(
            np.mean(all_mask)
        )
        genetic_fraction[
            generation
        ] = float(
            np.mean(genetic)
        )
        detectable_fraction[
            generation
        ] = float(
            np.mean(detectable)
        )
        mean_founder_fraction[
            generation
        ] = float(
            np.mean(
                founder_fractions
            )
        )
        max_founder_fraction[
            generation
        ] = float(
            np.max(
                founder_fractions
            )
        )

        not_all_founders[
            generation
        ] = float(
            np.mean(~all_mask)
        )
        all_no_dna[
            generation
        ] = float(
            np.mean(
                all_mask
                & ~genetic
            )
        )
        all_subdetectable[
            generation
        ] = float(
            np.mean(
                all_mask
                & genetic
                & ~detectable
            )
        )
        all_detectable[
            generation
        ] = float(
            np.mean(
                all_mask
                & detectable
            )
        )

        if (
            any_fixation_generation
            is None
            and any_descendant[
                generation
            ]
            == 1.0
        ):
            any_fixation_generation = int(
                generation
            )

        if (
            all_universal_generation
            is None
            and all_descendant[
                generation
            ]
            == 1.0
        ):
            all_universal_generation = int(
                generation
            )

        if (
            genetic_extinction_generation
            is None
            and generation > 0
            and genetic_fraction[
                generation
            ]
            == 0.0
        ):
            genetic_extinction_generation = int(
                generation
            )

        if (
            ghost_generation
            is None
            and all_descendant[
                generation
            ]
            == 1.0
            and genetic_fraction[
                generation
            ]
            == 0.0
        ):
            ghost_generation = int(
                generation
            )

        if (
            generation
            == max_generations
        ):
            break

        (
            parent_a,
            parent_b,
        ) = _sample_parents(
            population_size,
            rng,
            distinct_parents,
        )

        next_population: list[
            Genome
        ] = []
        next_masks: list[int] = []

        for a_value, b_value in zip(
            parent_a,
            parent_b,
        ):
            a = int(a_value)
            b = int(b_value)
            parent_genome_a = (
                population[a]
            )
            parent_genome_b = (
                population[b]
            )

            child_genome: Genome = []
            for (
                chromosome_index,
                chromosome_length,
            ) in enumerate(
                chromosome_lengths
            ):
                (
                    a_homolog_0,
                    a_homolog_1,
                ) = parent_genome_a[
                    chromosome_index
                ]
                (
                    b_homolog_0,
                    b_homolog_1,
                ) = parent_genome_b[
                    chromosome_index
                ]

                gamete_a = _make_gamete(
                    a_homolog_0,
                    a_homolog_1,
                    float(
                        chromosome_length
                    ),
                    rng,
                )
                gamete_b = _make_gamete(
                    b_homolog_0,
                    b_homolog_1,
                    float(
                        chromosome_length
                    ),
                    rng,
                )
                child_genome.append(
                    (
                        gamete_a,
                        gamete_b,
                    )
                )

            next_population.append(
                child_genome
            )
            next_masks.append(
                ancestry_masks[a]
                | ancestry_masks[b]
            )

        population = (
            next_population
        )
        ancestry_masks = (
            next_masks
        )

    return PedigreeGenomeResult(
        population_size=population_size,
        founder_count=founder_count,
        generations=generations,
        any_founder_descendant_fraction=(
            any_descendant
        ),
        all_founders_descendant_fraction=(
            all_descendant
        ),
        genetic_carrier_fraction=(
            genetic_fraction
        ),
        detectable_carrier_fraction=(
            detectable_fraction
        ),
        mean_founder_dna_fraction=(
            mean_founder_fraction
        ),
        max_founder_dna_fraction=(
            max_founder_fraction
        ),
        not_all_founders_fraction=(
            not_all_founders
        ),
        all_founders_no_dna_fraction=(
            all_no_dna
        ),
        all_founders_subdetectable_fraction=(
            all_subdetectable
        ),
        all_founders_detectable_fraction=(
            all_detectable
        ),
        any_founder_fixation_generation=(
            any_fixation_generation
        ),
        all_founders_universal_generation=(
            all_universal_generation
        ),
        genetic_extinction_generation=(
            genetic_extinction_generation
        ),
        ghost_generation=(
            ghost_generation
        ),
        chromosome_lengths_morgans=(
            chromosome_lengths
        ),
        detectable_threshold_cm=float(
            detectable_threshold_cm
        ),
        distinct_parents=(
            distinct_parents
        ),
        seed=seed,
    )


def simulate_pedigree_genome_replicates(
    population_size: int = 100,
    max_generations: int = 20,
    founder_count: int = 2,
    chromosome_lengths_morgans: Sequence[float] | None = None,
    detectable_threshold_cm: float = 6.0,
    distinct_parents: bool = True,
    replicates: int = 20,
    seed: int | None = None,
) -> PedigreeGenomeReplicateSummary:
    """Repeat the integrated pedigree-genome simulation."""
    if replicates < 1:
        raise ValueError(
            "replicates must be at least 1"
        )

    master_rng = np.random.default_rng(
        seed
    )
    child_seeds = master_rng.integers(
        0,
        np.iinfo(
            np.uint32
        ).max,
        size=replicates,
    )

    n_timepoints = (
        max_generations + 1
    )
    sum_any = np.zeros(
        n_timepoints,
        dtype=float,
    )
    sum_all = np.zeros(
        n_timepoints,
        dtype=float,
    )
    sum_genetic = np.zeros(
        n_timepoints,
        dtype=float,
    )
    sum_detectable = np.zeros(
        n_timepoints,
        dtype=float,
    )
    sum_founder_fraction = (
        np.zeros(
            n_timepoints,
            dtype=float,
        )
    )

    universal_generations = (
        np.full(
            replicates,
            np.nan,
            dtype=float,
        )
    )
    ghost_generations = np.full(
        replicates,
        np.nan,
        dtype=float,
    )
    final_genetic = np.empty(
        replicates,
        dtype=float,
    )
    final_detectable = np.empty(
        replicates,
        dtype=float,
    )

    for replicate_index, child_seed in enumerate(
        child_seeds
    ):
        result = simulate_pedigree_genome(
            population_size=population_size,
            max_generations=max_generations,
            founder_count=founder_count,
            chromosome_lengths_morgans=(
                chromosome_lengths_morgans
            ),
            detectable_threshold_cm=(
                detectable_threshold_cm
            ),
            distinct_parents=(
                distinct_parents
            ),
            seed=int(
                child_seed
            ),
        )

        sum_any += (
            result.any_founder_descendant_fraction
        )
        sum_all += (
            result.all_founders_descendant_fraction
        )
        sum_genetic += (
            result.genetic_carrier_fraction
        )
        sum_detectable += (
            result.detectable_carrier_fraction
        )
        sum_founder_fraction += (
            result.mean_founder_dna_fraction
        )

        if (
            result.all_founders_universal_generation
            is not None
        ):
            universal_generations[
                replicate_index
            ] = (
                result.all_founders_universal_generation
            )
        if (
            result.ghost_generation
            is not None
        ):
            ghost_generations[
                replicate_index
            ] = result.ghost_generation

        final_genetic[
            replicate_index
        ] = (
            result.genetic_carrier_fraction[
                -1
            ]
        )
        final_detectable[
            replicate_index
        ] = (
            result.detectable_carrier_fraction[
                -1
            ]
        )

    divisor = float(
        replicates
    )
    return PedigreeGenomeReplicateSummary(
        generations=np.arange(
            n_timepoints,
            dtype=int,
        ),
        mean_any_founder_descendant_fraction=(
            sum_any / divisor
        ),
        mean_all_founders_descendant_fraction=(
            sum_all / divisor
        ),
        mean_genetic_carrier_fraction=(
            sum_genetic / divisor
        ),
        mean_detectable_carrier_fraction=(
            sum_detectable / divisor
        ),
        mean_founder_dna_fraction=(
            sum_founder_fraction
            / divisor
        ),
        all_founders_universal_generations=(
            universal_generations
        ),
        ghost_generations=(
            ghost_generations
        ),
        final_genetic_carrier_fraction=(
            final_genetic
        ),
        final_detectable_carrier_fraction=(
            final_detectable
        ),
        population_size=(
            population_size
        ),
        founder_count=(
            founder_count
        ),
        max_generations=(
            max_generations
        ),
        replicates=replicates,
        detectable_threshold_cm=float(
            detectable_threshold_cm
        ),
        seed=seed,
    )
