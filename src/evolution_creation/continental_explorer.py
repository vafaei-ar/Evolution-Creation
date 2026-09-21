"""Interactive continental founder-spread explorer.

This module is a synthesis layer over the earlier genealogy, migration,
endogamy, historical-constraint, and admixture models. It is intended for
transparent sensitivity analysis, not as a reconstruction of exact human
history.

The deterministic model tracks four pedigree states in each region:
0 = neither founder, 1 = Adam only, 2 = Eve only, 3 = both founders.

The stochastic model samples those pedigree states in finite populations and
therefore captures early lineage loss and run-to-run variation.

Migration is represented as a parent-source matrix: row i gives the probability
that one parental draw for a child born in region i comes from source region j.
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
    "Australia/Oceania",
    "Tasmania",
)

DEFAULT_COORDINATES = np.array(
    [
        [33.0, 44.0],
        [7.0, 20.0],
        [51.0, 15.0],
        [35.0, 100.0],
        [15.0, -90.0],
        [-22.0, 135.0],
        [-42.0, 147.0],
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
    barrier_pairs: tuple[tuple[int, int], ...]
    barrier_release_age_years: float | None

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
        return self.descendant_counts.sum(axis=1) / total

    @property
    def global_any_founder_fraction(self) -> np.ndarray:
        total = self.populations.sum(axis=1)
        return (
            self.populations
            * self.any_founder_fraction
        ).sum(axis=1) / total

    @property
    def global_genetic_ancestry(self) -> np.ndarray:
        total = self.populations.sum(axis=1)
        return (
            self.populations
            * self.genetic_ancestry
        ).sum(axis=1) / total


@dataclass(frozen=True)
class StochasticExplorerResult:
    generations: np.ndarray
    years_before_present: np.ndarray
    populations: np.ndarray
    both_founders_fraction: np.ndarray
    any_founder_fraction: np.ndarray
    region_names: tuple[str, ...]
    replicates: int
    seed: int | None

    @property
    def global_both_founders_fraction(self) -> np.ndarray:
        weights = self.populations[None, :, :]
        return (
            weights
            * self.both_founders_fraction
        ).sum(axis=2) / weights.sum(axis=2)

    @property
    def global_any_founder_fraction(self) -> np.ndarray:
        weights = self.populations[None, :, :]
        return (
            weights
            * self.any_founder_fraction
        ).sum(axis=2) / weights.sum(axis=2)

    def regional_quantile(
        self,
        q: float,
        metric: str = "both",
    ) -> np.ndarray:
        if not 0.0 <= q <= 1.0:
            raise ValueError("q must lie in [0, 1]")
        values = (
            self.both_founders_fraction
            if metric == "both"
            else self.any_founder_fraction
        )
        if metric not in {"both", "any"}:
            raise ValueError("metric must be both or any")
        return np.quantile(values, q, axis=0)

    def global_quantile(
        self,
        q: float,
        metric: str = "both",
    ) -> np.ndarray:
        if metric == "both":
            values = self.global_both_founders_fraction
        elif metric == "any":
            values = self.global_any_founder_fraction
        else:
            raise ValueError("metric must be both or any")
        return np.quantile(values, q, axis=0)

    def probability_all_regions_above(
        self,
        threshold: float,
        metric: str = "both",
        generation: int = -1,
    ) -> float:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must lie in [0, 1]")
        values = (
            self.both_founders_fraction
            if metric == "both"
            else self.any_founder_fraction
        )
        if metric not in {"both", "any"}:
            raise ValueError("metric must be both or any")
        return float(
            np.mean(
                np.all(
                    values[:, generation, :] >= threshold,
                    axis=1,
                )
            )
        )

    @property
    def any_founder_extinction_probability(self) -> float:
        return float(
            np.mean(
                np.all(
                    self.any_founder_fraction[:, -1, :] == 0.0,
                    axis=1,
                )
            )
        )

    @property
    def both_founders_absent_probability(self) -> float:
        return float(
            np.mean(
                np.all(
                    self.both_founders_fraction[:, -1, :] == 0.0,
                    axis=1,
                )
            )
        )


@dataclass(frozen=True)
class ScenarioDiagnosis:
    reached_global_99: bool
    global_present_both_fraction: float
    limiting_region: str
    limiting_region_fraction: float
    last_region_to_99: str | None
    last_region_to_99_years_ago: float | None
    hard_barrier_regions: tuple[str, ...]
    messages: tuple[str, ...]


def parent_source_matrix_from_offdiag(
    offdiag: Sequence[Sequence[float]],
) -> np.ndarray:
    """Build a row-stochastic parent-source matrix from off-diagonal rates."""
    arr = np.asarray(offdiag, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("offdiag must be a square matrix")
    if np.any(arr < 0.0):
        raise ValueError("parent-source fractions must be non-negative")
    arr = arr.copy()
    np.fill_diagonal(arr, 0.0)
    row_external = arr.sum(axis=1)
    if np.any(row_external >= 1.0):
        raise ValueError(
            "off-diagonal parent-source fractions must sum to < 1 in every row"
        )
    np.fill_diagonal(arr, 1.0 - row_external)
    return arr


def validate_parent_source_matrix(
    matrix: Sequence[Sequence[float]],
) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("parent-source matrix must be square")
    if np.any(arr < 0.0):
        raise ValueError("parent-source matrix must be non-negative")
    if not np.allclose(arr.sum(axis=1), 1.0, atol=1e-10):
        raise ValueError("each parent-source row must sum to 1")
    return arr.copy()


def scale_external_parent_sources(
    matrix: Sequence[Sequence[float]],
    multiplier: float,
) -> np.ndarray:
    """Scale off-diagonal parental sources while preserving row sums."""
    if multiplier < 0.0:
        raise ValueError("multiplier must be non-negative")
    base = validate_parent_source_matrix(matrix)
    out = np.zeros_like(base)
    for i in range(base.shape[0]):
        external = base[i].copy()
        external[i] = 0.0
        external *= multiplier
        external_sum = float(external.sum())
        if external_sum >= 1.0:
            raise ValueError(
                "scaled external parent-source fraction reaches or exceeds 1"
            )
        out[i] = external
        out[i, i] = 1.0 - external_sum
    return out


def apply_hard_barriers(
    matrix: Sequence[Sequence[float]],
    barrier_pairs: Sequence[tuple[int, int]],
) -> np.ndarray:
    """Set selected bidirectional reproductive links to zero and renormalize."""
    out = validate_parent_source_matrix(matrix)
    n = out.shape[0]
    for a, b in barrier_pairs:
        if not (0 <= a < n and 0 <= b < n and a != b):
            raise ValueError("invalid barrier pair")
        out[a, b] = 0.0
        out[b, a] = 0.0
    for i in range(n):
        external = out[i].copy()
        external[i] = 0.0
        total_external = float(external.sum())
        if total_external >= 1.0:
            raise ValueError("barrier-renormalized external fraction invalid")
        out[i, i] = 1.0 - total_external
    return out


def log_population_schedule(
    initial_population: Sequence[float],
    target_population: Sequence[float],
    generations: int,
) -> np.ndarray:
    """Smooth positive population path between initial and target sizes."""
    initial = np.asarray(initial_population, dtype=float)
    target = np.asarray(target_population, dtype=float)
    if (
        initial.ndim != 1
        or target.ndim != 1
        or initial.shape != target.shape
    ):
        raise ValueError(
            "initial and target populations must be same-length vectors"
        )
    if np.any(initial <= 0.0) or np.any(target <= 0.0):
        raise ValueError("population sizes must be positive")
    if generations < 1:
        raise ValueError("generations must be at least 1")
    u = np.linspace(0.0, 1.0, generations + 1)[:, None]
    return np.exp(
        (1.0 - u) * np.log(initial)[None, :]
        + u * np.log(target)[None, :]
    )


def _random_mating_or_distribution(
    states: np.ndarray,
) -> np.ndarray:
    """Child pedigree-state distribution from two random parental draws."""
    out = np.zeros(4, dtype=float)
    for a in range(4):
        for b in range(4):
            out[a | b] += states[a] * states[b]
    return out


def _random_mating_or_distribution_batch(
    states: np.ndarray,
) -> np.ndarray:
    """Vectorized version for arrays ending in four pedigree states."""
    out = np.zeros_like(states, dtype=float)
    for a in range(4):
        for b in range(4):
            out[..., a | b] += states[..., a] * states[..., b]
    return out


def _active_parent_matrix(
    base_matrix: np.ndarray,
    late_matrix: np.ndarray,
    years_ago: float,
    late_contact_age_years: float,
    barrier_pairs: Sequence[tuple[int, int]],
    barrier_release_age_years: float | None,
) -> np.ndarray:
    matrix = (
        late_matrix
        if years_ago <= late_contact_age_years
        else base_matrix
    )
    if (
        barrier_pairs
        and (
            barrier_release_age_years is None
            or years_ago > barrier_release_age_years
        )
    ):
        matrix = apply_hard_barriers(matrix, barrier_pairs)
    return matrix


def _validate_common_inputs(
    parent_source_matrix: Sequence[Sequence[float]],
    mixing_strength: Sequence[float],
    founder_region: int,
    region_names: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    matrix = validate_parent_source_matrix(parent_source_matrix)
    n_regions = matrix.shape[0]
    names = tuple(region_names)
    if len(names) != n_regions:
        raise ValueError("region_names length must match matrix size")
    if not 0 <= founder_region < n_regions:
        raise ValueError("invalid founder_region")
    mixing = np.asarray(mixing_strength, dtype=float)
    if mixing.shape != (n_regions,):
        raise ValueError("mixing_strength must have one value per region")
    if np.any((mixing < 0.0) | (mixing > 1.0)):
        raise ValueError("mixing strengths must lie in [0, 1]")
    return matrix, mixing, names


def simulate_continental_explorer(
    initial_population: Sequence[float],
    target_population: Sequence[float],
    parent_source_matrix: Sequence[Sequence[float]],
    mixing_strength: Sequence[float],
    founder_age_years: float = 11_000.0,
    generation_interval_years: float = 28.0,
    founder_region: int = 0,
    founder_pair_joint_children: int = 2,
    late_contact_age_years: float = 500.0,
    late_contact_multiplier: float = 4.0,
    region_names: Sequence[str] = DEFAULT_REGIONS,
    barrier_pairs: Sequence[tuple[int, int]] = (),
    barrier_release_age_years: float | None = None,
) -> ContinentalExplorerResult:
    """Run the deterministic macroregional founder-spread explorer.

    mixing_strength q lies in [0, 1]. q=1 applies full random mating to the
    pooled regional parental state. q=0 preserves pooled state frequencies.

    barrier_pairs are bidirectional reproductive links that remain closed until
    years_before_present <= barrier_release_age_years. If the release age is
    None, they remain closed for the entire simulation.
    """
    if founder_age_years <= 0.0:
        raise ValueError("founder_age_years must be positive")
    if generation_interval_years <= 0.0:
        raise ValueError("generation_interval_years must be positive")
    if late_contact_age_years < 0.0:
        raise ValueError("late_contact_age_years must be non-negative")
    if founder_pair_joint_children < 0:
        raise ValueError("founder_pair_joint_children must be non-negative")
    if (
        barrier_release_age_years is not None
        and barrier_release_age_years < 0.0
    ):
        raise ValueError("barrier release age must be non-negative")

    matrix, mixing, names = _validate_common_inputs(
        parent_source_matrix,
        mixing_strength,
        founder_region,
        region_names,
    )
    n_regions = matrix.shape[0]
    generations = max(
        1,
        int(round(founder_age_years / generation_interval_years)),
    )
    population = log_population_schedule(
        initial_population,
        target_population,
        generations,
    )
    if population.shape[1] != n_regions:
        raise ValueError("population vectors must match region count")

    late_matrix = scale_external_parent_sources(
        matrix,
        late_contact_multiplier,
    )
    years_before_present = np.linspace(
        founder_age_years,
        0.0,
        generations + 1,
    )

    pedigree = np.zeros(
        (generations + 1, n_regions, 4),
        dtype=float,
    )
    pedigree[0, :, 0] = 1.0

    founder_n = float(population[0, founder_region])
    if founder_n < 2.0:
        raise ValueError("founder region must contain at least two people")
    founder_mass = min(1.0, 1.0 / founder_n)
    pedigree[0, founder_region, 0] = max(
        0.0,
        1.0 - 2.0 * founder_mass,
    )
    pedigree[0, founder_region, 1] = founder_mass
    pedigree[0, founder_region, 2] = founder_mass

    genetic = np.zeros(
        (generations + 1, n_regions),
        dtype=float,
    )
    genetic[0, founder_region] = min(1.0, 2.0 / founder_n)

    external_fraction = np.zeros(
        (generations + 1, n_regions),
        dtype=float,
    )

    for generation in range(generations + 1):
        active = _active_parent_matrix(
            matrix,
            late_matrix,
            years_before_present[generation],
            late_contact_age_years,
            barrier_pairs,
            barrier_release_age_years,
        )
        external_fraction[generation] = 1.0 - np.diag(active)
        if generation == 0:
            continue

        pooled_states = active @ pedigree[generation - 1]
        pooled_genetic = active @ genetic[generation - 1]

        for region in range(n_regions):
            random_child = _random_mating_or_distribution(
                pooled_states[region]
            )
            q = float(mixing[region])
            pedigree[generation, region] = (
                (1.0 - q) * pooled_states[region]
                + q * random_child
            )
            pedigree[generation, region] /= (
                pedigree[generation, region].sum()
            )

        genetic[generation] = pooled_genetic

        if (
            generation == 1
            and founder_pair_joint_children > 0
        ):
            seed = min(
                pedigree[generation, founder_region, 0],
                founder_pair_joint_children
                / population[generation, founder_region],
            )
            pedigree[generation, founder_region, 0] -= seed
            pedigree[generation, founder_region, 3] += seed
            genetic[generation, founder_region] = max(
                genetic[generation, founder_region],
                seed,
            )

    return ContinentalExplorerResult(
        generations=np.arange(generations + 1, dtype=int),
        years_before_present=years_before_present,
        populations=population,
        pedigree_states=pedigree,
        genetic_ancestry=genetic,
        parent_source_external_fraction=external_fraction,
        region_names=names,
        founder_region=int(founder_region),
        founder_age_years=float(founder_age_years),
        generation_interval_years=float(generation_interval_years),
        barrier_pairs=tuple(tuple(x) for x in barrier_pairs),
        barrier_release_age_years=(
            None
            if barrier_release_age_years is None
            else float(barrier_release_age_years)
        ),
    )


def _sample_multinomial_rows(
    rng: np.random.Generator,
    population_size: int,
    probabilities: np.ndarray,
) -> np.ndarray:
    """Vectorized multinomial sampler using sequential binomial draws."""
    p = np.asarray(probabilities, dtype=float)
    p = np.clip(p, 0.0, 1.0)
    p /= p.sum(axis=1, keepdims=True)
    replicates = p.shape[0]
    out = np.zeros((replicates, 4), dtype=np.int64)
    remaining_n = np.full(replicates, population_size, dtype=np.int64)
    remaining_p = np.ones(replicates, dtype=float)

    for state in range(3):
        conditional = np.divide(
            p[:, state],
            remaining_p,
            out=np.zeros(replicates, dtype=float),
            where=remaining_p > 0.0,
        )
        conditional = np.clip(conditional, 0.0, 1.0)
        draw = rng.binomial(remaining_n, conditional)
        out[:, state] = draw
        remaining_n -= draw
        remaining_p -= p[:, state]

    out[:, 3] = remaining_n
    return out


def simulate_continental_stochastic(
    initial_population: Sequence[float],
    target_population: Sequence[float],
    parent_source_matrix: Sequence[Sequence[float]],
    mixing_strength: Sequence[float],
    founder_age_years: float = 11_000.0,
    generation_interval_years: float = 28.0,
    founder_region: int = 0,
    founder_pair_joint_children: int = 2,
    late_contact_age_years: float = 500.0,
    late_contact_multiplier: float = 4.0,
    region_names: Sequence[str] = DEFAULT_REGIONS,
    barrier_pairs: Sequence[tuple[int, int]] = (),
    barrier_release_age_years: float | None = None,
    replicates: int = 200,
    seed: int | None = None,
) -> StochasticExplorerResult:
    """Finite-population Monte Carlo for regional pedigree-state spread."""
    if replicates < 1:
        raise ValueError("replicates must be positive")

    matrix, mixing, names = _validate_common_inputs(
        parent_source_matrix,
        mixing_strength,
        founder_region,
        region_names,
    )
    deterministic = simulate_continental_explorer(
        initial_population=initial_population,
        target_population=target_population,
        parent_source_matrix=matrix,
        mixing_strength=mixing,
        founder_age_years=founder_age_years,
        generation_interval_years=generation_interval_years,
        founder_region=founder_region,
        founder_pair_joint_children=founder_pair_joint_children,
        late_contact_age_years=late_contact_age_years,
        late_contact_multiplier=late_contact_multiplier,
        region_names=names,
        barrier_pairs=barrier_pairs,
        barrier_release_age_years=barrier_release_age_years,
    )
    population = np.maximum(
        2,
        np.rint(deterministic.populations).astype(np.int64),
    )
    generations = len(deterministic.generations) - 1
    n_regions = len(names)
    rng = np.random.default_rng(seed)

    current = np.zeros(
        (replicates, n_regions, 4),
        dtype=np.int64,
    )
    current[:, :, 0] = population[0][None, :]
    current[:, founder_region, 0] -= 2
    current[:, founder_region, 1] += 1
    current[:, founder_region, 2] += 1

    both = np.zeros(
        (replicates, generations + 1, n_regions),
        dtype=np.float32,
    )
    any_founder = np.zeros_like(both)

    denom0 = population[0][None, :]
    both[:, 0, :] = current[:, :, 3] / denom0
    any_founder[:, 0, :] = (
        1.0
        - current[:, :, 0] / denom0
    )

    late_matrix = scale_external_parent_sources(
        matrix,
        late_contact_multiplier,
    )

    for generation in range(1, generations + 1):
        previous_fraction = (
            current
            / population[generation - 1][None, :, None]
        )
        active = _active_parent_matrix(
            matrix,
            late_matrix,
            deterministic.years_before_present[generation],
            late_contact_age_years,
            barrier_pairs,
            barrier_release_age_years,
        )
        pooled = np.einsum(
            "ij,rjk->rik",
            active,
            previous_fraction,
        )
        random_child = _random_mating_or_distribution_batch(pooled)
        probs = (
            (1.0 - mixing[None, :, None]) * pooled
            + mixing[None, :, None] * random_child
        )
        probs /= probs.sum(axis=2, keepdims=True)

        next_counts = np.zeros_like(current)
        for region in range(n_regions):
            next_counts[:, region, :] = _sample_multinomial_rows(
                rng,
                int(population[generation, region]),
                probs[:, region, :],
            )

        if (
            generation == 1
            and founder_pair_joint_children > 0
        ):
            move = np.minimum(
                founder_pair_joint_children,
                next_counts[:, founder_region, 0],
            )
            next_counts[:, founder_region, 0] -= move
            next_counts[:, founder_region, 3] += move

        current = next_counts
        denom = population[generation][None, :]
        both[:, generation, :] = current[:, :, 3] / denom
        any_founder[:, generation, :] = (
            1.0
            - current[:, :, 0] / denom
        )

    return StochasticExplorerResult(
        generations=deterministic.generations,
        years_before_present=deterministic.years_before_present,
        populations=deterministic.populations,
        both_founders_fraction=both,
        any_founder_fraction=any_founder,
        region_names=names,
        replicates=int(replicates),
        seed=seed,
    )


def first_generation_reaching(
    result: ContinentalExplorerResult,
    threshold: float,
    region: int | None = None,
    metric: str = "both",
) -> int | None:
    """Return the first deterministic generation reaching a threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must lie in [0, 1]")
    if metric == "both":
        values = result.both_founders_fraction
    elif metric == "any":
        values = result.any_founder_fraction
    elif metric == "genetic":
        values = result.genetic_ancestry
    else:
        raise ValueError("metric must be both, any, or genetic")

    if region is None:
        if metric == "genetic":
            series = result.global_genetic_ancestry
        else:
            series = (
                result.populations
                * values
            ).sum(axis=1) / result.populations.sum(axis=1)
    else:
        series = values[:, region]

    hits = np.flatnonzero(series >= threshold)
    return int(hits[0]) if hits.size else None


def diagnose_scenario(
    result: ContinentalExplorerResult,
    threshold: float = 0.99,
) -> ScenarioDiagnosis:
    """Generate a compact mechanistic explanation of a deterministic run."""
    final = result.both_founders_fraction[-1]
    limiting_index = int(np.argmin(final))
    limiting_name = result.region_names[limiting_index]
    limiting_value = float(final[limiting_index])

    threshold_hits: list[tuple[int, int]] = []
    for region in range(len(result.region_names)):
        hits = np.flatnonzero(
            result.both_founders_fraction[:, region] >= threshold
        )
        if hits.size:
            threshold_hits.append((region, int(hits[0])))

    last_name: str | None = None
    last_year: float | None = None
    if threshold_hits:
        last_region, last_generation = max(
            threshold_hits,
            key=lambda x: x[1],
        )
        last_name = result.region_names[last_region]
        last_year = float(
            result.years_before_present[last_generation]
        )

    hard_barrier_regions: list[str] = []
    for region, name in enumerate(result.region_names):
        if (
            result.parent_source_external_fraction[:, region].max()
            == 0.0
            and region != result.founder_region
        ):
            hard_barrier_regions.append(name)

    reached = bool(result.global_both_founders_fraction[-1] >= threshold)
    messages: list[str] = []

    if hard_barrier_regions:
        messages.append(
            "No reproductive path ever opens into: "
            + ", ".join(hard_barrier_regions)
            + ". Universal ancestry is impossible there under this scenario."
        )
    if not reached:
        messages.append(
            f"The present limiting region is {limiting_name} at "
            f"{100*limiting_value:.2f}% descended from both founders."
        )
    elif last_name is not None:
        messages.append(
            f"All modeled regions exceed {100*threshold:.0f}% both-founder "
            f"ancestry; {last_name} is the last to cross the threshold."
        )

    if (
        result.barrier_pairs
        and result.barrier_release_age_years is not None
    ):
        messages.append(
            "At least one hard reproductive barrier is explicitly closed "
            f"until {result.barrier_release_age_years:,.0f} years before present."
        )

    dna = float(result.global_genetic_ancestry[-1])
    genealogy = float(result.global_both_founders_fraction[-1])
    if genealogy > 0.9 and dna < 0.01:
        messages.append(
            "Genealogy is near-universal while mean founder-pair autosomal "
            "ancestry remains below 1%, illustrating genealogy-DNA divergence."
        )

    if not messages:
        messages.append(
            "No single hard barrier dominates this run; timing, migration, "
            "mixing, and finite founder seeding jointly determine the outcome."
        )

    return ScenarioDiagnosis(
        reached_global_99=reached,
        global_present_both_fraction=float(
            result.global_both_founders_fraction[-1]
        ),
        limiting_region=limiting_name,
        limiting_region_fraction=limiting_value,
        last_region_to_99=last_name,
        last_region_to_99_years_ago=last_year,
        hard_barrier_regions=tuple(hard_barrier_regions),
        messages=tuple(messages),
    )


def compare_scenarios(
    a: ContinentalExplorerResult,
    b: ContinentalExplorerResult,
) -> dict[str, object]:
    """Summarize two deterministic runs for an A/B interface."""
    if a.region_names != b.region_names:
        raise ValueError("scenario region names must match")
    return {
        "regions": a.region_names,
        "present_both_a": a.both_founders_fraction[-1].copy(),
        "present_both_b": b.both_founders_fraction[-1].copy(),
        "present_genetic_a": a.genetic_ancestry[-1].copy(),
        "present_genetic_b": b.genetic_ancestry[-1].copy(),
        "global_both_a": float(a.global_both_founders_fraction[-1]),
        "global_both_b": float(b.global_both_founders_fraction[-1]),
        "global_genetic_a": float(a.global_genetic_ancestry[-1]),
        "global_genetic_b": float(b.global_genetic_ancestry[-1]),
    }
