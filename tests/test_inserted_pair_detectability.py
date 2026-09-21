import pytest

from evolution_creation.inserted_pair_detectability import (
    at_least_one_marker_detected,
    initial_pair_genome_fraction,
    sample_detection_probability,
    simulate_private_marker,
)


def test_pair_fraction():
    assert initial_pair_genome_fraction(10_000) == pytest.approx(0.0002)


def test_sampling_detection():
    assert sample_detection_probability(0.01, 1000) > 0.999999


def test_many_markers_easier_to_detect():
    one = at_least_one_marker_detected(0.01, 1)
    hundred = at_least_one_marker_detected(0.01, 100)
    assert hundred > one
    assert hundred > 0.6


def test_neutral_marker_mostly_lost_after_400_generations():
    r = simulate_private_marker(
        effective_population_size=10_000,
        generations=400,
        initial_copies=2,
        replicates=8_000,
        sample_diploids=1000,
        seed=7,
    )
    assert r["survival_probability"] < 0.03
    assert r["survival_probability"] > 0.001
    assert r["fixation_probability_by_time"] < 0.01


def test_zero_private_markers_means_no_unique_marker_detection():
    assert at_least_one_marker_detected(0.5, 0) == 0.0
