from __future__ import annotations

from pathlib import Path
from typing import Mapping

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.reporting import report_to_json_payload


def build_request_from_payload(payload: Mapping[str, object]) -> AnalyzeRequest:
    """Build a bounded analysis request from a JSON-friendly payload."""

    reference = _require_string(payload, "reference_path")
    take = _require_string(payload, "take_path")
    out_dir = _optional_string(payload, "out_dir")

    config = AnalysisConfig(
        target_sample_rate=_optional_int(payload, "sample_rate", 16_000),
        frame_length=_optional_int(payload, "frame_length", 2_048),
        hop_length=_optional_int(payload, "hop_length", 512),
        segment_duration_s=_optional_float(payload, "segment_duration", 8.0),
    )

    return AnalyzeRequest(
        reference_path=Path(reference),
        take_path=Path(take),
        out_dir=Path(out_dir) if out_dir is not None else None,
        config=config,
    )


def analyze_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Run one offline analysis request from a JSON-like payload."""

    request = build_request_from_payload(payload)
    result = OfflineReferenceAnalysisPipeline().analyze(request)
    return report_to_json_payload(result.report)


def _require_string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_string(payload: Mapping[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string when provided")
    return value


def _optional_int(payload: Mapping[str, object], key: str, default: int) -> int:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _optional_float(payload: Mapping[str, object], key: str, default: float) -> float:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")
    return float(value)
