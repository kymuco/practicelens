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
| Single-take CLI analysis | Working |
| Multi-take batch comparison | Working |
| Optional FastAPI surface | Working |
| GitHub Actions CI | Working |

This is still **pre-alpha**, but it is already a real bounded vertical slice, not just a project shell.

## Evaluate it quickly

If you want to understand the repo in a few minutes, use this order:

1. [Quickstart](docs/quickstart.md)
2. [Architecture overview](docs/architecture.md)
3. [Repository map](docs/repository-map.md)
4. [API notes](docs/api.md)
5. [Examples](examples/api) and [CLI notes](examples/cli/README.md)

If you want a sharper evaluator path, use [docs/evaluate.md](docs/evaluate.md).

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
- Evaluate the repo: [docs/evaluate.md](docs/evaluate.md)
- Architecture overview: [docs/architecture.md](docs/architecture.md)
- Repository map: [docs/repository-map.md](docs/repository-map.md)
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
- per-take artifact folders under `out/takes/`

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

CI runs the same baseline checks on pushes to `main` and on pull requests.

For a more practical maintainer view, see [docs/development.md](docs/development.md).

## Project principles

- **Local-first**: the tool should be useful without cloud infrastructure.
- **Actionable output**: reports should help practice decisions, not just produce numbers.
- **Signal processing first, ML second**: solid features come before model hype.
- **Clear interfaces**: the project should evolve cleanly into CLI and API layers.
- **Extensible design**: future scoring models should fit on top of the core pipeline, not replace it chaotically.

## Roadmap direction

Near-term work should focus on:

- stronger evaluation examples and demo assets;
- higher-confidence reporting UX;
- more polished API and artifact ergonomics;
- future model-assisted scoring on top of the deterministic baseline.

## License

Apache License 2.0.
