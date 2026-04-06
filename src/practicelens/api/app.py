from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
except ImportError:  # pragma: no cover - optional dependency
    FastAPI = None  # type: ignore[assignment]
    JSONResponse = None  # type: ignore[assignment]

from practicelens.api.contracts import (
    AnalyzeResponsePayload,
    ApiErrorPayload,
    ApiHealthPayload,
    BatchCompareResponsePayload,
)
from practicelens.api.service import analyze_payload, compare_batch_payload


def create_app() -> Any:
    """Create the optional FastAPI app surface for PracticeLens."""

    if FastAPI is None or JSONResponse is None:
        raise RuntimeError(
            "FastAPI is not installed. Install the 'api' extra to use the HTTP service."
        )

    app = FastAPI(title="PracticeLens API", version="0.1.0a0")

    @app.get("/health")
    def health() -> ApiHealthPayload:
        return {
            "status": "ok",
            "service": "practicelens-api",
            "version": "0.1.0a0",
        }

    @app.post("/analyze")
    def analyze(payload: dict[str, object]) -> AnalyzeResponsePayload | JSONResponse:
        try:
            return analyze_payload(payload)
        except Exception as exc:
            return _bad_request_response(exc)

    @app.post("/compare-batch")
    def compare_batch(payload: dict[str, object]) -> BatchCompareResponsePayload | JSONResponse:
        try:
            return compare_batch_payload(payload)
        except Exception as exc:
            return _bad_request_response(exc)

    return app


def _bad_request_response(exc: Exception) -> JSONResponse:
    error_payload: ApiErrorPayload = {
        "error": "bad_request",
        "message": str(exc),
        "code": "invalid_payload",
    }
    return JSONResponse(status_code=400, content=error_payload)


app = create_app() if FastAPI is not None else None
