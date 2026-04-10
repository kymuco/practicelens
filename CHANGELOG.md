# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog, and the project currently follows a pragmatic pre-alpha flow rather than strict semantic release discipline.

## [Unreleased]

### Added

- Package/release discipline improvements: centralized version source, CI build smoke, and release notes.

## [0.1.0a0] - 2026-04-06

### Added

- Core domain contracts and bounded analysis model.
- WAV loading and preprocessing primitives.
- Deterministic feature extraction.
- Reference-aware DTW alignment.
- Explainable component scoring and section synthesis.
- JSON and Markdown report rendering.
- Offline analysis pipeline.
- CLI support for single-take analysis.
- CSV and SVG artifact generation.
- Batch comparison across multiple takes.
- Optional API surface for single and batch analysis.
- Typed API payload contracts and explicit error payloads.
- GitHub Actions CI.
- GitHub trust surface improvements: contributing guide, security policy, templates, quickstart, and examples.

### Notes

- This is still a bounded pre-alpha baseline.
- Current scoring is deterministic and explainable by design.
- The project is optimized for local-first, offline, monophonic or near-monophonic workflows first.
