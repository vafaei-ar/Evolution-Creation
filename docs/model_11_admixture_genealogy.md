# Model 11: genetic admixture versus genealogical spread

## Claim from the debate

The debate repeatedly contrasts genetic ancestry with genealogical ancestry. One
version of the disagreement is whether low or absent detectable European genetic
admixture in an Indigenous population rules out a European genealogical ancestor,
or more generally whether a small genetic contribution implies that only a small
fraction of the population can be genealogical descendants.

## What the model tests

Model 11 separates two quantities:

- **mean source-DNA proportion**, which follows Mendelian averaging;
- **genealogical descendant status**, which is inherited if either parent is a
  descendant.

For constant external parental input at rate `m`, expected genetic ancestry obeys

```math
A_{t+1}=m+(1-m)A_t.
```

Genealogical descendant fraction obeys

```math
f_{t+1}=1-[(1-m)(1-f_t)]^2.
```

The second process can approach one far faster than the first.

## Pulse example

Suppose one generation receives a source contribution whose expected genetic
ancestry is 1%, followed by random mating and no additional source input.

The expected population mean source-DNA fraction remains about 1% under neutral
inheritance. Genealogical descent, however, spreads because descendants mate with
non-descendants.

After ten generations the deterministic descendant fraction exceeds 99.99%.
For a population of 1,000, an independence approximation gives a high probability
that everyone is a genealogical descendant; the notebook also performs finite
Monte Carlo simulation because real pedigree states are correlated.

## Empirical interpretation

Published genomic studies of post-contact populations show that genetic admixture
can be estimated from ancestry tracts and that its timing is often only several to
dozens of generations old. Examples include South American colonial admixture
events dated roughly 9-14 generations ago and ancient Rapanui genomes carrying
about 10% Native American ancestry from a pre-European-contact event dated to
approximately 1250-1430 CE.

These examples calibrate the *type* of information genomic admixture studies can
provide. They do not estimate the Tasmania-specific parameter required by Models
09-10.

## Judgment on the claim

**The claim that genetic percentage and genealogical descendant fraction are the
same is rejected.** A small source-DNA percentage can coexist with near-universal
genealogical descent after enough random mating.

However, the reverse overstatement is also rejected: observing little or no
aggregate genetic admixture does not automatically prove that an outside
genealogical ancestor existed. A historically specified claim still requires a
reproductive path, timing, and a demographic model.

### What must be corrected

To use genomic admixture as evidence about a proposed ancestor:

1. distinguish individual genealogical ancestry from population mean DNA ancestry;
2. infer an admixture history rather than equating a present percentage with a
   per-generation parentage rate;
3. propagate uncertainty in pulse timing and continuous gene flow;
4. avoid using one population's admixture estimate as another population's rate.

## References

- Homburger et al. / related South American genomic work summarized in
  *Genomic Insights into the Ancestry and Demographic History of South America*,
  PLOS Genetics (2015), DOI 10.1371/journal.pgen.1005602.
- Moreno-Mayar et al. / Rapanui ancient genomes: *Ancient Rapanui genomes reveal
  resilience and pre-European contact with the Americas*, Nature (2024),
  DOI 10.1038/s41586-024-07881-4.
- Rasmussen et al. (2011), *An Aboriginal Australian genome reveals separate
  human dispersals into Asia*, Science, DOI 10.1126/science.1211177.
