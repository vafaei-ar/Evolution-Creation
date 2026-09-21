"""Model 12: domestication dates are not biological origin dates."""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class LivestockEvidence:
    name: str
    domestication_low_ka: float
    domestication_high_ka: float
    older_wild_evidence_ka: float
    wild_progenitor: str
    source_note: str


EVIDENCE = (
    LivestockEvidence(
        "sheep", 10.0, 11.0, 13.0, "wild sheep / mouflon-related populations",
        "13 ka wild sheep paleogenome; Southwest Asian domestication followed later",
    ),
    LivestockEvidence(
        "goat", 9.5, 10.5, 103.0, "bezoar (Capra aegagrus)",
        "domestic haplogroup divergences far predate ~10 ka domestication",
    ),
    LivestockEvidence(
        "taurine cattle", 9.5, 10.5, 650.0, "aurochs (Bos primigenius)",
        "aurochs lineage long predates Near Eastern cattle domestication",
    ),
    LivestockEvidence(
        "dromedary camel", 3.0, 4.5, 11.7, "wild dromedary populations",
        "wild dromedary lineage extends into the Pleistocene; domestication is much later",
    ),
)


def interval_overlap_fraction(
    low: float,
    high: float,
    window_low: float,
    window_high: float,
) -> float:
    if high < low or window_high < window_low:
        raise ValueError("invalid interval")
    length = high - low
    overlap = max(0.0, min(high, window_high) - max(low, window_low))
    if length == 0:
        return float(window_low <= low <= window_high)
    return float(overlap / length)


def probability_all_domestications_in_window(
    window_low_ka: float = 9.0,
    window_high_ka: float = 12.0,
) -> float:
    """Uniform-within-range consistency calculation, not a historical posterior."""
    p = 1.0
    for item in EVIDENCE:
        p *= interval_overlap_fraction(
            item.domestication_low_ka,
            item.domestication_high_ka,
            window_low_ka,
            window_high_ka,
        )
    return float(p)


def domestication_window_summary(
    window_low_ka: float = 9.0,
    window_high_ka: float = 12.0,
) -> dict[str, float]:
    return {
        item.name: interval_overlap_fraction(
            item.domestication_low_ka,
            item.domestication_high_ka,
            window_low_ka,
            window_high_ka,
        )
        for item in EVIDENCE
    }


def preexisting_lineage_gaps(origin_age_ka: float = 11.0) -> dict[str, float]:
    """Minimum amount by which evidence for the wild lineage predates origin age."""
    return {
        item.name: max(0.0, item.older_wild_evidence_ka - origin_age_ka)
        for item in EVIDENCE
    }


def count_preexisting_lineages(origin_age_ka: float = 11.0) -> int:
    return sum(item.older_wild_evidence_ka > origin_age_ka for item in EVIDENCE)


def sample_domestication_ages(
    samples: int = 10000,
    seed: int | None = None,
) -> dict[str, np.ndarray]:
    if samples < 1:
        raise ValueError("samples must be positive")
    rng = np.random.default_rng(seed)
    return {
        item.name: rng.uniform(
            item.domestication_low_ka,
            item.domestication_high_ka,
            size=samples,
        )
        for item in EVIDENCE
    }
