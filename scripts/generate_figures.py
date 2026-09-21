"""Generate reproducible figures for the README and documentation."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from evolution_creation.genealogy import (
    deterministic_random_mating_curve,
    simulate_replicates,
)


def main() -> None:
    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    population_size = 1_000
    generations = 25
    founder_count = 1
    replicates = 250
    seed = 20260920

    curves = simulate_replicates(
        population_size=population_size,
        generations=generations,
        founder_count=founder_count,
        replicates=replicates,
        seed=seed,
    )
    generation = np.arange(generations + 1)
    median = np.median(curves, axis=0)
    lower = np.quantile(curves, 0.10, axis=0)
    upper = np.quantile(curves, 0.90, axis=0)

    deterministic = deterministic_random_mating_curve(
        initial_fraction=founder_count / population_size,
        generations=generations,
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(generation, lower, upper, alpha=0.2, label="10th-90th percentile")
    ax.plot(generation, median, label="simulation median")
    ax.plot(generation, deterministic, linestyle="--", label="deterministic approximation")
    ax.set(
        xlabel="Generation",
        ylabel="Fraction with founder ancestry",
        title="Spread of genealogical ancestry in a panmictic population",
        ylim=(0, 1.02),
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "founder_spread.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
