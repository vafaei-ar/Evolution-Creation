# Model 14: agency inference, artifacts, and fine-tuning

## Claim from the debate

The debate argues that archaeologists infer **agency** from patterned stone
artifacts rather than attributing them to random natural processes. It then
extends that intuition to cosmic order, regularity, and fine-tuning: if patterned
stones can justify an agency inference, perhaps fine-tuning can justify a cosmic
agency inference.

## What can be modeled

Both arguments can be written as likelihood comparisons.

For a binary hypothesis:

```math
\mathrm{posterior\ odds}
=
\mathrm{prior\ odds}
\times
\frac{P(E\mid H_1)}{P(E\mid H_0)}.
```

The ratio is the likelihood ratio or Bayes factor.

The crucial scientific question is not whether both arguments use the same
algebra. They can. The question is whether the inputs have comparable empirical
status.

## Artifact inference

Experimental archaeology can compare:

- human-knapped assemblages;
- naturally fractured stone / geofacts;
- diagnostic attributes;
- false positives and false negatives.

Lubinski et al. (2014), for example, compared candidate flakes with experimental
flintknapping and naturally occurring toolstone and explicitly described the
inference as probabilistic rather than definitive.

This makes empirical calibration of a classifier possible in principle.

The notebook uses a **synthetic demonstration**, not a published artifact
classifier: true-positive rate 0.95 and false-positive rate 0.01 gives a
likelihood ratio of 95.

With the same LR:

- prior agency 1% -> posterior about 49%;
- prior agency 10% -> posterior about 91%.

Even a strong likelihood ratio does not erase the role of prior odds.

## Fine-tuning inference

Fine-tuning arguments can also be represented in Bayesian form:

```math
\frac{P(D\mid R)}{P(\neg D\mid R)}
=
\frac{P(R\mid D)}{P(R\mid \neg D)}
\frac{P(D)}{P(\neg D)}.
```

But the Stanford Encyclopedia review emphasizes major disputes over:

- how probabilities over constants / possible universes should be defined;
- the design likelihood;
- prior probability of a designer;
- observer-selection / anthropic effects;
- alternatives such as future physics and multiverse hypotheses.

Thus there is no experimentally calibrated confusion matrix analogous to a
controlled artifact/geofact experiment.

## Judgment on the claim

**The analogy is valid at the level of logical form, but not at the level of
calibrated evidential strength.** Patterned evidence can increase the probability
of agency when the evidence is demonstrably more likely under an agency
hypothesis than under relevant non-agency alternatives.

Archaeology can sometimes estimate that contrast using experimental controls.
For cosmic fine-tuning, the required priors and likelihoods are contested and
cannot be imported from stone-tool classification.

Therefore the stronger claim that fine-tuning makes cosmic agency scientifically
unavoidable is **not established by the artifact analogy**.

### What would need to be specified

A quantitative fine-tuning argument must specify:

1. the competing hypotheses, not merely "agency" versus "random";
2. the probability measure over physical possibilities under each hypothesis;
3. the design likelihood, including what a designer is predicted to produce;
4. observer-selection effects;
5. prior odds or a prior-robust likelihood argument;
6. sensitivity to multiverse / new-physics alternatives.

The notebook therefore exposes prior and likelihood-ratio sensitivity instead
of assigning a single "probability of design."

## References

- Lubinski P, Terry K, McCutcheon PT. (2014). *Comparative methods for
  distinguishing flakes from geofacts: a case study from the Wenas Creek
  Mammoth site*. Journal of Archaeological Science 52:308-320.
- Stanford Encyclopedia of Philosophy, *Fine-Tuning*, substantive revision 2026.
