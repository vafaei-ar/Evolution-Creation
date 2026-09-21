# Model 13: population-genetic detectability of a specially inserted pair

## Claim from the debate

A proposed Adam-and-Eve pair could appear within an already existing human
population around 11 ka and later become genealogical ancestors without modern
genetics necessarily identifying them as a distinct founding population.

## Question

When is that statement scientifically plausible?

Model 13 separates two cases:

1. **genetically ordinary insertion**: the pair is drawn from the same genetic
   distribution as surrounding humans and has no uniquely identifying marker;
2. **genetically distinctive insertion**: the pair carries private neutral
   variants absent from the surrounding population.

The first case is unidentifiable by genetics by construction. The second is a
population-genetic question.

## Wright-Fisher marker model

For each private autosomal marker, the model begins with a chosen number of
copies in a diploid population and propagates it neutrally for hundreds of
generations.

The default example uses:

- effective population size: 10,000;
- 400 generations;
- two starting copies of a private marker;
- a present-day sample of 1,000 diploid individuals.

This effective population size is an illustrative sensitivity value, not a
reconstruction of the entire human census population.

With these settings, a single neutral private marker is usually lost. Across
large Monte Carlo runs, survival after 400 generations is on the order of one
percent.

If a surviving marker reaches around percent-level frequency, a modern sample of
1,000 diploid individuals would detect it with high probability.

## Many private markers

A genetically unusual pair would not be represented by one independent variant.
If `p` is the per-marker probability that a distinctive marker survives and is
sampled, an independent-marker approximation gives

```math
P(\mathrm{detect\ at\ least\ one})=1-(1-p)^K,
```

where `K` is the number of distinctive markers.

Linkage means real markers are not independent, so this is a sensitivity
calculation rather than a genome-wide likelihood.

For a per-marker detection probability near 1%:

- 1 marker: ~1% chance of detection;
- 10 markers: ~9%;
- 100 markers: ~63%;
- 500 markers: >99%.

## Genealogy versus marker survival

A pair can become genealogically widespread while a particular private allele
is lost. These processes are not contradictory.

Conversely, genealogical universality does not imply that a highly distinctive
founder genome becomes invisible. A large set of unusual variants is much harder
to erase than one rare marker.

## Judgment on the claim

**The weak claim is supported: genetics need not detect a specially inserted pair.**
If the pair was genetically similar to the surrounding population, there may be
no unique signature to detect. If only a few neutral private variants distinguish
them, most such variants can be lost by drift over ~400 generations.

**The strong claim "genetics could never detect them" is not supported.** A pair
with many unusual private variants would have many opportunities to leave a
detectable signal. Under the model's illustrative one-percent per-marker
detection probability, 100 independent distinctive markers already give roughly
a 63% chance that at least one is detected, and 500 exceed 99%.

### What must be specified

A scientifically testable insertion claim must state:

- how genetically different the pair is from contemporaneous humans;
- effective population size and structure;
- reproductive success;
- whether distinctive variants are neutral or selected;
- the sampling scheme and what qualifies as detection.

Without a predicted genetic difference, "no genetic evidence" is not a test of
the event.

## References

- Gravel & Steel (2015), *The existence and abundance of ghost ancestors in
  biparental populations*, Theoretical Population Biology.
- Standard neutral Wright-Fisher population-genetic inheritance.
- Human effective population size is time-varying and structured; 10,000 is
  used only as an illustrative order-of-magnitude sensitivity value.
