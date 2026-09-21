import numpy as np
import pytest

from evolution_creation.continental_explorer import (
    DEFAULT_REGIONS,
    first_generation_reaching,
    parent_source_matrix_from_offdiag,
    scale_external_parent_sources,
    simulate_continental_explorer,
)


def identity_matrix(n=6):
    return np.eye(n)


def test_offdiag_builder_and_scaler():
    off = np.zeros((3, 3))
    off[0, 1] = 0.01
    off[1, 0] = 0.02
    m = parent_source_matrix_from_offdiag(off)
    np.testing.assert_allclose(m.sum(axis=1), 1.0)
    assert m[0, 0] == pytest.approx(0.99)

    scaled = scale_external_parent_sources(m, 2.0)
    assert scaled[0, 1] == pytest.approx(0.02)
    assert scaled[0, 0] == pytest.approx(0.98)


def test_no_migration_keeps_other_regions_unseeded():
    result = simulate_continental_explorer(
        initial_population=[100] * 6,
        target_population=[100] * 6,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 6,
        founder_age_years=280,
        generation_interval_years=28,
        founder_pair_joint_children=2,
        late_contact_multiplier=1.0,
    )
    assert np.all(
        result.any_founder_fraction[:, 1:]
        == 0.0
    )
    assert result.both_founders_fraction[-1, 0] > 0.0


def test_migration_spreads_founder_lineage():
    off = np.zeros((6, 6))
    off[1, 0] = 0.05
    m = parent_source_matrix_from_offdiag(off)
    result = simulate_continental_explorer(
        initial_population=[100] * 6,
        target_population=[100] * 6,
        parent_source_matrix=m,
        mixing_strength=[1.0] * 6,
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    assert result.any_founder_fraction[-1, 1] > 0.0


def test_random_mating_spreads_faster_than_no_mixing():
    kwargs = dict(
        initial_population=[100] * 6,
        target_population=[100] * 6,
        parent_source_matrix=identity_matrix(),
        founder_age_years=560,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    low = simulate_continental_explorer(
        mixing_strength=[0.0] * 6,
        **kwargs,
    )
    high = simulate_continental_explorer(
        mixing_strength=[1.0] * 6,
        **kwargs,
    )
    assert (
        high.both_founders_fraction[-1, 0]
        > low.both_founders_fraction[-1, 0]
    )


def test_genealogical_and_genetic_outputs_diverge():
    result = simulate_continental_explorer(
        initial_population=[100] * 6,
        target_population=[100] * 6,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 6,
        founder_age_years=840,
        generation_interval_years=28,
        founder_pair_joint_children=4,
        late_contact_multiplier=1.0,
    )
    assert (
        result.any_founder_fraction[-1, 0]
        > result.genetic_ancestry[-1, 0]
    )


def test_threshold_helper():
    result = simulate_continental_explorer(
        initial_population=[50] * 6,
        target_population=[50] * 6,
        parent_source_matrix=identity_matrix(),
        mixing_strength=[1.0] * 6,
        founder_age_years=840,
        generation_interval_years=28,
        founder_pair_joint_children=8,
        late_contact_multiplier=1.0,
    )
    g = first_generation_reaching(
        result,
        0.5,
        region=0,
        metric="any",
    )
    assert g is not None


def test_default_region_count():
    assert len(DEFAULT_REGIONS) == 6
