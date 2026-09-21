import numpy as np
import pytest

from evolution_creation.evidence_calibration import (
    BYARD_POPULATION_MODEL_SET,
    contact_generations,
    descendant_fraction_best_case,
    founder_generations,
    independent_fixation_approximation,
    preclosure_generations,
    required_external_parent_rate,
    sample_evidence_envelope,
    simulate_bottleneck_fixation_probability,
    simulate_fixation_rates,
)


def test_11ka_generation_range_matches_26_to_30_year_intervals():
    assert founder_generations(
        11_000,
        26,
    ) == 423
    assert founder_generations(
        11_000,
        30,
    ) == 367


def test_contact_window_1797_is_eight_or_nine_generations():
    assert contact_generations(
        1797,
        2026,
        26,
    ) == 9
    assert contact_generations(
        1797,
        2026,
        30,
    ) == 8


def test_direct_isolation_bracket_is_before_11ka_founders():
    for isolation in [
        11_960,
        12_890,
    ]:
        assert preclosure_generations(
            11_000,
            isolation,
            28,
        ) == 0


def test_younger_isolation_creates_preclosure_window():
    assert preclosure_generations(
        11_000,
        10_000,
        25,
    ) == 40


def test_descendant_fraction_is_monotone_in_external_rate():
    vals = [
        descendant_fraction_best_case(
            m,
            8,
        )
        for m
        in [
            0.001,
            0.005,
            0.01,
            0.02,
        ]
    ]
    assert np.all(
        np.diff(
            vals
        )
        > 0
    )


def test_required_rate_hits_target_under_independence_approximation():
    rate = required_external_parent_rate(
        0.5,
        generations=8,
        population_size=7000,
    )
    p = independent_fixation_approximation(
        rate,
        generations=8,
        population_size=7000,
    )
    assert p == pytest.approx(
        0.5,
        rel=1e-9,
    )


def test_required_rate_decreases_with_more_generations():
    rates = [
        required_external_parent_rate(
            0.95,
            g,
            7000,
        )
        for g
        in [
            7,
            8,
            9,
        ]
    ]
    assert np.all(
        np.diff(
            rates
        )
        < 0
    )


def test_byard_model_set_spans_low_mid_high_models():
    assert (
        BYARD_POPULATION_MODEL_SET.min()
        == 3848
    )
    assert (
        BYARD_POPULATION_MODEL_SET.max()
        == 12106
    )
    assert (
        7465
        in BYARD_POPULATION_MODEL_SET
    )


def test_evidence_envelope_has_no_preclosure_window_for_default_bracket():
    result = sample_evidence_envelope(
        samples=1000,
        seed=3,
    )
    assert np.all(
        result.preclosure_generations
        == 0
    )
    assert set(
        np.unique(
            result.late_contact_generations
        )
    ).issubset(
        {
            8,
            9,
        }
    )
    assert (
        result.required_rate_50.shape
        == (
            1000,
        )
    )
    assert np.all(
        result.required_rate_95
        > result.required_rate_50
    )


def test_monte_carlo_fixation_increases_with_rate():
    result = simulate_fixation_rates(
        [
            0.005,
            0.01,
            0.02,
            0.04,
        ],
        generations=8,
        population_size=500,
        replicates=1500,
        seed=5,
    )
    assert np.all(
        np.diff(
            result.fixation_probability
        )
        >= 0
    )
    assert (
        result.fixation_probability[
            -1
        ]
        > result.fixation_probability[
            0
        ]
    )


def test_bottleneck_can_change_fixation_probability():
    low = simulate_bottleneck_fixation_probability(
        0.02,
        [
            7000,
        ]
        * 9,
        replicates=1500,
        seed=8,
    )
    bottleneck = simulate_bottleneck_fixation_probability(
        0.02,
        [
            7000,
            350,
            350,
            350,
            350,
            350,
            350,
            350,
            350,
        ],
        replicates=1500,
        seed=8,
    )
    assert bottleneck != pytest.approx(
        low
    )
