import numpy as np
import pytest

from evolution_creation.continental_explorer import (
    DEFAULT_REGIONS,
    apply_hard_barriers,
    compare_scenarios,
    diagnose_scenario,
    first_generation_reaching,
    parent_source_matrix_from_offdiag,
    scale_external_parent_sources,
    simulate_continental_explorer,
    simulate_continental_stochastic,
)


def identity_matrix(n=7):
    return np.eye(n)


def test_offdiag_builder_scaler_and_barrier():
    off = np.zeros((3, 3))
    off[0, 1] = 0.01
    off[1, 0] = 0.02
    m = parent_source_matrix_from_offdiag(off)
    np.testing.assert_allclose(m.sum(axis=1), 1.0)
    assert m[0, 0] == pytest.approx(0.99)

    scaled = scale_external_parent_sources(m, 2.0)
    assert scaled[0, 1] == pytest.approx(0.02)
    assert scaled[0, 0] == pytest.approx(0.98)

    blocked = apply_hard_barriers(m, [(0, 1)])
    assert blocked[0, 1] == 0.0
    assert blocked[1, 0] == 0.0
    np.testing.assert_allclose(blocked.sum(axis=1), 1.0)


def test_no_migration_keeps_other_regions_unseeded():
    result = simulate_continental_explorer(
        initial_population=[100] * 7,
        target_population=[100] * 7,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 7,
        founder_age_years=280,
        generation_interval_years=28,
        founder_pair_joint_children=2,
        late_contact_multiplier=1.0,
    )
    assert np.all(result.any_founder_fraction[:, 1:] == 0.0)
    assert result.both_founders_fraction[-1, 0] > 0.0


def test_migration_spreads_founder_lineage():
    off = np.zeros((7, 7))
    off[1, 0] = 0.05
    m = parent_source_matrix_from_offdiag(off)
    result = simulate_continental_explorer(
        initial_population=[100] * 7,
        target_population=[100] * 7,
        parent_source_matrix=m,
        mixing_strength=[1.0] * 7,
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    assert result.any_founder_fraction[-1, 1] > 0.0


def test_random_mating_spreads_faster_than_no_mixing():
    kwargs = dict(
        initial_population=[100] * 7,
        target_population=[100] * 7,
        parent_source_matrix=identity_matrix(),
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    low = simulate_continental_explorer(
        mixing_strength=[0.0] * 7,
        **kwargs,
    )
    high = simulate_continental_explorer(
        mixing_strength=[1.0] * 7,
        **kwargs,
    )
    assert high.both_founders_fraction[-1, 0] > low.both_founders_fraction[-1, 0]


def test_genealogical_and_genetic_outputs_diverge():
    result = simulate_continental_explorer(
        initial_population=[100] * 7,
        target_population=[100] * 7,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 7,
        founder_age_years=840,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    assert result.any_founder_fraction[-1, 0] > result.genetic_ancestry[-1, 0]


def test_threshold_helper():
    result = simulate_continental_explorer(
        initial_population=[50] * 7,
        target_population=[50] * 7,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 7,
        founder_age_years=840,
        generation_interval_years=28,
        founder_pair_joint_children=8,
        late_contact_multiplier=1.0,
    )
    assert first_generation_reaching(result, 0.5, region=0, metric="any") is not None


def test_tasmania_hard_barrier_blocks_until_release():
    off = np.zeros((7, 7))
    off[5, 0] = 0.05
    off[6, 5] = 0.10
    off[5, 6] = 0.01
    m = parent_source_matrix_from_offdiag(off)

    closed = simulate_continental_explorer(
        initial_population=[100] * 7,
        target_population=[100] * 7,
        parent_source_matrix=m,
        mixing_strength=[1.0] * 7,
        founder_age_years=1120,
        generation_interval_years=28,
        founder_pair_joint_children=6,
        late_contact_multiplier=1.0,
        barrier_pairs=[(5, 6)],
        barrier_release_age_years=None,
    )
    assert np.all(closed.any_founder_fraction[:, 6] == 0.0)

    opened = simulate_continental_explorer(
        initial_population=[100] * 7,
        target_population=[100] * 7,
        parent_source_matrix=m,
        mixing_strength=[1.0] * 7,
        founder_age_years=1120,
        generation_interval_years=28,
        founder_pair_joint_children=6,
        late_contact_multiplier=1.0,
        barrier_pairs=[(5, 6)],
        barrier_release_age_years=280,
    )
    assert opened.any_founder_fraction[-1, 6] > 0.0


def test_stochastic_shapes_and_probabilities():
    result = simulate_continental_stochastic(
        initial_population=[80] * 7,
        target_population=[80] * 7,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 7,
        founder_age_years=280,
        generation_interval_years=28,
        founder_pair_joint_children=2,
        late_contact_multiplier=1.0,
        replicates=40,
        seed=4,
    )
    assert result.both_founders_fraction.shape == (40, 11, 7)
    assert result.any_founder_fraction.shape == (40, 11, 7)
    assert 0.0 <= result.any_founder_extinction_probability <= 1.0
    assert 0.0 <= result.probability_all_regions_above(0.5) <= 1.0


def test_stochastic_permanent_barrier_has_zero_tasmania_fixation():
    off = np.zeros((7, 7))
    off[5, 0] = 0.10
    off[6, 5] = 0.10
    m = parent_source_matrix_from_offdiag(off)
    result = simulate_continental_stochastic(
        initial_population=[50] * 7,
        target_population=[50] * 7,
        parent_source_matrix=m,
        mixing_strength=[1.0] * 7,
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
        barrier_pairs=[(5, 6)],
        barrier_release_age_years=None,
        replicates=30,
        seed=9,
    )
    assert np.all(result.both_founders_fraction[:, -1, 6] == 0.0)


def test_diagnosis_and_comparison():
    a = simulate_continental_explorer(
        initial_population=[60] * 7,
        target_population=[60] * 7,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 7,
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    off = np.zeros((7, 7))
    off[1:, 0] = 0.03
    b = simulate_continental_explorer(
        initial_population=[60] * 7,
        target_population=[60] * 7,
        parent_source_matrix=parent_source_matrix_from_offdiag(off),
        mixing_strength=[1.0] * 7,
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    diagnosis = diagnose_scenario(a)
    assert diagnosis.limiting_region in DEFAULT_REGIONS
    comparison = compare_scenarios(a, b)
    assert comparison["global_both_b"] >= comparison["global_both_a"]


def test_default_region_count_and_tasmania():
    assert len(DEFAULT_REGIONS) == 7
    assert DEFAULT_REGIONS[-1] == "Tasmania"
