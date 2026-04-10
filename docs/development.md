# Development Guide

This project is intentionally small enough to move quickly, but already large enough that consistency matters.

## Local setup

Base development setup:

```bash
pip install -e .[dev]
```

Optional API extras:

```bash
pip install -e .[dev,api]
```

## Main local checks

```bash
ruff check .
pytest tests
```

## Recommended daily loop

```bash
make check
```

If you want the regression-only sanity layer:

```bash
make regression
```

If you want a package build smoke locally:

```bash
make build-package
```

If you only want the split commands:

```bash
make lint
make test
make regression
make build-package
```

## Version source of truth

Package version is defined in:

```text
src/practicelens/__about__.py
```

That version is reused by package metadata and the optional API surface.

## Regression harness

The regression harness is intentionally lightweight.

It is meant to catch obvious drift in:

- ranking order;
- top-level score sanity;
- simple synthetic reference-match expectations.

It is **not** trying to present itself as a final benchmark suite.

## Current repository shape

The project currently has four practical user-facing layers:

- offline single-take analysis;
- batch comparison across takes;
- CLI workflows;
- optional API workflows.

When changing the repo, be careful around:

- CLI flags and command names;
- API request and response shapes;
- report artifact names;
- scoring semantics;
- generated output layout.

## PR guidance

- Keep PRs focused.
- Prefer additive changes over broad rewrites.
- Say clearly whether contracts changed.
- Mention artifact changes explicitly.
- Run lint and tests before opening the PR.

## Release/readiness expectations

This repository is still pre-alpha, but it should still feel disciplined.

Before cutting a release-like milestone or sharing the repo more broadly, check:

- CI is green;
- README is still accurate;
- quickstart and example files still match reality;
- API docs still reflect actual request/response shapes;
- changelog has been updated for meaningful user-facing changes;
- package build smoke passes.

## Common commands

```bash
make install-dev
make install-api
make lint
make test
make regression
make build-package
make check
```
