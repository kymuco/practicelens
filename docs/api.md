# PracticeLens API Notes

PracticeLens exposes an optional FastAPI app surface.

The current API is intentionally simple:

- `GET /health`
- `POST /analyze`
- `POST /compare-batch`
- `POST /practice-session`

The API keeps local storage explicit. `POST /practice-session` can append to a JSONL history index when `history_index` is provided, but the API does not currently expose `sessions list/show/compare` endpoints.

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
- `examples/api/practice_session_payload.json`
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
- `analysis_confidence`
- `practice_loops`
- `top_strengths`
- `top_weaknesses`
- `next_practice_step`
- `feedback`
- `artifacts`
- `summary`

`analysis_confidence` includes:

- `level` — `high`, `medium`, or `low`
- `reasons` — evidence-quality notes supporting the confidence level
- `limitations` — explicit caveats about deterministic v0.1 analysis

`practice_loops` includes focused section-repeat recommendations:

- `section_index`
- `start_s`
- `end_s`
- `focus`
- `instruction`

`overview.kind` is currently `analysis_report` and `overview.schema_version` is currently `1`.

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

- `overview`
- `reference_path`
- `summary`
- `session_summary`
- `entries`
- `artifacts`

`overview.kind` is currently `batch_compare_report` and `overview.schema_version` is currently `1`.

`session_summary` includes the session-level best take, weakest take, recurring weakness, strongest stable area, next recording target, and selected practice loops.

Each `entries[]` item includes:

- `rank`
- `take_path`
- `overall_score`
- `summary`
- `output_dir`
- `practice_loops`
- `artifacts`

`entries[].practice_loops` mirrors the single-take practice loop payload for that take.

Runnable `curl` example:

```bash
curl -X POST http://127.0.0.1:8000/compare-batch \
  -H "Content-Type: application/json" \
  --data @examples/api/compare_batch_payload.json
```

## POST /practice-session

Runs the same analysis engine as `POST /compare-batch`, but treats the request as a practice-session review. It requires `out_dir` because the practice-session workflow is artifact-oriented.

Example payload:

```json
{
  "reference_path": "reference.wav",
  "take_paths": ["take_a.wav", "take_b.wav", "take_c.wav"],
  "out_dir": "practice-session-out",
  "history_index": ".practicelens/sessions/index.jsonl",
  "sample_rate": 16000,
  "frame_length": 2048,
  "hop_length": 512,
  "segment_duration": 8.0
}
```

Top-level response fields mirror `POST /compare-batch` and additionally include:

- `history_index_path` — the JSONL history index path when provided, otherwise `null`
- `history_entry_appended` — whether a compact history entry was appended

When `history_index` is provided, the endpoint appends one JSONL entry to that path after the session artifacts are written. When omitted, no history entry is written.

Runnable `curl` example:

```bash
curl -X POST http://127.0.0.1:8000/practice-session \
  -H "Content-Type: application/json" \
  --data @examples/api/practice_session_payload.json
```

## Why there are no sessions list/show/compare API endpoints yet

The CLI supports local history inspection with `sessions list`, `sessions show`, and `sessions compare`.

The HTTP API intentionally stops at `POST /practice-session` for now because listing, opening, and comparing stored sessions would expose a broader local storage surface. That should be designed deliberately instead of being added as a thin wrapper by accident.

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
