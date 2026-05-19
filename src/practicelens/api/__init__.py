"""HTTP/API helpers for PracticeLens."""

from practicelens.api.contracts import (
    AnalyzeRequestPayload,
    AnalyzeResponsePayload,
    ApiErrorPayload,
    ApiHealthPayload,
    BatchCompareRequestPayload,
    BatchCompareResponsePayload,
    PracticeSessionRequestPayload,
    PracticeSessionResponsePayload,
)
from practicelens.api.service import (
    analyze_payload,
    build_batch_request_from_payload,
    build_request_from_payload,
    compare_batch_payload,
    practice_session_payload,
)

__all__ = [
    "AnalyzeRequestPayload",
    "AnalyzeResponsePayload",
    "ApiErrorPayload",
    "ApiHealthPayload",
    "BatchCompareRequestPayload",
    "BatchCompareResponsePayload",
    "PracticeSessionRequestPayload",
    "PracticeSessionResponsePayload",
    "analyze_payload",
    "build_batch_request_from_payload",
    "build_request_from_payload",
    "compare_batch_payload",
    "practice_session_payload",
]
