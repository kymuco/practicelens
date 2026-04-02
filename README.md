# PracticeLens

**PracticeLens** is a local-first audio practice analysis tool for singing and instrument takes.

It is designed to help musicians turn raw practice recordings into precise, actionable feedback by analyzing pitch, rhythm, timing, alignment, and take consistency.

## Why this project exists

Practice recordings usually answer only one vague question: "did that sound good?"

PracticeLens aims to answer the questions that actually matter during improvement:

- where timing drift starts;
- where pitch becomes unstable;
- which phrases are rhythmically weak;
- which sections need focused repetition;
- how a take differs from a reference recording.

## Core idea

Given a user take and, optionally, a reference recording, PracticeLens will extract audio features, align comparable sections, compute quality-oriented metrics, and generate feedback that is both machine-readable and human-readable.

The long-term goal is to provide a strong foundation for:

- a command-line workflow;
- a lightweight API service;
- future desktop or creator-tool integrations;
- ML-based quality scoring on top of robust signal-processing features.

## Initial scope

The first milestone focuses on a practical MVP rather than fake AI theater.

Planned MVP capabilities:

- load a reference take and a user take;
- extract pitch, onset, tempo, and timing features;
- compare the two takes with alignment-aware analysis;
- report weak sections and unstable passages;
- export structured reports as JSON and readable summaries as Markdown.

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

PracticeLens is expected to eventually produce outputs such as:

- pitch stability metrics;
- rhythm deviation metrics;
- onset mismatch summaries;
- timing drift indicators;
- phrase-level difficulty or inconsistency markers;
- human-readable practice recommendations.

## Status

This repository is currently in the project-definition phase.

The README establishes the product intent and scope first. The implementation architecture, repository structure, and MVP execution plan will be defined next.

## License

Apache License 2.0.
