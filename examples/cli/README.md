# CLI Examples

These examples are meant to show the current local-first workflow shape.

## Fastest practical path

If you want the shortest path from WAV files to artifacts, use:

- `docs/cli-walkthrough.md`
- `examples/cli/run_demo.sh`

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

## What to open first after running

Single analysis:

- `out/single/report.svg`
- `out/single/report.md`

Batch comparison:

- `out/batch/batch_report.svg`
- `out/batch/batch_report.md`

## Notes

- The repository does not currently ship real demo WAV files.
- Replace the example paths with your own local WAV files.
- Outputs are written into the selected `--out` directory.
