import numpy as np
import pytest

from evolution_creation.genetic_ancestry import (
    balanced_autosome_map,
    coop_fragment_mean,
    coop_genetic_ancestor_probability,
    expected_genetic_ancestor_count,
    simulate_path_replicates,
    simulate_single_path,
)


def test_balanced_map_has_expected_total_length():
    lengths = balanced_autosome_map()
    assert lengths.shape == (22,)
    assert lengths.sum() == pytest.approx(33.0)


def test_published_probability_examples():
    assert coop_genetic_ancestor_probability(
        8
    ) == pytest.approx(
        0.8615,
        abs=5e-5,
    )
    assert coop_genetic_ancestor_probability(
        16
    ) == pytest.approx(
        0.0157,
        abs=5e-5,
    )


def test_first_generation_is_certain_and_half_diploid_genome():
    result = simulate_single_path(
        max_generations=1,
        seed=1,
    )
    assert result.has_any_founder_dna[0]
    assert (
        result.founder_fraction_diploid[0]
        == pytest.approx(0.5)
    )
    assert result.segment_counts[0] == 22


def test_expected_fraction_halves_each_generation_in_monte_carlo():
    summary = simulate_path_replicates(
        max_generations=8,
        replicates=1500,
        seed=5,
    )
    assert (
        summary.mean_founder_fraction[4]
        == pytest.approx(
            0.5**5,
            abs=0.004,
        )
    )
    assert (
        summary.mean_founder_fraction[7]
        == pytest.approx(
            0.5**8,
            abs=0.001,
        )
    )


def test_detection_probability_cannot_exceed_any_dna_probability():
    summary = simulate_path_replicates(
        max_generations=12,
        detectable_threshold_cm=6.0,
        replicates=500,
        seed=7,
    )
    assert np.all(
        summary.detectable_probability
        <= summary.any_dna_probability
    )


def test_genetic_ancestor_count_is_far_below_genealogical_slots_late():
    k = 16
    expected = expected_genetic_ancestor_count(
        k
    )
    assert expected < 0.02 * (2**k)


def test_fragment_mean_formula():
    assert coop_fragment_mean(1) == 22.0
    assert coop_fragment_mean(
        8
    ) == pytest.approx(
        (22 + 33 * 7) / 2**7
    )


@pytest.mark.parametrize(
    "generation",
    [0, -1],
)
def test_invalid_generation(generation):
    with pytest.raises(ValueError):
        coop_fragment_mean(
            generation
        )
