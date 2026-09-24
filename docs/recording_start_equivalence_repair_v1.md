# Recording-Start Equivalence Repair v1

Status: pre-registered repair candidate

## Evidence that admits this repair

R0.5a established exact algorithmic repeatability but exposed a deterministic recording-window defect.

Equivalent 16 ms and 64 ms leading silence changed the frozen instrument by:

```text
pitch_fidelity       -2.016078
rhythm_fidelity      -1.419644
timing_consistency   -7.009045
section_stability    -3.837666
```

The timing movement exceeded the R0.4 local-timing target response.

The repair is therefore admitted at the preprocessing/frame-origin boundary before any score or representation change.

## Root cause

The old offline path used:

```text
peak_normalize
-> trim_silence(threshold=0.01, pad_samples=hop_length // 4)
```

The padding was clipped at file boundaries.

That means the amount of retained pre-active context depended on whether the same performance happened to begin close to sample zero.

## Repair

The existing `trim_silence` helper remains unchanged.

A new `trim_silence_fixed_padding` helper:

1. locates the same threshold-defined active interval;
2. retains exactly `pad_samples` of context on both sides;
3. uses available real samples when present;
4. zero-fills only the missing context at a file boundary;
5. returns empty output for an all-silent input.

Only `OfflineReferenceAnalysisPipeline` switches to the fixed-padding helper.

No score, alignment, feature-extraction, confidence, or report semantics change.

## Pre-registered acceptance

### Primary equivalence requirement

Re-running the exact R0.5a experiment must make the `recording_window` family invariant within deterministic floating-point tolerance:

```text
max abs delta <= 1e-9
```

for:

- `pitch_fidelity`;
- `rhythm_fidelity`;
- `timing_consistency`;
- `section_stability`.

### Previously exact families

These must remain exactly invariant within `1e-9`:

- exact copy;
- PCM roundtrip;
- polarity inversion;
- gain.

### DC-bias non-regression

The small ±0.01 DC-bias family must not exceed its pre-repair maxima by more than `1e-9`:

```text
pitch_fidelity       0.000000
rhythm_fidelity      0.000000
timing_consistency   0.246074345212
section_stability    0.211174895824
```

This repair does not attempt to remove DC sensitivity.

## Non-tuning R0.4 replay

After the repair satisfies the equivalence requirements, the complete R0.4 controlled audit is replayed unchanged.

The replay is observational.

The repair must not be adjusted to improve target scores after seeing that replay.

A catastrophic disappearance or reversal of previously established target sensitivity would block merge and trigger architectural reassessment rather than score tuning in this PR.

## Evidence preservation

The original frozen files remain immutable:

- `docs/measurement_validity_baseline_v1.json`;
- `docs/synthetic_equivalence_baseline_v1.json`.

Post-repair results are recorded under new filenames.

## Out of scope

This repair does not:

- define a human longitudinal threshold;
- solve microphone/room noise;
- change score weights;
- add event/perceptual primitives;
- add ML;
- claim that R0.5b is no longer required.
