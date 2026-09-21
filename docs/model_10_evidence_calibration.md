# Model 10: evidence-calibrated uncertainty envelopes

## Purpose

Model 09 showed that the proposed ~11,000-year founder scenario depends on time-dependent reproductive connectivity. Model 10 asks a stricter question:

**Which inputs are numerically supported by published evidence, and which decisive inputs remain unknown?**

The main output is therefore a **required post-contact mixing threshold**, not a posterior probability that the historical scenario occurred.

A machine-readable evidence ledger is stored in `data/model10_evidence.json`.

## Evidence classes

Model 10 distinguishes:

1. **Debate assumption**: for example, an ~11 ka founder date.
2. **Direct quantitative evidence**: a reported numerical estimate or interval.
3. **Published scenario-model output**: numerical outputs explored in a paper without posterior probabilities over them.
4. **Historical date**: a documented chronological marker.
5. **Qualitative constraint**: evidence that changes model structure but does not justify a single numerical rate.
6. **Unconstrained parameter**: a quantity for which the reviewed literature does not provide a defensible numerical estimate.

A central rule is that category 6 must not silently be turned into category 2.

## Generation interval

Moorjani et al. (2016) estimated a mean human generation interval of approximately **26-30 years** over the last 45,000 years. Wang et al. (2023) independently estimated an average of **26.9 years** across the past 250,000 years, with variation through time and among populations.

Model 10 therefore uses 26-30 years as its default propagation envelope. An 11,000-year founder date then corresponds to approximately **367-423 generations**, rather than the pedagogical 440 generations obtained with 25 years per generation.

## Tasmania isolation chronology

Fuller et al. (2023), using a sea-level synthesis, place the last continuous Bassian land bridge in a bracket of approximately **11,960-12,890 years BP**.

For a founder appearing outside Tasmania at 11 ka, this entire direct-evidence bracket places geographic closure **before** founder insertion. The proposed founder date is about 960-1,890 years later, approximately **32-73 generations after closure** under the 26-30 year interval.

Thus the default direct-evidence envelope contains **zero pre-closure generations**.

Broader historical estimates can still be explored as sensitivity analyses, but they are not mixed into this direct bracket without labeling the change.

## Contact chronology

Byard and Maxwell-Stewart (2024) report sealing crews occupying offshore islands from **1797** and official British settlement beginning in **1803**.

Using 1797 as the default earliest sustained-contact marker gives 229 years to 2026, or approximately **8-9 generations** under the evidence-calibrated generation interval. The notebook exposes 1803 as an alternative.

## Contact-era population size

Byard and Maxwell-Stewart (2024) report nine pre-contact population outputs in their Table 6:

- Model 1: 3,848; 4,232; 4,616
- Model 2: 6,789; 7,465; 8,144
- Model 3: 10,093; 11,099; 12,106

Model 10 stores these as a **published model set**. Equal weighting of these nine values in the uncertainty-envelope sampler is a Model 10 propagation convention, not a posterior distribution supplied by the paper.

The same paper reports a documented minimum of **311 palawa people in January 1831** and explores undercount adjustments including 342 and 373. Those values are used only for demographic-collapse sensitivity.

## The decisive parameter that remains missing

Let `m` be the probability that a parental draw inside the formerly isolated population comes from an external population already descended from the proposed founders.

The reviewed sources do **not** provide a defensible Tasmania-specific per-generation estimate of `m`.

Contact, migration, settlement, violence, abduction, intermarriage, and genomic admixture are not interchangeable measurements. Model 10 therefore does not invent an empirical prior for `m`.

Instead, it asks what value of `m` would be required.

## Best-case late-contact model

The calculation intentionally favors the founder scenario:

1. the formerly isolated population begins with zero founder ancestry;
2. the external parent pool is already 100% descended from both founders;
3. each parental draw is external with probability `m`;
4. otherwise the parent is drawn locally.

If `f_t` is the local descendant fraction,

```math
f_{t+1}=1-[(1-m)(1-f_t)]^2.
```

With `f_0=0`,

```math
1-f_g=(1-m)^{2(2^g-1)}.
```

To approximate complete fixation in a population of size `N`, Model 10 also uses

```math
P(\mathrm{all\ descended})\approx f_g^N.
```

This independence approximation is not exact because pedigree states are correlated, so the repository includes finite-population Monte Carlo validation.

## Required rate thresholds

Across the nine published population-model outputs:

| Post-contact generations | Target complete-fixation probability | Approximate required external-parent rate |
| ---: | ---: | ---: |
| 8 | 50% | 1.68-1.90% per parental draw |
| 8 | 95% | 2.18-2.40% |
| 9 | 50% | 0.84-0.95% |
| 9 | 95% | 1.09-1.20% |

Monte Carlo validation gives similar 50% thresholds and slightly higher 95% thresholds.

These are **required-rate calculations**, not claims that historical rates actually had these values.

## Evidence-envelope propagation

`sample_evidence_envelope` propagates:

- generation interval uniformly within 26-30 years;
- isolation age uniformly within 11,960-12,890 BP;
- population size by sampling the nine published model outputs;
- a fixed 11 ka debate founder date;
- the default 1797 contact date.

Uniform sampling and equal scenario weights are explicitly **propagation conventions**, not source-paper posterior distributions.

Under this envelope:

- founder depth is approximately 367-423 generations;
- the late-contact window is 8-9 generations;
- the pre-closure window is always zero;
- the required-rate distribution is strongly bimodal because the difference between 8 and 9 generations matters more than the population-size variation.

## Demographic-collapse sensitivity

A toy comparison uses:

- constant `N=7,465` for eight generations;
- `N=7,465` at contact followed by `N=342` from the next generation onward.

The severe bottleneck can substantially increase fixation probability at the same external-parent rate. This is **sensitivity only**. Historical population decline was not random with respect to ancestry, movement, survival, or reproduction, and 342 is not a complete count of all descendants.

## Wider structural evidence

Australian genomic studies report deep regional structure and limited Holocene gene flow, arguing against a panmictic Holocene Australia. Ancient-genomic reviews of the Americas likewise describe a history of isolation, admixture, continuity, and replacement rather than one constant migration rate.

These findings constrain model structure but do not provide a single per-generation parental-source rate suitable for Model 10.

## What Model 10 establishes

It can identify:

- the chronology supported by the direct evidence envelope;
- the implied number of generations;
- how published population-size uncertainty changes the required mixing threshold;
- how severe demographic collapse changes the threshold in a toy model;
- which inputs are measured and which remain assumptions.

It **cannot** provide a posterior probability that the proposed founders became universal ancestors. The critical Tasmania-specific reproductive-mixing rate is not directly estimated by the reviewed evidence.

## References

- Moorjani P, et al. (2016). *PNAS* 113:5652-5657. DOI: 10.1073/pnas.1514696113.
- Wang RJ, et al. (2023). *Science Advances* 9:eabm7047. DOI: 10.1126/sciadv.abm7047.
- Fuller RS, et al. (2023). *Journal of Archaeological Science*, 105819. DOI: 10.1016/j.jas.2023.105819.
- Byard R, Maxwell-Stewart H. (2024). *Asia-Pacific Economic History Review* 64:72-93. DOI: 10.1111/aehr.12282.
- Malaspinas AS, et al. (2016). *Nature* 538:207-214. DOI: 10.1038/nature18299.
- Tobler R, et al. (2017). *Nature* 544:180-184. DOI: 10.1038/nature21416.
- Silcocks M, et al. (2023). *Nature*. DOI: 10.1038/s41586-023-06831-w.
- Willerslev E, Meltzer DJ. (2021). *Nature* 594:356-364. DOI: 10.1038/s41586-021-03499-y.
