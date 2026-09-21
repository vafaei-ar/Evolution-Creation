# Model 01: founder ancestry spread

## Question

If one or more tagged founders enter a finite population, under what assumptions can their genealogical ancestry spread to a large fraction of later generations?

## Assumptions

The baseline model has a constant population size N. Generations do not overlap. Each child independently samples two parents uniformly from the previous generation. The model tracks a Boolean state: whether an individual has at least one tagged founder anywhere in their pedigree.

The model does **not** track DNA.

## Mechanism

A child has founder ancestry if either sampled parent has founder ancestry.

The observed ancestry fraction is the number of people with founder ancestry divided by N.

For an infinite, perfectly mixed population, a deterministic approximation is:

f_(t+1) = 1 - (1 - f_t)^2.

The finite stochastic model can behave differently because a rare founder lineage may disappear by chance.

## What this model can show

It can show how quickly genealogical ancestry can spread **if random mating and complete mixing are assumed**.

It can quantify early lineage-extinction risk.

It can show the difference between deterministic intuition and finite-population stochastic simulations.

## What this model cannot show

It does not establish that any historical founder existed.

It does not establish that ancient human populations were panmictic.

It says nothing about detectable DNA from a founder.

It does not yet represent migration barriers, continents, cultural endogamy, sex-biased reproduction, selection, population growth, or extinction events.

Those limitations are not minor details. They are precisely the assumptions that later models must test.
