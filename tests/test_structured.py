import numpy as np
import pytest

from evolution_creation.structured import (
    add_linear_barrier,
    make_linear_migration_matrix,
    probability_of_global_fixation,
    simulate_structured_founder_spread,
    simulate_structured_replicates,
    validate_migration_matrix,
)


def test_linear_matrix_rows_sum_to_one():
    matrix = make_linear_migration_matrix(5, 0.2)
    np.testing.assert_allclose(matrix.sum(axis=1), 1.0)
    assert matrix[0, 1] == pytest.approx(0.2)
    assert matrix[2, 1] == pytest.approx(0.1)
    assert matrix[2, 3] == pytest.approx(0.1)


def test_zero_migration_prevents_spread_between_demes():
    matrix = np.eye(3)
    result = simulate_structured_founder_spread(
        deme_sizes=[100, 100, 100],
        generations=20,
        migration_matrix=matrix,
        founder_deme=0,
        founder_count=10,
        seed=11,
    )
    assert np.all(result.fractions_by_deme[:, 1:] == 0.0)


def test_positive_migration_can_reach_other_demes():
    matrix = make_linear_migration_matrix(3, 0.2)
    result = simulate_structured_founder_spread(
        deme_sizes=[200, 200, 200],
        generations=25,
        migration_matrix=matrix,
        founder_deme=0,
        founder_count=20,
        seed=2,
    )
    assert result.fractions_by_deme[-1, 1] > 0.0
    assert result.fractions_by_deme[-1, 2] > 0.0


def test_replicate_shape():
    matrix = make_linear_migration_matrix(4, 0.05)
    curves = simulate_structured_replicates(
        deme_sizes=[50, 60, 70, 80],
        generations=8,
        migration_matrix=matrix,
        founder_count=2,
        replicates=7,
        seed=5,
    )
    assert curves.shape == (7, 9, 4)


def test_global_fraction_is_weighted_by_deme_size():
    matrix = np.eye(2)
    result = simulate_structured_founder_spread(
        deme_sizes=[100, 300],
        generations=0,
        migration_matrix=matrix,
        founder_deme=0,
        founder_count=100,
    )
    assert result.global_fractions[0] == pytest.approx(0.25)


def test_fixation_grid_shape():
    grid = probability_of_global_fixation(
        migration_rates=[0.0, 0.05],
        generations=[2, 5, 10],
        deme_sizes=[25, 25],
        founder_count=5,
        replicates=3,
        seed=1,
    )
    assert grid.shape == (3, 2)
    assert np.all((grid >= 0.0) & (grid <= 1.0))


def test_invalid_migration_matrix_rejected():
    with pytest.raises(ValueError):
        validate_migration_matrix(np.array([[0.8, 0.1], [0.2, 0.8]]), 2)


def test_barrier_blocks_crossing_edge():
    matrix = add_linear_barrier(make_linear_migration_matrix(4, 0.2), barrier_after=1)
    assert matrix[1, 2] == 0.0
    assert matrix[2, 1] == 0.0
    np.testing.assert_allclose(matrix.sum(axis=1), 1.0)

    result = simulate_structured_founder_spread(
        deme_sizes=[100] * 4,
        generations=50,
        migration_matrix=matrix,
        founder_deme=0,
        founder_count=20,
        seed=3,
    )
    assert np.all(result.fractions_by_deme[:, 2:] == 0.0)
