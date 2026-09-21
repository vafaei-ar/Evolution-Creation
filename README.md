# Evolution-Creation

A reproducible Python project for testing quantitative claims raised in a debate about evolution, creation, human genealogy, migration, and genetic ancestry.

The project does **not** assume that a theological or historical claim is true. Each model is framed conditionally:

> Given a stated set of assumptions, what follows mathematically or computationally?

## Model 01: spread of a genealogical founder

The baseline asks:

> If one individual enters a finite, completely mixed population and reproduces within it, how does that individual's genealogical ancestry spread through later generations?

It assumes fixed population size, non-overlapping generations, two parents per child, random mating, no geography, no migration, no selection, and no genetics.

[![Open Model 01 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/01_founder_spread.ipynb)

Under the infinite-population deterministic approximation:

[
f_{t+1}=1-(1-f_t)^2.
]

The stochastic simulation samples parents explicitly, so rare founder lineages can disappear by chance.

## Model 02: structured populations and migration

Model 02 removes the strongest unrealistic assumption from Model 01: complete mixing.

The population is divided into demes. For a child born in deme (i), the migration matrix entry (M_{ij}) is the probability that a parent is sampled from source deme (j). This is an abstraction of parental-source mixing or gene flow.

[![Open Model 02 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/02_structured_migration.ipynb)

### Example trajectory

The figure below uses five equal demes in a line, one founder population at the left edge, and a total nearest-neighbor migration rate of 0.02 per parental draw.

![Founder ancestry across connected demes](figures/model02_deme_spread.svg)

The parameter values above are illustrative. They are **not** estimates of ancient human migration.

### Sensitivity to migration and elapsed time

The next figure estimates the probability that founder ancestry has fixed in all four demes by the stated generation. It uses 30 stochastic replicates per cell.

![Migration sensitivity heatmap](figures/model02_fixation_heatmap.svg)

At migration rate zero, the founder lineage cannot cross between demes. With nonzero connectivity, elapsed time and migration rate jointly control whether the lineage spreads through the entire system.

### Animated ancestry front

The generated SVG below animates one stochastic run across seven demes.

![Animated ancestry spread](figures/model02_spread_animation.svg)

Model 02 also has a hard-barrier control. A permanent barrier makes the migration matrix block-disconnected. If the founder starts on one side, ancestry cannot reach the other side regardless of how many generations pass.

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
~~~

## Modeling roadmap

1. Founder ancestry in a single panmictic population: implemented
2. Multiple demes, migration, and fixed barriers: implemented
3. Time-varying barriers and historically changing connectivity
4. Time-varying population size and carrying capacity
5. Endogamy and assortative mating
6. Genealogical MRCA and identical-ancestors behavior
7. Chromosomes, recombination, and loss of detectable founder DNA
8. Historically constrained scenarios

## Interpretation rule

Every model should separate:

**Assumptions → mechanism → output → interpretation → what the model does not establish**

A simulation can demonstrate compatibility under assumptions. It cannot by itself establish that a historical or theological event occurred.
