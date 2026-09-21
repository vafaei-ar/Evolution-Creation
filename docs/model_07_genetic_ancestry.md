# Model 07: genealogical ancestry versus autosomal genetic ancestry

## Question

Can a person be a genuine genealogical ancestor while leaving no autosomal DNA in a particular descendant?

Yes. Genealogical ancestry records parent-child paths. Genetic ancestry records the subset of those paths through which chromosomal material was actually transmitted.

Model 07 makes that distinction quantitative.

## Published autosomal-fragment approximation

Agranat-Tamir, Mooney, and Rosenberg (2024), following an approximation attributed to Coop (2013), model the number of autosomal fragments inherited from a specific genealogical ancestor k generations back as approximately Poisson distributed.

For humans, their approximation uses 22 autosome pairs and about 33 crossover breakpoints added across a haploid autosomal genome per generation after the first.

For k >= 2,

$$
\lambda_k=\frac{22+33(k-1)}{2^{k-1}}.
$$

If the fragment count is Poisson with mean lambda_k, then the probability that a genealogical ancestor contributes at least one autosomal fragment is

$$
p_k=1-e^{-\lambda_k}.
$$

For a parent, p_1 = 1.

The published examples are useful checks on the implementation:

- p_8 = 0.8615;
- p_16 = 0.0157.

So a genealogical ancestor can be certain in the pedigree while being unlikely to contribute autosomal DNA after enough generations.

## Expected DNA fraction is a different quantity

Along one specified genealogical path, the expected fraction of the descendant's diploid autosomal genome inherited from the focal ancestor is

$$
E[F_k]=2^{-k}.
$$

This does not mean every ancestor contributes exactly that fraction.

The distribution becomes highly variable. Many ancestors contribute zero DNA, while the subset that do contribute can transmit one or more surviving segments.

## Why a gene-count argument is misleading

Genes are not independent inheritance units.

Meiosis transmits long linked chromosome segments. Recombination breaks and rearranges those segments, but neighboring loci can travel together for many generations.

Therefore a calculation based on a fixed count such as "20,000 genes divided by 2^k" does not represent the inheritance process correctly.

Model 07 tracks continuous chromosome segments in genetic-map units instead.

## Explicit segment simulation

The default simulator uses a deliberately transparent approximation:

- 22 autosomes;
- total haploid map length of 33 Morgans;
- the 33 Morgans are divided equally among the 22 simulated autosomes;
- crossover events on each chromosome follow a Poisson process in genetic-map distance;
- the focal ancestor is followed down one specified genealogical path;
- in each later generation, the lineage-carrying individual mates with a partner carrying no DNA from the focal ancestor;
- the child receives one recombinant gamete from the lineage-carrying parent.

Generation 1 therefore receives one complete haploid genome from the focal ancestor. In later generations, founder-derived intervals are broken up and can be lost entirely.

The equal-length chromosome map is not intended as a high-resolution human recombination map. It is chosen to keep the simulation auditable while matching the total crossover burden in the analytic approximation.

Real recombination rates vary by genomic location, sex, population, and individual. Kong et al. (2010) directly documented such variation in human pedigree data.

## Genetic ancestry versus detectable ancestry

Model 07 separates two events:

1. the descendant carries any positive-length autosomal segment from the ancestor;
2. the descendant carries at least one segment longer than a chosen detection threshold.

The threshold is specified in centimorgans.

A threshold such as 6 cM is only an illustrative computational rule. It is not claimed to be a universal consumer-DNA detection cutoff, because practical detection depends on marker density, phasing, algorithms, reference data, and false-positive filtering.

Consequently,

$$
P(\text{detectable}) \leq P(\text{any inherited DNA}).
$$

## Genealogical ancestors grow much faster than genetic ancestors

Ignoring pedigree collapse, generation k contains 2^k genealogical pedigree slots.

The expected number of those slots that correspond to genetic ancestors is

$$
2^k p_k.
$$

As k becomes large, p_k becomes small enough that the expected genetic-ancestor count grows only approximately linearly while the number of genealogical slots continues to grow exponentially.

This is the core reason the genetic pedigree becomes a small subset of the genealogical pedigree.

## Important multipath caveat

The explicit segment simulator follows **one genealogical path** from the focal ancestor to the descendant.

A distant ancestor in a real pedigree can appear through multiple paths because of pedigree collapse and repeated descent.

Multiple paths can increase the probability that some DNA from that ancestor survives. Those paths are not independent because they can share meioses and chromosome segments.

Therefore the single-path probability p_k must not be naively interpreted as the probability that a historically distant universal genealogical ancestor contributes no DNA to a present person.

A population-scale pedigree-plus-genome model is needed for that question.

## Ghost ancestors

The distinction remains important even at population scale. Gravel and Steel (2015) proved, under standard biparental population and recombination models, that "ghost" ancestors can exist: individuals who are genealogical ancestors of all present-day individuals but genetic ancestors of none of them.

Model 07 does not reproduce their full population-level result. It provides the chromosome-level mechanism that makes such a result possible.

## What this model does not establish

It does not show that any proposed historical ancestor existed.

It does not infer the genetic contribution of a proposed 11,000-year-old ancestor from the single-path curve.

It does not use a sex-specific or chromosome-specific contemporary recombination map.

It does not yet combine the Model 06 population pedigree with chromosomal inheritance across every pedigree path.

That combined population-scale question is the natural next model.

## References

Agranat-Tamir, L., Mooney, J. A., & Rosenberg, N. A. (2024). Counting the genetic ancestors from source populations in members of an admixed population. *Genetics*, 226(4), iyae011. https://doi.org/10.1093/genetics/iyae011

Gravel, S., & Steel, M. (2015). The existence and abundance of ghost ancestors in biparental populations. *Theoretical Population Biology*, 101, 47-53. https://doi.org/10.1016/j.tpb.2015.02.002

Kong, A., Thorleifsson, G., Gudbjartsson, D. F., et al. (2010). Fine-scale recombination rate differences between sexes, populations and individuals. *Nature*, 467, 1099-1103. https://doi.org/10.1038/nature09525
