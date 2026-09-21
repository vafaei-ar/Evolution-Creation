# Model 04: population growth, carrying capacity, and overlapping ancestry

## Question

If one founder enters a much larger population, why can that founder eventually become a genealogical ancestor of a large fraction of the population even though everyone else is also reproducing?

This model targets the debate exchange in which the founder lineage and the rest of the population were described as two exponential populations, followed by an appeal to environmental limiting factors or carrying capacity.

## The key distinction

"Descendants of the founder" and "descendants of the original background population" are not mutually exclusive groups after intermarriage.

A child can descend from both.

Therefore these two descendant sets cannot generally be modeled as two disjoint populations that compete numerically.

The correct binary complement to "has founder ancestry" is:

> has no founder ancestry anywhere in the pedigree.

That complement can shrink rapidly even while total population size grows.

## Variable population size

Let:

- N_t be total population size in generation t.
- D_t be the number of people with founder ancestry.
- f_t = D_t / N_t.

Under neutral random mating, the expected ancestry fraction follows:

$$
f_{t+1}=1-(1-f_t)^2.
$$

The expected descendant count is:

$$
E[D_{t+1}]=N_{t+1}\left[1-\left(1-\frac{D_t}{N_t}\right)^2\right].
$$

Notice that the fraction recurrence does not contain N_t.

This means that, in the infinite-population neutral expectation, changing future population size changes absolute descendant counts but not the ancestry-fraction trajectory.

Finite populations are different because lineages can disappear by chance.

## Carrying capacity

The logistic schedule is:

$$
N(t)=\frac{K}{1+\left(\frac{K-N_0}{N_0}\right)e^{-rt}},
$$

where K is carrying capacity and r controls growth speed.

Carrying capacity limits total population size. In a neutral model it does not automatically give a relative advantage to the smaller ancestry class.

If density-dependent mortality is ancestry-independent, a larger class can experience more deaths in absolute number simply because it contains more people, while having the same expected per-capita effect.

## Bottlenecks

A temporary bottleneck can strongly affect stochastic lineage survival.

A founder lineage that is still rare can disappear during a bottleneck. Conversely, if founder ancestry is already common, the same bottleneck may have little effect on its genealogical prevalence.

The notebook lets the user vary bottleneck timing, duration, and size.

## Unequal reproductive success

The parameter ancestry_parent_weight changes the probability that a sampled parent comes from the founder-descended class.

- weight = 1: neutral reproduction
- weight > 1: founder-descended parents are overrepresented
- weight < 1: founder-descended parents are underrepresented

This is a sensitivity parameter, not a historical estimate.

## Overlapping ancestry sets

The model also tracks four mutually exclusive categories:

1. founder-only ancestry
2. background-only ancestry
3. both
4. neither

The two sets "founder descendants" and "background descendants" are obtained by combining these categories.

After intermarriage, the "both" category grows. The sum of the two descendant-set fractions can exceed 1 because the sets overlap.

That is the mathematical reason two separate exponential curves are the wrong representation of the verbal argument.

## What this model does not establish

It does not estimate actual prehistoric population sizes, carrying capacities, fertility, mortality, or bottleneck histories.

It does not yet model geography, cultural endogamy, sex-specific reproduction, age structure, or genetic inheritance.

It is a conceptual demographic model for genealogical ancestry.
