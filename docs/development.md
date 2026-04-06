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

If you only want the split commands:

```bash
make lint
make test
```

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
- changelog has been updated for meaningful user-facing changes.

## Common commands

```bash
make install-dev
make install-api
make lint
make test
make check
```
