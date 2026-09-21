# Interactive continental founder-spread explorer

## Purpose

This explorer is a synthesis of Models 02-05 and 07-11. It is not Model 16.

It lets a user vary founder timing, macroregional population sizes, reproductive
migration, within-region mixing/endogamy, recent contact, and a Tasmania-specific
hard barrier, then compare deterministic and finite-population stochastic outcomes.

The scientific question is conditional:

> Under these explicit assumptions, what fraction of each region becomes
> descended from Adam, Eve, or both, and how often does stochastic finite-
> population reproduction change that outcome?

It does not estimate the posterior probability that Adam and Eve existed.

## Seven modeled regions

The engine uses:

1. Middle East;
2. Africa;
3. Europe;
4. Asia;
5. Americas;
6. Australia/Oceania;
7. Tasmania.

Tasmania is separated from Australia/Oceania because the debate explicitly uses
Tasmanian isolation as a stress test of a recent universal-genealogy claim.

## Population defaults

The continental start values are coarse historical teaching presets derived from
a regional reconstruction around 9000 BCE. The notebook also stores 1000-year
anchors and can log-interpolate start populations to the selected founder date.

Tasmania is different. The repository does not contain a defensible Tasmania-
specific population estimate for 11 ka. Its default start value is therefore
explicitly marked as a **teaching placeholder**, using 7,465 because that is the
middle early-contact population model stored in Model 10. It must not be read as
a 9000 BCE census or estimate.

Every population value is editable.

## Parent-source migration matrix

The migration control is a **parent-source matrix**. For a child born in
destination region i, entry M[i,j] is the probability that one parental draw
comes from source region j.

This is more precise than saying "migration rate" because genealogy spreads
through reproduction, not physical movement alone.

The supplied matrix is a sensitivity preset. It is not claimed to be an
empirically estimated Holocene migration matrix.

## Mixing/endogamy

Each region has a mixing parameter q in [0,1].

- q = 0 preserves pooled pedigree-state frequencies without additional random-
  mating diffusion.
- q = 1 applies full random mating within the pooled regional parental state.
- intermediate values interpolate between them.

This is a compact teaching parameter, not a measured biological constant.

## Tasmania hard barrier

The Australia/Oceania-Tasmania edge can be made a true zero-reproduction
barrier until a selected release time.

The default structural chronology reflects Model 10:

- final continuous Bassian land bridge before the 11 ka founder date;
- barrier remains closed through most of the simulation;
- default release uses 1797-to-2026, about 229 years, as an earliest sustained-
  contact sensitivity marker.

The **post-release parent-source rate is still a user-selected sensitivity
parameter**. The chronology does not supply that rate.

A permanent-barrier toggle is included. Under a permanent hard barrier, founder
ancestry outside Tasmania cannot enter Tasmania at any later generation.

## Four pedigree states

The deterministic and stochastic models track:

- neither founder;
- Adam only;
- Eve only;
- both founders.

At insertion, Adam and Eve enter as distinct individuals. A user-selected number
of first-generation joint children can seed the both-founder state explicitly.

This avoids the unrealistic requirement that two newly inserted individuals in
a large population happen to find one another by random mating.

## Mean autosomal founder ancestry

The genetic layer tracks the expected mean autosomal ancestry contributed by the
pair.

Migration changes the regional mean. Random mating can spread **genealogical
descendant status** rapidly without increasing the population mean founder-DNA
fraction.

The map can therefore switch between:

- either-founder genealogy;
- both-founder genealogy;
- mean founder-pair autosomal ancestry.

## Deterministic mode

Deterministic mode follows expected state fractions. It is fast and useful for
understanding parameter sensitivity and barrier topology.

A deterministic success establishes compatibility under the chosen parameters.
It does not tell the user how often finite-population lineage loss would occur.

## Monte Carlo mode

Monte Carlo mode samples the four pedigree-state counts in every region every
generation.

It therefore captures:

- early founder-lineage extinction;
- run-to-run variation;
- stochastic crossing after rare migration;
- probability that all regions exceed 50%, 90%, or 99% both-founder descent;
- 5th-95th percentile uncertainty bands.

These probabilities are **conditional on the selected parameter values**. They
are not historical posterior probabilities.

## Scenario presets

The notebook includes clearly labeled sensitivity presets:

- Teaching default;
- Very low connectivity;
- High connectivity;
- Strong endogamy;
- Permanent Tasmania isolation;
- No interregional reproduction.

Presets are starting points, not historical claims. Every parameter remains
editable.

## A/B scenario comparison

Any run can be saved as Scenario A or Scenario B.

The comparison plot shows the present regional both-founder fraction side by
side. This is especially useful for questions such as:

- What changes if migration is reduced tenfold?
- Does endogamy or migration matter more?
- What happens if Tasmania never reopens?
- How much does one extra late-contact assumption change the result?

## Automatic diagnosis

The deterministic run generates a compact mechanistic diagnosis.

It identifies:

- the present limiting region;
- whether global 99% both-founder ancestry is reached;
- which region crosses 99% last;
- regions with no external reproductive path;
- whether a hard barrier remains important;
- whether genealogy is near-universal while mean founder DNA is below 1%.

This turns the visualization into an explanatory tool rather than only an
animation.

## Scenario export

The current parameterization can be exported as JSON.

That makes claims reproducible. If a user says "I obtained universal ancestry",
the exact population, migration, mixing, barrier, and timing assumptions can be
shared and rerun.

## Visual design

The notebook uses a coordinated Plotly visual system:

1. animated geographic map with population-scaled nodes;
2. regional genealogy trajectories;
3. global deterministic plus Monte Carlo 5-95% band;
4. present genealogy-versus-DNA comparison;
5. log-scale population trajectories;
6. parental-source heatmap;
7. A/B scenario comparison.

The Australia/Oceania-Tasmania barrier is displayed separately so the user can
see that a zero reproductive edge is qualitatively different from a low rate.

## Scientific interpretation

A successful run means:

> Under the selected population, migration, mating, barrier, and timing
> assumptions, universal founder genealogy is compatible with this model.

A failed run means:

> Under the selected assumptions, one or more mechanisms prevent universal
> ancestry by the present.

Neither result alone establishes which assumptions occurred historically.

## Sources and constraints

- Historical regional population table used for the separate Middle East
  population preset:
  https://www.statista.com/statistics/1006557/global-population-per-continent-10000bce-2000ce/
- Klein Goldewijk et al. (2017), HYDE 3.2, *Earth System Science Data* 9,
  927-953. DOI 10.5194/essd-9-927-2017.
- Fuller et al. (2023), Bassian land-bridge chronology, *Journal of
  Archaeological Science*. DOI 10.1016/j.jas.2023.105819.
- Byard & Maxwell-Stewart (2024), early contact-era Tasmania population models,
  *Asia-Pacific Economic History Review*. DOI 10.1111/aehr.12282.

The default Tasmania start population and all migration/mixing rates are
explicitly sensitivity assumptions unless separately supported.
