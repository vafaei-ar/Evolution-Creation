import numpy as np
import pytest

from evolution_creation.coalescence import (
    chang_asymptotic_generations,
    make_parent_source_matrix,
    simulate_coalescence_replicates,
    simulate_pedigree_coalescence,
    simulate_structured_pedigree_coalescence,
)


def test_chang_asymptotic_benchmark_at_power_of_two():
    mrca, iap = chang_asymptotic_generations(1024)
    assert mrca == pytest.approx(10.0)
    assert iap == pytest.approx(17.7)


def test_status_counts_partition_population():
    result = simulate_pedigree_coalescence(
        population_size=80,
        max_generations=30,
        seed=2,
        stop_at_iap=False,
    )
    np.testing.assert_array_equal(
        result.noncontributing_counts
        + result.partial_counts
        + result.universal_counts,
        np.full(result.generations_back.size, 80),
    )


def test_mrca_precedes_iap_for_fixed_seed():
    result = simulate_pedigree_coalescence(
        population_size=100,
        max_generations=40,
        seed=7,
    )
    assert result.mrca_generation is not None
    assert result.iap_generation is not None
    assert result.mrca_generation <= result.iap_generation


def test_reproducible_with_fixed_seed():
    first = simulate_pedigree_coalescence(
        120,
        40,
        seed=123,
    )
    second = simulate_pedigree_coalescence(
        120,
        40,
        seed=123,
    )
    np.testing.assert_array_equal(
        first.contributing_counts,
        second.contributing_counts,
    )
    np.testing.assert_array_equal(
        first.universal_counts,
        second.universal_counts,
    )
    assert first.mrca_generation == second.mrca_generation
    assert first.iap_generation == second.iap_generation


def test_replicate_summary_shapes_and_bounds():
    summary = simulate_coalescence_replicates(
        population_size=60,
        max_generations=30,
        replicates=8,
        seed=11,
    )
    assert summary.mrca_generations.shape == (8,)
    assert summary.iap_generations.shape == (8,)
    assert 0.0 <= summary.mrca_reached_fraction <= 1.0
    assert 0.0 <= summary.iap_reached_fraction <= 1.0


def test_zero_isolation_is_size_proportional_panmixia():
    sizes = np.array([100, 200, 300])
    matrix = make_parent_source_matrix(sizes, 0.0)
    expected = sizes / sizes.sum()
    for row in matrix:
        np.testing.assert_allclose(row, expected)


def test_complete_isolation_is_identity():
    matrix = make_parent_source_matrix(
        [100, 100, 100],
        1.0,
    )
    np.testing.assert_array_equal(matrix, np.eye(3))


def test_complete_isolation_prevents_global_mrca():
    sizes = [30, 30]
    result = simulate_structured_pedigree_coalescence(
        community_sizes=sizes,
        parent_source_matrix=make_parent_source_matrix(
            sizes,
            1.0,
        ),
        max_generations=40,
        seed=4,
    )
    assert result.mrca_generation is None
    assert result.iap_generation is None
    assert np.all(result.universal_counts == 0)


def test_structured_status_counts_partition_population():
    sizes = [25, 35, 40]
    result = simulate_structured_pedigree_coalescence(
        community_sizes=sizes,
        parent_source_matrix=make_parent_source_matrix(
            sizes,
            0.8,
        ),
        max_generations=30,
        seed=5,
        stop_at_iap=False,
    )
    total = sum(sizes)
    np.testing.assert_array_equal(
        result.noncontributing_counts
        + result.partial_counts
        + result.universal_counts,
        np.full(result.generations_back.size, total),
    )


@pytest.mark.parametrize("strength", [-0.1, 1.1])
def test_invalid_isolation_strength(strength):
    with pytest.raises(ValueError):
        make_parent_source_matrix(
            [50, 50],
            strength,
        )
