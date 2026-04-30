# Evaluation Assets

PracticeLens can generate a small deterministic set of synthetic evaluation WAV files.

These assets are meant to make the project easier to judge without committing third-party audio or pretending the current scoring layer is already a final musical benchmark.

## Generate assets

```bash
make generate-evaluation-assets
```

This writes files under:

```text
examples/evaluation_assets/generated/
```

The generated directory includes:

- `reference_phrase.wav`
- `exact_take.wav`
- `pitch_drift_take.wav`
- `timing_drift_take.wav`
- `rhythm_mistake_take.wav`
- `noisy_take.wav`
- `silence_mismatch_take.wav`
- `vibrato_take.wav`
- `pluck_take.wav`
- `tempo_mismatch_take.wav`
- `manifest.json`

## Why these are generated

The existing demo assets are intentionally simple and good for onboarding.

The evaluation assets add more realistic synthetic failure modes:

- pitch drift;
- timing drift;
- onset/rhythm mistakes;
- inserted silence;
- deterministic noise;
- vibrato-like modulation;
- plucked/instrument-like envelopes;
- tempo mismatch.

These cases are still synthetic. They are not a replacement for real musician-recorded examples or a scientific benchmark.

They are a safer next layer between clean sine-wave demos and future real-world validation.

## Suggested local checks

After generation, try a single analysis:

```bash
practicelens analyze \
  --reference examples/evaluation_assets/generated/reference_phrase.wav \
  --take examples/evaluation_assets/generated/pitch_drift_take.wav \
  --out out/evaluation-pitch-drift
```

Or compare a few takes:

```bash
practicelens compare-batch \
  --reference examples/evaluation_assets/generated/reference_phrase.wav \
  --take examples/evaluation_assets/generated/exact_take.wav \
  --take examples/evaluation_assets/generated/pitch_drift_take.wav \
  --take examples/evaluation_assets/generated/timing_drift_take.wav \
  --out out/evaluation-batch
```

Use these outputs to inspect whether PracticeLens reports the expected broad weakness for each case.
