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

1. Start the API with `make run-api` or `uvicorn practicelens.api.app:app --reload`
2. Adjust local WAV paths inside the JSON payloads
3. Run the shell examples or execute the `.http` requests from your editor

Replace the file paths with your own local WAV paths before using them.
