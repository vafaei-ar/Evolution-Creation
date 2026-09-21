import numpy as np
import pytest

from evolution_creation.historical_constraints import (
    apply_region_bottleneck,
    deterministic_historical_genealogy,
    deterministic_late_contact_fraction,
    earliest_reachable_generations,
    make_debate_historical_scenario,
    simulate_historical_genealogy,
    simulate_historical_pedigree_genome,
    simulate_late_contact_sensitivity,
    years_to_generations,
)


def test_founder_age_converts_to_440_generations():
    assert years_to_generations(
        11_000,
        25,
    ) == 440


def test_default_tasmania_barrier_is_closed_at_founder_insertion():
    scenario = make_debate_historical_scenario()
    assert (
        scenario.metadata[
            "isolation_generation"
        ]
        == 0
    )
    assert (
        scenario.metadata[
            "late_contact_generations"
        ]
        == 9
    )
    assert (
        scenario.metadata[
            "late_contact_start_generation"
        ]
        == 432
    )


def test_hard_isolation_makes_tasmania_unreachable():
    scenario = make_debate_historical_scenario(
        tasmania_late_contact_rate=0.0,
        tasmania_isolation_age_years=12_000,
    )
    reach = earliest_reachable_generations(
        scenario
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert np.isinf(
        reach[
            tasmania
        ]
    )


def test_positive_late_contact_makes_tasmania_topologically_reachable():
    scenario = make_debate_historical_scenario(
        tasmania_late_contact_rate=0.01,
        tasmania_isolation_age_years=12_000,
    )
    reach = earliest_reachable_generations(
        scenario
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert reach[
        tasmania
    ] == pytest.approx(
        432.0
    )


def test_younger_isolation_date_creates_preclosure_window():
    scenario = make_debate_historical_scenario(
        tasmania_isolation_age_years=10_000,
        tasmania_late_contact_rate=0.0,
    )
    assert (
        scenario.metadata[
            "isolation_generation"
        ]
        == 40
    )
    reach = earliest_reachable_generations(
        scenario
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert np.isfinite(
        reach[
            tasmania
        ]
    )


def test_deterministic_state_probabilities_partition_each_region():
    scenario = make_debate_historical_scenario(
        founder_age_years=500,
        region_sizes=(
            10,
            10,
            10,
            10,
            10,
            10,
        ),
        founder_pair_joint_children=1,
    )
    result = deterministic_historical_genealogy(
        scenario
    )
    np.testing.assert_allclose(
        result.mask_fractions_by_region.sum(
            axis=2
        ),
        np.ones(
            (
                scenario.generations
                + 1,
                6,
            )
        ),
        atol=1e-12,
    )


def test_deterministic_hard_barrier_keeps_tasmania_founder_free():
    scenario = make_debate_historical_scenario(
        tasmania_isolation_age_years=12_000,
        tasmania_late_contact_rate=0.0,
    )
    result = deterministic_historical_genealogy(
        scenario
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert np.all(
        result.any_founder_fraction_by_region[
            :,
            tasmania,
        ]
        == 0.0
    )


def test_stochastic_genealogy_respects_hard_barrier():
    scenario = make_debate_historical_scenario(
        founder_age_years=500,
        region_sizes=(
            12,
            12,
            12,
            12,
            12,
            12,
        ),
        tasmania_isolation_age_years=12_000,
        tasmania_late_contact_rate=0.0,
        founder_pair_joint_children=2,
    )
    result = simulate_historical_genealogy(
        scenario,
        seed=2,
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert np.all(
        result.any_founder_fraction_by_region[
            :,
            tasmania,
        ]
        == 0.0
    )


def test_late_contact_zero_rate_stays_zero():
    assert deterministic_late_contact_fraction(
        0.0,
        generations=9,
    ) == 0.0


def test_late_contact_probability_increases_with_rate():
    summary = simulate_late_contact_sensitivity(
        [
            0.001,
            0.005,
            0.01,
        ],
        generations=9,
        population_size=80,
        replicates=1_000,
        seed=4,
    )
    assert np.all(
        np.diff(
            summary.mean_final_fraction
        )
        > 0
    )
    assert np.all(
        np.diff(
            summary.fixation_probability
        )
        > 0
    )


def test_bottleneck_changes_only_requested_region_and_window():
    scenario = make_debate_historical_scenario(
        founder_age_years=500,
        region_sizes=(
            20,
            20,
            20,
            20,
            20,
            20,
        ),
    )
    changed = apply_region_bottleneck(
        scenario,
        "Tasmania",
        5,
        10,
        0.5,
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert np.all(
        changed.population_sizes[
            5:11,
            tasmania,
        ]
        == 10
    )
    assert (
        changed.population_sizes[
            4,
            tasmania,
        ]
        == 20
    )
    assert (
        changed.population_sizes[
            11,
            tasmania,
        ]
        == 20
    )



def test_structured_pedigree_genome_keeps_genetics_inside_genealogy():
    scenario = make_debate_historical_scenario(
        founder_age_years=100,
        region_sizes=(
            6,
            6,
            6,
            6,
            6,
            6,
        ),
        tasmania_isolation_age_years=12_000,
        tasmania_late_contact_rate=0.0,
        founder_pair_joint_children=2,
    )
    result = simulate_historical_pedigree_genome(
        scenario,
        max_generations=4,
        chromosome_lengths_morgans=[
            0.3,
            0.4,
        ],
        detectable_threshold_cm=5.0,
        seed=9,
    )
    assert np.all(
        result.genetic_carrier_fraction_by_region
        <= (
            result.any_founder_fraction_by_region
            + 1e-12
        )
    )


def test_structured_pedigree_genome_respects_hard_tasmania_barrier():
    scenario = make_debate_historical_scenario(
        founder_age_years=100,
        region_sizes=(
            6,
            6,
            6,
            6,
            6,
            6,
        ),
        tasmania_isolation_age_years=12_000,
        tasmania_late_contact_rate=0.0,
        founder_pair_joint_children=2,
    )
    result = simulate_historical_pedigree_genome(
        scenario,
        max_generations=4,
        chromosome_lengths_morgans=[
            0.3,
            0.4,
        ],
        seed=10,
    )
    tasmania = scenario.region_names.index(
        "Tasmania"
    )
    assert np.all(
        result.any_founder_fraction_by_region[
            :,
            tasmania,
        ]
        == 0.0
    )
    assert np.all(
        result.genetic_carrier_fraction_by_region[
            :,
            tasmania,
        ]
        == 0.0
    )
