# Regression Harness

This directory contains **sanity-style regression checks** for PracticeLens.

These tests are intentionally lightweight.

They are not trying to prove scientific correctness.
They are trying to catch accidental drift in:

- score ordering;
- top-level score sanity;
- expected ranking behavior for simple synthetic cases;
- expected top-level artifact coverage for batch outputs.

## Why this exists

The project already has working integration tests, but those mostly confirm that flows run and artifacts exist.

Regression checks add another layer:

- the best take should still be the best take;
- a perfect synthetic reference match should not suddenly look mediocre;
- a clearly shifted take should still score worse than an exact match;
- the batch pipeline should not silently stop emitting expected artifacts like SVG.

## Scope

Current cases are synthetic and intentionally small:

- exact reference match;
- exact match vs shifted single-take comparison;
- three-take ranking sanity;
- batch artifact-kind coverage.

This is enough to catch many obvious regressions without pretending the project already has a full benchmark suite.
