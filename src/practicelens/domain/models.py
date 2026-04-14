from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from practicelens.domain.enums import AnalysisMode, ArtifactKind, MetricName, Severity
from practicelens.domain.errors import InvalidAnalysisConfigError, InvalidAnalysisInputError
from practicelens.domain.types import MetricValue, SchemaVersion, ScoreValue, Seconds


@dataclass(slots=True, frozen=True)
class AnalysisInput:
    """Canonical analysis input for one reference-aware run."""

    reference_path: Path
    take_path: Path
    mode: AnalysisMode = AnalysisMode.REFERENCE

    def __post_init__(self) -> None:
        if self.mode is not AnalysisMode.REFERENCE:
            raise InvalidAnalysisInputError(f"unsupported analysis mode: {self.mode}")
        if not str(self.reference_path):
            raise InvalidAnalysisInputError("reference_path must not be empty")
        if not str(self.take_path):
            raise InvalidAnalysisInputError("take_path must not be empty")


@dataclass(slots=True, frozen=True)
class AnalysisConfig:
    """Stable configuration surface for v0.1 analysis runs."""

    schema_version: SchemaVersion = SchemaVersion(1)
    target_sample_rate: int = 16_000
    frame_length: int = 2_048
    hop_length: int = 512
    segment_duration_s: Seconds = Seconds(8.0)
    pitch_weight: float = 0.35
    rhythm_weight: float = 0.30
    timing_weight: float = 0.20
    stability_weight: float = 0.15

    def __post_init__(self) -> None:
        if self.target_sample_rate <= 0:
            raise InvalidAnalysisConfigError("target_sample_rate must be positive")
        if self.frame_length <= 0:
            raise InvalidAnalysisConfigError("frame_length must be positive")
        if self.hop_length <= 0:
            raise InvalidAnalysisConfigError("hop_length must be positive")
        if self.segment_duration_s <= 0:
            raise InvalidAnalysisConfigError("segment_duration_s must be positive")

        total_weight = (
            self.pitch_weight
            + self.rhythm_weight
            + self.timing_weight
            + self.stability_weight
        )
        if abs(total_weight - 1.0) > 1e-9:
            raise InvalidAnalysisConfigError(
                "score weights must sum to 1.0 for deterministic aggregation"
            )


@dataclass(slots=True, frozen=True)
class FeatureFlags:
    """Declares which analysis capabilities contributed to a report."""

    pitch_enabled: bool = True
    onset_enabled: bool = True
    tempo_enabled: bool = True
    energy_enabled: bool = True
    voicing_enabled: bool = True


@dataclass(slots=True, frozen=True)
class ComponentScore:
    """One explainable report component score."""

    name: MetricName
    score: ScoreValue
    weight: float


@dataclass(slots=True, frozen=True)
class MetricResult:
    """One concrete metric value plus its normalized score."""

    name: MetricName
    value: MetricValue
    score: ScoreValue
    severity: Severity = Severity.INFO
    detail: str | None = None


@dataclass(slots=True, frozen=True)
class SectionFinding:
    """Human-readable section-level finding tied to a time span."""

    start_s: Seconds
    end_s: Seconds
    severity: Severity
    message: str


@dataclass(slots=True, frozen=True)
class SectionReport:
    """Per-section synthesized report surface."""

    index: int
    start_s: Seconds
    end_s: Seconds
    component_scores: tuple[ComponentScore, ...] = ()
    findings: tuple[SectionFinding, ...] = ()


@dataclass(slots=True, frozen=True)
class ArtifactLink:
    """Stable reference to one generated artifact."""

    kind: ArtifactKind
    path: str
    description: str | None = None


@dataclass(slots=True, frozen=True)
class AnalysisOverview:
    """Compact, stable top-level overview contract for a finished analysis."""

    kind: str = "analysis_report"
    schema_version: SchemaVersion = SchemaVersion(1)
    status: str = "completed"
    ok: bool = True
    mode: AnalysisMode = AnalysisMode.REFERENCE


@dataclass(slots=True, frozen=True)
class BatchCompareOverview:
    """Compact, stable top-level overview contract for a finished batch comparison."""

    kind: str = "batch_compare_report"
    schema_version: SchemaVersion = SchemaVersion(1)
    status: str = "completed"
    ok: bool = True


@dataclass(slots=True, frozen=True)
class AnalysisReport:
    """Stable additive report surface for v0.1 analysis outputs."""

    overview: AnalysisOverview
    inputs: AnalysisInput
    feature_flags: FeatureFlags
    scores: tuple[ComponentScore, ...]
    metrics: tuple[MetricResult, ...]
    sections: tuple[SectionReport, ...]
    top_strengths: tuple[str, ...] = ()
    top_weaknesses: tuple[str, ...] = ()
    next_practice_step: str | None = None
    feedback: tuple[str, ...] = ()
    artifacts: tuple[ArtifactLink, ...] = ()
    summary: str | None = None

    def metric_map(self) -> dict[str, MetricResult]:
        return {metric.name.value: metric for metric in self.metrics}

    def score_map(self) -> dict[str, ComponentScore]:
        return {score.name.value: score for score in self.scores}

    def artifact_map(self) -> dict[str, ArtifactLink]:
        return {artifact.kind.value: artifact for artifact in self.artifacts}
