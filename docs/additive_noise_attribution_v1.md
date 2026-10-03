# R0.5g — Additive Noise Attribution Audit v1

Status: active experiment

## Trigger

R0.5f separated the timing alignment problem from the remaining additive-noise nuisance.

With metric-specific readouts, the unresolved synthetic noise envelope is now:

```text
pitch_fidelity max delta   3.560936
rhythm_fidelity max delta  1.184859
```

Timing noise movement is largely alignment-mediated and can be reduced independently.

R0.5g asks:

> Where do the remaining pitch and rhythm noise responses first become observable?

No estimator, alignment, or score is modified.

## Pitch attribution

Pitch fidelity depends on:

```text
pitch_contour_hz
voiced_mask
alignment pairs
score mapping
```

For every additive-noise condition R0.5g computes:

### Production path

```text
noisy extracted features
    -> production DTW
    -> production pitch score
```

### Linear-alignment counterfactual

```text
same noisy extracted features
    -> relative-position alignment
    -> same production pitch score mapping
```

This removes feature-similarity path selection while preserving the extracted noisy pitch/voiced representation.

The audit records:

- mean cents error;
- voiced mismatch count/fraction;
- voiced-ratio movement;
- production score;
- linear-alignment score;
- production-minus-linear alignment contribution.

The current pitch score is also reconstructed term by term to verify that attribution numbers exactly match the production score mapping.

## Rhythm attribution

Current rhythm fidelity does not consume DTW alignment.

Its path is:

```text
energy curve
    -> onset detector
    -> normalized onset positions + onset count
    -> rhythm score
```

R0.5g therefore decomposes the current score into:

- reference/take onset counts;
- mean normalized nearest-onset distance;
- count penalty fraction;
- distance score;
- count score;
- final rhythm score.

This distinguishes two different extraction failures:

```text
onset location movement
vs
spurious/missing onset count
```

The final rhythm score is reconstructed exactly from those terms.

## Attribution vocabulary

```text
none
feature_extraction
feature_extraction_with_alignment_contribution
alignment
score_construction
score_construction_with_alignment_contribution
```

"First stage" refers to the earliest stage at which the nuisance becomes observable.

For example, if noisy pitch estimates already differ before alignment and DTW changes the final magnitude further, the result is:

```text
feature_extraction_with_alignment_contribution
```

not merely "alignment".

## Decision value

### Pitch first appears in extraction

Then a future repair should investigate the deterministic pitch estimator / voiced decision before changing scoring.

### Pitch is mostly alignment-mediated

Then the metric-specific alignment work remains the narrower repair family.

### Rhythm is onset-extraction driven

Then the next repair question belongs to energy/onset evidence, not DTW.

### Score-only movement

That would indicate a score construction issue despite stable relevant feature evidence.

## Non-goals

R0.5g does not:

- change the pitch estimator;
- change the onset detector;
- change alignment;
- change score tolerances;
- tune noise thresholds;
- claim human significance;
- replace R0.5b.
