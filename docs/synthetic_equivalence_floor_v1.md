# R0.5a — Synthetic Equivalence Floor v1

Status: active experiment

## Why R0.5 is split

"Noise floor" contains at least three different sources:

1. **algorithmic repeatability** — same bytes, same configuration, repeated analysis;
2. **representation/acquisition equivalence** — different recordings that preserve the intended performance;
3. **human/session repeatability** — the same musician at effectively the same skill state producing repeated takes.

R0.5a measures the first two.

R0.5b will measure the third with local real takes and must remain separate because performer execution variance is real behavior, not merely software noise.

## Frozen instrument

R0.5a does not modify scoring, features, alignment, preprocessing, or confidence logic.

It uses the same 16 kHz / 1024 / 256 / 1 s analysis configuration as R0.4.

## Exact rerun repeatability

The canonical R0.3 phrase is analyzed three times using fresh pipeline instances.

This checks whether:

```text
same audio bytes
+ same configuration
+ same code
-> same measurements
```

Any nonzero movement is an algorithmic repeatability defect.

## Synthetic equivalence transformations

The tested cases intentionally avoid changing musical pitch, note durations, or note order.

### exact byte copy

Same WAV bytes at a different path.

Tests path/cache independence.

### polarity inversion

```text
x -> -x
```

Waveform polarity changes, while musical content is intended to remain equivalent.

### gain

```text
-6 dB
-12 dB
```

This rechecks the R0.4 amplitude-invariance result inside the equivalence envelope.

### DC sensor bias

```text
-0.01
+0.01 full scale
```

A DC component is not a musical-performance change. This probes whether an acquisition-chain bias leaks into candidate skill measurements.

### recording-window padding

```text
16 ms leading silence
64 ms leading silence
16 ms trailing silence
64 ms trailing silence
```

The performed phrase is unchanged; only where it sits inside the recorded WAV changes.

This probes trimming/frame-grid sensitivity.

## Deliberate exclusion: additive noise

R0.4 deterministic additive noise is not admitted into the equivalence floor.

Noise changes the acoustic observation itself. It may preserve the performer’s skill state, but it is not mathematically equivalent audio and its practical magnitude needs an empirical recording model.

R0.5a therefore keeps it as a separate nuisance result rather than allowing an arbitrary noise amplitude to define the floor.

## Floor definition

For each candidate measurement:

```text
exact_repeat_floor
    = max absolute delta across exact reruns

tested_equivalence_floor
    = max(
        exact_repeat_floor,
        max absolute delta across admitted equivalence cases
      )
```

The source case producing each maximum is recorded.

This is a conservative envelope over the tested equivalence class, not a confidence interval.

## Interpretation rule

A prior R0.4 cross-delta smaller than the tested equivalence floor cannot yet be treated as evidence of meaningful construct cross-talk.

A prior delta larger than the floor is evidence that the effect exceeds this synthetic equivalence envelope.

Neither statement establishes human longitudinal significance.

## R0.5b boundary

R0.5b must use repeated real takes collected close enough in time and conditions that no skill-development claim is intended between them.

Its output should estimate within-session variation locally without committing private audio.

Only after R0.5b should PracticeLens define a human-facing minimum detectable longitudinal change.
