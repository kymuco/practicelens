# R0.5f — Metric-Specific Alignment Readout Ablation v1

Status: active experiment

## Trigger

R0.5e showed that one global positional alignment path solves the main timing-path defect but regresses two pitch-related boundaries:

- additive-noise pitch movement;
- local-timing-warp -> pitch cross-talk.

This suggests a narrower failure mode than "the positional alignment is bad":

> pitch and timing measurements may need different alignment readouts over the same extracted representation.

## Counterfactual ownership

R0.5f freezes this readout split:

```text
pitch_fidelity
    -> production flexible feature-driven DTW

rhythm_fidelity
    -> unchanged onset/time representation

timing_consistency
    -> current_positional_0p10 DTW
```

No production behavior is changed.

No profile weight is tuned.

## Why section_stability is not hybridized

Current `section_stability` is derived from section-level pitch, rhythm, and timing scores that are all produced from one alignment path.

Constructing a "hybrid" section stability score from two different paths would define a new measurement, not merely ablate alignment ownership.

R0.5f therefore:

- records production section stability;
- records positional section stability as context;
- does not include section stability in the strict metric-specific readout verdict.

This keeps the experiment about alignment ownership rather than silently redesigning a fourth metric.

## Frozen families

The experiment reuses all existing R0.3 families:

- `amplitude_gain`;
- `deterministic_additive_noise`;
- `pitch_drift`;
- `local_timing_warp`.

## Preregistered checks

The metric-specific readout passes only if all of the following hold.

### Nuisance

- amplitude-gain movement is exactly zero for pitch/rhythm/timing;
- additive-noise movement is no worse than production for each of pitch/rhythm/timing.

### Pitch drift

- pitch directional sensitivity is PASS;
- pitch monotonicity is PASS;
- timing cross-talk is strictly lower than production;
- rhythm cross-talk is no worse than production.

### Local timing warp

- timing directional sensitivity is PASS;
- timing monotonicity is PASS;
- pitch cross-talk is no worse than production.

### Alignment

Both current and positional paths retain full coverage relative to the existing controlled baseline.

## Interpretation

### If all checks pass

Then R0.5e's trade-off is explained by shared-alignment coupling.

The same frame-level features are sufficient for the tested pitch/timing targets when each construct reads from an alignment appropriate to its measurement semantics.

That would weaken the case for an event/transition representation as the next response to the current timing defects.

### If checks fail

Then separating alignment ownership is insufficient.

The remaining failure would identify which construct still needs a deeper representation or feature boundary investigation.

## Important non-claim

Even a full synthetic PASS does not establish a production architecture.

It only demonstrates that the measured conflict can be removed without changing the underlying frame-level feature representation.

R0.5b human/session evidence remains necessary before score magnitudes receive longitudinal meaning.
