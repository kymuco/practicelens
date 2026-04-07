# PracticeLens API Notes

PracticeLens exposes an optional FastAPI app surface.

The current API is intentionally simple:

- `GET /health`
- `POST /analyze`
- `POST /compare-batch`

## Fastest way to run it locally

Install API extras first:

```bash
pip install -e .[dev,api]
```

Then run the packaged app directly:

```bash
uvicorn practicelens.api.app:app --reload
```

Or use the local helper target:

```bash
make run-api
```

Default local address:

```text
http://127.0.0.1:8000
```

## Quick smoke check

```bash
curl http://127.0.0.1:8000/health
```

Expected response shape:

```json
{
  "status": "ok",
  "service": "practicelens-api",
  "version": "0.1.0a0"
}
```

## Example payload files in this repo

- `examples/api/analyze_payload.json`
- `examples/api/compare_batch_payload.json`
- `examples/api/curl_examples.sh`
- `examples/api/practicelens.http`

These are meant as copyable starting points for local use and manual testing.

## POST /analyze

Runs single-take analysis.

Example payload:

```json
{
  "reference_path": "reference.wav",
  "take_path": "take.wav",
  "out_dir": "out",
  "sample_rate": 16000,
  "frame_length": 2048,
  "hop_length": 512,
  "segment_duration": 8.0
}
```

Top-level response fields:

- `overview`
- `inputs`
- `feature_flags`
- `overall_score`
- `scores`
- `metrics`
- `sections`
- `feedback`
- `artifacts`
- `summary`

Runnable `curl` example:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  --data @examples/api/analyze_payload.json
```

## POST /compare-batch

Runs batch comparison for one reference against multiple takes.

Example payload:

```json
{
  "reference_path": "reference.wav",
  "take_paths": ["take_a.wav", "take_b.wav", "take_c.wav"],
  "out_dir": "batch-out",
  "sample_rate": 16000,
  "frame_length": 2048,
  "hop_length": 512,
  "segment_duration": 8.0
}
```

Top-level response fields:

- `reference_path`
- `summary`
- `entries`
- `artifacts`

Each `entries[]` item includes:

- `rank`
- `take_path`
- `overall_score`
- `summary`
- `output_dir`
- `artifacts`

Runnable `curl` example:

```bash
curl -X POST http://127.0.0.1:8000/compare-batch \
  -H "Content-Type: application/json" \
  --data @examples/api/compare_batch_payload.json
```

## Error shape

Bad payloads currently return a JSON error response with this general shape:

```json
{
  "error": "bad_request",
  "message": "...",
  "code": "invalid_payload"
}
```

## Notes

- Replace example file paths with your own local WAV paths.
- The example payloads are for local use and manual smoke testing.
- The `.http` file is useful if your editor or IDE supports HTTP request execution.
