import numpy as np
import pytest

from evolution_creation.agency_bayes import (
    likelihood_ratio_from_classifier,
    normalize_hypotheses,
    posterior_from_prior_lr,
    posterior_surface,
    required_likelihood_ratio,
)


def test_lr_one_leaves_prior_unchanged():
    for p in [0.01, 0.2, 0.8]:
        assert posterior_from_prior_lr(p, 1.0) == pytest.approx(p)


def test_synthetic_classifier_example():
    lr = likelihood_ratio_from_classifier(0.95, 0.01)
    assert lr == pytest.approx(95.0)
    assert posterior_from_prior_lr(0.01, lr) == pytest.approx(
        0.4896907216494846
    )


def test_prior_matters_even_with_same_evidence():
    lr = 100.0
    assert posterior_from_prior_lr(0.001, lr) < posterior_from_prior_lr(0.1, lr)


def test_required_lr_round_trip():
    lr = required_likelihood_ratio(0.01, 0.95)
    assert posterior_from_prior_lr(0.01, lr) == pytest.approx(0.95)


def test_surface_shape():
    out = posterior_surface(np.array([0.01, 0.1]), np.array([1, 10, 100]))
    assert out.shape == (2, 3)


def test_multi_hypothesis_normalizes():
    p = normalize_hypotheses(np.array([0.3, 0.4, 0.3]), np.array([0.1, 0.2, 0.8]))
    assert p.sum() == pytest.approx(1.0)
    assert p[2] > p[0]


def test_invalid_input():
    with pytest.raises(ValueError):
        posterior_from_prior_lr(0.0, 10)
    with pytest.raises(ValueError):
        likelihood_ratio_from_classifier(1.2, 0.1)
