# Repository Map

This file gives a practical overview of what currently lives where in PracticeLens.

## Top-level structure

- `src/practicelens/` — application code
- `tests/` — unit and integration tests
- `docs/` — quickstart, API notes, architecture, development docs
- `examples/` — copyable CLI and API example files
- `.github/` — CI and collaboration templates

## Source tree

### `src/practicelens/application/`

User-facing orchestration workflows.

Current responsibilities:

- single-take analysis request/result flow;
- batch comparison request/result flow;
- offline orchestration pipelines.

### `src/practicelens/io/`

Local audio loading and validation.

Current responsibilities:

- WAV loading;
- loaded audio representation;
- finite-sample checks.

### `src/practicelens/preprocessing/`

Basic signal normalization helpers.

Current responsibilities:

- peak normalization;
- resampling;
- silence trimming.

### `src/practicelens/features/`

Deterministic feature extraction.

Current responsibilities:

- feature bundle models;
- pitch, energy, onset, tempo-oriented extraction steps.

### `src/practicelens/alignment/`

Reference-aware comparison between feature bundles.

Current responsibilities:

- alignment path models;
- DTW-style matching.

### `src/practicelens/scoring/`

Explainable scoring built on aligned evidence.

Current responsibilities:

- component scores;
- metric summaries;
- section findings and section reports.

### `src/practicelens/reporting/`

Artifact generation and serializer-like reporting helpers.

Current responsibilities:

- single-analysis JSON/Markdown/CSV/SVG rendering;
- batch comparison report rendering;
- artifact writing helpers.

### `src/practicelens/api/`

Optional API-facing layer.

Current responsibilities:

- payload contracts;
- payload parsing/builders;
- explicit API error payload shape;
- optional FastAPI app.

### `src/practicelens/cli/`

Command-line surface.

Current responsibilities:

- `analyze` command;
- `compare-batch` command.

### `src/practicelens/domain/`

Stable cross-layer enums, models, and error types.

Current responsibilities:

- analysis mode and metric enums;
- report model objects;
- shared typed values.

## Tests

### `tests/unit/`

Fast, focused checks for isolated logic.

### `tests/integration/`

Higher-level flows covering:

- offline analysis pipeline;
- batch comparison pipeline;
- CLI command behavior.

## Docs and examples

### `docs/`

Human-facing project guidance.

Current docs:

- `quickstart.md`
- `api.md`
- `development.md`
- `architecture.md`
- `repository-map.md`

### `examples/`

Copyable payloads and usage notes.

Current examples:

- CLI usage notes;
- API payload examples.

## Practical reading order

If you are new to the repo, the quickest path is:

1. `README.md`
2. `docs/quickstart.md`
3. `docs/architecture.md`
4. `src/practicelens/application/`
5. `src/practicelens/reporting/`
6. `tests/integration/`

That order usually gives the fastest understanding of both the user flow and the internal boundaries.
