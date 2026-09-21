# Interactive continental founder-spread explorer

## Purpose

This explorer synthesizes Models 02-05 and 09-11 into one user-facing teaching
simulation.

The user chooses:

- how many years ago Adam and Eve enter the modeled population;
- generation interval;
- founder region;
- macroregional starting populations;
- target populations used for the visual growth trajectory;
- parental-source migration matrix;
- within-region mixing strength;
- timing and multiplier for a late increase in interregional contact.

The simulation then shows how the founder-pair genealogy and expected mean
founder DNA spread through **five macrocontinents plus a separate Middle East
source region**.

## Why six nodes instead of five

If the Middle East is collapsed into "Asia", the founder location disappears
inside a very large compartment. The engine therefore uses:

1. Middle East;
2. Africa;
3. Europe;
4. Asia outside the separate Middle East source node;
5. Americas;
6. Oceania.

The display still functions as a five-continent model with the Middle East
shown as the source region.

## Population defaults

The default founder time is 11,000 years before present, approximately 9000 BCE.

A historical regional table provides the following 9000 BCE values:

- Middle East: 241,000;
- Africa: 343,000;
- Europe: 759,000;
- Asia + CIS: 1,555,000;
- Americas: 415,000;
- Oceania: 252,000.

Total: about 3.565 million.

These are not census counts. Prehistoric population estimates are highly
uncertain. HYDE 3.2, for example, places global population near 4.4 million in
10,000 BCE and reports a very broad scenario range.

Every population field is editable.

The target populations are taken from the same regional source's 2000 CE row
only to create a smooth, visually interpretable population-size trajectory.
That trajectory is not a reconstruction of every historical demographic shock.

## Migration semantics

The migration matrix is more precisely a **parent-source matrix**.

For a child born in destination region i, entry M[i,j] is the probability that
one parental draw comes from source region j.

The diagonal is the local parental fraction.

This is preferable to an ambiguous "migration rate" because genealogy spreads
through reproduction.

The supplied matrix is explicitly a **teaching sensitivity preset**. It is not
claimed to be an empirically estimated Holocene migration matrix.

## Mixing strength

Each region has a parameter q between 0 and 1.

After regional parent-source pooling:

- q = 0 preserves pedigree-state frequencies;
- q = 1 applies full random mating within that macroregion;
- intermediate values interpolate between them.

This is a compact representation of endogamy / assortative structure, not a
measured biological constant.

## Adam and Eve states

The explorer tracks four pedigree states:

- neither founder;
- Adam only;
- Eve only;
- both founders.

At insertion, Adam and Eve are represented separately. A configurable number of
first-generation joint children seeds the "both founders" state.

The map can display:

- any founder;
- both founders;
- mean founder-pair genetic ancestry.

## Genetics

The genetic layer tracks only expected mean autosomal ancestry contributed by
the pair.

Migration changes the regional mean.

Random mating does not by itself increase the population mean genetic
contribution, even though genealogical descendant status can spread rapidly.

This is the visual lesson from Models 07, 08, and 11.

## Population trajectory

For speed and transparency, the explorer interpolates population size smoothly
in log space between the chosen starting and target population.

This affects absolute descendant counts and visual marker sizes.

It is not intended as a reconstruction of epidemics, wars, agriculture,
colonization, or regional demographic transitions. Users can change the start
and target populations.

## Late-contact control

The explorer can multiply all off-diagonal parental-source fractions during the
last chosen number of years.

This is useful for visually exploring the effect of increased recent global
connectivity.

The default timing and multiplier are sensitivity controls, not historical
measurements.

## Scientific interpretation

The explorer can answer conditional questions such as:

> Under these population, migration, and mating assumptions, what fraction of
> each macroregion becomes descended from Adam, Eve, or both?

It cannot answer:

> What is the historical probability that Adam and Eve existed?

Nor does a visually successful spread demonstrate that the chosen migration
matrix is historically correct.

The key scientific use is sensitivity analysis: change a disputed assumption
and watch which conclusions are robust and which collapse.

## Population sources

- Statista historical regional population table, 10,000 BCE to 2000 CE,
  used for the separate Middle East regional preset.
- Klein Goldewijk et al. (2017), HYDE 3.2, *Earth System Science Data* 9,
  927-953, DOI 10.5194/essd-9-927-2017, used as a global prehistoric
  population cross-check.
