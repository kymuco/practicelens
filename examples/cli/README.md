# CLI Examples

These examples are meant to show the current local-first workflow shape.

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

## Notes

- The repository does not currently ship real demo WAV files.
- Replace the example paths with your own local WAV files.
- Outputs are written into the selected `--out` directory.
