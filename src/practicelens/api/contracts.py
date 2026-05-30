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


class PracticeSessionRequestPayload(BatchCompareRequestPayload, total=False):
    history_index: str


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


class AnalysisConfidencePayload(TypedDict):
    level: str
    reasons: list[str]
    limitations: list[str]


class InputSuitabilitySummaryPayload(TypedDict):
    schema_version: int
    status: str
    reference_duration_s: float
    take_duration_s: float
    duration_ratio: float
    duration_diagnostic: str
    duration_diagnostic_message: str | None
    reference_activity_start_s: float | None
    take_activity_start_s: float | None
    start_offset_s: float | None
    leading_noise_duration_s: float
    start_diagnostic: str
    start_diagnostic_message: str | None
    alignment_coverage: float
    voiced_frame_coverage: float
    reference_voiced_frame_coverage: float
    take_voiced_frame_coverage: float
    onset_evidence: str
    reference_onset_count: int
    take_onset_count: int
    reasons: list[str]


class PracticeLoopPayload(TypedDict):
    section_index: int
    start_s: float
    end_s: float
    focus: str
    instruction: str


class SessionTakeSummaryPayload(TypedDict):
    rank: int
    take_path: str
    overall_score: float


class SessionPracticeLoopPayload(TypedDict):
    take_rank: int
    take_path: str
    section_index: int
    start_s: float
    end_s: float
    focus: str
    instruction: str


class BatchSessionSummaryPayload(TypedDict):
    schema_version: int
    compared_takes: int
    best_take: SessionTakeSummaryPayload
    weakest_take: SessionTakeSummaryPayload
    recurring_weakness: str
    recurring_weakness_count: int
    strongest_stable_area: str
    strongest_stable_area_average_score: float
    next_recording_target: str
    practice_loops: list[SessionPracticeLoopPayload]


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
    analysis_confidence: AnalysisConfidencePayload
    input_suitability: InputSuitabilitySummaryPayload
    practice_loops: list[PracticeLoopPayload]
    top_strengths: list[str]
    top_weaknesses: list[str]
    next_practice_step: str | None
    feedback: list[str]
    artifacts: list[ArtifactPayload]
    summary: str | None


class BatchEntryPayload(TypedDict):
    rank: int
    take_path: str
    overall_score: float
    summary: str | None
    input_suitability: InputSuitabilitySummaryPayload
    output_dir: str | None
    practice_loops: list[PracticeLoopPayload]
    artifacts: list[ArtifactPayload]


class BatchCompareResponsePayload(TypedDict):
    overview: BatchCompareOverviewPayload
    reference_path: str
    summary: str | None
    session_summary: BatchSessionSummaryPayload | None
    entries: list[BatchEntryPayload]
    artifacts: list[ArtifactPayload]


class PracticeSessionResponsePayload(BatchCompareResponsePayload):
    history_index_path: str | None
    history_entry_appended: bool


class ApiHealthPayload(TypedDict):
    status: str
    service: str
    version: str


class ApiErrorPayload(TypedDict):
    error: str
    message: str
    code: NotRequired[str]
