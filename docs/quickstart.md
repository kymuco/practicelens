# PracticeLens Quickstart

This quickstart is for the current local-first v0.1 workflow.

## 1. Install

For normal development:

```bash
pip install -e .[dev]
```

For API usage as well:

```bash
pip install -e .[dev,api]
```

## 2. Generate demo audio files

PracticeLens does not commit real practice audio into the repository.

Instead, it ships a deterministic generator for small synthetic demo WAV files.

Generate them with:

```bash
make generate-demo-assets
```

This writes demo WAVs under:

```text
examples/demo_assets/generated/
```

## 3. Run single analysis

```bash
practicelens analyze \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take.wav \
  --out out/demo/single
```

Generated artifacts:

- `report.json`
- `report.md`
- `report.csv`
- `report.svg`

## 4. Run batch comparison

```bash
practicelens compare-batch \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take_01.wav \
  --take examples/demo_assets/generated/take_02.wav \
  --take examples/demo_assets/generated/take_03.wav \
  --out out/demo/batch
```

Generated batch artifacts:

- `batch_report.json`
- `batch_report.md`
- `batch_report.csv`
- per-take subdirectories under `out/batch/takes/`

## 5. Useful tuning flags

Shared flags:

- `--sample-rate`
- `--frame-length`
- `--hop-length`
- `--segment-duration`

Example:

```bash
practicelens analyze \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take.wav \
  --out out/demo/single \
  --sample-rate 16000 \
  --frame-length 1024 \
  --hop-length 256 \
  --segment-duration 2.0
```

## 6. Run checks locally

```bash
ruff check .
pytest tests
```

## Notes

- The current workflow is bounded and offline-first.
- The project is aimed first at monophonic or near-monophonic material.
- This is a practical baseline, not a final polished DSP standard.
- The generator under `tools/generate_demo_assets.py` is the intended demo asset path for onboarding, examples, and smoke tests.
