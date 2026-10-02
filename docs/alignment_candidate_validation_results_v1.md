# R0.5e — Alignment Candidate Validation Results v1

Status: complete / candidate does not pass all preregistered checks

Frozen production revision:

`45384707dde57c874e76ba6e77501f12181623d9`

Frozen candidate:

`current_positional_0p10`

Machine-readable snapshot:

`docs/alignment_candidate_validation_baseline_v1.json`

## Executive result

The R0.5d positional candidate remains useful as a diagnostic alignment substrate, but it is **not ready for production admission**.

Preregistered result:

```text
passes_all_preregistered_checks = false
```

Passed checks:

```text
amplitude_gain_strict_invariance                 PASS
pitch_drift_directional_sensitivity_preserved    PASS
pitch_drift_monotonicity_preserved               PASS
pitch_drift_protected_cross_talk_no_worse        PASS
local_timing_directional_sensitivity_preserved   PASS
local_timing_monotonicity_improved_to_pass       PASS
minimum_alignment_coverage_preserved             PASS
```

Failed checks:

```text
additive_noise_no_measurement_regression          FAIL
local_timing_protected_cross_talk_no_worse        FAIL
```

The candidate therefore solves the narrow timing-path defect but moves two other boundaries in the wrong direction.

## Amplitude gain remains fully invariant

Production and candidate both remain exactly invariant:

```text
pitch_fidelity       0
rhythm_fidelity      0
timing_consistency   0
section_stability    0
```

Coverage remains 1.0.

This confirms that the positional prior does not reopen the acquisition-gain defect closed earlier in R0.5a.

## Pitch drift remains strong

Primary pitch response is preserved:

```text
production endpoint delta   -25.348476
candidate endpoint delta    -25.384572
retention ratio              1.001424
```

Candidate:

```text
directional sensitivity = PASS
monotonicity            = PASS
```

The important R0.5d improvement also survives:

```text
pitch -> timing max delta

production   2.275722
candidate    0.536953
ratio        0.235948
```

So approximately 76.4% of this protected timing movement is removed.

Rhythm cross-talk is unchanged:

```text
0.013356 -> 0.013356
```

This check passes.

## Local timing becomes monotonic, but pitch cross-talk worsens

Timing response:

```text
production
100.000
95.509
97.882
95.611

candidate
100.000
99.349
99.154
98.390
```

The candidate changes:

```text
monotonicity
PARTIAL -> PASS
```

and preserves directional sensitivity.

But the response magnitude is compressed:

```text
80 ms endpoint delta

production   -4.388514
candidate    -1.609774
retention     0.366815
```

More importantly, protected pitch movement increases:

```text
timing warp -> pitch max delta

production   0.763684
candidate    1.022111
ratio        1.338396
```

This is a preregistered validation failure.

R0.5c already showed that frame-level pitch movement exists before DTW around shifted event boundaries and that flexible DTW compensates much of it.

The positional prior constrains that compensation, so more of the pre-alignment boundary artifact reaches the final pitch score.

## Additive-noise behavior is mixed and fails strict no-regression

The candidate improves two nuisance responses substantially:

```text
timing_consistency
production max delta   4.509643
candidate max delta    0.641228
ratio                  0.142190

section_stability
production max delta   3.273450
candidate max delta    1.926507
ratio                  0.588525
```

Rhythm is unchanged:

```text
1.184859 -> 1.184859
```

But pitch becomes slightly more noise-sensitive:

```text
pitch_fidelity

production max delta   3.560936
candidate max delta    3.769585
ratio                  1.058594
```

That is about a 5.9% increase.

Because R0.5e preregistered a per-measurement no-regression rule, the additive-noise family fails even though the aggregate picture is mixed.

The criterion is not relaxed after seeing the result.

## Alignment coverage

Every production and candidate series retains:

```text
minimum coverage = 1.0
```

The failures are therefore not caused by losing aligned frames.

## Architectural interpretation

R0.5d and R0.5e together expose a more specific architecture conflict:

```text
timing readout wants
    stronger geometric path regularity

pitch readout benefits from
    flexible feature-driven alignment
    that can compensate local boundary/noise effects
```

A single shared alignment path is therefore acting as a coupling point between different measurement constructs.

This is a stronger and narrower conclusion than:

> choose a better global DTW weight.

The positional candidate is not uniformly better, and further scalar weight tuning would risk turning the research track into post-hoc optimization.

## What R0.5e rules out

R0.5e rules out immediate production admission of `current_positional_0p10`.

It also weakens the case for searching another single global alignment weight next.

The existing evidence instead motivates a new falsifiable hypothesis:

> pitch and timing may require different alignment readouts over the same extracted representation.

## Recommended next machine-side experiment

**R0.5f — Metric-Specific Alignment Readout Ablation v1**

Diagnostic hypothesis:

```text
pitch_fidelity
    -> current flexible feature-driven DTW

timing_consistency
    -> current_positional_0p10 geometry-regularized DTW

rhythm_fidelity
    -> unchanged onset/time path
```

The experiment should remain counterfactual and must not change production behavior.

It should test whether separating alignment ownership can simultaneously recover:

- current pitch robustness under additive noise;
- current/strong pitch-drift sensitivity;
- reduced pitch->timing cross-talk;
- monotonic local-timing response;
- current pitch robustness under local timing warp;
- full alignment coverage.

If this succeeds, the problem is primarily shared-alignment coupling rather than insufficient audio representation.

If it fails, the case for an event/transition representation becomes stronger.

## Human evidence boundary

R0.5b remains pending.

No synthetic validation result establishes whether the remaining 0.5–1 point protected movements matter relative to real within-session human variation.
