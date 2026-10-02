# R0.5f — Metric-Specific Alignment Readout Results v1

Status: complete / strict synthetic hypothesis supported

Frozen production revision:

`352e89ec8b0cc4bfb7ff020c44b523c94fe8f712`

Machine-readable snapshot:

`docs/metric_specific_alignment_readout_baseline_v1.json`

## Executive result

The preregistered metric-specific readout passes every strict R0.5f check:

```text
passes_all_preregistered_checks = true
```

Readout ownership:

```text
pitch_fidelity
    -> production flexible alignment

rhythm_fidelity
    -> unchanged onset/time representation

timing_consistency
    -> current_positional_0p10 alignment
```

This supports the R0.5e hypothesis that the main pitch/timing trade-off is caused by forcing different constructs to share one alignment path.

It does **not** admit a production architecture.

## Amplitude gain

All three independent readouts remain exactly invariant:

```text
pitch_fidelity       0
rhythm_fidelity      0
timing_consistency   0
```

Both production and positional alignment coverage remain 1.0.

## Additive noise

The metric-specific split keeps pitch and rhythm at their production behavior while allowing timing to use the geometry-regularized path.

Maximum absolute movement:

```text
                     production   metric-specific

pitch_fidelity         3.560936      3.560936
rhythm_fidelity        1.184859      1.184859
timing_consistency     4.509643      0.641228
```

So:

- pitch noise sensitivity is restored to production rather than the positional candidate's 3.769585 regression;
- rhythm is unchanged;
- timing noise movement is reduced by about 85.8%.

The preregistered additive-noise no-regression check passes.

Strict additive-noise invariance itself is still **not** solved because pitch and rhythm continue to move.

## Pitch drift

Pitch target behavior is exactly the production readout:

```text
pitch_fidelity endpoint delta   -25.348476
directional sensitivity         PASS
monotonicity                    PASS
```

Protected rhythm movement is unchanged:

```text
0.013356 -> 0.013356
```

Protected timing movement becomes:

```text
production max delta   2.275722
metric-specific        0.536953
```

a reduction of approximately 76.4%.

This preserves the narrow R0.5d timing-path improvement without paying the R0.5e pitch-readout cost.

## Local timing warp

Pitch uses the production flexible alignment, so protected pitch movement returns exactly to the production envelope:

```text
production max delta   0.763684
metric-specific        0.763684
```

Timing uses the positional path:

```text
metric-specific timing sequence

100.000000
99.348869
99.154426
98.390226
```

Therefore:

```text
directional sensitivity = PASS
monotonicity            = PASS
endpoint delta          = -1.609774
```

The original production sequence remains:

```text
100.000000
95.509288
97.882204
95.611486
```

with `PARTIAL` monotonicity.

R0.5f therefore simultaneously retains production pitch robustness under local timing warp and the positional timing path's monotonic behavior.

## Alignment coverage

Across every current R0.3 family:

```text
production min coverage   = 1.0
positional min coverage   = 1.0
```

No result is explained by dropping aligned frames.

## Section stability boundary

R0.5f intentionally does not define a hybrid `section_stability`.

The current section-stability score aggregates section-level pitch/rhythm/timing generated from one alignment path. Mixing two paths would be a new measurement definition.

For context only, the positional path often changes section-stability behavior, including improved additive-noise movement:

```text
noise section_stability max delta

production    3.273450
positional    1.926507
```

But no R0.5f PASS/FAIL claim is made for a metric-specific section-stability construct.

## Architectural conclusion

R0.5d showed that timing can be repaired inside alignment-space.

R0.5e showed that using that alignment globally harms pitch behavior.

R0.5f now shows that the conflict disappears when alignment ownership is construct-specific:

```text
same frame-level feature representation
        |
        +--> flexible correspondence -> pitch readout
        |
        +--> geometry-regularized correspondence -> timing readout
        |
        +--> onset/time evidence -> rhythm readout
```

For the tested synthetic pitch/timing failures, the evidence therefore favors:

> shared-alignment coupling is the defect.

It does **not** support:

> frame-level representation must be replaced to solve these timing failures.

That substantially weakens the timing-based case for immediately introducing Event / Attack / Sustain / Transition / Rest primitives.

## Remaining machine-side failure boundary

The largest unresolved synthetic nuisance is now additive noise itself.

Metric-specific alignment removes most timing noise movement, but:

```text
pitch_fidelity max noise delta    3.560936
rhythm_fidelity max noise delta   1.184859
```

remain.

These are no longer explained by the shared timing-alignment problem.

The next narrow machine-side question is therefore:

> does additive-noise movement originate primarily in feature extraction, alignment correspondence, or score construction?

A suitable next experiment is **R0.5g — Additive Noise Attribution Audit v1**.

No repair should be attempted before that attribution.

## Human evidence boundary

R0.5b remains pending.

R0.5f establishes a synthetic architecture distinction, not practical human significance.

In particular, the compressed positional timing response cannot be assigned a minimum useful magnitude until real within-session repeatability is measured.
