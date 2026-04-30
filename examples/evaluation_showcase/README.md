# Evaluation Showcase

This directory describes a reproducible showcase workflow for PracticeLens.

The showcase generates synthetic evaluation WAV files, analyzes selected cases, runs a batch comparison, and writes human-readable reports that are easy to inspect.

## Generate the showcase

```bash
make generate-evaluation-showcase
```

Generated outputs are written under:

```text
examples/evaluation_showcase/generated/
```

## Generated structure

```text
examples/evaluation_showcase/generated/
  README.md
  summary.json
  assets/
    reference_phrase.wav
    exact_take.wav
    pitch_drift_take.wav
    timing_drift_take.wav
    rhythm_mistake_take.wav
    tempo_mismatch_take.wav
    ...
  single/
    exact_take/report.md
    pitch_drift_take/report.md
    timing_drift_take/report.md
    rhythm_mistake_take/report.md
    tempo_mismatch_take/report.md
  batch/
    batch_report.md
    batch_report.json
    batch_report.csv
    batch_report.svg
```

## What to inspect

Start with:

```text
examples/evaluation_showcase/generated/summary.json
```

Then inspect:

```text
examples/evaluation_showcase/generated/batch/batch_report.md
```

For focused feedback examples, compare:

```text
examples/evaluation_showcase/generated/single/pitch_drift_take/report.md
examples/evaluation_showcase/generated/single/timing_drift_take/report.md
examples/evaluation_showcase/generated/single/rhythm_mistake_take/report.md
```

## Important caveat

These assets are synthetic and deterministic.

They are useful for demos, smoke checks, and quick repo evaluation. They are not a scientific benchmark and they do not replace real musician-recorded validation data.

The point is to make PracticeLens easier to judge quickly without committing third-party audio files.
