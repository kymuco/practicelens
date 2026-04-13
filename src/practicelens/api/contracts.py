from __future__ import annotations

from typing import NotRequired, TypedDict

# These payloads mirror both the API response shapes and the stable JSON artifact
# shapes written to disk by PracticeLens reporting.


class AnalyzeRequestPayload(TypedDict, total=False):
    reference_path: str
    take_path: str
    out_dir: str
    sample_rate: int
    frame_length: int
    hop_length: int
    segment_duration: float


class BatchCompareRequestPayload(TypedDict, total=False):
    reference_path: str
    take_paths: list[str]
    out_dir: str
    sample_rate: int
    frame_length: int
    hop_length: int
    segment_duration: float


class AnalysisOverviewPayload(TypedDict):
    kind: str
    schema_version: int
    status: str
    ok: bool
    mode: str


class BatchCompareOverviewPayload(TypedDict):
    kind: str
    schema_version: int
    status: str
    ok: bool


class AnalysisInputsPayload(TypedDict):
    reference_path: str
    take_path: str
    mode: str


class FeatureFlagsPayload(TypedDict):
    pitch_enabled: bool
    onset_enabled: bool
    tempo_enabled: bool
    energy_enabled: bool
    voicing_enabled: bool


class ComponentScorePayload(TypedDict):
    name: str
    score: float
    weight: float


class MetricPayload(TypedDict):
    name: str
    value: float
    score: float
    severity: str
    detail: str | None


class SectionFindingPayload(TypedDict):
    start_s: float
    end_s: float
    severity: str
    message: str


class SectionPayload(TypedDict):
    index: int
    start_s: float
    end_s: float
    component_scores: list[ComponentScorePayload]
    findings: list[SectionFindingPayload]


class ArtifactPayload(TypedDict):
    kind: str
    path: str
    description: str | None


class AnalyzeResponsePayload(TypedDict):
    overview: AnalysisOverviewPayload
    inputs: AnalysisInputsPayload
    feature_flags: FeatureFlagsPayload
    overall_score: float
    scores: list[ComponentScorePayload]
    metrics: list[MetricPayload]
    sections: list[SectionPayload]
    feedback: list[str]
    artifacts: list[ArtifactPayload]
    summary: str | None


class BatchEntryPayload(TypedDict):
    rank: int
    take_path: str
    overall_score: float
    summary: str | None
    output_dir: str | None
    artifacts: list[ArtifactPayload]


class BatchCompareResponsePayload(TypedDict):
    overview: BatchCompareOverviewPayload
    reference_path: str
    summary: str | None
    entries: list[BatchEntryPayload]
    artifacts: list[ArtifactPayload]


class ApiHealthPayload(TypedDict):
    status: str
    service: str
    version: str


class ApiErrorPayload(TypedDict):
    error: str
    message: str
    code: NotRequired[str]
