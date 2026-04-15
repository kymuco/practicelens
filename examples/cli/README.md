# CLI Examples

These examples are meant to show the current local-first workflow shape.

For the full end-to-end story, use:

- [docs/cli_walkthrough.md](../../docs/cli_walkthrough.md)

Before running the CLI examples below, generate the demo WAV assets:

```bash
make generate-demo-assets
```

## Single analysis

```bash
practicelens analyze \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take.wav \
  --out out/demo/single
```

## Batch comparison

```bash
practicelens compare-batch \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take_01.wav \
  --take examples/demo_assets/generated/take_02.wav \
  --take examples/demo_assets/generated/take_03.wav \
  --out out/demo/batch
```

## What to open first

Single analysis:

1. `report.svg`
2. `report.md`
3. `report.csv`
4. `report.json`

Batch comparison:

1. `batch_report.svg`
2. `batch_report.md`
3. `batch_report.csv`
4. per-take `report.md` / `report.svg`

## Notes

- The repository does not commit real demo WAV files.
- Use the generator under `examples/demo_assets/` to create deterministic synthetic demo assets.
- Outputs are written into the selected `--out` directory.
