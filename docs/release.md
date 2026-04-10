# Release Notes

This project is still pre-alpha, so the release process should stay lightweight.

The goal is not ceremony.
The goal is to avoid silent drift between package metadata, API version reporting, and what CI actually verifies.

## Single source of truth for versioning

Package version lives in:

```text
src/practicelens/__about__.py
```

That version is consumed by:

- package metadata via `pyproject.toml`;
- `practicelens.__version__`;
- API app version metadata;
- `/health` version reporting.

If you want to cut a new version, change it there first.

## Minimal release flow

1. Update `src/practicelens/__about__.py`
2. Update `CHANGELOG.md`
3. Run local checks
4. Build the package locally
5. Make sure CI is green
6. Tag and publish only when the state is actually shareable

## Local commands

```bash
make check
make regression
make build-package
```

Direct build command:

```bash
python -m build
```

## What CI now proves

CI should prove at least this much:

- lint passes;
- tests pass;
- the package can build as both sdist and wheel.

That is still not a full release guarantee.
But it is a much stronger signal than only checking source-tree execution.

## Practical reminder

Do not bump the version just because code changed.
Bump it when the externally meaningful state of the package changed enough to justify a new release marker.
