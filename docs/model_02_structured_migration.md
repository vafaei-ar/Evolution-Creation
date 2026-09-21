# Model 02: structured populations and migration

## Question

How does genealogical ancestry spread when the population is divided into partially connected groups rather than one fully mixed population?

This is the first model that can represent the central migration objection in the debate. A founder can become common in one region while remaining absent from another. If a barrier is complete, ancestry cannot cross it.

## State variables

The population is divided into demes. Deme $i$ has fixed size $N_i$.

For each person we track only a Boolean genealogical state:

- 1: at least one tagged founder occurs somewhere in the pedigree
- 0: no tagged founder occurs in the pedigree

This is still a genealogy model, not a genetic model.

## Migration matrix

The model uses a row-stochastic matrix $M$.

$M_{ij}$ is the probability that a parent of a child born in destination deme $i$ is sampled from source deme $j$.

Every row sums to one.

This is best interpreted as **parental-source mixing or gene flow**, not literal adult migration. It is a transparent abstraction that can later be replaced by explicit movement and geography.

## Linear chain

The helper function creates nearest-neighbor mixing:

~~~text
Deme 1 <-> Deme 2 <-> Deme 3 <-> Deme 4 <-> Deme 5
~~~

For interior demes, total migration probability $m$ is split equally between the left and right neighbors.

## Hard barrier

A barrier can remove one edge:

~~~text
Deme 1 <-> Deme 2  |  Deme 3 <-> Deme 4
                    ^
                 barrier
~~~

The removed probability is returned to the diagonal, so the affected demes draw those parents locally instead.

If the founder starts on the left and the barrier remains complete, founder ancestry is mathematically unable to reach the right side. This is a structural result, not a matter of waiting longer.

## Main outputs

The model reports:

- founder-ancestry fraction in each deme by generation
- population-size weighted global ancestry fraction
- whether every deme has been reached
- whether founder ancestry has fixed in every deme
- stochastic probability of global fixation across repeated simulations

## Sensitivity surface

The repository includes a generated heatmap of:

$$
P(\text{global genealogical fixation by generation } t)
$$

over migration rate and elapsed generations.

The parameter values in that figure are illustrative. They are not estimates of ancient human migration.

## What this model shows

It demonstrates that the single-population result from Model 01 is highly sensitive to connectivity.

Low but nonzero migration can eventually spread genealogical ancestry through connected demes.

A complete persistent barrier prevents spread across that barrier.

## What it does not establish

It does not tell us which migration matrix describes actual human history.

It does not yet use archaeological dates, settlement histories, ancient DNA, population-size reconstructions, sex-biased migration, changing coastlines, or time-varying barriers.

It does not model genetic inheritance.

Those are the next empirical and computational layers.
