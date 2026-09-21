import numpy as np
import pytest

from evolution_creation.pedigree_genome import (
    simulate_pedigree_genome,
    simulate_pedigree_genome_replicates,
)


SMALL_MAP = [0.5, 0.75, 1.0]


def test_initial_founder_fractions_are_exact():
    result = simulate_pedigree_genome(
        population_size=20,
        max_generations=0,
        founder_count=2,
        chromosome_lengths_morgans=SMALL_MAP,
        seed=1,
    )
    assert (
        result.any_founder_descendant_fraction[0]
        == pytest.approx(0.1)
    )
    assert (
        result.all_founders_descendant_fraction[0]
        == pytest.approx(0.0)
    )
    assert (
        result.genetic_carrier_fraction[0]
        == pytest.approx(0.1)
    )
    assert (
        result.mean_founder_dna_fraction[0]
        == pytest.approx(0.1)
    )


def test_genetic_carriers_are_genealogical_descendants():
    result = simulate_pedigree_genome(
        population_size=30,
        max_generations=8,
        founder_count=2,
        chromosome_lengths_morgans=SMALL_MAP,
        seed=3,
    )
    assert np.all(
        result.genetic_carrier_fraction
        <= (
            result.any_founder_descendant_fraction
            + 1e-12
        )
    )


def test_detectable_is_subset_of_genetic():
    result = simulate_pedigree_genome(
        population_size=30,
        max_generations=8,
        founder_count=2,
        chromosome_lengths_morgans=SMALL_MAP,
        detectable_threshold_cm=15.0,
        seed=4,
    )
    assert np.all(
        result.detectable_carrier_fraction
        <= (
            result.genetic_carrier_fraction
            + 1e-12
        )
    )


def test_zero_threshold_equals_any_genetic_dna():
    result = simulate_pedigree_genome(
        population_size=25,
        max_generations=6,
        founder_count=1,
        chromosome_lengths_morgans=SMALL_MAP,
        detectable_threshold_cm=0.0,
        seed=5,
    )
    np.testing.assert_allclose(
        result.detectable_carrier_fraction,
        result.genetic_carrier_fraction,
    )


def test_joint_categories_partition_population():
    result = simulate_pedigree_genome(
        population_size=30,
        max_generations=8,
        founder_count=2,
        chromosome_lengths_morgans=SMALL_MAP,
        detectable_threshold_cm=10.0,
        seed=6,
    )
    total = (
        result.not_all_founders_fraction
        + result.all_founders_no_dna_fraction
        + result.all_founders_subdetectable_fraction
        + result.all_founders_detectable_fraction
    )
    np.testing.assert_allclose(
        total,
        np.ones_like(total),
    )


def test_all_founders_universality_is_absorbing():
    result = simulate_pedigree_genome(
        population_size=20,
        max_generations=20,
        founder_count=2,
        chromosome_lengths_morgans=SMALL_MAP,
        seed=2,
    )
    generation = (
        result.all_founders_universal_generation
    )
    if generation is not None:
        assert np.all(
            result.all_founders_descendant_fraction[
                generation:
            ]
            == 1.0
        )


def test_replicate_summary_shapes():
    summary = simulate_pedigree_genome_replicates(
        population_size=16,
        max_generations=5,
        founder_count=2,
        chromosome_lengths_morgans=[
            0.4,
            0.6,
        ],
        replicates=4,
        seed=8,
    )
    assert (
        summary.mean_genetic_carrier_fraction.shape
        == (6,)
    )
    assert (
        summary.final_genetic_carrier_fraction.shape
        == (4,)
    )
    assert (
        summary.all_founders_universal_generations.shape
        == (4,)
    )
    assert (
        0.0
        <= summary.all_founders_universal_probability
        <= 1.0
    )


@pytest.mark.parametrize(
    "population_size, founder_count",
    [
        (1, 1),
        (20, 0),
        (20, 21),
    ],
)
def test_invalid_population_or_founders(
    population_size,
    founder_count,
):
    with pytest.raises(ValueError):
        simulate_pedigree_genome(
            population_size=population_size,
            founder_count=founder_count,
            max_generations=1,
            chromosome_lengths_morgans=SMALL_MAP,
        )
