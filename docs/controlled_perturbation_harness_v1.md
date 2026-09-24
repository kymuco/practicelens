# Controlled Perturbation Harness v1

Status: R0.3

## Purpose

R0.3 creates deterministic, one-factor-at-a-time audio conditions for the first PracticeLens measurement-validity audit.

The harness does not decide whether any current measurement is good. It only creates reproducible conditions with explicit intervention metadata.

## Design rules

1. Start from one deterministic canonical phrase.
2. Change one intervention family at a time.
3. Include a zero-strength control for every family.
4. Keep ordered intervention strengths.
5. Preserve sample rate, channel count, sample width, and frame count across conditions.
6. Store SHA-256 digests for the reference and every generated WAV.
7. Use R0.2 `ExperimentCondition` and `InterventionSpec` contracts.
8. Do not change the current PracticeLens analysis pipeline.

## Initial families

### amplitude_gain

Role: nuisance.

Strengths:

```text
0, 3, 6, 12 dB magnitude
```

Nonzero cases attenuate the canonical signal by the corresponding negative gain.

Scientific question for R0.4:

> Do candidate pitch/rhythm/timing/stability measurements remain sufficiently invariant when only overall signal gain changes?

### deterministic_additive_noise

Role: nuisance.

Strengths:

```text
0.00, 0.01, 0.03, 0.06 full-scale fraction
```

The additive disturbance is deterministic rather than random so identical harness generation produces identical bytes. R0.3 does not claim a particular spectral distribution for this disturbance.

Scientific question for R0.4:

> At what noise level do current measurements begin to move, and does that movement appear first in suitability/confidence evidence or directly in candidate skill measurements?

### pitch_drift

Role: target.

Strengths:

```text
0.00, 0.01, 0.03, 0.06 terminal fractional drift
```

Pitch drift grows linearly across the phrase while note durations remain fixed.

Scientific question for R0.4:

> Is the response of `pitch_fidelity` sensitive and ordered as pitch drift increases, and how much cross-talk appears in unrelated score dimensions?

### local_timing_warp

Role: target.

Strengths:

```text
0, 20, 40, 80 ms internal boundary shift
```

One internal note boundary is shifted later by the intervention strength. The preceding event is lengthened and the following event is shortened by the same amount, so total duration and the configured note frequencies remain unchanged. This avoids the pitch modulation that time-domain resampling would introduce.

Scientific question for R0.4:

> Do timing-related measurements respond to a growing local temporal deformation without requiring a global tempo change?

## Zero controls

Each family owns its own zero-strength condition even though all zero controls are byte-identical to the canonical reference.

This redundancy is intentional.

A family-local control allows later audit artifacts to remain self-contained and prevents an intervention series from silently borrowing a baseline generated under different conditions.

## Manifest

The harness writes:

```text
reference.wav
cases/
  amplitude_gain/
  deterministic_additive_noise/
  pitch_drift/
  local_timing_warp/
manifest.json
```

The manifest contains:

- schema version;
- generator version;
- sample rate;
- reference identity/path/SHA-256;
- every condition's R0.2 intervention metadata;
- generated WAV path and SHA-256.

The manifest contains no expected score direction and no PASS/FAIL thresholds.

## Why only four families

R0.1 named more possible nuisance and target interventions. R0.3 intentionally starts smaller.

These four families are enough to exercise all four first-audit questions:

- nuisance invariance;
- target sensitivity;
- monotonic response;
- measurement cross-talk / specificity.

Additional families such as leading silence, onset shift, missing events, global tempo changes, and articulation changes should be added only after the first audit shows what information is still missing.

## Non-goals

R0.3 does not:

- execute PracticeLens scoring;
- define scientific verdicts;
- tune metrics;
- add real-musician data;
- add event/perceptual primitives;
- add ML;
- add product UI.

## Next step

R0.4 will freeze the current analysis instrument, run every controlled condition, capture candidate measurement records, and produce the first sensitivity / monotonicity / specificity / nuisance-invariance audit.

The audit may fail. That is an expected and useful outcome.
