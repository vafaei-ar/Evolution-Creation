# Evolution-Creation

A reproducible Python project for testing quantitative claims raised in a debate about evolution, creation, human genealogy, migration, and genetic ancestry.

The project does **not** assume that a theological or historical claim is true. Each model is framed conditionally:

> Given a stated set of assumptions, what follows mathematically or computationally?

## Model 01: spread of a genealogical founder

The baseline asks what happens when one founder enters a finite, completely mixed population.

[![Open Model 01 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/01_founder_spread.ipynb)

## Model 02: structured populations and migration

Model 02 divides the population into demes and represents parental-source mixing with a migration matrix.

[![Open Model 02 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/02_structured_migration.ipynb)

![Founder ancestry across connected demes](figures/model02_deme_spread.svg)

![Migration sensitivity heatmap](figures/model02_fixation_heatmap.svg)

![Animated ancestry spread](figures/model02_spread_animation.svg)

## Model 03: time-varying connectivity

Model 03 allows barriers to appear or disappear over time.

[![Open Model 03 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/03_time_varying_connectivity.ipynb)

A population isolated from the start is different from a population that becomes isolated only after founder ancestry has crossed.

### Barrier closure timing

![Barrier closure timing](figures/model03_closure_timing.svg)

These are illustrative Monte Carlo estimates, not historical migration estimates.

### Same barrier, different histories

The barrier is between Deme 3 and Deme 4.

![Time-varying barrier scenarios](figures/model03_scenario_heatmap.svg)

### Animation: isolation after ancestry crosses

In this run, the barrier closes at generation 20. Founder ancestry has already entered Deme 4, so later isolation does not erase that prior genealogical connection.

![Time-varying barrier animation](figures/model03_barrier_animation.svg)

## Repository structure

~~~text
src/evolution_creation/   reusable model code
notebooks/                interactive Colab notebooks
scripts/                  reproducible output-generation scripts
tests/                    unit tests
docs/                     assumptions and interpretation
figures/                  generated outputs shown in this README
~~~

## Run locally

~~~bash
python -m pip install -e ".[dev]"
pytest
python scripts/generate_figures.py
python scripts/generate_model02_outputs.py
python scripts/generate_model03_outputs.py
~~~

## Modeling roadmap

1. Founder ancestry in a single panmictic population: implemented
2. Multiple demes, migration, and fixed barriers: implemented
3. Time-varying barriers and historically changing connectivity: implemented
4. Time-varying population size and carrying capacity
5. Endogamy and assortative mating
6. Genealogical MRCA and identical-ancestors behavior
7. Chromosomes, recombination, and loss of detectable founder DNA
8. Historically constrained scenarios

## Interpretation rule

Every model should separate assumptions, mechanism, output, interpretation, and what the model does not establish.

A simulation can demonstrate compatibility under assumptions. It cannot by itself establish that a historical or theological event occurred.
