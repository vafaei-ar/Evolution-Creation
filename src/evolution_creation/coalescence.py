"""Genealogical MRCA and Identical Ancestors Point simulations.

The baseline model is a two-parent analog of Wright-Fisher reproduction. Every
individual in a generation independently chooses two parents, with replacement,
from the previous generation. Ancestry is traced backward from all individuals
in the present generation.

For each past individual we track the set of present-day descendants as a Python
integer bit mask. This makes exact finite-population MRCA/IAP calculations
possible for populations of a few thousand individuals without storing an
N-by-N Boolean matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


CHANG_IAP_MULTIPLIER = 1.77


@dataclass(frozen=True)
class PedigreeCoalescenceResult:
    """Status counts while tracing a pedigree backward in time."""

    population_size: int
    generations_back: np.ndarray
    contributing_counts: np.ndarray
    partial_counts: np.ndarray
    universal_counts: np.ndarray
    mrca_generation: int | None
    iap_generation: int | None
    seed: int | None
    community_sizes: np.ndarray | None = None
    parent_source_matrix: np.ndarray | None = None

    @property
    def noncontributing_counts(self) -> np.ndarray:
        """Individuals with no descendants in the present generation."""
        return self.population_size - self.contributing_counts

    @property
    def reached_mrca(self) -> bool:
        return self.mrca_generation is not None

    @property
    def reached_iap(self) -> bool:
        return self.iap_generation is not None


@dataclass(frozen=True)
class CoalescenceReplicateSummary:
    """MRCA/IAP times from repeated pedigree simulations."""

    mrca_generations: np.ndarray
    iap_generations: np.ndarray
    population_size: int
    max_generations: int
    replicates: int
    seed: int | None

    @property
    def mrca_reached_fraction(self) -> float:
        return float(np.mean(np.isfinite(self.mrca_generations)))

    @property
    def iap_reached_fraction(self) -> float:
        return float(np.mean(np.isfinite(self.iap_generations)))

    @property
    def median_mrca_generation(self) -> float:
        finite = self.mrca_generations[np.isfinite(self.mrca_generations)]
        return float(np.median(finite)) if finite.size else float("nan")

    @property
    def median_iap_generation(self) -> float:
        finite = self.iap_generations[np.isfinite(self.iap_generations)]
        return float(np.median(finite)) if finite.size else float("nan")


def chang_asymptotic_generations(population_size: int) -> tuple[float, float]:
    """Chang (1999) large-N random-mating benchmarks.

    Returns approximately log2(N) generations to an MRCA and
    1.77 * log2(N) generations to the Identical Ancestors Point.
    These are asymptotic benchmarks for the idealized model, not estimates for
    real human populations.
    """
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    log_n = float(np.log2(population_size))
    return log_n, CHANG_IAP_MULTIPLIER * log_n


def _status_counts(
    descendant_masks: list[int],
    universal_mask: int,
) -> tuple[int, int, int]:
    contributing = 0
    universal = 0
    for mask in descendant_masks:
        if mask:
            contributing += 1
            if mask == universal_mask:
                universal += 1
    partial = contributing - universal
    return contributing, partial, universal


def _finalize_result(
    population_size: int,
    contributing: list[int],
    partial: list[int],
    universal: list[int],
    mrca_generation: int | None,
    iap_generation: int | None,
    seed: int | None,
    community_sizes: np.ndarray | None = None,
    parent_source_matrix: np.ndarray | None = None,
) -> PedigreeCoalescenceResult:
    return PedigreeCoalescenceResult(
        population_size=population_size,
        generations_back=np.arange(len(contributing), dtype=int),
        contributing_counts=np.asarray(contributing, dtype=int),
        partial_counts=np.asarray(partial, dtype=int),
        universal_counts=np.asarray(universal, dtype=int),
        mrca_generation=mrca_generation,
        iap_generation=iap_generation,
        seed=seed,
        community_sizes=community_sizes,
        parent_source_matrix=parent_source_matrix,
    )


def simulate_pedigree_coalescence(
    population_size: int = 1_000,
    max_generations: int | None = None,
    seed: int | None = None,
    stop_at_iap: bool = True,
) -> PedigreeCoalescenceResult:
    """Trace all present-day individuals backward in a panmictic population."""
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    if max_generations is None:
        max_generations = int(
            np.ceil(4.0 * np.log2(population_size) + 20)
        )
    if max_generations < 1:
        raise ValueError("max_generations must be at least 1")

    rng = np.random.default_rng(seed)
    descendant_masks = [1 << i for i in range(population_size)]
    universal_mask = (1 << population_size) - 1

    contributing = [population_size]
    partial = [population_size]
    universal = [0]
    mrca_generation: int | None = None
    iap_generation: int | None = None

    for generation in range(1, max_generations + 1):
        parent_a = rng.integers(
            0,
            population_size,
            size=population_size,
        )
        parent_b = rng.integers(
            0,
            population_size,
            size=population_size,
        )
        parent_masks = [0] * population_size

        for child_mask, a, b in zip(
            descendant_masks,
            parent_a,
            parent_b,
        ):
            a_index = int(a)
            b_index = int(b)
            parent_masks[a_index] |= child_mask
            parent_masks[b_index] |= child_mask

        descendant_masks = parent_masks
        c, p, u = _status_counts(
            descendant_masks,
            universal_mask,
        )
        contributing.append(c)
        partial.append(p)
        universal.append(u)

        if mrca_generation is None and u > 0:
            mrca_generation = generation
        if iap_generation is None and c > 0 and u == c:
            iap_generation = generation
            if stop_at_iap:
                break

    return _finalize_result(
        population_size,
        contributing,
        partial,
        universal,
        mrca_generation,
        iap_generation,
        seed,
    )


def simulate_coalescence_replicates(
    population_size: int = 1_000,
    max_generations: int | None = None,
    replicates: int = 100,
    seed: int | None = None,
) -> CoalescenceReplicateSummary:
    """Repeat the panmictic simulation and collect MRCA/IAP times."""
    if replicates < 1:
        raise ValueError("replicates must be at least 1")
    if max_generations is None:
        max_generations = int(
            np.ceil(4.0 * np.log2(population_size) + 20)
        )

    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(
        0,
        np.iinfo(np.uint32).max,
        size=replicates,
    )

    mrca = np.full(replicates, np.nan, dtype=float)
    iap = np.full(replicates, np.nan, dtype=float)
    for index, child_seed in enumerate(child_seeds):
        result = simulate_pedigree_coalescence(
            population_size=population_size,
            max_generations=max_generations,
            seed=int(child_seed),
        )
        if result.mrca_generation is not None:
            mrca[index] = result.mrca_generation
        if result.iap_generation is not None:
            iap[index] = result.iap_generation

    return CoalescenceReplicateSummary(
        mrca_generations=mrca,
        iap_generations=iap,
        population_size=population_size,
        max_generations=max_generations,
        replicates=replicates,
        seed=seed,
    )


def make_parent_source_matrix(
    community_sizes: Sequence[int],
    isolation_strength: float,
) -> np.ndarray:
    """Interpolate between panmixia and complete community isolation.

    At isolation_strength=0, every parent is sampled from the whole population,
    so source-community probabilities are proportional to community size.
    At isolation_strength=1, both parents are sampled from the child's own
    community, making communities genealogically disconnected.
    """
    sizes = np.asarray(community_sizes, dtype=int)
    if sizes.ndim != 1 or sizes.size < 2:
        raise ValueError(
            "community_sizes must contain at least two communities"
        )
    if np.any(sizes < 2):
        raise ValueError(
            "each community must contain at least 2 individuals"
        )
    if not 0.0 <= isolation_strength <= 1.0:
        raise ValueError(
            "isolation_strength must lie between 0 and 1"
        )

    baseline = sizes / sizes.sum()
    matrix = (1.0 - isolation_strength) * np.tile(
        baseline,
        (sizes.size, 1),
    )
    matrix += isolation_strength * np.eye(sizes.size)
    return matrix


def _validate_parent_source_matrix(
    matrix: np.ndarray,
    n_communities: int,
) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (n_communities, n_communities):
        raise ValueError(
            "parent_source_matrix must have shape "
            f"{(n_communities, n_communities)}"
        )
    if np.any(matrix < 0.0) or np.any(matrix > 1.0):
        raise ValueError(
            "parent-source probabilities must lie between 0 and 1"
        )
    if not np.allclose(matrix.sum(axis=1), 1.0):
        raise ValueError(
            "each parent-source row must sum to 1"
        )
    return matrix


def simulate_structured_pedigree_coalescence(
    community_sizes: Sequence[int],
    parent_source_matrix: np.ndarray,
    max_generations: int | None = None,
    seed: int | None = None,
    stop_at_iap: bool = True,
) -> PedigreeCoalescenceResult:
    """Trace the complete present population backward through communities.

    For each child in destination community i, both parents independently draw
    a source community from row i of parent_source_matrix, then draw one parent
    uniformly from that source community.
    """
    sizes = np.asarray(community_sizes, dtype=int)
    if sizes.ndim != 1 or sizes.size < 2:
        raise ValueError(
            "community_sizes must contain at least two communities"
        )
    if np.any(sizes < 2):
        raise ValueError(
            "each community must contain at least 2 individuals"
        )
    total_population = int(sizes.sum())
    matrix = _validate_parent_source_matrix(
        parent_source_matrix,
        sizes.size,
    )

    if max_generations is None:
        max_generations = int(
            np.ceil(6.0 * np.log2(total_population) + 40)
        )
    if max_generations < 1:
        raise ValueError("max_generations must be at least 1")

    rng = np.random.default_rng(seed)
    descendant_masks = [
        1 << i for i in range(total_population)
    ]
    universal_mask = (1 << total_population) - 1
    offsets = np.concatenate(([0], np.cumsum(sizes)))

    contributing = [total_population]
    partial = [total_population]
    universal = [0]
    mrca_generation: int | None = None
    iap_generation: int | None = None

    for generation in range(1, max_generations + 1):
        parent_masks = [0] * total_population

        for destination, destination_size in enumerate(sizes):
            start = int(offsets[destination])
            end = int(offsets[destination + 1])
            source_a = rng.choice(
                sizes.size,
                size=int(destination_size),
                p=matrix[destination],
            )
            source_b = rng.choice(
                sizes.size,
                size=int(destination_size),
                p=matrix[destination],
            )
            parent_a = np.empty(
                int(destination_size),
                dtype=int,
            )
            parent_b = np.empty(
                int(destination_size),
                dtype=int,
            )

            for source in range(sizes.size):
                mask_a = source_a == source
                if np.any(mask_a):
                    parent_a[mask_a] = (
                        int(offsets[source])
                        + rng.integers(
                            0,
                            int(sizes[source]),
                            size=int(mask_a.sum()),
                        )
                    )
                mask_b = source_b == source
                if np.any(mask_b):
                    parent_b[mask_b] = (
                        int(offsets[source])
                        + rng.integers(
                            0,
                            int(sizes[source]),
                            size=int(mask_b.sum()),
                        )
                    )

            for child_index, a, b in zip(
                range(start, end),
                parent_a,
                parent_b,
            ):
                child_mask = descendant_masks[child_index]
                parent_masks[int(a)] |= child_mask
                parent_masks[int(b)] |= child_mask

        descendant_masks = parent_masks
        c, p, u = _status_counts(
            descendant_masks,
            universal_mask,
        )
        contributing.append(c)
        partial.append(p)
        universal.append(u)

        if mrca_generation is None and u > 0:
            mrca_generation = generation
        if iap_generation is None and c > 0 and u == c:
            iap_generation = generation
            if stop_at_iap:
                break

    return _finalize_result(
        total_population,
        contributing,
        partial,
        universal,
        mrca_generation,
        iap_generation,
        seed,
        community_sizes=sizes,
        parent_source_matrix=matrix,
    )
