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

$$
f_{t+1}=1-(1-f_t)^2.
$$

The stochastic simulation samples parents explicitly, so rare founder lineages can disappear by chance.

## Model 02: structured populations and migration

Model 02 removes the strongest unrealistic assumption from Model 01: complete mixing.

The population is divided into demes. For a child born in deme $i$, the migration matrix entry $M_{ij}$ is the probability that a parent is sampled from source deme $j$. This is an abstraction of parental-source mixing or gene flow.

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

## Model 03: time-varying connectivity

Model 03 allows migration barriers to appear or disappear over time.

[![Open Model 03 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/03_time_varying_connectivity.ipynb)

This distinction is important:

- a population isolated from the start cannot receive founder ancestry across the barrier;
- a population that becomes isolated later may already contain that ancestry;
- reopening a route can restart spread after a period of isolation.

### When does isolation begin?

The figure below varies the generation when a permanent barrier appears. The final-generation fixation probability changes strongly with both migration rate and barrier timing.

![Barrier closure timing](figures/model03_closure_timing.svg)

These are small illustrative simulations. The plotted probabilities include Monte Carlo error and are not historical estimates.

### Same barrier, different histories

The barrier in these scenarios is between Deme 3 and Deme 4.

![Time-varying barrier scenarios](figures/model03_scenario_heatmap.svg)

A barrier present from generation 1 keeps the right component free of founder ancestry. Closing the same barrier later can give a completely different result because ancestry may already have crossed.

### Animation: isolation after ancestry crosses

In this run, the barrier closes at generation 20. Founder ancestry has already entered Deme 4. After isolation, ancestry continues spreading inside the now-separated right component.

![Time-varying barrier animation](figures/model03_barrier_animation.svg)

## Model 04: population growth, carrying capacity, and overlapping ancestry

Model 04 addresses a common intuition trap: treating "descendants of the founder" and "descendants of everyone else" as two disjoint populations that each grow exponentially.

After intermarriage, those descendant sets overlap. A person can be descended from both the founder and members of the original background population.

[![Open Model 04 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/04_demography_carrying_capacity.ipynb)

Under neutral random mating,

$
f_{t+1}=1-(1-f_t)^2
$

still governs the expected founder-descendant fraction even when total population size changes. Demography changes absolute descendant counts and finite-population extinction risk, but not this infinite-population neutral fraction recurrence.

### Growth and carrying capacity

The upper panel below compares constant, exponential, and logistic population-size schedules. The lower panel shows the same expected genealogical ancestry fraction for all three because they begin with the same founder fraction.

![Demography versus ancestry fraction](figures/model04_demography_vs_fraction.svg)

### Why two exponential lineages are the wrong picture

The next figure separately tracks descendants of the founder group, descendants of the original background group, and people descended from both.

![Overlapping descendant sets](figures/model04_overlapping_descendants.svg)

Once intermarriage occurs, "founder descendants" and "background descendants" are overlapping sets, not mutually exclusive clans.

### Animated overlap

![Animated overlapping descendant sets](figures/model04_overlap_animation.svg)

The notebook also lets you introduce logistic carrying capacity, temporary bottlenecks, and a relative reproductive-weight sensitivity parameter. These are conceptual experiments, not estimates of prehistoric demography.

## Model 05: endogamy and assortative mating

Model 05 replaces purely geographic barriers with persistent **social mating structure**.

[![Open Model 05 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/05_endogamy_assortative_mating.ipynb)

An endogamy strength of 0 means mate communities are sampled according to population size, while 1 means perfect within-community mating. Perfect endogamy is therefore a true reproductive barrier even if communities are geographically adjacent.

### Endogamy slows cross-community spread

![Endogamy trajectories](figures/model05_endogamy_trajectories.svg)

As endogamy approaches 1, the time required for founder ancestry to penetrate other communities can become much longer. At exactly 1, other communities are unreachable.

### Endogamy plus assortative mating

![Endogamy and assortment sensitivity](figures/model05_endogamy_assortment_heatmap.svg)

The vertical axis is an abstract same-state mate-choice weight. It is included as a sensitivity analysis only. Deep genealogical ancestry itself is not assumed to be observable.

### Animated high-endogamy example

![Endogamy animation](figures/model05_endogamy_animation.svg)

The model distinguishes **perfect isolation** from **rare bridging marriages**. A single cross-community genealogical bridge can seed ancestry inside an otherwise highly endogamous community, after which within-community reproduction can propagate it.

## Model 06: genealogical MRCA and the Identical Ancestors Point

Model 06 traces complete two-parent pedigrees **backward** from the present generation.

- The genealogical **MRCA** is the first past generation containing at least one person who is an ancestor of everyone in the present population.
- The **Identical Ancestors Point (IAP)** is farther back: every person in that generation who has any present-day descendants is an ancestor of everyone in the present population.

The IAP is a time threshold, not a single ancestor.

[![Open Model 06 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vafaei-ar/Evolution-Creation/blob/main/notebooks/06_mrca_iap.ipynb)

### Exact finite pedigree

Each past individual is classified as having no present descendants, being a partial ancestor, or being a universal ancestor. The first universal ancestor marks the MRCA; the disappearance of all partial ancestors marks the IAP.

![Exact MRCA and IAP trajectory](figures/model06_status_trajectory.svg)

### Chang random-mating benchmark

For Chang's idealized constant-size two-parent model, the large-population benchmarks are

$
T_{MRCA}\approx\log_2N
$

and

$
T_{IAP}\approx1.77\log_2N.
$

The exact finite simulations approach these only gradually.

![MRCA and IAP scaling](figures/model06_scaling.svg)

These equations are asymptotic results for an idealized random-mating population. They are not historical dates for humanity.

### Population structure

The structured extension interpolates between population-size-proportional panmixia and complete within-community isolation.

![Isolation sensitivity](figures/model06_isolation_sensitivity.svg)

Near-complete isolation can substantially delay MRCA and IAP. At complete persistent isolation, a global MRCA is impossible across disconnected present-day communities.

### Animated backward pedigree

![Animated MRCA-IAP transition](figures/model06_status_animation.svg)

This is genealogical ancestry only. A genealogical common ancestor does not imply that detectable DNA from that ancestor survives in every present-day descendant. Chromosomal inheritance is reserved for Model 07.

Primary references:

- Joseph T. Chang (1999), Recent common ancestors of all present-day individuals, Advances in Applied Probability 31(4), 1002-1026. https://doi.org/10.1239/aap/1029955256
- Douglas L. T. Rohde, Steve Olson, and Joseph T. Chang (2004), Modelling the recent common ancestry of all living humans, Nature 431, 562-566. https://doi.org/10.1038/nature02842

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
python scripts/generate_model04_outputs.py
python scripts/generate_model05_outputs.py
python scripts/generate_model06_outputs.py
~~~

## Modeling roadmap

1. Founder ancestry in a single panmictic population: implemented
2. Multiple demes, migration, and fixed barriers: implemented
3. Time-varying barriers and historically changing connectivity: implemented
4. Time-varying population size, carrying capacity, bottlenecks, and overlapping ancestry: implemented
5. Endogamy and assortative mating: implemented
6. Genealogical MRCA and identical-ancestors behavior: implemented
7. Chromosomes, recombination, and loss of detectable founder DNA
8. Historically constrained scenarios

## Interpretation rule

Every model should separate:

**Assumptions → mechanism → output → interpretation → what the model does not establish**

A simulation can demonstrate compatibility under assumptions. It cannot by itself establish that a historical or theological event occurred.
