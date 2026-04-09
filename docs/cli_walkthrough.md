# CLI Walkthrough

This guide shows the current **end-to-end local CLI story** for PracticeLens.

It is meant to answer one practical question:

**If I have local WAV files, what do I run, what appears on disk, and which artifact should I open first?**

## Who this is for

Use this walkthrough if you want to:

- run PracticeLens locally from the CLI;
- understand the difference between single analysis and batch comparison;
- know which generated files matter first;
- evaluate the project quickly without reading source code.

## What you need

You need local WAV files:

- one reference WAV;
- one take WAV for single analysis;
- or several take WAV files for batch comparison.

The repository does **not** currently ship real demo WAV files.
So replace the example paths below with your own files.

## 1. Install the project

```bash
pip install -e .[dev]
```

## 2. Run a single-take analysis

```bash
practicelens analyze \
  --reference samples/reference.wav \
  --take samples/take.wav \
  --out out/single
```

### What gets written

```text
out/single/
├── report.json
├── report.md
├── report.csv
└── report.svg
```

### What to open first

Recommended order:

1. `report.svg` — fastest visual summary
2. `report.md` — readable explanation of what happened
3. `report.csv` — section-by-section table view
4. `report.json` — machine-readable structure

### What each one tells you

- `report.svg`: overall score, component balance, section trend
- `report.md`: summary, feedback, per-section findings
- `report.csv`: compact tabular view of section breakdown
- `report.json`: stable payload for automation or later tooling

## 3. Run a batch comparison

```bash
practicelens compare-batch \
  --reference samples/reference.wav \
  --take samples/take_01.wav \
  --take samples/take_02.wav \
  --take samples/take_03.wav \
  --out out/batch
```

### What gets written

```text
out/batch/
├── batch_report.json
├── batch_report.md
├── batch_report.csv
├── batch_report.svg
└── takes/
    ├── 01-take_01/
    │   ├── report.json
    │   ├── report.md
    │   ├── report.csv
    │   └── report.svg
    ├── 02-take_02/
    │   ├── report.json
    │   ├── report.md
    │   ├── report.csv
    │   └── report.svg
    └── 03-take_03/
        ├── report.json
        ├── report.md
        ├── report.csv
        └── report.svg
```

### What to open first

Recommended order:

1. `batch_report.svg` — quickest visual ranking overview
2. `batch_report.md` — readable ranked summary
3. `batch_report.csv` — spreadsheet-friendly comparison
4. one of the per-take `report.md` or `report.svg` files for deeper inspection

### How to use the batch result

A practical review loop looks like this:

1. Open `batch_report.svg` to see the ranked takes fast
2. Open `batch_report.md` to confirm the best take and the score deltas
3. Open the best take’s `report.md` to see why it won
4. Open the weakest take’s `report.md` to understand where it fell behind

## 4. Useful tuning flags

Shared CLI flags:

- `--sample-rate`
- `--frame-length`
- `--hop-length`
- `--segment-duration`

Example with tighter analysis windows:

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

## 5. What “good usage” looks like

A good practical path is:

- use single analysis when you want to understand one take deeply;
- use batch comparison when you want to decide which take to keep;
- use SVG first for glanceable review;
- use Markdown next for explanation;
- use JSON/CSV when you want structure or external tooling.

## 6. If you just want to browse example outputs

Use the illustrative snapshots already in the repo:

- `examples/results/single/`
- `examples/results/batch/`

These are useful when you want to understand the artifact shapes before running your own audio.
