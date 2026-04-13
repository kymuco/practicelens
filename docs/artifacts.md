# Understanding PracticeLens Artifacts

PracticeLens currently produces a small set of artifact types for single-take analysis and batch comparison.

This guide explains what each artifact is good for.

## Stable JSON contract envelope

Both `report.json` and `batch_report.json` are versioned JSON artifacts.

Consumers should treat `overview.kind` and `overview.schema_version` as the dispatch keys for the payload shape instead of guessing based on filename or path.

Current envelopes:

- `report.json` → `overview.kind = "analysis_report"`, `overview.schema_version = 1`
- `batch_report.json` → `overview.kind = "batch_compare_report"`, `overview.schema_version = 1`

Stable top-level fields for `report.json`:

- `overview`
- `inputs`
- `feature_flags`
- `overall_score`
- `scores`
- `metrics`
- `sections`
- `feedback`
- `artifacts`
- `summary`

Stable top-level fields for `batch_report.json`:

- `overview`
- `reference_path`
- `summary`
- `entries`
- `artifacts`

This contract is intended to evolve additively. If a future breaking change becomes necessary, it should move through a new schema version instead of silently mutating the current shape.

## Single-take artifacts

### `report.json`

Use this when you want the full machine-readable result.

Best for:

- integrations;
- programmatic inspection;
- future dashboards or automation.

### `report.md`

Use this when you want a readable summary that a human can scan quickly.

Best for:

- quick review;
- sharing the result in plain text form;
- understanding the analysis structure.

### `report.csv`

Use this when you care about section-by-section comparisons and want something spreadsheet-friendly.

Best for:

- sorting and filtering sections;
- quick spreadsheet inspection;
- later plotting or aggregation.

### `report.svg`

Use this when you want a fast visual impression of the result.

Best for:

- glanceable score overview;
- showing component balance;
- lightweight visual demos.

## Batch artifacts

### `batch_report.json`

Use this for machine-readable ranking across multiple takes.

Best for:

- integrations;
- ranking pipelines;
- future evaluation tooling.

### `batch_report.md`

Use this for human review of multiple takes.

Best for:

- quick decision-making;
- reviewing which take came out strongest;
- understanding score differences at a glance.

### `batch_report.csv`

Use this when you want to inspect the ranked takes in a spreadsheet or other tabular tool.

Best for:

- sorting takes by score;
- comparing deltas from the best take;
- lightweight external analysis.

### `batch_report.svg`

Use this when you want the quickest visual overview of ranked takes.

Best for:

- showing best-take dominance at a glance;
- comparing deltas visually;
- demo browsing directly inside GitHub.

## Which artifact should you look at first?

### If you are a developer

Start with:

1. `report.json` or `batch_report.json`
2. then inspect Markdown, CSV, or SVG if needed

### If you are evaluating output quality visually

Start with:

1. `report.svg`
2. then read `report.md`

### If you are comparing many takes

Start with:

1. `batch_report.svg`
2. then `batch_report.md`
3. then `batch_report.csv`

## Practical advice

- Use Markdown when you want the result explained.
- Use CSV when you want to compare rows quickly.
- Use JSON when you want stable machine-readable structure.
- Use SVG when you want the fastest visual summary.
