# PracticeLens API Notes

PracticeLens exposes an optional FastAPI app surface.

The current API is intentionally simple:

- `GET /health`
- `POST /analyze`
- `POST /compare-batch`

## Running the app

```python
from practicelens.api.app import create_app

app = create_app()
```

Example with uvicorn:

```bash
uvicorn your_module:app --reload
```

## Health endpoint

Returns a small status payload.

Example response shape:

```json
{
  "status": "ok",
  "service": "practicelens-api",
  "version": "0.1.0a0"
}
```

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

## Error shape

Bad payloads currently return a JSON error response with this general shape:

```json
{
  "error": "bad_request",
  "message": "...",
  "code": "invalid_payload"
}
```

## Example files in this repo

- `examples/api/analyze_payload.json`
- `examples/api/compare_batch_payload.json`

These are meant as copyable starting points for local use and manual testing.
