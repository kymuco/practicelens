# CLI Walkthrough

This guide shows the current **end-to-end local CLI story** for PracticeLens.

It is meant to answer one practical question:

**If I have local WAV files, what do I run, what appears on disk, and which artifact should I open first?**

## Who this is for

Use this walkthrough if you want to:

- run PracticeLens locally from the CLI;
- understand the difference between single analysis, batch comparison, and practice-session review;
- know which generated files matter first;
- evaluate the project quickly without reading source code.

## What you need

You need local WAV files:

- one reference WAV;
- one take WAV for single analysis;
- or several take WAV files for batch comparison / practice-session review.

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
├── report.svg
├── practice_plan.md
└── debug_payload.json
```

### What to open first

Recommended order:

1. `practice_plan.md` — shortest path to the next concrete practice action
2. `report.svg` — fastest visual summary
3. `report.md` — readable explanation of what happened
4. `report.csv` — section-by-section table view
5. `report.json` — machine-readable structure
6. `debug_payload.json` — developer-facing diagnostics

### What each one tells you

- `practice_plan.md`: what to keep, what to improve, which loop to practice next
- `report.svg`: overall score, component balance, section trend
- `report.md`: summary, feedback, per-section findings
- `report.csv`: compact tabular view of section breakdown
- `report.json`: stable payload for automation or later tooling
- `debug_payload.json`: score contributions, evidence counts, confidence notes, and diagnostics

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
├── practice_plan.md
├── session_manifest.json
└── takes/
    ├── 01-take_01/
    │   ├── report.json
    │   ├── report.md
    │   ├── report.csv
    │   ├── report.svg
    │   ├── practice_plan.md
    │   └── debug_payload.json
    ├── 02-take_02/
    │   ├── report.json
    │   ├── report.md
    │   ├── report.csv
    │   ├── report.svg
    │   ├── practice_plan.md
    │   └── debug_payload.json
    └── 03-take_03/
        ├── report.json
        ├── report.md
        ├── report.csv
        ├── report.svg
        ├── practice_plan.md
        └── debug_payload.json
```

### What to open first

Recommended order:

1. `practice_plan.md` — session-level next action across all takes
2. `batch_report.md` — readable ranked summary and session decision
3. `session_manifest.json` — machine-readable entrypoints for the whole session folder
4. `batch_report.svg` — quickest visual ranking overview
5. `batch_report.csv` — spreadsheet-friendly comparison
6. one of the per-take `practice_plan.md`, `report.md`, or `report.svg` files for deeper inspection

### How to use the batch result

A practical review loop looks like this:

1. Open `practice_plan.md` to see the session goal and recommended loops
2. Open `batch_report.md` to confirm the best take, weakest take, and score deltas
3. Open the best take’s `report.md` to see why it won
4. Open the weakest take’s `practice_plan.md` to understand what to fix first

## 4. Run a practice session

```bash
practicelens practice-session \
  --reference samples/reference.wav \
  --take samples/take_01.wav \
  --take samples/take_02.wav \
  --take samples/take_03.wav \
  --out out/session
```

`practice-session` writes the same artifact set as `compare-batch`, but its CLI output is optimized for the musician workflow:

- best take;
- weakest take;
- recurring weakness;
- next recording target;
- generated `practice_plan.md` path.

Use this command when your intent is not only to rank takes, but to decide what to practice before recording the next take.

### Optional session history index

`practice-session` can append one compact JSONL entry to an explicit history index:

```bash
practicelens practice-session \
  --reference samples/reference.wav \
  --take samples/take_01.wav \
  --take samples/take_02.wav \
  --take samples/take_03.wav \
  --out out/session \
  --history-index .practicelens/sessions/index.jsonl
```

This index is opt-in. PracticeLens does not write it unless `--history-index` is provided.

## 5. List indexed practice sessions

```bash
practicelens sessions list
```

By default this reads:

```text
.practicelens/sessions/index.jsonl
```

For a custom index path:

```bash
practicelens sessions list \
  --history-index .practicelens/sessions/index.jsonl
```

Example output:

```text
2026-05-16  out/session-a  best=take_02.wav  score=88.4  focus=rhythm_fidelity
2026-05-17  out/session-b  best=take_03.wav  score=90.1  focus=timing_consistency
```

## 6. Show one practice session

```bash
practicelens sessions show out/session
```

You can also pass a manifest file directly:

```bash
practicelens sessions show out/session/session_manifest.json
```

Or show an indexed session by 1-based id:

```bash
practicelens sessions show 1 \
  --history-index .practicelens/sessions/index.jsonl
```

The output includes the best take, weakest take, recurring weakness, next recording target, `practice_plan.md`, and `batch_report.md` paths.

## 7. Useful tuning flags

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

## 8. What “good usage” looks like

A good practical path is:

- use single analysis when you want to understand one take deeply;
- use batch comparison when you want to decide which take to keep;
- use practice-session when you want the next concrete practice action across several takes;
- use `--history-index` when you want to build a local practice history intentionally;
- use `sessions list` when you want to see previous indexed practice sessions;
- use `sessions show` when you want to reopen one session through its manifest;
- use practice plans first when you want action;
- use SVG first when you want a glanceable visual review;
- use Markdown next for explanation;
- use JSON/CSV when you want structure or external tooling.

## 9. If you just want to browse example outputs

Use the illustrative snapshots already in the repo:

- `examples/results/single/`
- `examples/results/batch/`

These are useful when you want to understand the artifact shapes before running your own audio.