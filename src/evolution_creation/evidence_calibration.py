"""Evidence-calibrated uncertainty envelopes for Model 10.

Model 10 deliberately distinguishes direct quantitative evidence from modeler-
chosen uncertainty envelopes. It does not convert an unsupported historical
mixing rate into an empirical prior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


BYARD_POPULATION_MODEL_SET = np.array(
    [
        3848,
        4232,
        4616,
        6789,
        7465,
        8144,
        10093,
        11099,
        12106,
    ],
    dtype=int,
)


@dataclass(frozen=True)
class EvidenceEnvelopeResult:
    generation_interval_years: np.ndarray
    isolation_age_years_bp: np.ndarray
    population_size: np.ndarray
    founder_generations: np.ndarray
    late_contact_generations: np.ndarray
    preclosure_generations: np.ndarray
    required_rate_50: np.ndarray
    required_rate_95: np.ndarray
    samples: int
    founder_age_years: float
    contact_start_year: int
    present_year: int
    seed: int | None


@dataclass(frozen=True)
class FixationSimulationResult:
    bridge_rates: np.ndarray
    fixation_probability: np.ndarray
    mean_final_fraction: np.ndarray
    q05_final_fraction: np.ndarray
    median_final_fraction: np.ndarray
    q95_final_fraction: np.ndarray
    generations: int
    population_size: int
    replicates: int
    seed: int | None


def founder_generations(
    founder_age_years: float = 11_000.0,
    generation_interval_years: float = 28.0,
) -> int:
    if founder_age_years < 0:
        raise ValueError(
            "founder_age_years must be non-negative"
        )
    if generation_interval_years <= 0:
        raise ValueError(
            "generation_interval_years must be positive"
        )
    return int(
        round(
            founder_age_years
            / generation_interval_years
        )
    )


def contact_generations(
    contact_start_year: int,
    present_year: int = 2026,
    generation_interval_years: float = 28.0,
) -> int:
    if present_year < contact_start_year:
        raise ValueError(
            "present_year must not precede contact_start_year"
        )
    if generation_interval_years <= 0:
        raise ValueError(
            "generation_interval_years must be positive"
        )
    elapsed = (
        present_year
        - contact_start_year
    )
    return int(
        round(
            elapsed
            / generation_interval_years
        )
    )


def preclosure_generations(
    founder_age_years: float,
    isolation_age_years_bp: float,
    generation_interval_years: float,
) -> int:
    """Generations between founder insertion and geographic closure.

    Ages are years before present. A positive result exists only if the
    isolation event is younger than the founder insertion date.
    """
    if (
        founder_age_years < 0
        or isolation_age_years_bp < 0
    ):
        raise ValueError(
            "ages must be non-negative"
        )
    if generation_interval_years <= 0:
        raise ValueError(
            "generation_interval_years must be positive"
        )
    window_years = max(
        0.0,
        founder_age_years
        - isolation_age_years_bp,
    )
    return int(
        round(
            window_years
            / generation_interval_years
        )
    )


def descendant_fraction_best_case(
    external_parent_rate: float,
    generations: int,
    initial_fraction: float = 0.0,
) -> float:
    """Deterministic best-case descendant fraction after barrier reopening.

    Every external parent is assumed already descended from all focal founders.
    Each parental draw is external with probability external_parent_rate.
    """
    if not (
        0.0
        <= external_parent_rate
        <= 1.0
    ):
        raise ValueError(
            "external_parent_rate must lie between 0 and 1"
        )
    if generations < 0:
        raise ValueError(
            "generations must be non-negative"
        )
    if not (
        0.0
        <= initial_fraction
        <= 1.0
    ):
        raise ValueError(
            "initial_fraction must lie between 0 and 1"
        )

    f = float(
        initial_fraction
    )
    for _ in range(
        generations
    ):
        f = (
            1.0
            - (
                (
                    1.0
                    - external_parent_rate
                )
                * (
                    1.0
                    - f
                )
            )
            ** 2
        )
    return float(
        f
    )


def independent_fixation_approximation(
    external_parent_rate: float,
    generations: int,
    population_size: int,
    initial_fraction: float = 0.0,
) -> float:
    """Approximate P(all individuals are descendants at the final generation).

    This treats final descendant indicators as independent Bernoulli draws from
    the deterministic descendant fraction. Shared pedigree makes this only an
    approximation, so Monte Carlo should be used when a numerical probability is
    important.
    """
    if population_size < 1:
        raise ValueError(
            "population_size must be positive"
        )
    f = descendant_fraction_best_case(
        external_parent_rate,
        generations,
        initial_fraction,
    )
    if f <= 0.0:
        return 0.0
    if f >= 1.0:
        return 1.0
    return float(
        np.exp(
            population_size
            * np.log(
                f
            )
        )
    )


def required_external_parent_rate(
    target_fixation_probability: float,
    generations: int,
    population_size: int,
) -> float:
    """Solve the independence approximation for the required external rate.

    The initial isolated-deme founder fraction is zero. The result is a threshold
    under the stated approximation, not an empirical estimate of historical
    intermarriage.
    """
    if not (
        0.0
        < target_fixation_probability
        < 1.0
    ):
        raise ValueError(
            "target_fixation_probability must lie strictly between 0 and 1"
        )
    if generations < 1:
        raise ValueError(
            "generations must be at least 1"
        )
    if population_size < 1:
        raise ValueError(
            "population_size must be positive"
        )

    final_fraction = (
        target_fixation_probability
        ** (
            1.0
            / population_size
        )
    )
    remaining_fraction = max(
        0.0,
        1.0
        - final_fraction,
    )
    exponent = (
        2
        * (
            2
            ** generations
            - 1
        )
    )
    if remaining_fraction <= 0.0:
        return 1.0
    return float(
        1.0
        - remaining_fraction
        ** (
            1.0
            / exponent
        )
    )


def simulate_fixation_rates(
    bridge_rates: Sequence[float],
    generations: int,
    population_size: int,
    replicates: int = 5_000,
    seed: int | None = None,
) -> FixationSimulationResult:
    """Finite-population Monte Carlo for a reopened barrier.

    The external population is assumed already descended from all founders.
    """
    rates = np.asarray(
        bridge_rates,
        dtype=float,
    )
    if (
        rates.ndim != 1
        or rates.size == 0
    ):
        raise ValueError(
            "bridge_rates must be a non-empty one-dimensional sequence"
        )
    if np.any(
        (
            rates < 0.0
        )
        | (
            rates > 1.0
        )
    ):
        raise ValueError(
            "bridge rates must lie between 0 and 1"
        )
    if generations < 0:
        raise ValueError(
            "generations must be non-negative"
        )
    if population_size < 2:
        raise ValueError(
            "population_size must be at least 2"
        )
    if replicates < 1:
        raise ValueError(
            "replicates must be positive"
        )

    rng = np.random.default_rng(
        seed
    )
    fixation = np.empty(
        rates.size,
        dtype=float,
    )
    mean = np.empty(
        rates.size,
        dtype=float,
    )
    q05 = np.empty(
        rates.size,
        dtype=float,
    )
    median = np.empty(
        rates.size,
        dtype=float,
    )
    q95 = np.empty(
        rates.size,
        dtype=float,
    )

    for i, rate in enumerate(
        rates
    ):
        counts = np.zeros(
            replicates,
            dtype=int,
        )
        for _ in range(
            generations
        ):
            f = (
                counts
                / population_size
            )
            p = (
                1.0
                - (
                    (
                        1.0
                        - rate
                    )
                    * (
                        1.0
                        - f
                    )
                )
                ** 2
            )
            counts = rng.binomial(
                population_size,
                p,
            )
        final = (
            counts
            / population_size
        )
        fixation[
            i
        ] = float(
            np.mean(
                counts
                == population_size
            )
        )
        mean[
            i
        ] = float(
            np.mean(
                final
            )
        )
        (
            q05[
                i
            ],
            median[
                i
            ],
            q95[
                i
            ],
        ) = np.quantile(
            final,
            [
                0.05,
                0.5,
                0.95,
            ],
        )

    return FixationSimulationResult(
        bridge_rates=rates,
        fixation_probability=(
            fixation
        ),
        mean_final_fraction=(
            mean
        ),
        q05_final_fraction=(
            q05
        ),
        median_final_fraction=(
            median
        ),
        q95_final_fraction=(
            q95
        ),
        generations=int(
            generations
        ),
        population_size=int(
            population_size
        ),
        replicates=int(
            replicates
        ),
        seed=seed,
    )


def simulate_bottleneck_fixation_probability(
    external_parent_rate: float,
    population_sizes: Sequence[int],
    replicates: int = 5_000,
    seed: int | None = None,
) -> float:
    """Fixation probability for a changing-size contact-era population.

    population_sizes contains generation 0 followed by the size of each child
    generation. Descendant counts in each child generation are sampled from the
    stated size. The bottleneck is therefore demographic only and is not assumed
    to be ancestry-neutral in real history; this is a sensitivity model.
    """
    sizes = np.asarray(
        population_sizes,
        dtype=int,
    )
    if (
        sizes.ndim != 1
        or sizes.size < 2
        or np.any(
            sizes < 2
        )
    ):
        raise ValueError(
            "population_sizes must contain at least two values >= 2"
        )
    if not (
        0.0
        <= external_parent_rate
        <= 1.0
    ):
        raise ValueError(
            "external_parent_rate must lie between 0 and 1"
        )
    if replicates < 1:
        raise ValueError(
            "replicates must be positive"
        )

    rng = np.random.default_rng(
        seed
    )
    counts = np.zeros(
        replicates,
        dtype=int,
    )
    current_size = int(
        sizes[
            0
        ]
    )

    for next_size_value in sizes[
        1:
    ]:
        next_size = int(
            next_size_value
        )
        f = (
            counts
            / current_size
        )
        p = (
            1.0
            - (
                (
                    1.0
                    - external_parent_rate
                )
                * (
                    1.0
                    - f
                )
            )
            ** 2
        )
        counts = rng.binomial(
            next_size,
            p,
        )
        current_size = (
            next_size
        )

    return float(
        np.mean(
            counts
            == current_size
        )
    )


def sample_evidence_envelope(
    samples: int = 10_000,
    founder_age_years: float = 11_000.0,
    generation_interval_low: float = 26.0,
    generation_interval_high: float = 30.0,
    isolation_age_low: float = 11_960.0,
    isolation_age_high: float = 12_890.0,
    contact_start_year: int = 1797,
    present_year: int = 2026,
    population_model_set: Sequence[int] = BYARD_POPULATION_MODEL_SET,
    seed: int | None = None,
) -> EvidenceEnvelopeResult:
    """Sample an illustrative uncertainty envelope over supported ranges.

    Uniform sampling inside published numerical intervals and equal weighting of
    published population-model outputs are modeling conventions for propagation,
    not posterior distributions supplied by the cited studies.
    """
    if samples < 1:
        raise ValueError(
            "samples must be positive"
        )
    if not (
        0
        < generation_interval_low
        <= generation_interval_high
    ):
        raise ValueError(
            "invalid generation-interval bounds"
        )
    if not (
        0
        <= isolation_age_low
        <= isolation_age_high
    ):
        raise ValueError(
            "invalid isolation-age bounds"
        )
    if present_year < contact_start_year:
        raise ValueError(
            "present_year must not precede contact_start_year"
        )

    populations = np.asarray(
        population_model_set,
        dtype=int,
    )
    if (
        populations.ndim != 1
        or populations.size == 0
        or np.any(
            populations < 1
        )
    ):
        raise ValueError(
            "population_model_set must contain positive sizes"
        )

    rng = np.random.default_rng(
        seed
    )
    generation_intervals = (
        rng.uniform(
            generation_interval_low,
            generation_interval_high,
            size=samples,
        )
    )
    isolation_ages = (
        rng.uniform(
            isolation_age_low,
            isolation_age_high,
            size=samples,
        )
    )
    population_sizes = (
        rng.choice(
            populations,
            size=samples,
            replace=True,
        )
    )

    founder_g = np.rint(
        founder_age_years
        / generation_intervals
    ).astype(
        int
    )
    contact_g = np.rint(
        (
            present_year
            - contact_start_year
        )
        / generation_intervals
    ).astype(
        int
    )
    preclosure_g = np.rint(
        np.maximum(
            0.0,
            founder_age_years
            - isolation_ages,
        )
        / generation_intervals
    ).astype(
        int
    )

    required_50 = np.array(
        [
            required_external_parent_rate(
                0.50,
                int(
                    g
                ),
                int(
                    n
                ),
            )
            for g, n
            in zip(
                contact_g,
                population_sizes,
            )
        ],
        dtype=float,
    )
    required_95 = np.array(
        [
            required_external_parent_rate(
                0.95,
                int(
                    g
                ),
                int(
                    n
                ),
            )
            for g, n
            in zip(
                contact_g,
                population_sizes,
            )
        ],
        dtype=float,
    )

    return EvidenceEnvelopeResult(
        generation_interval_years=(
            generation_intervals
        ),
        isolation_age_years_bp=(
            isolation_ages
        ),
        population_size=(
            population_sizes
        ),
        founder_generations=(
            founder_g
        ),
        late_contact_generations=(
            contact_g
        ),
        preclosure_generations=(
            preclosure_g
        ),
        required_rate_50=(
            required_50
        ),
        required_rate_95=(
            required_95
        ),
        samples=int(
            samples
        ),
        founder_age_years=float(
            founder_age_years
        ),
        contact_start_year=int(
            contact_start_year
        ),
        present_year=int(
            present_year
        ),
        seed=seed,
    )
