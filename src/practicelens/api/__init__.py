"""HTTP/API helpers for PracticeLens."""

from practicelens.api.contracts import (
    AnalyzeRequestPayload,
    AnalyzeResponsePayload,
    ApiErrorPayload,
    ApiHealthPayload,
    BatchCompareRequestPayload,
    BatchCompareResponsePayload,
)
from practicelens.api.service import (
    analyze_payload,
    build_batch_request_from_payload,
    build_request_from_payload,
    compare_batch_payload,
)

__all__ = [
    "AnalyzeRequestPayload",
    "AnalyzeResponsePayload",
    "ApiErrorPayload",
    "ApiHealthPayload",
    "BatchCompareRequestPayload",
    "BatchCompareResponsePayload",
    "analyze_payload",
    "build_batch_request_from_payload",
    "build_request_from_payload",
    "compare_batch_payload",
]
