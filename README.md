# Evolution-Creation

A reproducible Python project for testing quantitative claims raised in a debate about evolution, creation, human genealogy, migration, and genetic ancestry.

The project does **not** assume that a theological or historical claim is true. Each model is framed conditionally:

> Given a stated set of assumptions, what follows mathematically or computationally?

## Model 01: spread of a genealogical founder

The first model addresses a narrow question from the debate:

> If one individual enters a finite population and reproduces within it, how does that individual's genealogical ancestry spread through later generations?

The baseline model deliberately assumes:

- fixed population size,
- discrete non-overlapping generations,
- two parents per child,
- random mating,
- no geography,
- no migration,
- no selection,
- no genetics or recombination.

These assumptions are intentionally unrealistic. They create a transparent baseline that we can progressively relax.

### Interactive notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/01_founder_spread.ipynb)

The notebook lets you change population size, number of founders, number of generations, number of stochastic replicates, and random seed.

### Core quantity

For generation t:

f_t = (number of people descended from the tagged founder(s)) / N.

A person counts as a genealogical descendant if at least one parent is already a genealogical descendant.

Under an infinite-population deterministic approximation with random mating:

f_(t+1) = 1 - (1 - f_t)^2.

The simulation does not force this recurrence. It samples parents explicitly, so founder lineages can disappear by chance, especially in early generations.

## Repository structure

~~~text
src/evolution_creation/   reusable model code
notebooks/                interactive Colab notebooks
scripts/                  reproducible figure-generation scripts
tests/                    unit tests
docs/                     assumptions and interpretation
figures/                  generated outputs
~~~

## Run locally

~~~bash
python -m pip install -e ".[dev]"
pytest
python scripts/generate_figures.py
~~~

## Modeling roadmap

1. Founder ancestry in a single panmictic population
2. Multiple demes and migration
3. Geographic barriers and complete isolation
4. Time-varying migration and population size
5. Endogamy and assortative mating
6. Genealogical MRCA and identical-ancestors behavior
7. Chromosomes, recombination, and loss of detectable founder DNA
8. Historically constrained scenarios

## Interpretation rule

Every model should separate:

**Assumptions → mechanism → output → interpretation → what the model does not establish**

A simulation can demonstrate compatibility under assumptions. It cannot by itself establish that a historical or theological event occurred.
