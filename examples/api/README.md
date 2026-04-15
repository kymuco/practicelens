# API Example Payloads and Requests

This directory contains copyable example payloads and runnable request examples for the optional API layer.

Files:

- `analyze_payload.json`
- `compare_batch_payload.json`
- `curl_examples.sh`
- `practicelens.http`

These examples are intended for:

- manual local testing;
- documentation reference;
- quick integration smoke tests;
- editor-based request execution for people using HTTP client plugins.

Typical flow:

1. Generate demo WAV assets with `make generate-demo-assets` or `python tools/generate_demo_assets.py`
2. Start the API with `make run-api` or `uvicorn practicelens.api.app:app --reload`
3. Execute the example payloads and requests in this directory

The example JSON payloads already point at `examples/demo_assets/generated/`, so they become directly runnable after you generate the demo assets.
