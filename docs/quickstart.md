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

## 2. Prepare audio files

PracticeLens currently expects local WAV files.

You need:

- one reference WAV file;
- one take WAV file for single analysis;
- or several take WAV files for batch comparison.

## 3. Run single analysis

```bash
practicelens analyze \
  --reference samples/reference.wav \
  --take samples/take.wav \
  --out out/single
```

Generated artifacts:

- `report.json`
- `report.md`
- `report.csv`
- `report.svg`

## 4. Run batch comparison

```bash
practicelens compare-batch \
  --reference samples/reference.wav \
  --take samples/take_01.wav \
  --take samples/take_02.wav \
  --take samples/take_03.wav \
  --out out/batch
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
  --reference samples/reference.wav \
  --take samples/take.wav \
  --out out/single \
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
