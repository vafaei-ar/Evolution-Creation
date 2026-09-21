"""Time-varying connectivity models for genealogical ancestry spread.

A matrix schedule contains one migration matrix per reproductive transition.
Schedule index 0 produces generation 1 from generation 0. Therefore a barrier
with barrier_start=21 leaves transitions producing generations 1-20 connected
and first blocks the transition producing generation 21.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .structured import add_linear_barrier, validate_migration_matrix


@dataclass(frozen=True)
class TemporalSpreadResult:
    """Output from a time-varying structured-population simulation."""

    fractions_by_deme: np.ndarray
    deme_sizes: np.ndarray
    founder_deme: int
    founder_count: int
    matrix_schedule: np.ndarray
    seed: int | None

    @property
    def generations(self) -> int:
        return int(self.matrix_schedule.shape[0])

    @property
    def global_fractions(self) -> np.ndarray:
        weights = self.deme_sizes / self.deme_sizes.sum()
        return self.fractions_by_deme @ weights

    @property
    def globally_fixed(self) -> bool:
        return bool(np.all(self.fractions_by_deme[-1] == 1.0))


def validate_matrix_schedule(
    matrix_schedule: np.ndarray,
    generations: int,
    n_demes: int,
) -> np.ndarray:
    schedule = np.asarray(matrix_schedule, dtype=float)
    expected = (generations, n_demes, n_demes)
    if schedule.shape != expected:
        raise ValueError(f"matrix_schedule must have shape {expected}")
    for matrix in schedule:
        validate_migration_matrix(matrix, n_demes)
    return schedule


def make_constant_schedule(
    migration_matrix: np.ndarray,
    generations: int,
) -> np.ndarray:
    if generations < 0:
        raise ValueError("generations must be non-negative")

    matrix = np.asarray(migration_matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("migration_matrix must be square")
    matrix = validate_migration_matrix(matrix, matrix.shape[0])

    return np.repeat(matrix[None, :, :], generations, axis=0)


def make_barrier_schedule(
    migration_matrix: np.ndarray,
    generations: int,
    barrier_after: int,
    barrier_start: int = 1,
    barrier_end: int | None = None,
) -> np.ndarray:
    """Create a schedule with one linear barrier active over a time interval.

    barrier_start is the first child generation produced with the barrier active.
    The active interval is [barrier_start, barrier_end). If barrier_end is None,
    the barrier remains active through the final transition.

    barrier_start = generations + 1 represents a barrier that never becomes
    active during the simulated period.
    """
    if generations < 0:
        raise ValueError("generations must be non-negative")
    if not 1 <= barrier_start <= generations + 1:
        raise ValueError("barrier_start must lie in 1..generations+1")

    if barrier_end is None:
        barrier_end = generations + 1
    if not barrier_start <= barrier_end <= generations + 1:
        raise ValueError(
            "barrier_end must satisfy barrier_start <= barrier_end <= generations+1"
        )

    schedule = make_constant_schedule(migration_matrix, generations)
    blocked = add_linear_barrier(migration_matrix, barrier_after)
    schedule[barrier_start - 1 : barrier_end - 1] = blocked
    return schedule


def simulate_time_varying_founder_spread(
    deme_sizes: Sequence[int],
    matrix_schedule: np.ndarray,
    founder_deme: int = 0,
    founder_count: int = 1,
    seed: int | None = None,
) -> TemporalSpreadResult:
    sizes = np.asarray(deme_sizes, dtype=int)
    if sizes.ndim != 1 or sizes.size < 2:
        raise ValueError("deme_sizes must contain at least two demes")
    if np.any(sizes < 2):
        raise ValueError("each deme size must be at least 2")

    schedule_array = np.asarray(matrix_schedule)
    if schedule_array.ndim != 3:
        raise ValueError("matrix_schedule must be three-dimensional")
    generations = schedule_array.shape[0]
    schedule = validate_matrix_schedule(schedule_array, generations, sizes.size)

    if not 0 <= founder_deme < sizes.size:
        raise ValueError("founder_deme is out of range")
    if not 1 <= founder_count <= sizes[founder_deme]:
        raise ValueError("founder_count must fit within founder_deme")

    rng = np.random.default_rng(seed)
    ancestry = [np.zeros(size, dtype=bool) for size in sizes]
    ancestry[founder_deme][:founder_count] = True

    fractions = np.empty((generations + 1, sizes.size), dtype=float)
    fractions[0] = [deme.mean() for deme in ancestry]

    for transition, matrix in enumerate(schedule, start=1):
        next_ancestry: list[np.ndarray] = []

        for destination, destination_size in enumerate(sizes):
            source_a = rng.choice(
                sizes.size,
                size=destination_size,
                p=matrix[destination],
            )
            source_b = rng.choice(
                sizes.size,
                size=destination_size,
                p=matrix[destination],
            )

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
        fractions[transition] = [deme.mean() for deme in ancestry]

    return TemporalSpreadResult(
        fractions_by_deme=fractions,
        deme_sizes=sizes,
        founder_deme=founder_deme,
        founder_count=founder_count,
        matrix_schedule=schedule,
        seed=seed,
    )


def simulate_time_varying_replicates(
    deme_sizes: Sequence[int],
    matrix_schedule: np.ndarray,
    founder_deme: int = 0,
    founder_count: int = 1,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    master_rng = np.random.default_rng(seed)
    child_seeds = master_rng.integers(
        0,
        np.iinfo(np.uint32).max,
        size=replicates,
    )

    curves = [
        simulate_time_varying_founder_spread(
            deme_sizes=deme_sizes,
            matrix_schedule=matrix_schedule,
            founder_deme=founder_deme,
            founder_count=founder_count,
            seed=int(child_seed),
        ).fractions_by_deme
        for child_seed in child_seeds
    ]
    return np.stack(curves, axis=0)


def probability_of_global_fixation_by_barrier_timing(
    base_matrix: np.ndarray,
    barrier_after: int,
    closure_generations: Sequence[int],
    final_generation: int,
    deme_sizes: Sequence[int],
    founder_deme: int = 0,
    founder_count: int = 1,
    replicates: int = 100,
    seed: int | None = None,
) -> np.ndarray:
    """Estimate fixation probability as a function of permanent closure time."""
    if final_generation < 1:
        raise ValueError("final_generation must be at least 1")

    closures = np.asarray(closure_generations, dtype=int)
    if np.any(closures < 1) or np.any(closures > final_generation + 1):
        raise ValueError(
            "closure_generations must lie in 1..final_generation+1"
        )

    master_rng = np.random.default_rng(seed)
    probabilities = np.empty(closures.size, dtype=float)

    for i, closure in enumerate(closures):
        schedule = make_barrier_schedule(
            migration_matrix=base_matrix,
            generations=final_generation,
            barrier_after=barrier_after,
            barrier_start=int(closure),
        )
        replicate_seed = int(
            master_rng.integers(0, np.iinfo(np.uint32).max)
        )
        curves = simulate_time_varying_replicates(
            deme_sizes=deme_sizes,
            matrix_schedule=schedule,
            founder_deme=founder_deme,
            founder_count=founder_count,
            replicates=replicates,
            seed=replicate_seed,
        )
        probabilities[i] = np.mean(
            np.all(curves[:, -1, :] == 1.0, axis=1)
        )

    return probabilities
