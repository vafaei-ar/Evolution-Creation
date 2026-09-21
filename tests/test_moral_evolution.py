import numpy as np
import pytest

from evolution_creation.moral_evolution import (
    final_cooperation_grid,
    selection_gradient,
    simulate_conformity_only,
    simulate_norm_dynamics,
)


def test_without_support_costly_cooperation_declines():
    r = simulate_norm_dynamics(
        initial_cooperation=0.5,
        cooperation_cost=0.2,
        punishment_strength=0.0,
        conformity_strength=0.0,
    )
    assert r.cooperative_fraction[-1] < r.cooperative_fraction[0]


def test_punishment_can_promote_cooperation():
    weak = simulate_norm_dynamics(
        initial_cooperation=0.6,
        cooperation_cost=0.2,
        punishment_strength=0.0,
        conformity_strength=0.0,
    )
    strong = simulate_norm_dynamics(
        initial_cooperation=0.6,
        cooperation_cost=0.2,
        punishment_strength=0.8,
        conformity_strength=0.0,
    )
    assert strong.cooperative_fraction[-1] > weak.cooperative_fraction[-1]
    assert strong.cooperative_fraction[-1] > 0.9


def test_conformity_is_majority_sensitive():
    high = simulate_conformity_only(0.8, conformity_strength=1.0)
    low = simulate_conformity_only(0.2, conformity_strength=1.0)
    assert high[-1] > 0.95
    assert low[-1] < 0.05


def test_conformity_does_not_encode_moral_content():
    # The exact same dynamics stabilize any majority label. If x denotes a
    # harmful norm rather than a cooperative norm, the mathematics is unchanged.
    harmful_majority = simulate_conformity_only(0.8, conformity_strength=1.0)
    beneficial_majority = simulate_conformity_only(0.8, conformity_strength=1.0)
    np.testing.assert_allclose(harmful_majority, beneficial_majority)


def test_selection_gradient_changes_sign():
    assert selection_gradient(0.2, 0.2, 0.0, 0.0) < 0
    assert selection_gradient(0.8, 0.2, 0.8, 0.0) > 0


def test_grid_shape_and_bounds():
    grid = final_cooperation_grid(
        np.array([0.2, 0.5, 0.8]),
        np.array([0.0, 0.5, 1.0]),
        conformity_strength=0.2,
        steps=100,
    )
    assert grid.shape == (3, 3)
    assert np.all((grid >= 0) & (grid <= 1))


def test_invalid_fraction_raises():
    with pytest.raises(ValueError):
        simulate_norm_dynamics(initial_cooperation=1.2)
