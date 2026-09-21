"""Historically constrained founder-spread scenarios.

This module focuses on constraints rather than pretending that a small model is
an empirically calibrated reconstruction of global Holocene demography.

A scenario contains a time-varying parent-source matrix. Rows are child regions
and columns are parent-source regions. Positive entries create reproductive
paths; zero entries create hard barriers. A founder pair is introduced in one
region and its genealogy can then be propagated stochastically across the
network.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class HistoricalScenario:
    region_names: tuple[str, ...]
    population_sizes: np.ndarray
    parent_source_matrices: np.ndarray
    founder_region: int
    founder_count: int
    founder_age_years: float
    years_per_generation: float
    tasmania_isolation_age_years: float
    tasmania_contact_year: int
    present_year: int
    founder_pair_joint_children: int
    metadata: dict[str, float | int | str]

    @property
    def generations(self) -> int:
        return int(self.population_sizes.shape[0] - 1)


@dataclass(frozen=True)
class HistoricalGenealogyResult:
    generations: np.ndarray
    founder_descendant_fraction_by_region: np.ndarray
    any_founder_fraction_by_region: np.ndarray
    all_founders_fraction_by_region: np.ndarray
    global_all_founders_fraction: np.ndarray
    global_universal_generation: int | None
    founder_extinction_generations: np.ndarray
    scenario: HistoricalScenario
    seed: int | None


@dataclass(frozen=True)
class LateContactSummary:
    bridge_rates: np.ndarray
    mean_final_fraction: np.ndarray
    fixation_probability: np.ndarray
    q05_final_fraction: np.ndarray
    median_final_fraction: np.ndarray
    q95_final_fraction: np.ndarray
    generations: int
    population_size: int
    replicates: int
    seed: int | None


@dataclass(frozen=True)
class DeterministicHistoricalResult:
    generations: np.ndarray
    mask_fractions_by_region: np.ndarray
    any_founder_fraction_by_region: np.ndarray
    all_founders_fraction_by_region: np.ndarray
    global_all_founders_fraction: np.ndarray
    scenario: HistoricalScenario


def years_to_generations(
    years: float,
    years_per_generation: float = 25.0,
) -> int:
    if years < 0:
        raise ValueError("years must be non-negative")
    if years_per_generation <= 0:
        raise ValueError(
            "years_per_generation must be positive"
        )
    return int(
        round(
            years
            / years_per_generation
        )
    )


def _matrix_from_bridge_rates(
    region_count: int,
    directed_rates: dict[
        tuple[int, int],
        float,
    ],
) -> np.ndarray:
    """Build a parent-source matrix from off-diagonal parental-source rates."""
    matrix = np.zeros(
        (
            region_count,
            region_count,
        ),
        dtype=float,
    )
    for child in range(
        region_count
    ):
        total = 0.0
        for (
            dest,
            source,
        ), rate in directed_rates.items():
            if dest != child:
                continue
            if source == child:
                raise ValueError(
                    "bridge rates must be off-diagonal"
                )
            if rate < 0:
                raise ValueError(
                    "bridge rates must be non-negative"
                )
            matrix[
                child,
                source,
            ] += rate
            total += rate
        if total > 1.0:
            raise ValueError(
                "off-diagonal bridge rates exceed 1 for a row"
            )
        matrix[
            child,
            child,
        ] = 1.0 - total
    return matrix


def make_debate_historical_scenario(
    founder_age_years: float = 11_000.0,
    years_per_generation: float = 25.0,
    founder_count: int = 2,
    founder_region: str = "West Asia",
    region_sizes: Sequence[int] = (
        50,
        60,
        70,
        55,
        30,
        60,
    ),
    ordinary_bridge_rate: float = 0.003,
    sahul_bridge_rate: float = 0.001,
    americas_bridge_rate: float = 0.0005,
    tasmania_pre_isolation_rate: float = 0.003,
    tasmania_isolation_age_years: float = 12_000.0,
    tasmania_contact_year: int = 1803,
    tasmania_late_contact_rate: float = 0.01,
    endogamy_strength: float = 0.0,
    present_year: int = 2026,
    founder_pair_joint_children: int = 2,
) -> HistoricalScenario:
    """Create a stylized scenario tied to the debate's chronology.

    The non-Tasmanian bridge rates are sensitivity parameters, not empirical
    migration estimates. Tasmania is treated specially because its long period
    of geographic isolation is a concrete historical constraint.
    """
    names = (
        "West Asia",
        "Africa",
        "South/East Asia",
        "Sahul",
        "Tasmania",
        "Americas",
    )
    if founder_region not in names:
        raise ValueError(
            f"founder_region must be one of {names}"
        )

    sizes = np.asarray(
        region_sizes,
        dtype=int,
    )
    if (
        sizes.shape
        != (
            len(
                names
            ),
        )
        or np.any(
            sizes < 2
        )
    ):
        raise ValueError(
            "region_sizes must contain six values >= 2"
        )

    source_index = names.index(
        founder_region
    )
    if (
        founder_count < 1
        or founder_count
        > sizes[
            source_index
        ]
    ):
        raise ValueError(
            "invalid founder_count"
        )
    if founder_pair_joint_children < 0:
        raise ValueError(
            "founder_pair_joint_children must be non-negative"
        )
    if (
        founder_pair_joint_children
        and founder_count != 2
    ):
        raise ValueError(
            "joint founder children currently require founder_count=2"
        )
    if not (
        0.0
        <= endogamy_strength
        <= 1.0
    ):
        raise ValueError(
            "endogamy_strength must lie between 0 and 1"
        )

    total_generations = (
        years_to_generations(
            founder_age_years,
            years_per_generation,
        )
    )
    size_schedule = np.tile(
        sizes,
        (
            total_generations
            + 1,
            1,
        ),
    )

    scale = (
        1.0
        - endogamy_strength
    )
    ordinary = (
        ordinary_bridge_rate
        * scale
    )
    sahul = (
        sahul_bridge_rate
        * scale
    )
    americas = (
        americas_bridge_rate
        * scale
    )
    tas_pre = (
        tasmania_pre_isolation_rate
        * scale
    )
    tas_late = (
        tasmania_late_contact_rate
        * scale
    )

    (
        west,
        africa,
        asia,
        sahul_i,
        tas,
        amer,
    ) = range(
        6
    )
    base_rates = {
        (
            west,
            africa,
        ): ordinary,
        (
            africa,
            west,
        ): ordinary,
        (
            west,
            asia,
        ): ordinary,
        (
            asia,
            west,
        ): ordinary,
        (
            asia,
            sahul_i,
        ): sahul,
        (
            sahul_i,
            asia,
        ): sahul,
        (
            asia,
            amer,
        ): americas,
        (
            amer,
            asia,
        ): americas,
    }

    matrices = np.empty(
        (
            total_generations,
            6,
            6,
        ),
        dtype=float,
    )

    years_until_isolation = max(
        0.0,
        founder_age_years
        - tasmania_isolation_age_years,
    )
    isolation_generation = (
        years_to_generations(
            years_until_isolation,
            years_per_generation,
        )
    )

    contact_years = max(
        0,
        present_year
        - tasmania_contact_year,
    )
    late_contact_generations = max(
        0,
        int(
            np.ceil(
                contact_years
                / years_per_generation
            )
        ),
    )
    late_contact_start = max(
        1,
        total_generations
        - late_contact_generations
        + 1,
    )

    for resulting_generation in range(
        1,
        total_generations + 1,
    ):
        rates = dict(
            base_rates
        )

        before_geographic_closure = (
            resulting_generation
            <= isolation_generation
            and isolation_generation
            > 0
        )
        after_late_contact = (
            resulting_generation
            >= late_contact_start
        )

        if before_geographic_closure:
            rates[
                (
                    tas,
                    sahul_i,
                )
            ] = tas_pre
            rates[
                (
                    sahul_i,
                    tas,
                )
            ] = tas_pre
        elif after_late_contact:
            external = (
                sizes.astype(
                    float
                ).copy()
            )
            external[
                tas
            ] = 0.0
            external /= (
                external.sum()
            )
            for source in range(
                6
            ):
                if source != tas:
                    rates[
                        (
                            tas,
                            source,
                        )
                    ] = (
                        tas_late
                        * external[
                            source
                        ]
                    )

        matrices[
            resulting_generation
            - 1
        ] = (
            _matrix_from_bridge_rates(
                6,
                rates,
            )
        )

    return HistoricalScenario(
        region_names=names,
        population_sizes=(
            size_schedule
        ),
        parent_source_matrices=(
            matrices
        ),
        founder_region=(
            source_index
        ),
        founder_count=(
            founder_count
        ),
        founder_age_years=float(
            founder_age_years
        ),
        years_per_generation=float(
            years_per_generation
        ),
        tasmania_isolation_age_years=float(
            tasmania_isolation_age_years
        ),
        tasmania_contact_year=int(
            tasmania_contact_year
        ),
        present_year=int(
            present_year
        ),
        founder_pair_joint_children=int(
            founder_pair_joint_children
        ),
        metadata={
            "ordinary_bridge_rate": float(
                ordinary_bridge_rate
            ),
            "sahul_bridge_rate": float(
                sahul_bridge_rate
            ),
            "americas_bridge_rate": float(
                americas_bridge_rate
            ),
            "tasmania_pre_isolation_rate": float(
                tasmania_pre_isolation_rate
            ),
            "tasmania_late_contact_rate": float(
                tasmania_late_contact_rate
            ),
            "endogamy_strength": float(
                endogamy_strength
            ),
            "isolation_generation": int(
                isolation_generation
            ),
            "late_contact_generations": int(
                late_contact_generations
            ),
            "late_contact_start_generation": int(
                late_contact_start
            ),
        },
    )


def apply_region_bottleneck(
    scenario: HistoricalScenario,
    region: str,
    start_generation: int,
    end_generation: int,
    size_multiplier: float,
) -> HistoricalScenario:
    """Return a scenario with a temporary region-specific population-size shock."""
    if region not in scenario.region_names:
        raise ValueError(
            "unknown region"
        )
    if not (
        0
        <= start_generation
        <= end_generation
        <= scenario.generations
    ):
        raise ValueError(
            "invalid bottleneck generation range"
        )
    if size_multiplier <= 0:
        raise ValueError(
            "size_multiplier must be positive"
        )

    schedule = (
        scenario.population_sizes.copy()
    )
    region_index = (
        scenario.region_names.index(
            region
        )
    )
    original = schedule[
        start_generation:
        end_generation + 1,
        region_index,
    ]
    schedule[
        start_generation:
        end_generation + 1,
        region_index,
    ] = np.maximum(
        2,
        np.rint(
            original
            * size_multiplier
        ).astype(
            int
        ),
    )

    metadata = dict(
        scenario.metadata
    )
    metadata[
        "bottleneck_region"
    ] = region
    metadata[
        "bottleneck_start_generation"
    ] = int(
        start_generation
    )
    metadata[
        "bottleneck_end_generation"
    ] = int(
        end_generation
    )
    metadata[
        "bottleneck_size_multiplier"
    ] = float(
        size_multiplier
    )

    return replace(
        scenario,
        population_sizes=(
            schedule
        ),
        metadata=metadata,
    )


def earliest_reachable_generations(
    scenario: HistoricalScenario,
) -> np.ndarray:
    """Earliest generation each region is reachable by a positive pedigree path."""
    region_count = len(
        scenario.region_names
    )
    earliest = np.full(
        region_count,
        np.inf,
        dtype=float,
    )
    reachable = np.zeros(
        region_count,
        dtype=bool,
    )
    reachable[
        scenario.founder_region
    ] = True
    earliest[
        scenario.founder_region
    ] = 0.0

    for (
        generation,
        matrix,
    ) in enumerate(
        scenario.parent_source_matrices,
        start=1,
    ):
        next_reachable = (
            reachable.copy()
        )
        for child_region in range(
            region_count
        ):
            if next_reachable[
                child_region
            ]:
                continue
            sources = np.flatnonzero(
                matrix[
                    child_region
                ]
                > 0.0
            )
            if np.any(
                reachable[
                    sources
                ]
            ):
                next_reachable[
                    child_region
                ] = True
                earliest[
                    child_region
                ] = float(
                    generation
                )
        reachable = (
            next_reachable
        )

    return earliest


def simulate_historical_genealogy(
    scenario: HistoricalScenario,
    seed: int | None = None,
    distinct_parents: bool = True,
) -> HistoricalGenealogyResult:
    """Propagate founder-specific genealogy through a time-varying region network."""
    rng = np.random.default_rng(
        seed
    )
    region_count = len(
        scenario.region_names
    )
    founder_count = (
        scenario.founder_count
    )
    full_mask = (
        (1 << founder_count)
        - 1
    )

    current_masks: list[
        np.ndarray
    ] = []

    for region_index in range(
        region_count
    ):
        n = int(
            scenario.population_sizes[
                0,
                region_index,
            ]
        )
        masks = np.zeros(
            n,
            dtype=object,
        )
        if (
            region_index
            == scenario.founder_region
        ):
            for founder in range(
                founder_count
            ):
                masks[
                    founder
                ] = (
                    1 << founder
                )
        current_masks.append(
            masks
        )

    generations = np.arange(
        scenario.generations
        + 1,
        dtype=int,
    )
    per_founder = np.zeros(
        (
            scenario.generations
            + 1,
            region_count,
            founder_count,
        ),
        dtype=float,
    )
    any_fraction = np.zeros(
        (
            scenario.generations
            + 1,
            region_count,
        ),
        dtype=float,
    )
    all_fraction = np.zeros(
        (
            scenario.generations
            + 1,
            region_count,
        ),
        dtype=float,
    )
    global_all = np.zeros(
        scenario.generations
        + 1,
        dtype=float,
    )
    extinction = np.full(
        founder_count,
        np.nan,
        dtype=float,
    )
    global_universal: (
        int | None
    ) = None

    def record(
        generation: int,
    ) -> None:
        total_all = 0
        total_population = 0
        global_founder_counts = np.zeros(
            founder_count,
            dtype=int,
        )

        for (
            region_index,
            masks,
        ) in enumerate(
            current_masks
        ):
            n = len(
                masks
            )
            total_population += n
            any_fraction[
                generation,
                region_index,
            ] = float(
                np.mean(
                    masks != 0
                )
            )

            all_here = (
                masks
                == full_mask
            )
            all_fraction[
                generation,
                region_index,
            ] = float(
                np.mean(
                    all_here
                )
            )
            total_all += int(
                np.sum(
                    all_here
                )
            )

            for founder in range(
                founder_count
            ):
                has_founder = np.array(
                    [
                        bool(
                            int(mask)
                            & (
                                1
                                << founder
                            )
                        )
                        for mask in masks
                    ],
                    dtype=bool,
                )
                per_founder[
                    generation,
                    region_index,
                    founder,
                ] = float(
                    np.mean(
                        has_founder
                    )
                )
                global_founder_counts[
                    founder
                ] += int(
                    np.sum(
                        has_founder
                    )
                )

        global_all[
            generation
        ] = (
            total_all
            / total_population
        )

        for founder in range(
            founder_count
        ):
            if (
                generation > 0
                and np.isnan(
                    extinction[
                        founder
                    ]
                )
                and global_founder_counts[
                    founder
                ]
                == 0
            ):
                extinction[
                    founder
                ] = float(
                    generation
                )

    record(
        0
    )

    for generation in range(
        1,
        scenario.generations
        + 1,
    ):
        matrix = (
            scenario.parent_source_matrices[
                generation
                - 1
            ]
        )
        next_masks: list[
            np.ndarray
        ] = []
        previous_sizes = (
            scenario.population_sizes[
                generation
                - 1
            ]
        )
        next_sizes = (
            scenario.population_sizes[
                generation
            ]
        )

        for child_region in range(
            region_count
        ):
            child_count = int(
                next_sizes[
                    child_region
                ]
            )
            source_a = rng.choice(
                region_count,
                size=child_count,
                p=matrix[
                    child_region
                ],
            )
            source_b = rng.choice(
                region_count,
                size=child_count,
                p=matrix[
                    child_region
                ],
            )
            children = np.zeros(
                child_count,
                dtype=object,
            )

            for child in range(
                child_count
            ):
                force_joint_founders = (
                    generation == 1
                    and founder_count == 2
                    and child_region
                    == scenario.founder_region
                    and child
                    < scenario.founder_pair_joint_children
                )

                if force_joint_founders:
                    sa = (
                        scenario.founder_region
                    )
                    sb = (
                        scenario.founder_region
                    )
                    ia = 0
                    ib = 1
                else:
                    sa = int(
                        source_a[
                            child
                        ]
                    )
                    sb = int(
                        source_b[
                            child
                        ]
                    )
                    ia = int(
                        rng.integers(
                            0,
                            int(
                                previous_sizes[
                                    sa
                                ]
                            ),
                        )
                    )
                    ib = int(
                        rng.integers(
                            0,
                            int(
                                previous_sizes[
                                    sb
                                ]
                            ),
                        )
                    )
                    if (
                        distinct_parents
                        and sa == sb
                        and previous_sizes[
                            sa
                        ]
                        > 1
                    ):
                        while ib == ia:
                            ib = int(
                                rng.integers(
                                    0,
                                    int(
                                        previous_sizes[
                                            sb
                                        ]
                                    ),
                                )
                            )

                children[
                    child
                ] = (
                    int(
                        current_masks[
                            sa
                        ][
                            ia
                        ]
                    )
                    | int(
                        current_masks[
                            sb
                        ][
                            ib
                        ]
                    )
                )

            next_masks.append(
                children
            )

        current_masks = (
            next_masks
        )
        record(
            generation
        )

        if (
            global_universal
            is None
            and global_all[
                generation
            ]
            == 1.0
        ):
            global_universal = (
                generation
            )

    return HistoricalGenealogyResult(
        generations=(
            generations
        ),
        founder_descendant_fraction_by_region=(
            per_founder
        ),
        any_founder_fraction_by_region=(
            any_fraction
        ),
        all_founders_fraction_by_region=(
            all_fraction
        ),
        global_all_founders_fraction=(
            global_all
        ),
        global_universal_generation=(
            global_universal
        ),
        founder_extinction_generations=(
            extinction
        ),
        scenario=scenario,
        seed=seed,
    )


def deterministic_late_contact_fraction(
    bridge_rate: float,
    generations: int,
    initial_fraction: float = 0.0,
) -> float:
    """Best-case expected ancestry fraction after late external contact.

    The external parent pool is assumed already 100% descended from the founder
    set. A parent is external with probability bridge_rate; otherwise it is drawn
    from the formerly isolated deme. This is intentionally a best-case bound.
    """
    if not (
        0.0
        <= bridge_rate
        <= 1.0
    ):
        raise ValueError(
            "bridge_rate must lie between 0 and 1"
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
                    - bridge_rate
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


def simulate_late_contact_sensitivity(
    bridge_rates: Sequence[float],
    generations: int = 9,
    population_size: int = 100,
    replicates: int = 2_000,
    seed: int | None = None,
) -> LateContactSummary:
    """Finite-population sensitivity after a hard barrier reopens.

    This conditions on the external pool already being universally descended
    from the founder set. It therefore gives an intentionally favorable test of
    how quickly ancestry can spread inside the formerly isolated deme.
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
            "bridge_rates must be a non-empty sequence"
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
            "replicates must be at least 1"
        )

    rng = np.random.default_rng(
        seed
    )

    mean = np.empty(
        rates.size,
        dtype=float,
    )
    fixation = np.empty(
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

    for (
        rate_index,
        rate,
    ) in enumerate(
        rates
    ):
        descendant_counts = np.zeros(
            replicates,
            dtype=int,
        )

        for _ in range(
            generations
        ):
            f = (
                descendant_counts
                / population_size
            )
            p_child = (
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
            descendant_counts = (
                rng.binomial(
                    population_size,
                    p_child,
                )
            )

        final = (
            descendant_counts
            / population_size
        )
        mean[
            rate_index
        ] = float(
            np.mean(
                final
            )
        )
        fixation[
            rate_index
        ] = float(
            np.mean(
                descendant_counts
                == population_size
            )
        )
        (
            q05[
                rate_index
            ],
            median[
                rate_index
            ],
            q95[
                rate_index
            ],
        ) = np.quantile(
            final,
            [
                0.05,
                0.5,
                0.95,
            ],
        )

    return LateContactSummary(
        bridge_rates=(
            rates
        ),
        mean_final_fraction=(
            mean
        ),
        fixation_probability=(
            fixation
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


def deterministic_historical_genealogy(
    scenario: HistoricalScenario,
) -> DeterministicHistoricalResult:
    """Infinite-population recursion for founder pedigree states.

    State m is a founder bit mask. For two founders the four states are neither,
    founder 1 only, founder 2 only, and both. Parent states are mixed according
    to the time-varying parent-source matrix and child state is the bitwise OR
    of two independently sampled parent states.
    """
    founder_count = (
        scenario.founder_count
    )
    if founder_count > 4:
        raise ValueError(
            "deterministic state recursion supports at most 4 founders"
        )

    region_count = len(
        scenario.region_names
    )
    state_count = (
        1 << founder_count
    )
    full_mask = (
        state_count
        - 1
    )

    fractions = np.zeros(
        (
            scenario.generations
            + 1,
            region_count,
            state_count,
        ),
        dtype=float,
    )
    fractions[
        0,
        :,
        0,
    ] = 1.0

    source = (
        scenario.founder_region
    )
    source_n = float(
        scenario.population_sizes[
            0,
            source,
        ]
    )
    fractions[
        0,
        source,
        0,
    ] = (
        1.0
        - founder_count
        / source_n
    )

    for founder in range(
        founder_count
    ):
        fractions[
            0,
            source,
            1 << founder,
        ] = (
            1.0
            / source_n
        )

    for generation in range(
        1,
        scenario.generations
        + 1,
    ):
        matrix = (
            scenario.parent_source_matrices[
                generation
                - 1
            ]
        )

        for child_region in range(
            region_count
        ):
            parent_state = (
                matrix[
                    child_region
                ]
                @ fractions[
                    generation
                    - 1
                ]
            )

            child_state = np.zeros(
                state_count,
                dtype=float,
            )

            for a in range(
                state_count
            ):
                if (
                    parent_state[
                        a
                    ]
                    == 0
                ):
                    continue

                for b in range(
                    state_count
                ):
                    if (
                        parent_state[
                            b
                        ]
                        == 0
                    ):
                        continue

                    child_state[
                        a | b
                    ] += (
                        parent_state[
                            a
                        ]
                        * parent_state[
                            b
                        ]
                    )

            if (
                generation == 1
                and child_region
                == source
                and scenario.founder_pair_joint_children
                > 0
                and founder_count
                == 2
            ):
                next_n = float(
                    scenario.population_sizes[
                        generation,
                        source,
                    ]
                )
                forced = min(
                    1.0,
                    scenario.founder_pair_joint_children
                    / next_n,
                )
                child_state *= (
                    1.0
                    - forced
                )
                child_state[
                    full_mask
                ] += forced

            fractions[
                generation,
                child_region,
            ] = (
                child_state
                / child_state.sum()
            )

    any_fraction = (
        1.0
        - fractions[
            :,
            :,
            0,
        ]
    )
    all_fraction = (
        fractions[
            :,
            :,
            full_mask,
        ]
    )

    global_all = np.empty(
        scenario.generations
        + 1,
        dtype=float,
    )

    for generation in range(
        scenario.generations
        + 1
    ):
        weights = (
            scenario.population_sizes[
                generation
            ].astype(
                float
            )
        )
        global_all[
            generation
        ] = float(
            np.average(
                all_fraction[
                    generation
                ],
                weights=weights,
            )
        )

    return DeterministicHistoricalResult(
        generations=np.arange(
            scenario.generations
            + 1,
            dtype=int,
        ),
        mask_fractions_by_region=(
            fractions
        ),
        any_founder_fraction_by_region=(
            any_fraction
        ),
        all_founders_fraction_by_region=(
            all_fraction
        ),
        global_all_founders_fraction=(
            global_all
        ),
        scenario=scenario,
    )
