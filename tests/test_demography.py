import numpy as np
import pytest

from evolution_creation.demography import (
    apply_population_bottleneck,
    constant_population_schedule,
    deterministic_ancestry_fraction_curve,
    deterministic_descendant_counts,
    deterministic_overlapping_ancestry_fractions,
    exponential_population_schedule,
    logistic_population_schedule,
    simulate_demographic_founder_spread,
    simulate_demographic_replicates,
    simulate_overlapping_ancestry_sets,
)


def test_logistic_schedule_starts_correctly_and_approaches_capacity():
    sizes = logistic_population_schedule(
        initial_population=100,
        carrying_capacity=1000,
        growth_rate=0.25,
        generations=50,
    )
    assert sizes[0] == 100
    assert np.all(sizes <= 1000)
    assert sizes[-1] > 900
    assert np.all(np.diff(sizes) >= 0)


def test_exponential_schedule_grows():
    sizes = exponential_population_schedule(100, 0.1, 10)
    assert sizes[0] == 100
    assert sizes[-1] > sizes[0]


def test_bottleneck_replaces_requested_interval():
    base = constant_population_schedule(100, 10)
    changed = apply_population_bottleneck(base, 3, 4, 20)
    np.testing.assert_array_equal(changed[3:7], np.full(4, 20))
    assert changed[2] == 100
    assert changed[7] == 100


def test_deterministic_fraction_does_not_depend_on_future_population_size():
    constant = constant_population_schedule(100, 8)
    logistic = logistic_population_schedule(100, 1000, 0.5, 8)

    constant_fraction = deterministic_descendant_counts(
        constant,
        founder_count=1,
    ) / constant
    logistic_fraction = deterministic_descendant_counts(
        logistic,
        founder_count=1,
    ) / logistic

    np.testing.assert_allclose(constant_fraction, logistic_fraction)


def test_weighted_ancestry_increases_next_generation_fraction():
    neutral = deterministic_ancestry_fraction_curve(0.01, 1, 1.0)
    advantaged = deterministic_ancestry_fraction_curve(0.01, 1, 2.0)
    assert advantaged[1] > neutral[1]


def test_all_founders_remain_fixed_under_any_schedule():
    schedule = np.array([50, 100, 20, 500, 1000])
    result = simulate_demographic_founder_spread(
        population_sizes=schedule,
        founder_count=50,
        seed=1,
    )
    np.testing.assert_array_equal(result.descendant_counts, schedule)


def test_replicate_shape():
    schedule = logistic_population_schedule(50, 300, 0.3, 12)
    curves = simulate_demographic_replicates(
        schedule,
        founder_count=2,
        replicates=7,
        seed=2,
    )
    assert curves.shape == (7, 13)
    assert np.all((curves >= 0.0) & (curves <= 1.0))


def test_overlap_sets_are_not_a_partition_after_mixing():
    fractions = deterministic_overlapping_ancestry_fractions(
        initial_population=100,
        founder_count=1,
        generations=8,
    )
    founder_descended = fractions[:, 0] + fractions[:, 2]
    background_descended = fractions[:, 1] + fractions[:, 2]

    assert fractions[1, 2] > 0.0
    assert np.any(founder_descended + background_descended > 1.0)


def test_stochastic_overlap_counts_sum_to_population():
    schedule = logistic_population_schedule(100, 500, 0.25, 15)
    result = simulate_overlapping_ancestry_sets(
        schedule,
        founder_count=1,
        seed=3,
    )
    np.testing.assert_array_equal(
        result.category_counts.sum(axis=1),
        schedule,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"initial_population": 1, "carrying_capacity": 10},
        {"initial_population": 100, "carrying_capacity": 50},
        {"initial_population": 100, "carrying_capacity": 1000, "growth_rate": -0.1},
    ],
)
def test_invalid_logistic_inputs(kwargs):
    defaults = {"growth_rate": 0.1, "generations": 10}
    defaults.update(kwargs)
    with pytest.raises(ValueError):
        logistic_population_schedule(**defaults)
