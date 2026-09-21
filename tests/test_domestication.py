import pytest

from evolution_creation.domestication import (
    EVIDENCE,
    count_preexisting_lineages,
    domestication_window_summary,
    interval_overlap_fraction,
    preexisting_lineage_gaps,
    probability_all_domestications_in_window,
)


def test_early_neolithic_window_contains_three_but_not_dromedary():
    s = domestication_window_summary(9.0, 12.0)
    assert s["sheep"] == pytest.approx(1.0)
    assert s["goat"] == pytest.approx(1.0)
    assert s["taurine cattle"] == pytest.approx(1.0)
    assert s["dromedary camel"] == pytest.approx(0.0)


def test_all_four_in_neolithic_window_is_zero_under_evidence_intervals():
    assert probability_all_domestications_in_window(9.0, 12.0) == 0.0


def test_all_four_have_wild_lineage_evidence_older_than_11ka():
    assert count_preexisting_lineages(11.0) == len(EVIDENCE)
    gaps = preexisting_lineage_gaps(11.0)
    assert all(value > 0 for value in gaps.values())


def test_dromedary_is_late():
    camel = [x for x in EVIDENCE if x.name == "dromedary camel"][0]
    assert camel.domestication_high_ka < 9.0


def test_overlap_math():
    assert interval_overlap_fraction(10, 12, 11, 13) == pytest.approx(0.5)
    assert interval_overlap_fraction(3, 4, 9, 12) == 0.0
