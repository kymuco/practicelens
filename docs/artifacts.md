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
- `analysis_confidence`
- `practice_loops`
- `top_strengths`
- `top_weaknesses`
- `next_practice_step`
- `feedback`
- `artifacts`
- `summary`

Stable top-level fields for `batch_report.json`:

- `overview`
- `reference_path`
- `summary`
- `session_summary`
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

### `practice_plan.md`

Use this when you want the shortest path from analysis to action.

Best for:

- deciding what to practice next;
- seeing what to keep stable while improving the weakest area;
- following focused loop recommendations before recording another take.

This artifact is derived from the same report data as `report.md`, but it is intentionally more action-oriented: goal, current snapshot, keep/improve notes, practice loops, next recording target, and confidence notes.

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

Use this for machine-readable ranking and session decisions across multiple takes.

Best for:

- integrations;
- ranking pipelines;
- future evaluation tooling;
- dashboards that need stable session-level fields.

The `session_summary` field is the compact structured contract for the whole comparison session. It includes the best take, weakest take, recurring weakness, strongest stable area, next recording target, and selected practice loops.

Each per-take output folder under `takes/` also contains the normal single-take artifacts, including `practice_plan.md`.

### `batch_report.md`

Use this for human review of multiple takes.

Best for:

- quick decision-making;
- reviewing which take came out strongest;
- understanding score differences at a glance.

### `practice_plan.md`

Use this when you want one session-level practice plan across all compared takes.

Best for:

- choosing the best take to keep;
- identifying the recurring weakness across takes;
- seeing the strongest stable area to preserve;
- picking the top practice loops from weaker takes;
- setting the next recording target.

This batch-level plan is different from the per-take `takes/<take>/practice_plan.md` files. The top-level plan summarizes the whole comparison session and is derived from `session_summary`.

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

### If you want to practice immediately

Start with:

1. `practice_plan.md`
2. then read `report.md` if you want the supporting details

### If you are comparing many takes

Start with:

1. top-level `practice_plan.md`
2. then `batch_report.md`
3. then per-take `practice_plan.md` files under `takes/`

## Practical advice

- Use Markdown when you want the result explained.
- Use `practice_plan.md` when you want the next concrete practice action.
- Use CSV when you want to compare rows quickly.
- Use JSON when you want stable machine-readable structure.
- Use SVG when you want the fastest visual summary.