"""Interactive continental founder-spread explorer.

This module is a synthesis layer over the earlier genealogy, migration, and
admixture models. It is designed for interactive sensitivity analysis rather
than historical reconstruction.

State variables:
- regional population size;
- pedigree-state fractions for neither founder / Adam only / Eve only / both;
- mean autosomal ancestry contributed by the founder pair.

Migration is represented as a parent-source matrix: row i gives the probability
that a parental draw for a child born in region i comes from source region j.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


DEFAULT_REGIONS = (
    "Middle East",
    "Africa",
    "Europe",
    "Asia",
    "Americas",
    "Oceania",
)

DEFAULT_COORDINATES = np.array(
    [
        [33.0, 44.0],
        [7.0, 20.0],
        [51.0, 15.0],
        [35.0, 100.0],
        [15.0, -90.0],
        [-20.0, 135.0],
    ],
    dtype=float,
)


@dataclass(frozen=True)
class ContinentalExplorerResult:
    generations: np.ndarray
    years_before_present: np.ndarray
    populations: np.ndarray
    pedigree_states: np.ndarray
    genetic_ancestry: np.ndarray
    parent_source_external_fraction: np.ndarray
    region_names: tuple[str, ...]
    founder_region: int
    founder_age_years: float
    generation_interval_years: float

    @property
    def any_founder_fraction(self) -> np.ndarray:
        return 1.0 - self.pedigree_states[:, :, 0]

    @property
    def both_founders_fraction(self) -> np.ndarray:
        return self.pedigree_states[:, :, 3]

    @property
    def descendant_counts(self) -> np.ndarray:
        return self.populations * self.both_founders_fraction

    @property
    def global_both_founders_fraction(self) -> np.ndarray:
        total = self.populations.sum(axis=1)
        return (
            self.descendant_counts.sum(axis=1)
            / total
        )

    @property
    def global_genetic_ancestry(self) -> np.ndarray:
        total = self.populations.sum(axis=1)
        return (
            (
                self.populations
                * self.genetic_ancestry
            ).sum(axis=1)
            / total
        )


def parent_source_matrix_from_offdiag(
    offdiag: Sequence[Sequence[float]],
) -> np.ndarray:
    """Build a row-stochastic parent-source matrix from off-diagonal rates."""
    arr = np.asarray(offdiag, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(
            "offdiag must be a square matrix"
        )
    if np.any(arr < 0.0):
        raise ValueError(
            "parent-source fractions must be non-negative"
        )
    arr = arr.copy()
    np.fill_diagonal(arr, 0.0)
    row_external = arr.sum(axis=1)
    if np.any(row_external >= 1.0):
        raise ValueError(
            "off-diagonal parent-source fractions must sum to < 1 in every row"
        )
    np.fill_diagonal(
        arr,
        1.0 - row_external,
    )
    return arr


def validate_parent_source_matrix(
    matrix: Sequence[Sequence[float]],
) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(
            "parent-source matrix must be square"
        )
    if np.any(arr < 0.0):
        raise ValueError(
            "parent-source matrix must be non-negative"
        )
    if not np.allclose(
        arr.sum(axis=1),
        1.0,
        atol=1e-10,
    ):
        raise ValueError(
            "each parent-source row must sum to 1"
        )
    return arr.copy()


def scale_external_parent_sources(
    matrix: Sequence[Sequence[float]],
    multiplier: float,
) -> np.ndarray:
    """Scale all off-diagonal parental sources while preserving row sums."""
    if multiplier < 0.0:
        raise ValueError(
            "multiplier must be non-negative"
        )
    base = validate_parent_source_matrix(
        matrix
    )
    out = np.zeros_like(
        base
    )
    for i in range(
        base.shape[0]
    ):
        external = base[
            i
        ].copy()
        external[
            i
        ] = 0.0
        external *= multiplier
        external_sum = float(
            external.sum()
        )
        if external_sum >= 1.0:
            raise ValueError(
                "scaled external parent-source fraction reaches or exceeds 1"
            )
        out[
            i
        ] = external
        out[
            i,
            i,
        ] = (
            1.0
            - external_sum
        )
    return out


def log_population_schedule(
    initial_population: Sequence[float],
    target_population: Sequence[float],
    generations: int,
) -> np.ndarray:
    """Smooth positive population path between initial and target sizes."""
    initial = np.asarray(
        initial_population,
        dtype=float,
    )
    target = np.asarray(
        target_population,
        dtype=float,
    )
    if (
        initial.ndim != 1
        or target.ndim != 1
        or initial.shape != target.shape
    ):
        raise ValueError(
            "initial and target populations must be same-length vectors"
        )
    if np.any(initial <= 0.0) or np.any(
        target <= 0.0
    ):
        raise ValueError(
            "population sizes must be positive"
        )
    if generations < 1:
        raise ValueError(
            "generations must be at least 1"
        )
    u = np.linspace(
        0.0,
        1.0,
        generations + 1,
    )[
        :,
        None,
    ]
    return np.exp(
        (
            1.0
            - u
        )
        * np.log(
            initial
        )[
            None,
            :
        ]
        + u
        * np.log(
            target
        )[
            None,
            :
        ]
    )


def _random_mating_or_distribution(
    states: np.ndarray,
) -> np.ndarray:
    """Child pedigree-state distribution from two random parental draws."""
    out = np.zeros(
        4,
        dtype=float,
    )
    for a in range(
        4
    ):
        for b in range(
            4
        ):
            out[
                a | b
            ] += (
                states[
                    a
                ]
                * states[
                    b
                ]
            )
    return out


def simulate_continental_explorer(
    initial_population: Sequence[float],
    target_population: Sequence[float],
    parent_source_matrix: Sequence[
        Sequence[
            float
        ]
    ],
    mixing_strength: Sequence[float],
    founder_age_years: float = 11_000.0,
    generation_interval_years: float = 28.0,
    founder_region: int = 0,
    founder_pair_joint_children: int = 2,
    late_contact_age_years: float = 500.0,
    late_contact_multiplier: float = 4.0,
    region_names: Sequence[str] = DEFAULT_REGIONS,
) -> ContinentalExplorerResult:
    """Run the deterministic macroregional founder-spread explorer.

    mixing_strength q lies in [0, 1]. q=1 applies full random mating to the
    pooled regional parental state. q=0 preserves the pooled state frequencies
    without descendant-status diffusion.

    The late-contact multiplier is a pedagogical sensitivity control. It is not
    an empirically estimated global migration multiplier.
    """
    if founder_age_years <= 0.0:
        raise ValueError(
            "founder_age_years must be positive"
        )
    if generation_interval_years <= 0.0:
        raise ValueError(
            "generation_interval_years must be positive"
        )
    if late_contact_age_years < 0.0:
        raise ValueError(
            "late_contact_age_years must be non-negative"
        )
    if founder_pair_joint_children < 0:
        raise ValueError(
            "founder_pair_joint_children must be non-negative"
        )

    matrix = validate_parent_source_matrix(
        parent_source_matrix
    )
    n_regions = matrix.shape[
        0
    ]
    names = tuple(
        region_names
    )
    if len(
        names
    ) != n_regions:
        raise ValueError(
            "region_names length must match matrix size"
        )
    if not (
        0
        <= founder_region
        < n_regions
    ):
        raise ValueError(
            "invalid founder_region"
        )

    mixing = np.asarray(
        mixing_strength,
        dtype=float,
    )
    if mixing.shape != (
        n_regions,
    ):
        raise ValueError(
            "mixing_strength must have one value per region"
        )
    if np.any(
        (
            mixing
            < 0.0
        )
        | (
            mixing
            > 1.0
        )
    ):
        raise ValueError(
            "mixing strengths must lie in [0, 1]"
        )

    generations = int(
        round(
            founder_age_years
            / generation_interval_years
        )
    )
    generations = max(
        1,
        generations,
    )
    population = log_population_schedule(
        initial_population,
        target_population,
        generations,
    )
    if population.shape[
        1
    ] != n_regions:
        raise ValueError(
            "population vectors must match region count"
        )

    late_matrix = (
        scale_external_parent_sources(
            matrix,
            late_contact_multiplier,
        )
    )

    years_before_present = np.linspace(
        founder_age_years,
        0.0,
        generations + 1,
    )
    pedigree = np.zeros(
        (
            generations
            + 1,
            n_regions,
            4,
        ),
        dtype=float,
    )
    pedigree[
        0,
        :,
        0,
    ] = 1.0

    founder_n = float(
        population[
            0,
            founder_region,
        ]
    )
    if founder_n < 2.0:
        raise ValueError(
            "founder region must contain at least two people"
        )
    founder_mass = min(
        1.0,
        1.0
        / founder_n,
    )
    pedigree[
        0,
        founder_region,
        0,
    ] = max(
        0.0,
        1.0
        - 2.0
        * founder_mass,
    )
    pedigree[
        0,
        founder_region,
        1,
    ] = founder_mass
    pedigree[
        0,
        founder_region,
        2,
    ] = founder_mass

    genetic = np.zeros(
        (
            generations
            + 1,
            n_regions,
        ),
        dtype=float,
    )
    genetic[
        0,
        founder_region,
    ] = min(
        1.0,
        2.0
        / founder_n,
    )

    external_fraction = np.zeros(
        (
            generations
            + 1,
            n_regions,
        ),
        dtype=float,
    )
    external_fraction[
        0
    ] = (
        1.0
        - np.diag(
            matrix
        )
    )

    for generation in range(
        1,
        generations
        + 1,
    ):
        years_ago = (
            years_before_present[
                generation
            ]
        )
        active_matrix = (
            late_matrix
            if years_ago
            <= late_contact_age_years
            else matrix
        )
        external_fraction[
            generation
        ] = (
            1.0
            - np.diag(
                active_matrix
            )
        )

        pooled_states = (
            active_matrix
            @ pedigree[
                generation
                - 1
            ]
        )
        pooled_genetic = (
            active_matrix
            @ genetic[
                generation
                - 1
            ]
        )

        for region in range(
            n_regions
        ):
            random_child = (
                _random_mating_or_distribution(
                    pooled_states[
                        region
                    ]
                )
            )
            q = float(
                mixing[
                    region
                ]
            )
            pedigree[
                generation,
                region,
            ] = (
                (
                    1.0
                    - q
                )
                * pooled_states[
                    region
                ]
                + q
                * random_child
            )
            pedigree[
                generation,
                region,
            ] /= pedigree[
                generation,
                region,
            ].sum()

        genetic[
            generation
        ] = pooled_genetic

        if (
            generation
            == 1
            and founder_pair_joint_children
            > 0
        ):
            seed = min(
                pedigree[
                    generation,
                    founder_region,
                    0,
                ],
                founder_pair_joint_children
                / population[
                    generation,
                    founder_region,
                ],
            )
            pedigree[
                generation,
                founder_region,
                0,
            ] -= seed
            pedigree[
                generation,
                founder_region,
                3,
            ] += seed
            genetic[
                generation,
                founder_region,
            ] = max(
                genetic[
                    generation,
                    founder_region,
                ],
                seed,
            )

    return ContinentalExplorerResult(
        generations=np.arange(
            generations
            + 1,
            dtype=int,
        ),
        years_before_present=(
            years_before_present
        ),
        populations=population,
        pedigree_states=pedigree,
        genetic_ancestry=genetic,
        parent_source_external_fraction=(
            external_fraction
        ),
        region_names=names,
        founder_region=int(
            founder_region
        ),
        founder_age_years=float(
            founder_age_years
        ),
        generation_interval_years=float(
            generation_interval_years
        ),
    )


def first_generation_reaching(
    result: ContinentalExplorerResult,
    threshold: float,
    region: int | None = None,
    metric: str = "both",
) -> int | None:
    """Return the first generation reaching a threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must lie in [0, 1]"
        )
    if metric == "both":
        values = (
            result.both_founders_fraction
        )
    elif metric == "any":
        values = (
            result.any_founder_fraction
        )
    elif metric == "genetic":
        values = (
            result.genetic_ancestry
        )
    else:
        raise ValueError(
            "metric must be both, any, or genetic"
        )

    if region is None:
        if metric == "genetic":
            series = (
                result.global_genetic_ancestry
            )
        else:
            weighted = (
                result.populations
                * values
            )
            series = (
                weighted.sum(
                    axis=1
                )
                / result.populations.sum(
                    axis=1
                )
            )
    else:
        series = values[
            :,
            region,
        ]

    hits = np.flatnonzero(
        series
        >= threshold
    )
    return (
        int(
            hits[
                0
            ]
        )
        if hits.size
        else None
    )
