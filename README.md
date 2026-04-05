# PracticeLens

![CI](https://github.com/kymuco/practicelens/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

**PracticeLens** is a local-first audio practice analysis tool for singing and instrument takes.

It helps musicians turn raw practice recordings into precise, actionable feedback by analyzing pitch, rhythm, timing, alignment, section consistency, and take ranking against a reference.

## Why this project exists

Practice recordings usually answer only one vague question: **"did that sound good?"**

PracticeLens aims to answer the questions that actually matter during improvement:

- where timing drift starts;
- where pitch becomes unstable;
- which phrases are rhythmically weak;
- which sections need focused repetition;
- which of several takes is actually the strongest;
- how a take differs from a reference recording.

## Current repository status

The repository already includes a bounded working vertical slice with:

- WAV loading and preprocessing;
- deterministic feature extraction;
- reference-aware DTW alignment;
- explainable scoring;
- JSON, Markdown, CSV, and SVG report artifacts;
- offline single-take analysis;
- batch comparison across multiple takes;
- a CLI surface;
- an optional FastAPI app surface;
- GitHub Actions CI for lint and tests.

This is not a final DSP product yet, but it is no longer just a skeleton repo.

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

## Repository conventions

- Keep PRs small and reviewable.
- Prefer additive changes over broad rewrites.
- Preserve CLI and API behavior unless the PR explicitly updates contracts.
- Avoid placeholder production paths.
- Prefer clear artifacts and explainable outputs over opaque magic.

## Project principles

- **Local-first**: the tool should be useful without cloud infrastructure.
- **Actionable output**: reports should help practice decisions, not just produce numbers.
- **Signal processing first, ML second**: solid features come before model hype.
- **Clear interfaces**: the project should evolve cleanly into CLI and API layers.
- **Extensible design**: future scoring models should fit on top of the core pipeline, not replace it chaotically.

## Potential use cases

- vocal take review;
- guitar practice feedback;
- reference-vs-take comparison;
- repeated section analysis;
- ranking multiple takes;
- building datasets for future learned scoring models.

## Roadmap direction

Near-term work should focus on:

- stronger API contracts and examples;
- higher-confidence reporting UX;
- better repo ergonomics and contributor trust;
- future model-assisted scoring on top of the current deterministic baseline.

## Contributing and security

- Contribution flow: see [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: see [SECURITY.md](SECURITY.md)

## License

Apache License 2.0.
