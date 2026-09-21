import numpy as np
import pytest

from evolution_creation.structured import make_linear_migration_matrix
from evolution_creation.temporal import (
    make_barrier_schedule,
    make_constant_schedule,
    probability_of_global_fixation_by_barrier_timing,
    simulate_time_varying_founder_spread,
    simulate_time_varying_replicates,
)


def test_constant_schedule_shape():
    matrix = make_linear_migration_matrix(3, 0.1)
    schedule = make_constant_schedule(matrix, 7)
    assert schedule.shape == (7, 3, 3)


def test_barrier_from_first_generation_blocks_right_component():
    matrix = make_linear_migration_matrix(4, 0.2)
    schedule = make_barrier_schedule(
        matrix,
        generations=40,
        barrier_after=1,
        barrier_start=1,
    )
    result = simulate_time_varying_founder_spread(
        deme_sizes=[100] * 4,
        matrix_schedule=schedule,
        founder_deme=0,
        founder_count=20,
        seed=3,
    )
    assert np.all(result.fractions_by_deme[:, 2:] == 0.0)


def test_late_barrier_does_not_erase_ancestry_that_already_crossed():
    matrix = make_linear_migration_matrix(3, 0.5)
    schedule = make_barrier_schedule(
        matrix,
        generations=25,
        barrier_after=0,
        barrier_start=8,
    )
    result = simulate_time_varying_founder_spread(
        deme_sizes=[200] * 3,
        matrix_schedule=schedule,
        founder_deme=0,
        founder_count=100,
        seed=4,
    )
    assert result.fractions_by_deme[7, 1] > 0.0
    assert result.fractions_by_deme[-1, 1] > 0.0


def test_temporary_barrier_can_reopen():
    matrix = make_linear_migration_matrix(3, 0.2)
    schedule = make_barrier_schedule(
        matrix,
        generations=50,
        barrier_after=0,
        barrier_start=1,
        barrier_end=16,
    )
    result = simulate_time_varying_founder_spread(
        deme_sizes=[200] * 3,
        matrix_schedule=schedule,
        founder_deme=0,
        founder_count=50,
        seed=6,
    )
    assert np.all(result.fractions_by_deme[:16, 1:] == 0.0)
    assert result.fractions_by_deme[-1, 1] > 0.0


def test_never_active_barrier_matches_connected_schedule():
    matrix = make_linear_migration_matrix(3, 0.1)
    connected = make_constant_schedule(matrix, 12)
    never_active = make_barrier_schedule(
        matrix,
        generations=12,
        barrier_after=0,
        barrier_start=13,
    )
    np.testing.assert_array_equal(connected, never_active)


def test_replicate_shape():
    matrix = make_linear_migration_matrix(3, 0.1)
    schedule = make_constant_schedule(matrix, 8)
    curves = simulate_time_varying_replicates(
        deme_sizes=[50] * 3,
        matrix_schedule=schedule,
        founder_count=5,
        replicates=4,
        seed=1,
    )
    assert curves.shape == (4, 9, 3)


def test_timing_probability_shape_and_bounds():
    matrix = make_linear_migration_matrix(3, 0.1)
    probabilities = probability_of_global_fixation_by_barrier_timing(
        base_matrix=matrix,
        barrier_after=0,
        closure_generations=[1, 5, 11],
        final_generation=10,
        deme_sizes=[30] * 3,
        founder_count=10,
        replicates=3,
        seed=1,
    )
    assert probabilities.shape == (3,)
    assert np.all((probabilities >= 0.0) & (probabilities <= 1.0))


def test_invalid_barrier_window():
    matrix = make_linear_migration_matrix(3, 0.1)
    with pytest.raises(ValueError):
        make_barrier_schedule(
            matrix,
            generations=10,
            barrier_after=0,
            barrier_start=8,
            barrier_end=7,
        )
