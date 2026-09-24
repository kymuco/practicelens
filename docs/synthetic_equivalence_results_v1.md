# R0.5a Synthetic Equivalence Results v1

Status: recorded baseline  
Frozen instrument revision: `b2369e07df8ad36046ad337db2327656483b6397`

Machine-readable snapshot: `docs/synthetic_equivalence_baseline_v1.json`

## Executive result

The current PracticeLens instrument is perfectly deterministic on exact reruns, but it is **not invariant to recording-window placement**.

Exact rerun floor:

```text
pitch_fidelity       0.000000
rhythm_fidelity      0.000000
timing_consistency   0.000000
section_stability    0.000000
```

The tested equivalence envelope is:

```text
pitch_fidelity       2.016078
rhythm_fidelity      1.419644
timing_consistency   7.009045
section_stability    3.837666
```

All four maxima come from the same case:

```text
leading_silence_16ms
```

The 64 ms leading-silence case produces exactly the same measurement deltas.

This means the envelope is dominated by a systematic recording-start bias, not stochastic software noise.

## What remained exactly invariant

The following transformations produced exactly zero movement in all four candidate measurements:

- repeated analysis of the exact same WAV;
- exact byte copy to another path;
- int16 PCM decode/encode roundtrip;
- polarity inversion;
- -6 dB gain;
- -12 dB gain.

This gives a strong result for deterministic repeatability and confirms the R0.4 gain-invariance result.

## DC sensor bias

Adding a small DC offset did not move pitch or rhythm.

Maximum absolute movement:

```text
pitch_fidelity       0.000000
rhythm_fidelity      0.000000
timing_consistency   0.246074
section_stability    0.211175
```

The effect is small relative to the recording-window defect.

## Recording-window placement

### Leading silence

Both 16 ms and 64 ms leading silence produced:

```text
pitch_fidelity       -2.016078
rhythm_fidelity      -1.419644
timing_consistency   -7.009045
section_stability    -3.837666
```

The performed phrase is unchanged.

Therefore these deltas are measurement/preprocessing sensitivity to recording placement, not skill change.

### Trailing silence

Both 16 ms and 64 ms trailing silence produced much smaller movement:

```text
pitch_fidelity       -0.047007
rhythm_fidelity      -0.227232
timing_consistency    0.000000
section_stability    -0.425271
```

The strong leading/trailing asymmetry is important.

## Root-cause localization

The current offline pipeline runs:

```text
peak_normalize
-> trim_silence(threshold=0.01, pad_samples=hop_length // 4)
```

With the frozen R0.4/R0.5 configuration:

```text
hop_length = 256
pad_samples = 64
```

For the canonical synthetic phrase, the first post-normalization sample crossing the 0.01 threshold is at sample index 9.

Therefore the unpadded reference computes:

```text
start = max(0, 9 - 64) = 0
```

When at least 55 samples of leading silence are added, the detected start is shifted by the padding but no longer clips at the file boundary. The trimmed result retains 55 samples of pre-roll before the original phrase:

```text
64 - 9 = 55 samples
55 / 16000 = 3.4375 ms
```

That explains why both 16 ms and 64 ms added leading silence collapse to the same downstream measurement result.

The observed 7.01-point timing movement is therefore consistent with a deterministic trim/frame-origin boundary effect.

R0.5a records this defect; it does not repair it.

## Comparison with R0.4

The R0.4 responses can now be compared with the tested equivalence envelope.

### Pitch drift primary signal

R0.4 maximum pitch response:

```text
24.934732
```

R0.5a pitch equivalence envelope:

```text
2.016078
```

Ratio:

```text
12.37x
```

The pitch-drift signal clearly exceeds the tested synthetic equivalence instability.

This strengthens the case that the existing pitch path contains real controlled signal.

### Local timing warp primary signal

R0.4 maximum timing response:

```text
4.347350
```

R0.5a timing equivalence envelope:

```text
7.009045
```

Ratio:

```text
0.62x
```

The intended timing signal is smaller than the current response to an equivalent recording-start change.

Therefore the current timing candidate cannot yet support a clean magnitude interpretation.

This is now a stronger and more specific limitation than the R0.4 non-monotonicity result alone.

### R0.4 protected-dimension cross-talk

`local_timing_warp -> pitch_fidelity`:

```text
R0.4 cross-delta     0.576328
R0.5a pitch envelope 2.016078
ratio                0.29x
```

This strict cross-talk failure is inside the current synthetic equivalence envelope and should not yet be treated as a practically meaningful independent defect.

`pitch_drift -> rhythm_fidelity`:

```text
R0.4 cross-delta      2.196657
R0.5a rhythm envelope 1.419644
ratio                 1.55x
```

This one exceeds the tested equivalence envelope and remains a live cross-talk signal.

`pitch_drift -> timing_consistency`:

```text
R0.4 cross-delta      2.228232
R0.5a timing envelope 7.009045
ratio                 0.32x
```

This does not exceed the current timing equivalence instability.

### Additive-noise nuisance

Pitch movement under R0.4 additive noise:

```text
3.402435
```

is above the pitch equivalence envelope:

```text
2.016078
```

by about 1.69x.

Timing and section-stability movement under additive noise remain below their current recording-window envelopes.

## Architectural consequence

R0.5a narrows the next step substantially.

The first thing to repair is **not** the score weights and not an event/perceptual representation.

The most immediate demonstrated defect is earlier:

```text
recording start
-> trimming boundary
-> frame origin
-> alignment/features
-> timing score
```

A representation change before controlling this boundary would risk solving a downstream symptom while leaving a larger upstream nuisance intact.

## What R0.5a does not establish

R0.5a still does not give a human longitudinal noise floor.

It does not model:

- performer execution variance;
- microphone repositioning;
- room changes;
- real background noise distributions;
- instrument tuning drift;
- day-to-day physiology;
- repeated practice takes.

Therefore a human-facing "minimum detectable improvement" remains unsupported.

## Next step

R0.5 should now proceed in two ordered moves:

1. freeze this R0.5a evidence and repair/re-audit recording-start equivalence without tuning against target interventions;
2. run R0.5b local within-session repeatability on real repeated takes.

Only after both should R0.6 decide whether the remaining timing limitation requires a new event/perceptual representation.
