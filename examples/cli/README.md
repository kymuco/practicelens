# CLI Examples

These examples are meant to show the current local-first workflow shape.

For the full end-to-end story, use:

- [docs/cli_walkthrough.md](../../docs/cli_walkthrough.md)

## Single analysis

```bash
practicelens analyze \
  --reference samples/reference.wav \
  --take samples/take.wav \
  --out out/single
```

## Batch comparison

```bash
practicelens compare-batch \
  --reference samples/reference.wav \
  --take samples/take_01.wav \
  --take samples/take_02.wav \
  --take samples/take_03.wav \
  --out out/batch
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

- The repository does not currently ship real demo WAV files.
- Replace the example paths with your own local WAV files.
- Outputs are written into the selected `--out` directory.
