from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
except ImportError:  # pragma: no cover - optional dependency
    FastAPI = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]

from practicelens.api.service import analyze_payload


def create_app() -> Any:
    """Create the optional FastAPI app surface for PracticeLens."""

    if FastAPI is None or HTTPException is None:
        raise RuntimeError(
            "FastAPI is not installed. Install the 'api' extra to use the HTTP service."
        )

    app = FastAPI(title="PracticeLens API", version="0.1.0a0")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "service": "practicelens-api"}

    @app.post("/analyze")
    def analyze(payload: dict[str, object]) -> dict[str, object]:
        try:
            return analyze_payload(payload)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app() if FastAPI is not None else None
