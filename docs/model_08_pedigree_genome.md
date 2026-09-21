# Model 08: integrated pedigree and autosomal founder DNA

## Question

Can a founder, or a founder pair, become genealogical ancestors of everyone in a finite population while some descendants carry no autosomal DNA from them?

Model 08 answers that question inside one simulation instead of combining separate genealogical and genetic approximations.

It jointly tracks:

- genealogy from each founder;
- explicit autosomal founder-derived chromosome segments;
- whether each person carries any founder DNA;
- whether each person carries a segment above an illustrative detection threshold.

## Founder-set genealogy

Generation 0 contains a finite population of size N and a designated founder set.

Pedigree ancestry is tracked separately for each founder with a bit mask.

For two founders, an individual can therefore be:

- descended from neither founder;
- descended from founder 1 only;
- descended from founder 2 only;
- descended from both founders.

The **all-founders descendant fraction** is the fraction of the population descended from every member of the founder set.

The **all-founders universal generation** is the first generation in which every person is descended from every founder.

This is deliberately stronger than merely being descended from at least one founder.

## Genetic ancestry

All autosomal DNA initially carried by the founder set is tagged collectively.

Each generation:

1. every child chooses two distinct parents uniformly from the preceding generation;
2. each parent produces one recombinant gamete;
3. crossovers follow a Poisson process in genetic-map distance;
4. tagged intervals are transmitted according to the recombinant chromosome;
5. the child receives one homolog from each parent.

The default map is the same transparent Model 07 approximation:

- 22 autosomes;
- total haploid map length of 33 Morgans;
- equal genetic-map length assigned to each simulated autosome.

This is not a chromosome-specific human recombination map.

## Collective founder tag

Genetic segments are tagged as **founder-set DNA**, not by the identity of the particular founder.

For a two-founder run:

- genetic carrier means the person carries DNA from at least one of the two founders;
- detectable carrier means at least one founder-set segment exceeds the chosen threshold.

The simulation does not currently require a person to carry DNA from both founders.

Genealogy, however, is tracked separately and can require descent from both founders.

## Joint categories

Each generation is partitioned into four categories:

1. not yet descended from all founders;
2. descended from all founders but carrying no founder-set autosomal DNA;
3. descended from all founders and carrying founder DNA, but no segment above the detection threshold;
4. descended from all founders and carrying at least one segment above the threshold.

These four fractions sum to one.

They let the model show directly that universal genealogy and universal genetic contribution are different events.

## What changes relative to Model 07

Model 07 followed one specified ancestor-descendant path.

Along one path, the expected fraction inherited from one ancestor is 2^-k, and the probability of inheriting any DNA eventually becomes small.

Model 08 allows the founder to reach the same present person through **multiple pedigree paths**.

That changes the problem substantially.

A founder's DNA can enter a descendant through any of those paths. Once founder ancestry has spread through the population, genetic material can be redistributed among many people rather than simply shrinking along one isolated line.

Therefore the single-path 2^-k intuition cannot be applied directly to a population after pedigree collapse.

## Population mean founder-DNA fraction

Under neutral Mendelian transmission, the ensemble expectation of the population-wide founder-DNA fraction is conserved from one generation to the next.

For F fully tagged founders introduced into a population of size N, the initial mean fraction is

$$
\frac{F}{N}.
$$

A finite stochastic realization can drift above or below that value and founder DNA can ultimately be lost or can fix at particular loci.

The key point is that this population-level quantity is not the same as the 2^-k expectation along one specified genealogical path.

## Representative behavior

The README uses one explicitly labeled stochastic example:

- N = 500;
- two founders;
- 30 generations;
- 6 cM illustrative threshold;
- distinct parents;
- seed = 3.

In that realization, both founders become genealogical ancestors of everyone before the end of the run.

At and after that point, the population can contain a mixture of:

- universal genealogical descendants carrying no founder DNA;
- universal descendants carrying only sub-threshold founder segments;
- universal descendants carrying detectable founder segments.

The exact percentages are seed-specific and are not historical estimates.

## Ghost ancestors

A designated founder becomes a population-level ghost in this model if:

1. the founder is genealogically universal; and
2. no member of the present population carries any tagged autosomal DNA from that founder set.

For a multi-founder set, the current implementation detects complete loss of DNA from the collective founder set after all founders have become universal.

This event is possible but is not guaranteed for a particular founder or pair.

Gravel and Steel (2015) proved a stronger population-level existence result under standard biparental population and recombination models: sufficiently far in the past, there can be individuals who are genealogical ancestors of everyone present but genetic ancestors of nobody present.

Model 08 should not be read as claiming that every genealogically universal ancestor becomes a ghost.

## Founder-lineage survival

With finite random reproduction, a founder's genealogical lineage can disappear by chance before becoming universal.

For two independently introduced founders, one lineage can survive while the other disappears.

The notebook therefore reports:

- ancestry from at least one founder;
- ancestry from all founders;
- the probability across replicates that all founders become universal.

A historically specified founder couple with known joint offspring would require an additional initial-family assumption. Model 08 does not silently impose that assumption.

## Detection threshold

The default README example uses 6 cM only as an illustrative threshold.

This is not a universal consumer-DNA cutoff.

Practical detectability depends on marker density, phasing, reference panels, algorithms, error filters, and the distinction between identity by descent and chance matching.

The model therefore keeps:

- any positive-length founder DNA;
- DNA above a user-chosen cM threshold;

as separate quantities.

## What this model does not establish

It does not show that any proposed historical founder pair existed.

It does not simulate 11,000 years of realistic human demography.

It assumes a constant-size panmictic population with no geography, migration, endogamy, age structure, sex-specific recombination, selection, or realistic fertility distribution.

It does not distinguish the DNA of founder 1 from founder 2 after tagging the founder set.

It does not yet combine the integrated pedigree-genome engine with the structured migration and endogamy models.

Those are the next requirements for historically constrained scenarios.

## References

Agranat-Tamir, L., Mooney, J. A., & Rosenberg, N. A. (2024). Counting the genetic ancestors from source populations in members of an admixed population. *Genetics*, 226(4), iyae011. https://doi.org/10.1093/genetics/iyae011

Gravel, S., & Steel, M. (2015). The existence and abundance of ghost ancestors in biparental populations. *Theoretical Population Biology*, 101, 47-53. https://doi.org/10.1016/j.tpb.2015.02.002

Kong, A., Thorleifsson, G., Gudbjartsson, D. F., et al. (2010). Fine-scale recombination rate differences between sexes, populations and individuals. *Nature*, 467, 1099-1103. https://doi.org/10.1038/nature09525
