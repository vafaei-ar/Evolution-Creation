"""Community endogamy and assortative-mating models.

Children are assigned to persistent communities. For a child in community i,
one anchor parent is sampled from community i. The mate's community is drawn
from a row-stochastic mate-choice matrix.

An optional same-state weight changes mate choice within the selected community
according to whether the mate shares the anchor parent's modeled founder-
ancestry state. This is an abstract sensitivity parameter, not a claim that deep
genealogical ancestry is observable to real people.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class EndogamySpreadResult:
    """Founder-ancestry spread across persistent social communities."""

    fractions_by_community: np.ndarray
    community_sizes: np.ndarray
    founder_community: int
    founder_count: int
    mate_choice_matrix: np.ndarray
    same_state_weight: float
    seed: int | None

    @property
    def generations(self) -> int:
        return int(self.fractions_by_community.shape[0] - 1)

    @property
    def global_fractions(self) -> np.ndarray:
        weights = self.community_sizes / self.community_sizes.sum()
        return self.fractions_by_community @ weights

    @property
    def all_communities_reached(self) -> bool:
        return bool(np.all(self.fractions_by_community[-1] > 0.0))

    @property
    def globally_fixed(self) -> bool:
        return bool(np.all(self.fractions_by_community[-1] == 1.0))


def validate_community_sizes(community_sizes: Sequence[int]) -> np.ndarray:
    sizes = np.asarray(community_sizes, dtype=int)
    if sizes.ndim != 1 or sizes.size < 2:
        raise ValueError("community_sizes must contain at least two communities")
    if np.any(sizes < 2):
        raise ValueError("each community must contain at least 2 individuals")
    return sizes


def validate_mate_choice_matrix(
    mate_choice_matrix: np.ndarray,
    n_communities: int,
) -> np.ndarray:
    matrix = np.asarray(mate_choice_matrix, dtype=float)
    if matrix.shape != (n_communities, n_communities):
        raise ValueError(
            f"mate_choice_matrix must have shape {(n_communities, n_communities)}"
        )
    if np.any(matrix < 0.0) or np.any(matrix > 1.0):
        raise ValueError("mate-choice probabilities must lie between 0 and 1")
    if not np.allclose(matrix.sum(axis=1), 1.0):
        raise ValueError("each mate-choice row must sum to 1")
    return matrix


def make_endogamy_matrix(
    community_sizes: Sequence[int],
    endogamy_strength: float,
) -> np.ndarray:
    """Interpolate between size-proportional mixing and perfect endogamy.

    endogamy_strength = 0:
        Mate community is drawn from the whole population in proportion to
        community size.

    endogamy_strength = 1:
        Mate always comes from the anchor parent's own community.

    Intermediate values mix these two processes.
    """
    sizes = validate_community_sizes(community_sizes)
    if not 0.0 <= endogamy_strength <= 1.0:
        raise ValueError("endogamy_strength must lie between 0 and 1")

    baseline = sizes / sizes.sum()
    matrix = (1.0 - endogamy_strength) * np.tile(
        baseline,
        (sizes.size, 1),
    )
    matrix += endogamy_strength * np.eye(sizes.size)
    return matrix


def _mate_ancestry_probability(
    ancestry_fraction: float,
    anchor_has_ancestry: bool,
    same_state_weight: float,
) -> float:
    """Probability selected mate has founder ancestry after state weighting."""
    if same_state_weight <= 0:
        raise ValueError("same_state_weight must be positive")
    if not 0.0 <= ancestry_fraction <= 1.0:
        raise ValueError("ancestry_fraction must lie between 0 and 1")

    f = ancestry_fraction
    if anchor_has_ancestry:
        numerator = same_state_weight * f
        denominator = numerator + (1.0 - f)
    else:
        numerator = f
        denominator = numerator + same_state_weight * (1.0 - f)

    if denominator == 0.0:
        return 0.0
    return float(numerator / denominator)


def deterministic_endogamy_curve(
    community_sizes: Sequence[int],
    generations: int,
    mate_choice_matrix: np.ndarray,
    founder_community: int = 0,
    founder_count: int = 1,
    same_state_weight: float = 1.0,
) -> np.ndarray:
    """Infinite-population approximation for community ancestry fractions."""
    sizes = validate_community_sizes(community_sizes)
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 0 <= founder_community < sizes.size:
        raise ValueError("founder_community is out of range")
    if not 1 <= founder_count <= sizes[founder_community]:
        raise ValueError("founder_count must fit within founder_community")
    if same_state_weight <= 0:
        raise ValueError("same_state_weight must be positive")

    matrix = validate_mate_choice_matrix(
        mate_choice_matrix,
        sizes.size,
    )

    fractions = np.zeros((generations + 1, sizes.size), dtype=float)
    fractions[0, founder_community] = (
        founder_count / sizes[founder_community]
    )

    for generation in range(generations):
        current = fractions[generation]
        next_fraction = np.empty(sizes.size, dtype=float)

        for community in range(sizes.size):
            anchor_fraction = current[community]

            mate_prob_if_anchor_negative = np.array(
                [
                    _mate_ancestry_probability(
                        ancestry_fraction=float(current[source]),
                        anchor_has_ancestry=False,
                        same_state_weight=same_state_weight,
                    )
                    for source in range(sizes.size)
                ]
            )
            mate_ancestry_probability = float(
                matrix[community] @ mate_prob_if_anchor_negative
            )

            next_fraction[community] = (
                anchor_fraction
                + (1.0 - anchor_fraction) * mate_ancestry_probability
            )

        fractions[generation + 1] = next_fraction

    return fractions


def simulate_endogamy_founder_spread(
    community_sizes: Sequence[int],
    generations: int,
    mate_choice_matrix: np.ndarray,
    founder_community: int = 0,
    founder_count: int = 1,
    same_state_weight: float = 1.0,
    seed: int | None = None,
) -> EndogamySpreadResult:
    """Stochastic founder-ancestry spread under community endogamy.

    For every child in community i:
    1. an anchor parent's ancestry state is sampled from community i;
    2. the mate's community is drawn from row i of mate_choice_matrix;
    3. the mate's ancestry state is sampled from that community, optionally
       weighted toward matching the anchor parent's ancestry state;
    4. the child has founder ancestry if either parent has it.

    Community sizes stay fixed in this model.
    """
    sizes = validate_community_sizes(community_sizes)
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 0 <= founder_community < sizes.size:
        raise ValueError("founder_community is out of range")
    if not 1 <= founder_count <= sizes[founder_community]:
        raise ValueError("founder_count must fit within founder_community")
    if same_state_weight <= 0:
        raise ValueError("same_state_weight must be positive")

    matrix = validate_mate_choice_matrix(
        mate_choice_matrix,
        sizes.size,
    )
    rng = np.random.default_rng(seed)

    counts = np.zeros(sizes.size, dtype=int)
    counts[founder_community] = founder_count

    fractions = np.empty((generations + 1, sizes.size), dtype=float)
    fractions[0] = counts / sizes

    for generation in range(1, generations + 1):
        current = counts / sizes
        next_counts = np.empty(sizes.size, dtype=int)

        for community, size in enumerate(sizes):
            anchor_fraction = float(current[community])

            mate_prob_if_anchor_negative = np.array(
                [
                    _mate_ancestry_probability(
                        ancestry_fraction=float(current[source]),
                        anchor_has_ancestry=False,
                        same_state_weight=same_state_weight,
                    )
                    for source in range(sizes.size)
                ]
            )
            mate_ancestry_probability = float(
                matrix[community] @ mate_prob_if_anchor_negative
            )

            child_ancestry_probability = (
                anchor_fraction
                + (1.0 - anchor_fraction) * mate_ancestry_probability
            )
            next_counts[community] = rng.binomial(
                int(size),
                child_ancestry_probability,
            )

        counts = next_counts
        fractions[generation] = counts / sizes

    return EndogamySpreadResult(
        fractions_by_community=fractions,
        community_sizes=sizes,
        founder_community=founder_community,
        founder_count=founder_count,
        mate_choice_matrix=matrix,
        same_state_weight=same_state_weight,
        seed=seed,
    )


def simulate_endogamy_replicates(
    community_sizes: Sequence[int],
    generations: int,
    mate_choice_matrix: np.ndarray,
    founder_community: int = 0,
    founder_count: int = 1,
    same_state_weight: float = 1.0,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Return shape (replicate, generation, community)."""
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(
        0,
        np.iinfo(np.uint32).max,
        size=replicates,
    )
    curves = [
        simulate_endogamy_founder_spread(
            community_sizes=community_sizes,
            generations=generations,
            mate_choice_matrix=mate_choice_matrix,
            founder_community=founder_community,
            founder_count=founder_count,
            same_state_weight=same_state_weight,
            seed=int(child_seed),
        ).fractions_by_community
        for child_seed in child_seeds
    ]
    return np.stack(curves, axis=0)


def probability_all_communities_reached(
    community_sizes: Sequence[int],
    endogamy_strengths: Sequence[float],
    generations: Sequence[int],
    founder_community: int = 0,
    founder_count: int = 1,
    same_state_weight: float = 1.0,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Estimate P(all communities contain descendants) over a sensitivity grid."""
    strengths = np.asarray(endogamy_strengths, dtype=float)
    generation_grid = np.asarray(generations, dtype=int)
    if np.any(strengths < 0.0) or np.any(strengths > 1.0):
        raise ValueError("endogamy_strengths must lie between 0 and 1")
    if np.any(generation_grid < 0):
        raise ValueError("generations must be non-negative")

    sizes = validate_community_sizes(community_sizes)
    master_rng = np.random.default_rng(seed)
    output = np.empty(
        (generation_grid.size, strengths.size),
        dtype=float,
    )

    for row, generation_count in enumerate(generation_grid):
        for col, strength in enumerate(strengths):
            matrix = make_endogamy_matrix(sizes, float(strength))
            replicate_seed = int(
                master_rng.integers(0, np.iinfo(np.uint32).max)
            )
            curves = simulate_endogamy_replicates(
                community_sizes=sizes,
                generations=int(generation_count),
                mate_choice_matrix=matrix,
                founder_community=founder_community,
                founder_count=founder_count,
                same_state_weight=same_state_weight,
                replicates=replicates,
                seed=replicate_seed,
            )
            output[row, col] = np.mean(
                np.all(curves[:, -1, :] > 0.0, axis=1)
            )

    return output
