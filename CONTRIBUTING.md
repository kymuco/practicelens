# Contributing to PracticeLens

Thanks for contributing.

This repository is still early, but it already has a working vertical slice and CI, so changes should aim to keep the project stable while it grows.

## Ground rules

- Keep pull requests focused and reviewable.
- Prefer additive changes over broad rewrites.
- Do not introduce placeholder production paths.
- Preserve existing CLI and API behavior unless the PR explicitly changes contracts.
- Keep report outputs explainable and deterministic unless the PR is intentionally about model-assisted scoring.

## Local setup

```bash
pip install -e .[dev]
```

Optional API extras:

```bash
pip install -e .[dev,api]
```

## Checks before opening a PR

```bash
ruff check .
pytest tests
```

## Branch and PR style

- Use descriptive branch names.
- Prefer small PRs over dump-style mega-PRs.
- Include a clear summary of what changed and what did not.
- Mention any contract changes explicitly.
- If a change affects artifacts, CLI, or API behavior, say so directly in the PR description.

## Commit style

Use scoped, meaningful commits when possible, for example:

- `feat(batch): add multi-take comparison pipeline`
- `feat(api): add batch comparison endpoint`
- `test(cli): cover compare-batch flow`
- `docs(readme): refresh usage examples`
- `ci(github): add baseline workflow`

## Areas where consistency matters most

Please be especially careful around:

- analysis contracts and report fields;
- CLI commands and flags;
- API payload shape;
- artifact filenames and meanings;
- scoring semantics.

## If you are unsure

Open a smaller PR first instead of trying to solve everything in one shot.
