# Model 05: endogamy and assortative mating

## Question

How much can social mating structure slow the spread of genealogical ancestry even when there is no geographic barrier?

The earlier models use random or matrix-based mixing. Model 05 adds persistent social communities and explicit mate-choice preferences.

## Community endogamy

Each child belongs to a persistent community.

For a child in community i:

1. one anchor parent is sampled from community i;
2. the mate's community is sampled from row i of a mate-choice matrix;
3. the child has founder ancestry if either parent has founder ancestry.

The helper function builds the mate-choice matrix as

$$
M=sI+(1-s)P,
$$

where s is endogamy strength, I is perfect within-community mating, and P draws mate communities in proportion to population size.

Therefore:

- s = 0 means no extra within-community preference beyond community-size frequency;
- s = 1 means perfect endogamy;
- intermediate values interpolate between them.

Perfect endogamy creates disconnected reproductive communities even if they occupy the same geographic region.

## Assortative mating by modeled ancestry state

The model also includes a same-state mate-choice weight.

A value of 1 means mate choice within the selected community is random with respect to the modeled founder-ancestry state.

Values above 1 make mates with the same modeled ancestry state more likely. Values below 1 favor different states.

This is deliberately labeled an abstract sensitivity experiment. Deep genealogical ancestry is generally not an observable trait that people can directly assort on. The parameter can stand in for an observable identity, status, ethnicity, religion, caste, or other social marker only when such a mapping is justified separately.

## Deterministic recurrence

Let f_i be the founder-ancestry fraction in community i.

For an anchor parent without founder ancestry, let q_j be the probability that a mate selected from community j has founder ancestry after the same-state weighting is applied.

Then

$$
f_i' = f_i + (1-f_i)\sum_j M_{ij}q_j.
$$

When the same-state weight equals 1,

$$
q_j=f_j.
$$

This makes the role of community endogamy explicit: ancestry can enter a new community only through a cross-community mating pathway.

## Structural result

At perfect endogamy, if founder ancestry begins in only one community, other communities are unreachable.

Below perfect endogamy, spread is possible but can be arbitrarily slow over a finite historical interval as endogamy approaches 1.

This differs from a geographic model mainly in interpretation. The barrier is social rather than spatial.

## Why timing still matters

A high-endogamy community that occasionally accepts cross-community marriages is not equivalent to a perfectly isolated community.

One successful cross-community genealogical connection can seed ancestry inside the group, after which within-community reproduction can propagate it.

The probability and timing of that first bridge therefore matter.

## What this model does not establish

It does not estimate historical endogamy rates for any named population.

It does not assume that genealogical ancestry is visible to mates.

It does not yet model named pedigrees, sex-specific marriage rules, cousin marriage, caste hierarchies, clan rules, conversion, adoption, or changing social identities.

Those can be added later as historically constrained scenarios.
