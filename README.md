# PracticeLens

**PracticeLens** is a local-first audio practice analysis tool for singing and instrument takes.

It helps musicians turn raw practice recordings into precise, actionable feedback by analyzing pitch, rhythm, timing, alignment, and take consistency.

## Why this project exists

Practice recordings usually answer only one vague question: "did that sound good?"

PracticeLens aims to answer the questions that actually matter during improvement:

- where timing drift starts;
- where pitch becomes unstable;
- which phrases are rhythmically weak;
- which sections need focused repetition;
- how a take differs from a reference recording.

## Current v0.1 baseline

The current repository now includes a bounded local-first analysis vertical slice:

- WAV loading and preprocessing;
- deterministic feature extraction;
- reference-aware DTW alignment;
- explainable scoring;
- JSON and Markdown report rendering;
- an offline pipeline;
- a CLI `analyze` command;
- an optional FastAPI app surface.

## Core idea

Given a user take and, optionally, a reference recording, PracticeLens extracts audio features, aligns comparable sections, computes quality-oriented metrics, and generates feedback that is both machine-readable and human-readable.

The longer-term goal is to provide a strong foundation for:

- a command-line workflow;
- a lightweight API service;
- future desktop or creator-tool integrations;
- ML-based quality scoring on top of robust signal-processing features.

## Current scope

PracticeLens v0.1 is intentionally bounded.

Current expectations:

- local-first execution;
- offline reference-based analysis;
- monophonic or near-monophonic material first;
- explainable component scoring instead of one opaque score.

Current non-goals:

- realtime feedback;
- polyphonic-first analysis;
- end-to-end learned scoring;
- artistic judgment or interpretation scoring.

## CLI usage

After installation, the current CLI entry point is:

```bash
practicelens analyze \
  --reference path/to/reference.wav \
  --take path/to/take.wav \
  --out out/
```

Optional tuning flags currently include:

- `--sample-rate`
- `--frame-length`
- `--hop-length`
- `--segment-duration`

The command writes:

- `report.json`
- `report.md`

## Optional API usage

PracticeLens also exposes an API-friendly service layer and an optional FastAPI app.

Install the API extra to use the HTTP app surface.

Example app import:

```python
from practicelens.api.app import create_app

app = create_app()
```

Example payload shape:

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

## Principles

- **Local-first**: the tool should be useful without requiring cloud infrastructure.
- **Actionable output**: reports should help practice decisions, not just produce numbers.
- **Signal processing first, ML second**: solid features come before model hype.
- **Clear interfaces**: the project should evolve cleanly into CLI and API layers.
- **Extensible design**: future scoring models should fit on top of the core pipeline, not replace it chaotically.

## Potential use cases

- vocal take review;
- guitar practice feedback;
- reference-vs-take comparison;
- repeated section analysis;
- building datasets for future learned scoring models.

## Planned outputs

PracticeLens currently produces and is expected to keep evolving around outputs such as:

- pitch stability metrics;
- rhythm deviation metrics;
- onset mismatch summaries;
- timing drift indicators;
- phrase-level difficulty or inconsistency markers;
- human-readable practice recommendations.

## Status

The repository has moved beyond the project-definition phase and now has a bounded working vertical slice for offline reference-aware analysis.

The next work should focus on strengthening service and integration surfaces, not on pretending the current DSP stack is already final.

## License

Apache License 2.0.
