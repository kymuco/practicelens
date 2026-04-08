# CLI Walkthrough

This walkthrough is the shortest practical path from local WAV files to readable PracticeLens artifacts.

It assumes you want to do two things:

- analyze one take against a reference;
- compare several takes and see which one is strongest.

## 1. Install the project

```bash
pip install -e .[dev]
```

## 2. Prepare local WAV files

You need local WAV files only.

Minimum setup:

- one `reference.wav`
- one `take.wav` for single analysis
- two or more take files for batch comparison

Example layout:

```text
samples/
  reference.wav
  take.wav
  take_01.wav
  take_02.wav
  take_03.wav
```

## 3. Run single-take analysis

```bash
practicelens analyze \
  --reference samples/reference.wav \
  --take samples/take.wav \
  --out out/single
```

Generated files:

- `out/single/report.json`
- `out/single/report.md`
- `out/single/report.csv`
- `out/single/report.svg`

What to inspect first:

1. `report.svg` for the fastest visual summary
2. `report.md` for the readable explanation
3. `report.json` if you want structured output
4. `report.csv` if you want section-level spreadsheet-style inspection

## 4. Run batch comparison

```bash
practicelens compare-batch \
  --reference samples/reference.wav \
  --take samples/take_01.wav \
  --take samples/take_02.wav \
  --take samples/take_03.wav \
  --out out/batch
```

Generated files:

- `out/batch/batch_report.json`
- `out/batch/batch_report.md`
- `out/batch/batch_report.csv`
- `out/batch/batch_report.svg`
- `out/batch/takes/...` per-take artifact folders

What to inspect first:

1. `batch_report.svg` for the quickest ranking view
2. `batch_report.md` for readable take summaries
3. `batch_report.csv` for table-style comparison
4. `out/batch/takes/...` if you want to inspect each take in detail

## 5. Try tighter settings when you want smaller sections

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

Useful shared flags:

- `--sample-rate`
- `--frame-length`
- `--hop-length`
- `--segment-duration`

## 6. Copyable shell example in this repo

See:

- `examples/cli/run_demo.sh`

That file shows the same single + batch flow in a ready-to-edit form.

## Notes

- The repo does not ship real demo WAV files.
- Replace the sample paths with your own local WAV files.
- The current workflow is local-first and bounded by design.
