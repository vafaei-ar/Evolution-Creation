import numpy as np
import pytest

from evolution_creation.genealogy import (
    deterministic_random_mating_curve,
    simulate_founder_spread,
    simulate_replicates,
)


def test_initial_fraction_is_correct():
    result = simulate_founder_spread(
        population_size=100,
        generations=5,
        founder_count=2,
        seed=1,
    )
    assert result.fractions[0] == pytest.approx(0.02)


def test_reproducible_with_fixed_seed():
    first = simulate_founder_spread(seed=123).fractions
    second = simulate_founder_spread(seed=123).fractions
    np.testing.assert_array_equal(first, second)


def test_fractions_stay_in_unit_interval():
    result = simulate_founder_spread(
        population_size=250,
        generations=100,
        founder_count=1,
        seed=7,
    )
    assert np.all((result.fractions >= 0.0) & (result.fractions <= 1.0))


def test_replicate_shape():
    curves = simulate_replicates(
        population_size=50,
        generations=12,
        founder_count=1,
        replicates=9,
        seed=9,
    )
    assert curves.shape == (9, 13)


def test_deterministic_curve_matches_recurrence():
    curve = deterministic_random_mating_curve(0.1, 2)
    assert curve[0] == pytest.approx(0.1)
    assert curve[1] == pytest.approx(0.19)
    assert curve[2] == pytest.approx(1 - 0.81**2)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"population_size": 1},
        {"generations": -1},
        {"founder_count": 0},
        {"population_size": 10, "founder_count": 11},
    ],
)
def test_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        simulate_founder_spread(**kwargs)
