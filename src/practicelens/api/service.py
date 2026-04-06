from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from practicelens.api.contracts import (
    AnalyzeRequestPayload,
    AnalyzeResponsePayload,
    BatchCompareRequestPayload,
    BatchCompareResponsePayload,
)
from practicelens.application import (
    AnalyzeRequest,
    BatchCompareRequest,
    OfflineBatchComparePipeline,
    OfflineReferenceAnalysisPipeline,
)
from practicelens.domain.models import AnalysisConfig
from practicelens.reporting import batch_compare_result_to_json_payload, report_to_json_payload


def build_request_from_payload(payload: Mapping[str, object]) -> AnalyzeRequest:
    """Build a bounded single-analysis request from a JSON-friendly payload."""

    reference = _require_string(payload, "reference_path")
    take = _require_string(payload, "take_path")
    out_dir = _optional_string(payload, "out_dir")

    return AnalyzeRequest(
        reference_path=Path(reference),
        take_path=Path(take),
        out_dir=Path(out_dir) if out_dir is not None else None,
        config=_build_config(payload),
    )


def build_batch_request_from_payload(payload: Mapping[str, object]) -> BatchCompareRequest:
    """Build a bounded batch-comparison request from a JSON-friendly payload."""

    reference = _require_string(payload, "reference_path")
    take_paths = _require_string_sequence(payload, "take_paths")
    out_dir = _optional_string(payload, "out_dir")

    return BatchCompareRequest(
        reference_path=Path(reference),
        take_paths=tuple(Path(value) for value in take_paths),
        out_dir=Path(out_dir) if out_dir is not None else None,
        config=_build_config(payload),
    )


def analyze_payload(payload: Mapping[str, object] | AnalyzeRequestPayload) -> AnalyzeResponsePayload:
    """Run one offline analysis request from a JSON-like payload."""

    request = build_request_from_payload(payload)
    result = OfflineReferenceAnalysisPipeline().analyze(request)
    return cast(AnalyzeResponsePayload, report_to_json_payload(result.report))


def compare_batch_payload(
    payload: Mapping[str, object] | BatchCompareRequestPayload,
) -> BatchCompareResponsePayload:
    """Run one batch comparison request from a JSON-like payload."""

    request = build_batch_request_from_payload(payload)
    result = OfflineBatchComparePipeline().compare(request)
    return cast(BatchCompareResponsePayload, batch_compare_result_to_json_payload(result))


def _build_config(payload: Mapping[str, object]) -> AnalysisConfig:
    return AnalysisConfig(
        target_sample_rate=_optional_int(payload, "sample_rate", 16_000),
        frame_length=_optional_int(payload, "frame_length", 2_048),
        hop_length=_optional_int(payload, "hop_length", 512),
        segment_duration_s=_optional_float(payload, "segment_duration", 8.0),
    )


def _require_string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _require_string_sequence(payload: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(f"{key} must be a sequence of non-empty strings")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} must contain only non-empty strings")
        normalized.append(item)
    if not normalized:
        raise ValueError(f"{key} must contain at least one take path")
    return tuple(normalized)


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
