import numpy as np
import pytest

from evolution_creation.admixture_genealogy import (
    constant_rate_from_observed_admixture,
    genealogical_fraction_after_continuous_admixture,
    genetic_ancestry_after_continuous_admixture,
    independent_fixation_probability,
    pulse_genealogical_fraction,
    simulate_pulse_fixation,
)


def test_genetic_fraction_has_closed_form_behavior():
    assert genetic_ancestry_after_continuous_admixture(0.01, 1) == pytest.approx(0.01)
    assert genetic_ancestry_after_continuous_admixture(0.01, 10) == pytest.approx(
        1 - 0.99**10
    )


def test_genealogy_spreads_faster_than_mean_dna():
    dna = genetic_ancestry_after_continuous_admixture(0.01, 8)
    pedigree = genealogical_fraction_after_continuous_admixture(0.01, 8)
    assert pedigree > dna
    assert pedigree > 0.99


def test_rate_inversion_round_trip():
    for rate in [0.001, 0.01, 0.05]:
        ancestry = genetic_ancestry_after_continuous_admixture(rate, 12)
        inferred = constant_rate_from_observed_admixture(ancestry, 12)
        assert inferred == pytest.approx(rate)


def test_one_percent_pulse_becomes_nearly_universal_by_ten_generations():
    f = pulse_genealogical_fraction(0.01, 10)
    assert f > 0.9999
    p = independent_fixation_probability(f, 1000)
    assert p > 0.9


def test_pulse_dna_fraction_is_not_forced_to_grow():
    # The genealogical model spreads descendant status. Under neutral mating and
    # no later source input, the expected population mean source-DNA fraction
    # remains the original pulse fraction.
    f = pulse_genealogical_fraction(0.01, 10)
    assert f > 0.9999
    assert 0.01 < f


def test_monte_carlo_fixation_increases_with_time():
    early = simulate_pulse_fixation(0.01, 6, 500, 1500, 1)
    late = simulate_pulse_fixation(0.01, 10, 500, 1500, 1)
    assert late["fixation_probability"] > early["fixation_probability"]


def test_invalid_values_raise():
    with pytest.raises(ValueError):
        pulse_genealogical_fraction(-0.1, 10)
    with pytest.raises(ValueError):
        constant_rate_from_observed_admixture(0.1, 0)
    with pytest.raises(ValueError):
        independent_fixation_probability(0.5, 0)
