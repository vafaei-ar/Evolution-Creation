import numpy as np
import pytest

from evolution_creation.assortment import (
    deterministic_endogamy_curve,
    make_endogamy_matrix,
    probability_all_communities_reached,
    simulate_endogamy_founder_spread,
    simulate_endogamy_replicates,
)


def test_endogamy_matrix_rows_sum_to_one():
    matrix = make_endogamy_matrix([100, 200, 300], 0.8)
    np.testing.assert_allclose(matrix.sum(axis=1), 1.0)


def test_zero_endogamy_uses_population_size_proportions():
    sizes = np.array([100, 200, 300])
    matrix = make_endogamy_matrix(sizes, 0.0)
    expected = sizes / sizes.sum()
    for row in matrix:
        np.testing.assert_allclose(row, expected)


def test_perfect_endogamy_is_identity():
    matrix = make_endogamy_matrix([100, 200, 300], 1.0)
    np.testing.assert_array_equal(matrix, np.eye(3))


def test_perfect_endogamy_blocks_other_communities():
    matrix = make_endogamy_matrix([100, 100, 100], 1.0)
    result = simulate_endogamy_founder_spread(
        community_sizes=[100, 100, 100],
        generations=40,
        mate_choice_matrix=matrix,
        founder_community=0,
        founder_count=20,
        seed=4,
    )
    assert np.all(result.fractions_by_community[:, 1:] == 0.0)


def test_partial_exogamy_can_spread_to_other_communities():
    matrix = make_endogamy_matrix([200, 200, 200], 0.5)
    result = simulate_endogamy_founder_spread(
        community_sizes=[200, 200, 200],
        generations=30,
        mate_choice_matrix=matrix,
        founder_community=0,
        founder_count=50,
        seed=2,
    )
    assert np.all(result.fractions_by_community[-1] > 0.0)


def test_same_state_assortment_slows_deterministic_spread():
    sizes = [1000, 1000, 1000]
    matrix = make_endogamy_matrix(sizes, 0.5)
    neutral = deterministic_endogamy_curve(
        sizes,
        generations=10,
        mate_choice_matrix=matrix,
        founder_count=10,
        same_state_weight=1.0,
    )
    assortative = deterministic_endogamy_curve(
        sizes,
        generations=10,
        mate_choice_matrix=matrix,
        founder_count=10,
        same_state_weight=5.0,
    )
    assert assortative[-1].mean() < neutral[-1].mean()


def test_higher_endogamy_slows_cross_community_deterministic_spread():
    sizes = [1000, 1000, 1000]
    low = deterministic_endogamy_curve(
        sizes,
        generations=8,
        mate_choice_matrix=make_endogamy_matrix(sizes, 0.2),
        founder_count=10,
    )
    high = deterministic_endogamy_curve(
        sizes,
        generations=8,
        mate_choice_matrix=make_endogamy_matrix(sizes, 0.95),
        founder_count=10,
    )
    assert high[-1, -1] < low[-1, -1]


def test_replicate_shape():
    sizes = [50, 60, 70, 80]
    curves = simulate_endogamy_replicates(
        community_sizes=sizes,
        generations=12,
        mate_choice_matrix=make_endogamy_matrix(sizes, 0.8),
        founder_count=5,
        replicates=7,
        seed=8,
    )
    assert curves.shape == (7, 13, 4)


def test_reachability_grid_shape_and_bounds():
    grid = probability_all_communities_reached(
        community_sizes=[30, 30, 30],
        endogamy_strengths=[0.0, 0.9, 1.0],
        generations=[5, 10],
        founder_count=5,
        replicates=4,
        seed=1,
    )
    assert grid.shape == (2, 3)
    assert np.all((grid >= 0.0) & (grid <= 1.0))
    assert np.all(grid[:, -1] == 0.0)


@pytest.mark.parametrize("strength", [-0.1, 1.1])
def test_invalid_endogamy_strength(strength):
    with pytest.raises(ValueError):
        make_endogamy_matrix([100, 100], strength)
