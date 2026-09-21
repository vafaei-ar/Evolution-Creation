# Model 09: historically constrained founder scenarios

## Target claim from the debate

The debate proposes a specific compatibility scenario rather than a standard population-genetic origin model:

- Adam and Eve appear approximately 11,000 years ago;
- the proposed location is broadly West Asia / the Middle East;
- pre-existing human populations already exist;
- descendants of the pair later intermarry with those populations;
- over enough generations, the pair could become genealogical ancestors of all living humans;
- genetic ancestry and genealogical ancestry are not required to remain identical.

The debate also explicitly raises Australia, the Americas, endogamous groups, and Tasmania as tests of the claim. Tasmania is acknowledged in the discussion as a case of complete historical isolation.

Model 09 turns that verbal argument into a time-dependent reproductive-connectivity problem.

## External empirical constraints

These are not outputs of the model.

### Sahul was occupied long before 11 ka

Genomic and archaeological work places the peopling of Sahul tens of thousands of years before the proposed founder date. Malaspinas et al. (2016) summarized settlement estimates around 47.5-55 ka, while later work has considered still earlier arrival scenarios.

Therefore an 11 ka founder scenario cannot treat Sahul as an empty region waiting to be colonized by descendants of the proposed pair. Founder ancestry must enter an already occupied population through later reproductive connections.

### The Americas were occupied before 11 ka

Ancient-genomic and archaeological syntheses place human history in the Americas at least around 15 ka and probably earlier.

Again, the relevant question is not first settlement. It is whether a reproductive path after 11 ka can carry founder ancestry into already established populations.

### Tasmania is the strongest chronological constraint

A 2015 review describes Aboriginal Tasmanians as having been separated from mainland Australia for about 12,000 years.

A 2023 Journal of Archaeological Science analysis estimates final submergence of the Bassian land bridge at approximately 11,960 years BP, while also reviewing older estimates that range roughly from 10,000 to 13,500 years BP depending on the criterion used.

That uncertainty matters.

If geographic isolation was already complete before the proposed 11 ka founders appeared outside Tasmania, then no pre-contact reproductive path exists into Tasmania.

If isolation happened after the founder date, then there is a finite pre-closure window during which founder ancestry could in principle enter.

Model 09 therefore makes the isolation date a parameter instead of selecting one convenient chronology.

### Later contact

Permanent British settlement in Tasmania began in 1803.

Using 2026 as the endpoint and 25 years per generation gives approximately nine generations between 1803 and the present.

Contact is not the same as random mating or a known migration rate. Model 09 uses that interval only as a time constraint and leaves the parental-source mixing probability as a sensitivity parameter.

## Time conversion

For the debate default,

```math
G = \frac{11000}{25} \approx 440
```

generations.

The generation interval is adjustable.

## Region network

The default pedagogical network contains:

1. West Asia;
2. Africa;
3. South/East Asia;
4. Sahul;
5. Tasmania;
6. the Americas.

The model is deliberately coarse.

The non-Tasmanian bridge rates are **not empirical Holocene migration estimates**. They are user-controlled sensitivity parameters.

A row of the parent-source matrix describes where the two parents of a child born in that region may come from.

A zero entry is a hard reproductive barrier.

A positive entry is only a possible reproductive path. It does not guarantee that a founder lineage successfully crosses in a finite stochastic population.

## Founder couple assumption

The pair is tracked as two distinct founders.

The model distinguishes:

- descent from at least one founder;
- descent from founder A;
- descent from founder B;
- descent from both founders.

The first generation can force a chosen number of joint children of the pair.

This is important because a model that treats Adam and Eve as two unrelated randomly mating individuals adds an unnecessary lineage-extinction assumption.

The default is two joint children, but the notebook exposes 0, 1, 2, or more.

## Deterministic two-founder recursion

For smooth sensitivity analysis, each region carries a probability distribution over four pedigree states:

- 00: descended from neither founder;
- 01: descended from founder A only;
- 10: descended from founder B only;
- 11: descended from both.

The parental state distribution for children in region i is the parent-source weighted mixture of all source regions.

If two parental states are a and b, the child's founder state is

```text
a OR b
```

in the founder bit mask.

This gives an exact infinite-population recursion for the stated parent-source probabilities.

## Finite stochastic simulation

The individual-based version explicitly samples:

- parent-source region;
- parent identity;
- the two-parent pedigree;
- founder-specific ancestry.

A founder lineage can therefore disappear by chance even when the deterministic fraction is positive.

Population sizes in these simulations are computational / effective sizes. They are not claimed to be regional census estimates.

## Hard-barrier result

If a region already contains a surviving population and there is no reproductive path from any founder-descended region into it, then founder ancestry in that region remains exactly zero.

This is a graph-connectivity statement, not a probabilistic estimate.

A hard barrier blocks both genealogical ancestry and founder DNA.

## Late-contact best-case model

Suppose a region has remained completely isolated and contains zero founder ancestry.

Then suppose the barrier reopens for g generations.

For an intentionally favorable upper-bound calculation, assume the external parent pool is already 100% descended from both founders.

Let m be the probability that each parental draw comes from that external pool and f_t the founder-descendant fraction within the formerly isolated population.

Then

```math
f_{t+1}
=
1-
\left[
(1-m)(1-f_t)
\right]^2.
```

This is a best-case conditional model because every external parent is assumed to carry the required genealogy.

With nine generations, the result is highly sensitive to m.

In a finite deme of N=100, 5,000 Monte Carlo replicates with seed 20260920 give approximately:

| External-parent probability | Mean final descendant fraction | Probability of complete fixation |
| ---: | ---: | ---: |
| 0.1% | 0.350 | 0.056 |
| 0.2% | 0.568 | 0.132 |
| 0.5% | 0.879 | 0.415 |
| 1.0% | 0.985 | 0.792 |
| 2.0% | 1.000 | 0.986 |

These are sensitivity values, not historical estimates.

## Endogamy

The scenario includes an endogamy-strength parameter from 0 to 1.

It scales all cross-region parent-source probabilities toward zero.

This is a deliberately simple abstraction. Real social endogamy can be asymmetric, group-specific, time-dependent, and unrelated to geographic distance.

## Demographic shocks

The helper `apply_region_bottleneck` changes the effective simulation population of one region over a chosen generation window.

It allows sensitivity tests for population contraction without pretending to reconstruct a particular historical event.

## Integrated chromosome diagnostic

Model 09 also exposes `simulate_historical_pedigree_genome`.

It applies the same time-varying parent-source matrices to:

- founder-specific genealogy;
- explicit tagged autosomal chromosome segments;
- any surviving founder DNA;
- a chosen cM detection threshold.

The complete 440-generation chromosome simulation can be computationally expensive, so the notebook uses it as an optional diagnostic with smaller effective population sizes.

The barrier logic is unchanged:

- if no reproductive path exists, neither genealogy nor founder DNA can enter;
- if a path opens, genealogy and DNA can both enter, but later recombination means their population distributions need not remain identical.

## What Model 09 can establish

It can establish conditional statements such as:

- under a hard barrier that predates founder insertion and remains closed, universal genealogy is impossible;
- if the barrier reopens, the result depends on the remaining generations and the effective parental-source mixing probability;
- if geographic closure happens after founder insertion, a pre-closure seeding window exists;
- higher endogamy reduces effective connectivity;
- a founder pair can be modeled as a pair rather than two independent lineages.

## What Model 09 cannot establish

It does not estimate an actual Holocene migration matrix.

It does not establish that Adam and Eve existed.

It does not infer a historical mixing rate for Tasmania, Australia, or the Americas.

It does not convert contact into mating automatically.

It does not model colonial violence, forced movement, sex-biased admixture, mortality, fertility differences, or population replacement.

It does not make a theological conclusion.

The correct interpretation remains:

**conditional compatibility under specified reproductive-connectivity assumptions.**

## References

Bowdler, S. (2015). The Bass Strait Islands revisited. *Quaternary International*, 385, 206-218. https://doi.org/10.1016/j.quaint.2014.07.047

Fuller, R. S., et al. (2023). The archaeology of orality: Dating Tasmanian Aboriginal oral traditions to the Late Pleistocene. *Journal of Archaeological Science*, 105819. https://doi.org/10.1016/j.jas.2023.105819

Malaspinas, A.-S., et al. (2016). A genomic history of Aboriginal Australia. *Nature*, 538, 207-214. https://doi.org/10.1038/nature18299

Willerslev, E., & Meltzer, D. J. (2021). Peopling of the Americas as inferred from ancient genomics. *Nature*, 594, 356-364. https://doi.org/10.1038/s41586-021-03499-y

National Museum of Australia. Separation of Tasmania; The Black Line. Permanent British settlement in Van Diemen's Land began in 1803.

Rohde, D. L. T., Olson, S., & Chang, J. T. (2004). Modelling the recent common ancestry of all living humans. *Nature*, 431, 562-566. https://doi.org/10.1038/nature02842
