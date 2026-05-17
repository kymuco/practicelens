# PracticeLens

![CI](https://github.com/kymuco/practicelens/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

**PracticeLens** is a local-first audio practice analysis tool for singing and instrument takes.

It helps musicians turn raw practice recordings into precise, actionable feedback by analyzing pitch, rhythm, timing, alignment, section consistency, and take ranking against a reference.

## What it is, in one line

PracticeLens answers a more useful question than **"did that sound good?"**:

**where exactly did this take diverge from the reference, and which of several takes is actually the strongest?**

## Why this project exists

Practice recordings usually leave musicians with fuzzy self-judgment.

PracticeLens aims to make that loop sharper by showing:

- where timing drift starts;
- where pitch becomes unstable;
- which phrases are rhythmically weak;
- which sections need focused repetition;
- which of several takes is actually the strongest;
- how a take differs from a reference recording.

## What works today

| Area | Current status |
| --- | --- |
| WAV loading and preprocessing | Working |
| Deterministic feature extraction | Working |
| Reference-aware DTW alignment | Working |
| Explainable scoring | Working |
| JSON / Markdown / CSV / SVG artifacts | Working |
| Practice plans and diagnostics artifacts | Working |
| Single-take CLI analysis | Working |
| Multi-take batch comparison | Working |
| Practice-session CLI review | Working |
| Optional FastAPI surface | Working |
| GitHub Actions CI | Working |

This is still **pre-alpha**, but it is already a real bounded vertical slice, not just a project shell.

## Evaluate it quickly

If you want to understand the repo in a few minutes, use this order:

1. [Quickstart](docs/quickstart.md)
2. Generate the [evaluation showcase](examples/evaluation_showcase/README.md)
3. Review the generated outputs with the [showcase review checklist](docs/showcase_review.md)
4. [Architecture overview](docs/architecture.md)
5. [Repository map](docs/repository-map.md)
6. [API notes](docs/api.md)
7. [Examples](examples/api), [sample results](examples/results), and [CLI notes](examples/cli/README.md)

If you want a sharper evaluator path, use [docs/evaluate.md](docs/evaluate.md).

## Evaluation showcase

The fastest way to see PracticeLens behave end-to-end is to generate the synthetic evaluation showcase from the repository root:

```bash
make generate-evaluation-showcase
```

On Windows, `make` may not be installed by default. You can run the equivalent Python command instead:

```bash
python tools/generate_evaluation_showcase.py
```

This creates deterministic synthetic WAV assets, single-take reports, a batch comparison, and a compact summary under:

```text
examples/evaluation_showcase/generated/
```

Generated showcase files are local review artifacts and are intentionally not committed to the repository.

Start with:

- `examples/evaluation_showcase/generated/README.md`
- `examples/evaluation_showcase/generated/summary.json`
- `examples/evaluation_showcase/generated/batch/batch_report.md`
- `examples/evaluation_showcase/generated/single/pitch_drift_take/report.md`
- `examples/evaluation_showcase/generated/single/timing_drift_take/report.md`

Use [docs/showcase_review.md](docs/showcase_review.md) to judge whether the generated reports behave plausibly.

These examples are synthetic sanity demos, not a scientific benchmark. They exist so a reviewer can inspect the product behavior quickly without third-party audio files.

## Why this repo feels trustworthy

The repo already includes:

- CI for lint and tests;
- explicit contribution and security docs;
- typed API payload contracts;
- deterministic and explainable report outputs;
- quickstart, architecture, API, and development documentation;
- copyable CLI and API examples.

That does not make the project finished.
It does make it reviewable, understandable, and much harder to mistake for a random code dump.

## Start here

- Quickstart: [docs/quickstart.md](docs/quickstart.md)
- Evaluation showcase: [examples/evaluation_showcase/README.md](examples/evaluation_showcase/README.md)
- Showcase review checklist: [docs/showcase_review.md](docs/showcase_review.md)
- CLI walkthrough: [docs/cli_walkthrough.md](docs/cli_walkthrough.md)
- Evaluate the repo: [docs/evaluate.md](docs/evaluate.md)
- Architecture overview: [docs/architecture.md](docs/architecture.md)
- Repository map: [docs/repository-map.md](docs/repository-map.md)
- Artifact guide: [docs/artifacts.md](docs/artifacts.md)
- Sample result snapshots: [examples/results](examples/results)
- API usage and payloads: [docs/api.md](docs/api.md)
- Development workflow: [docs/development.md](docs/development.md)
- Roadmap snapshot: [docs/roadmap.md](docs/roadmap.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- CLI example notes: [examples/cli/README.md](examples/cli/README.md)
- Example API payloads: [examples/api](examples/api)
- Contribution flow: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: [SECURITY.md](SECURITY.md)

## Core idea

Given a user take and a reference recording, PracticeLens extracts audio features, aligns comparable sections, computes quality-oriented metrics, and generates feedback that is both machine-readable and human-readable.

The project is designed to become a solid foundation for:

- local CLI workflows;
- lightweight API service usage;
- creator-tool integrations;
- future ML-based quality scoring on top of robust signal-processing features.

## Current scope

PracticeLens v0.1 is intentionally bounded.

### Current expectations

- local-first execution;
- offline reference-based analysis;
- monophonic or near-monophonic material first;
- explainable component scoring instead of one opaque score;
- single-take and multi-take comparison workflows.

### Current non-goals

- realtime feedback;
- polyphonic-first analysis;
- end-to-end learned scoring;
- artistic judgment or interpretation scoring.

## Installation

```bash
pip install -e .[dev]
```

Optional API extras:

```bash
pip install -e .[dev,api]
```

## CLI usage

### Analyze one take

```bash
practicelens analyze \
  --reference path/to/reference.wav \
  --take path/to/take.wav \
  --out out/
```

Outputs:

- `report.json`
- `report.md`
- `report.csv`
- `report.svg`
- `practice_plan.md`
- `debug_payload.json`

### Compare multiple takes

```bash
practicelens compare-batch \
  --reference path/to/reference.wav \
  --take path/to/take_01.wav \
  --take path/to/take_02.wav \
  --take path/to/take_03.wav \
  --out out/
```

Batch outputs:

- `batch_report.json`
- `batch_report.md`
- `batch_report.csv`
- `batch_report.svg`
- `practice_plan.md`
- `session_manifest.json`
- per-take artifact folders under `out/takes/`

### Run a practice session

```bash
practicelens practice-session \
  --reference path/to/reference.wav \
  --take path/to/take_01.wav \
  --take path/to/take_02.wav \
  --take path/to/take_03.wav \
  --out out/session
```

`practice-session` uses the same analysis engine as `compare-batch`, but prints a session-oriented CLI summary: best take, weakest take, recurring weakness, next recording target, and the generated `practice_plan.md` path.

Optionally append one compact JSONL entry to an explicit session history index:

```bash
practicelens practice-session \
  --reference path/to/reference.wav \
  --take path/to/take_01.wav \
  --take path/to/take_02.wav \
  --take path/to/take_03.wav \
  --out out/session \
  --history-index .practicelens/sessions/index.jsonl
```

PracticeLens does not write this history index unless `--history-index` is provided.

### List indexed practice sessions

```bash
practicelens sessions list
```

By default this reads:

```text
.practicelens/sessions/index.jsonl
```

You can point it at a custom index:

```bash
practicelens sessions list \
  --history-index path/to/index.jsonl
```

Example output:

```text
2026-05-16  out/session-a  best=take_02.wav  score=88.4  focus=rhythm_fidelity
2026-05-17  out/session-b  best=take_03.wav  score=90.1  focus=timing_consistency
```

### Show one practice session

```bash
practicelens sessions show out/session
```

You can also pass a manifest file or an indexed session id:

```bash
practicelens sessions show out/session/session_manifest.json
practicelens sessions show 1 --history-index .practicelens/sessions/index.jsonl
```

Output includes the best take, weakest take, recurring weakness, next recording target, and paths to `practice_plan.md` and `batch_report.md`.

### Compare two practice sessions

```bash
practicelens sessions compare old/session new/session
```

You can also compare manifest files or indexed session ids:

```bash
practicelens sessions compare old/session/session_manifest.json new/session/session_manifest.json
practicelens sessions compare 1 2 --history-index .practicelens/sessions/index.jsonl
```

Example output:

```text
Overall score: +3.2
Recurring weakness: rhythm_fidelity -> timing_consistency
Best take: improved
Stable area: preserved (section_stability)
```

### Shared tuning flags

- `--sample-rate`
- `--frame-length`
- `--hop-length`
- `--segment-duration`

## Optional API usage

PracticeLens also exposes an API-friendly service layer and an optional FastAPI app.

Example app import:

```python
from practicelens.api.app import create_app

app = create_app()
```

### Single analysis payload

```json
{
  "reference_path": "reference.wav",
  "take_path": "take.wav",
  "out_dir": "out",
  "sample_rate": 16000,
  "frame_length": 2048,
  "hop_length": 512,
  "segment_duration": 8.0
}
```

### Batch comparison payload

```json
{
  "reference_path": "reference.wav",
  "take_paths": ["take_a.wav", "take_b.wav", "take_c.wav"],
  "out_dir": "batch-out",
  "sample_rate": 16000,
  "frame_length": 2048,
  "hop_length": 512,
  "segment_duration": 8.0
}
```

## Development workflow

```bash
ruff check .
pytest tests
```
