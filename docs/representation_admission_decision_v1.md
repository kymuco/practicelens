# R0.6 — Representation Admission Decision v1

Status: complete / event-perceptual primitive layer not admitted

Frozen evidence base:

`e823d2bc7f63e402ebf309dbdaa5fea5302584f5`

Machine-readable decision:

`docs/representation_admission_decision_v1.json`

## Decision

For the current PracticeLens scope, retain the existing frame-level representation as the canonical measurement substrate.

Do **not** admit an additional:

```text
Event
Attack
Sustain
Transition
Rest
```

representation layer at this point.

The decision is deliberately narrow:

> no current machine-side failure remains that requires event semantics after lower-level attribution.

This is not a claim that frame-level features are universally sufficient.

## Admission rule

A new representation should be admitted only when all of the following are true:

1. a reproducible measurement failure remains after attribution across preprocessing, feature extraction, alignment, and score construction;
2. the failure maps to a construct that the current representation cannot expose with a bounded lower-complexity repair;
3. the proposed representation is tested against a preregistered falsifiable hypothesis;
4. it improves the target failure without unacceptable nuisance or protected-dimension regressions.

The current evidence does not satisfy the first two conditions.

Therefore running an event-primitive implementation now would test an attractive architecture without a demonstrated representational need.

## Evidence matrix

### Recording-start equivalence

R0.5a found a large systematic defect caused by leading recording silence.

The defect was localized to preprocessing and repaired with:

```text
material DC centering
-> peak normalization
-> exact activity trim
```

Post-repair equivalence movement returned to zero for the tested series.

Representation implication:

```text
preprocessing defect
!= representational insufficiency
```

### Timing cross-talk and monotonicity

R0.5c localized the principal timing defect to DTW path geometry.

R0.5d showed that weak positional regularization can reduce pitch-drift -> timing movement and restore local-timing monotonicity.

R0.5e then showed that applying that same positional path globally creates a pitch trade-off.

R0.5f resolved the conflict counterfactually by assigning alignment ownership per construct:

```text
pitch_fidelity
    -> production flexible alignment

timing_consistency
    -> current_positional_0p10 alignment

rhythm_fidelity
    -> onset/time path
```

Every preregistered R0.5f check passed.

Key results:

```text
pitch drift -> timing
2.275722 -> 0.536953

local timing monotonicity
PARTIAL -> PASS

local timing -> pitch
retained at production 0.763684

additive-noise timing movement
4.509643 -> 0.641228
```

The underlying frame-level features were unchanged.

Representation implication:

> the tested timing defect is shared-alignment coupling, not evidence that frame-level observations are insufficient.

### Additive noise -> pitch

R0.5g localized the remaining pitch nuisance to feature extraction.

Relative-position mean pitch error grows to:

```text
7.599 cents
```

at the strongest controlled noise condition.

Across the tested series:

```text
voiced mismatch fraction = 0
voiced ratio delta        = 0
```

So the failure is frequency-estimate robustness inside already-voiced frames.

Production DTW partially compensates the estimator error:

```text
linear-alignment pitch movement   3.799267
production pitch movement         3.560936
```

Representation implication:

```text
pitch-estimator robustness boundary
!= demonstrated need for event semantics
```

### Additive noise -> rhythm

R0.5g localized rhythm movement to onset extraction.

At low noise, onset count remains stable and only tiny onset-position movement appears.

At the strongest condition:

```text
reference onset count   23
take onset count        24
```

Approximately 91.7% of the resulting 1.184859-point rhythm movement comes from the extra-onset count term.

Rhythm does not consume DTW alignment.

Representation implication:

```text
spurious-onset admission boundary
!= demonstrated need for a new event representation
```

The current system already exposes an event-like onset observable; the current defect is robustness of that detector.

### Score construction

R0.5g reconstructed current pitch and rhythm scores exactly:

```text
pitch production reconstruction error   0
pitch linear reconstruction error       0
rhythm reconstruction error             0
```

No unexplained score-only effect remains for these nuisance paths.

### Section stability

`section_stability` remains a derived aggregate rather than an independent orthogonal construct.

R0.5f intentionally did not invent a hybrid section-stability definition from multiple alignment paths.

Its current behavior therefore does not constitute evidence for an event/perceptual layer.

## Current causal map

The machine-side R0 work now supports:

```text
recording-start variation
    -> preprocessing
    -> repaired

pitch -> timing cross-talk
    -> shared alignment ownership

local timing -> pitch
    -> frame-boundary pitch movement
    -> flexible DTW partially compensates

noise -> timing
    -> alignment geometry

noise -> pitch
    -> pitch estimator

noise -> rhythm
    -> onset detector
```

No row currently ends in:

```text
missing event semantics
```

or:

```text
current frame representation cannot expose the required observable
```

That is the decisive R0.6 result.

## Verdict

```text
CURRENT_FRAME_LEVEL_REPRESENTATION
    RETAIN

EVENT_PERCEPTUAL_PRIMITIVE_LAYER
    NOT_ADMITTED

REASON
    NO_DEMONSTRATED_REPRESENTATIONAL_GAP
```

This is a conservative architecture decision.

It avoids paying the complexity cost of a second representation without evidence that the current one is the limiting factor.

## What remains valid to improve later

R0.6 does not prohibit narrower improvements.

Future evidence may justify:

- a more noise-robust deterministic pitch estimator;
- a more robust onset detector;
- metric-specific alignment ownership;
- a careful redefinition of section stability;
- additional controlled target families.

Those are separate measurement questions and should not be bundled into a representation rewrite.

## Reopen conditions

The representation question should reopen only when new evidence satisfies at least one of these conditions.

### Unattributed real-session failure

Repeated real-session observations expose a stable measurement defect that cannot be explained by:

- recording/preprocessing nuisance;
- feature-estimator robustness;
- alignment ownership;
- score mapping.

### Missing observable

A target construct such as articulation or transition quality is shown under a controlled protocol to lack a sufficient observable in the current feature bundle.

### Falsifiable primitive hypothesis

A newly demonstrated representational gap supports a preregistered hypothesis such as:

> an event/transition representation separates a specific target change from nuisance variation that the current representation cannot separate.

Only then should an event-level candidate be implemented and compared.

### Scope change

A materially different scope, such as polyphonic analysis, may require different observables.

That would be a new scope-specific admission question rather than evidence that the current monophonic decision was wrong.

## Human evidence boundary

R0.5b remains pending.

This matters because the project still does not know the real within-session performance/noise envelope of a musician.

Therefore R0.6 does **not** establish:

- practical significance of 0.5-1 point residual movements;
- longitudinal skill-change thresholds;
- ecological validity;
- laboratory-grade status for real musician development tracking.

R0.6 only closes the current machine-side representation question.

## Consequence for R0

The synthetic machine-side architecture track is now sufficiently narrowed.

The next high-value evidence is not another representation or tuning PR.

It is the first R0.5b real-session repeatability sample when convenient.

Until that evidence exists, additional machine-side architecture expansion should require a new, explicit measurement failure rather than continuing by momentum.
