"""Structured-population models for genealogical ancestry spread.

Migration is represented as parental-source mixing. For a child born in deme i,
row i of the migration matrix gives the probability that each parent is sampled
from each source deme j. Rows therefore sum to one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class StructuredSpreadResult:
    """Output from one structured-population ancestry simulation."""

    fractions_by_deme: np.ndarray
    deme_sizes: np.ndarray
    founder_deme: int
    founder_count: int
    generations: int
    migration_matrix: np.ndarray
    seed: int | None

    @property
    def global_fractions(self) -> np.ndarray:
        """Population-size weighted founder-ancestry fraction by generation."""
        weights = self.deme_sizes / self.deme_sizes.sum()
        return self.fractions_by_deme @ weights

    @property
    def all_demes_reached(self) -> bool:
        """Whether every deme has at least one descendant in the final generation."""
        return bool(np.all(self.fractions_by_deme[-1] > 0.0))

    @property
    def globally_fixed(self) -> bool:
        """Whether every individual in every deme descends from the founder(s)."""
        return bool(np.all(self.fractions_by_deme[-1] == 1.0))


def validate_migration_matrix(migration_matrix: np.ndarray, n_demes: int) -> np.ndarray:
    """Validate and return a floating-point migration matrix."""
    matrix = np.asarray(migration_matrix, dtype=float)
    if matrix.shape != (n_demes, n_demes):
        raise ValueError(f"migration_matrix must have shape {(n_demes, n_demes)}")
    if np.any(matrix < 0.0) or np.any(matrix > 1.0):
        raise ValueError("migration probabilities must lie between 0 and 1")
    if not np.allclose(matrix.sum(axis=1), 1.0):
        raise ValueError("each migration-matrix row must sum to 1")
    return matrix


def make_linear_migration_matrix(n_demes: int, migration_rate: float) -> np.ndarray:
    """Create nearest-neighbor parental mixing for demes arranged in a line.

    migration_rate is the total probability that a parent comes from an adjacent
    deme instead of the child's own deme. Interior demes split that probability
    equally between their two neighbors. Edge demes have one neighbor.
    """
    if n_demes < 2:
        raise ValueError("n_demes must be at least 2")
    if not 0.0 <= migration_rate <= 1.0:
        raise ValueError("migration_rate must be between 0 and 1")

    matrix = np.zeros((n_demes, n_demes), dtype=float)
    for i in range(n_demes):
        neighbors = [j for j in (i - 1, i + 1) if 0 <= j < n_demes]
        matrix[i, i] = 1.0 - migration_rate
        for j in neighbors:
            matrix[i, j] = migration_rate / len(neighbors)
    return matrix


def add_linear_barrier(migration_matrix: np.ndarray, barrier_after: int) -> np.ndarray:
    """Block parental mixing across one edge of a linear chain.

    barrier_after uses zero-based indexing. For example, barrier_after=1 blocks
    the edge between demes with indices 1 and 2. The removed cross-barrier
    probability is returned to each affected deme's diagonal entry.
    """
    matrix = np.asarray(migration_matrix, dtype=float).copy()
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("migration_matrix must be square")
    n_demes = matrix.shape[0]
    if not 0 <= barrier_after < n_demes - 1:
        raise ValueError("barrier_after must identify an edge between adjacent demes")
    matrix = validate_migration_matrix(matrix, n_demes)

    left = barrier_after
    right = barrier_after + 1
    removed_left = matrix[left, right]
    removed_right = matrix[right, left]
    matrix[left, right] = 0.0
    matrix[right, left] = 0.0
    matrix[left, left] += removed_left
    matrix[right, right] += removed_right
    return matrix


def simulate_structured_founder_spread(
    deme_sizes: Sequence[int],
    generations: int,
    migration_matrix: np.ndarray,
    founder_deme: int = 0,
    founder_count: int = 1,
    seed: int | None = None,
) -> StructuredSpreadResult:
    """Simulate genealogical founder ancestry across connected demes.

    Each deme has a fixed size and generations do not overlap. For every child
    in destination deme i, two parental source demes are sampled independently
    from row i of migration_matrix. A parent is then sampled uniformly from the
    selected source deme. The child has founder ancestry if either parent has
    founder ancestry.

    The model tracks genealogy only. It does not track DNA or recombination.
    """
    sizes = np.asarray(deme_sizes, dtype=int)
    if sizes.ndim != 1 or sizes.size < 2:
        raise ValueError("deme_sizes must contain at least two demes")
    if np.any(sizes < 2):
        raise ValueError("each deme size must be at least 2")
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 0 <= founder_deme < sizes.size:
        raise ValueError("founder_deme is out of range")
    if not 1 <= founder_count <= sizes[founder_deme]:
        raise ValueError("founder_count must fit within founder_deme")

    matrix = validate_migration_matrix(migration_matrix, sizes.size)
    rng = np.random.default_rng(seed)

    ancestry = [np.zeros(size, dtype=bool) for size in sizes]
    ancestry[founder_deme][:founder_count] = True

    fractions = np.empty((generations + 1, sizes.size), dtype=float)
    fractions[0] = [deme.mean() for deme in ancestry]

    for generation in range(1, generations + 1):
        next_ancestry: list[np.ndarray] = []
        for destination, destination_size in enumerate(sizes):
            source_a = rng.choice(sizes.size, size=destination_size, p=matrix[destination])
            source_b = rng.choice(sizes.size, size=destination_size, p=matrix[destination])

            parent_a_has_ancestry = np.zeros(destination_size, dtype=bool)
            parent_b_has_ancestry = np.zeros(destination_size, dtype=bool)

            for source in range(sizes.size):
                mask_a = source_a == source
                if np.any(mask_a):
                    idx_a = rng.integers(0, sizes[source], size=int(mask_a.sum()))
                    parent_a_has_ancestry[mask_a] = ancestry[source][idx_a]

                mask_b = source_b == source
                if np.any(mask_b):
                    idx_b = rng.integers(0, sizes[source], size=int(mask_b.sum()))
                    parent_b_has_ancestry[mask_b] = ancestry[source][idx_b]

            next_ancestry.append(parent_a_has_ancestry | parent_b_has_ancestry)

        ancestry = next_ancestry
        fractions[generation] = [deme.mean() for deme in ancestry]

    return StructuredSpreadResult(
        fractions_by_deme=fractions,
        deme_sizes=sizes,
        founder_deme=founder_deme,
        founder_count=founder_count,
        generations=generations,
        migration_matrix=matrix,
        seed=seed,
    )


def simulate_structured_replicates(
    deme_sizes: Sequence[int],
    generations: int,
    migration_matrix: np.ndarray,
    founder_deme: int = 0,
    founder_count: int = 1,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Run replicates and return shape (replicates, generations + 1, n_demes)."""
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(0, np.iinfo(np.uint32).max, size=replicates)
    curves = [
        simulate_structured_founder_spread(
            deme_sizes=deme_sizes,
            generations=generations,
            migration_matrix=migration_matrix,
            founder_deme=founder_deme,
            founder_count=founder_count,
            seed=int(child_seed),
        ).fractions_by_deme
        for child_seed in child_seeds
    ]
    return np.stack(curves, axis=0)


def probability_of_global_fixation(
    migration_rates: Sequence[float],
    generations: Sequence[int],
    deme_sizes: Sequence[int],
    founder_deme: int = 0,
    founder_count: int = 1,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Estimate global-fixation probability over migration/generation grids."""
    rates = np.asarray(migration_rates, dtype=float)
    generation_grid = np.asarray(generations, dtype=int)
    if np.any(rates < 0.0) or np.any(rates > 1.0):
        raise ValueError("migration_rates must lie between 0 and 1")
    if np.any(generation_grid < 0):
        raise ValueError("generations must be non-negative")

    master_rng = np.random.default_rng(seed)
    result = np.empty((generation_grid.size, rates.size), dtype=float)
    n_demes = len(deme_sizes)

    for row, g in enumerate(generation_grid):
        for col, rate in enumerate(rates):
            matrix = make_linear_migration_matrix(n_demes, float(rate))
            replicate_seed = int(master_rng.integers(0, np.iinfo(np.uint32).max))
            curves = simulate_structured_replicates(
                deme_sizes=deme_sizes,
                generations=int(g),
                migration_matrix=matrix,
                founder_deme=founder_deme,
                founder_count=founder_count,
                replicates=replicates,
                seed=replicate_seed,
            )
            result[row, col] = np.mean(np.all(curves[:, -1, :] == 1.0, axis=1))

    return result
