# Model 06: genealogical MRCA and the Identical Ancestors Point

## Question

How far back must we trace a two-parent pedigree before at least one person is an ancestor of everyone alive in the present generation? How much farther back until every past individual who has any present-day descendants is an ancestor of everyone alive today?

These are the genealogical MRCA and Identical Ancestors Point (IAP) questions.

## Definitions

### Genealogical MRCA

The most recent common ancestor is the most recent past individual who is a genealogical ancestor of every member of the present population.

This is not the same concept as mitochondrial Eve, a Y-chromosomal MRCA, or the common ancestor of a particular DNA segment. Those are lineage- or locus-specific genetic concepts.

The genealogical MRCA is also not the only ancestor alive at that time. Many other people can be ancestors of subsets of the present population.

### Identical Ancestors Point

Trace farther into the past. At the IAP, the remaining ancestry becomes all or nothing:

- every past individual with at least one present-day descendant is an ancestor of all present-day individuals;
- everyone else has no present-day descendants.

The IAP is a time threshold, not a particular person.

## Chang random-mating baseline

Joseph T. Chang studied a constant-size two-parent analog of the Wright-Fisher model.

In the large-population limit, his results give the benchmarks

$$
T_{MRCA} \approx \log_2 N
$$

and

$$
T_{IAP} \approx 1.77\log_2 N.
$$

The implementation exposes these only as asymptotic benchmarks. Exact finite simulations do not have to equal them, especially at modest population sizes.

The baseline assumptions are intentionally strong:

- constant population size;
- discrete non-overlapping generations;
- two parents per person;
- parents sampled independently and uniformly from the previous generation;
- parent sampling with replacement;
- no geography;
- no social endogamy;
- no age structure or sex structure;
- no genetics.

## Exact finite pedigree simulation

The simulator assigns one bit to each person in the present generation.

For each past individual, a Python integer bit mask records which present-day people descend from that person.

At every past generation, an individual is therefore in exactly one of three states:

1. no present descendants;
2. partial ancestor, ancestor of some but not all present individuals;
3. universal ancestor, ancestor of everyone in the present generation.

The first universal ancestor marks the MRCA generation.

The first generation with zero partial ancestors marks the IAP.

This computes the finite pedigree exactly for the simulated parent assignments rather than approximating ancestry by a fraction.

## Population structure

The structured extension divides the population into persistent communities.

For a child in community i, each parent independently chooses a source community according to row i of a parent-source matrix, then chooses one parent uniformly inside that source community.

The helper parameter isolation strength interpolates between:

- 0: population-size-proportional panmixia;
- 1: complete within-community isolation.

Complete isolation makes a global genealogical MRCA impossible when the present population contains more than one disconnected community.

Near-complete isolation is different. Rare cross-community parentage can still connect pedigrees, but MRCA and IAP times can become much later.

## Relation to Rohde, Olson, and Chang

Rohde, Olson, and Chang (2004) explicitly addressed the criticism that a random-mating population is unrealistic. They analyzed models with substantial population substructure and found that recent genealogical common ancestry still emerged in those models.

Their historical simulations were substantially richer than Model 06. The current repository model should therefore be read as a transparent bridge between Chang's mathematical baseline and later historically constrained modeling, not as a reproduction of the full Rohde et al. world model.

## Genealogical ancestry is not genetic ancestry

A universal genealogical ancestor need not contribute detectable autosomal DNA to every descendant.

Model 06 tracks paths in a pedigree only.

Chromosomal inheritance, recombination, and loss of founder DNA are intentionally deferred to Model 07.

## What this model does not establish

It does not date the actual MRCA or IAP of living humans.

It does not establish that an 11,000-year-old proposed founder is historically real.

It does not estimate prehistoric migration rates or social mating patterns.

It shows what follows from specified pedigree assumptions and how those conclusions change as reproductive isolation is introduced.

## References

Chang, J. T. (1999). Recent common ancestors of all present-day individuals. Advances in Applied Probability, 31(4), 1002-1026. https://doi.org/10.1239/aap/1029955256

Rohde, D. L. T., Olson, S., & Chang, J. T. (2004). Modelling the recent common ancestry of all living humans. Nature, 431, 562-566. https://doi.org/10.1038/nature02842
