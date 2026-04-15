# Demo Asset Generator

PracticeLens does **not** store real practice audio in the repository.

Instead, it ships a deterministic generator for small synthetic demo WAV files.

Use it when you want:

- a reproducible local CLI demo;
- a reproducible API smoke flow;
- fast onboarding without hunting for your own WAVs first;
- bounded test fixtures without committing third-party audio.

## Generate the demo assets

```bash
make generate-demo-assets
```

Or run the script directly:

```bash
python tools/generate_demo_assets.py
```

Default output directory:

```text
examples/demo_assets/generated/
```

Generated files:

- `reference.wav`
- `take.wav`
- `take_01.wav`
- `take_02.wav`
- `take_03.wav`
- `manifest.json`

`manifest.json` explains the intended role of each demo take.

## Reproducible CLI demo

```bash
practicelens analyze \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take.wav \
  --out out/demo/single
```

```bash
practicelens compare-batch \
  --reference examples/demo_assets/generated/reference.wav \
  --take examples/demo_assets/generated/take_01.wav \
  --take examples/demo_assets/generated/take_02.wav \
  --take examples/demo_assets/generated/take_03.wav \
  --out out/demo/batch
```

## Reproducible API demo

After generating the assets, the example payloads under `examples/api/` point at the generated WAV paths.

That means you can run the API examples directly after:

1. generating demo assets;
2. starting the API;
3. executing the example requests.
