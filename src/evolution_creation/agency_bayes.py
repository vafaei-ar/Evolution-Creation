"""Model 14: Bayesian structure of agency inference.

The module compares *forms of inference*, not the truth of a theological
hypothesis. Archaeological artifact classification can sometimes be calibrated
against experimental and natural controls. Cosmic fine-tuning hypotheses do not
come with an analogous experimental frequency table.
"""

from __future__ import annotations

import numpy as np


def posterior_from_prior_lr(prior: float, likelihood_ratio: float) -> float:
    """Bayesian posterior for a binary hypothesis from prior and Bayes factor."""
    if not 0.0 < prior < 1.0:
        raise ValueError("prior must lie strictly between 0 and 1")
    if likelihood_ratio < 0.0:
        raise ValueError("likelihood_ratio must be non-negative")
    prior_odds = prior / (1.0 - prior)
    posterior_odds = prior_odds * likelihood_ratio
    if np.isinf(posterior_odds):
        return 1.0
    return float(posterior_odds / (1.0 + posterior_odds))


def likelihood_ratio_from_classifier(
    true_positive_rate: float,
    false_positive_rate: float,
) -> float:
    """Likelihood ratio for observing a positive classifier result."""
    if not 0.0 <= true_positive_rate <= 1.0:
        raise ValueError("true_positive_rate must lie in [0, 1]")
    if not 0.0 <= false_positive_rate <= 1.0:
        raise ValueError("false_positive_rate must lie in [0, 1]")
    if false_positive_rate == 0.0:
        return float("inf") if true_positive_rate > 0.0 else 1.0
    return float(true_positive_rate / false_positive_rate)


def required_likelihood_ratio(prior: float, target_posterior: float) -> float:
    """Bayes factor required to move prior to a specified posterior."""
    if not 0.0 < prior < 1.0:
        raise ValueError("prior must lie strictly between 0 and 1")
    if not 0.0 < target_posterior < 1.0:
        raise ValueError("target_posterior must lie strictly between 0 and 1")
    prior_odds = prior / (1.0 - prior)
    target_odds = target_posterior / (1.0 - target_posterior)
    return float(target_odds / prior_odds)


def posterior_surface(
    priors: np.ndarray,
    likelihood_ratios: np.ndarray,
) -> np.ndarray:
    """Return posterior matrix with rows=priors and columns=likelihood ratios."""
    priors = np.asarray(priors, dtype=float)
    lrs = np.asarray(likelihood_ratios, dtype=float)
    if np.any((priors <= 0.0) | (priors >= 1.0)):
        raise ValueError("all priors must lie strictly between 0 and 1")
    if np.any(lrs < 0.0):
        raise ValueError("likelihood ratios must be non-negative")
    odds = priors[:, None] / (1.0 - priors[:, None])
    post_odds = odds * lrs[None, :]
    return post_odds / (1.0 + post_odds)


def normalize_hypotheses(
    priors: np.ndarray,
    evidence_likelihoods: np.ndarray,
) -> np.ndarray:
    """Bayesian update for multiple mutually exclusive hypotheses."""
    priors = np.asarray(priors, dtype=float)
    likes = np.asarray(evidence_likelihoods, dtype=float)
    if priors.ndim != 1 or likes.ndim != 1 or priors.shape != likes.shape:
        raise ValueError("priors and likelihoods must be same-length vectors")
    if np.any(priors < 0.0) or np.any(likes < 0.0) or priors.sum() <= 0.0:
        raise ValueError("priors/likelihoods must be non-negative with positive prior sum")
    weighted = (priors / priors.sum()) * likes
    if weighted.sum() == 0.0:
        raise ValueError("evidence has zero likelihood under all hypotheses")
    return weighted / weighted.sum()
