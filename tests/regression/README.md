# Regression Harness

This directory contains **sanity-style regression checks** for PracticeLens.

These tests are intentionally lightweight.

They are not trying to prove scientific correctness.
They are trying to catch accidental drift in:

- score ordering;
- top-level score sanity;
- expected ranking behavior for simple synthetic cases;
- expected top-level artifact coverage for batch outputs;
- broad behavior on generated evaluation cases.

## Why this exists

The project already has working integration tests, but those mostly confirm that flows run and artifacts exist.

Regression checks add another layer:

- the best take should still be the best take;
- a perfect synthetic reference match should not suddenly look mediocre;
- a clearly shifted take should still score worse than an exact match;
- the batch pipeline should not silently stop emitting expected artifacts like SVG;
- generated evaluation cases should remain analyzable and preserve broad calibration expectations.

## Calibration expectations

`evaluation_expectations.json` stores broad, non-fragile expectations for generated evaluation assets.

These expectations are intentionally looser than exact score snapshots. They should catch obvious scoring drift without pretending PracticeLens already has a scientific benchmark suite.

Prefer expectations such as:

- minimum broad score bands for control cases;
- relative comparisons against a baseline case;
- required report structure like sections and artifacts.

Avoid expectations such as:

- exact floating-point scores;
- overly tight metric bands;
- assumptions that would make harmless scoring refactors painful.

## Scope

Current cases are synthetic and intentionally small:

- exact reference match;
- exact match vs shifted single-take comparison;
- three-take ranking sanity;
- batch artifact-kind coverage;
- generated evaluation assets with broad calibration expectations.

This is enough to catch many obvious regressions without pretending the project already has a full benchmark suite.
