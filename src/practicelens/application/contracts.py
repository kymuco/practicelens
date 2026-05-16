from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from practicelens.domain.enums import ArtifactKind, MetricName
from practicelens.domain.models import AnalysisConfig, AnalysisInput, AnalysisReport, BatchCompareOverview


@dataclass(slots=True, frozen=True)
class AnalyzeRequest:
    """Use-case request envelope for one offline analysis run."""

    reference_path: Path
    take_path: Path
    out_dir: Path | None = None
    config: AnalysisConfig = AnalysisConfig()

    def to_analysis_input(self) -> AnalysisInput:
        return AnalysisInput(
            reference_path=self.reference_path,
            take_path=self.take_path,
        )


@dataclass(slots=True, frozen=True)
class AnalyzeResult:
    """Use-case result envelope for one offline analysis run."""

    report: AnalysisReport

    @property
    def overview(self) -> dict[str, object]:
        return {
            "kind": self.report.overview.kind,
            "schema_version": int(self.report.overview.schema_version),
            "status": self.report.overview.status,
            "ok": self.report.overview.ok,
            "mode": self.report.overview.mode.value,
        }


@dataclass(slots=True, frozen=True)
class BatchCompareRequest:
    """Use-case request envelope for one reference against multiple takes."""

    reference_path: Path
    take_paths: tuple[Path, ...]
    out_dir: Path | None = None
    config: AnalysisConfig = AnalysisConfig()

    def __post_init__(self) -> None:
        if not self.take_paths:
            raise ValueError("take_paths must contain at least one take")


@dataclass(slots=True, frozen=True)
class BatchCompareEntry:
    """One ranked take result inside a batch comparison run."""

    rank: int
    take_path: Path
    overall_score: float
    result: AnalyzeResult
    output_dir: Path | None = None

    @property
    def summary(self) -> str | None:
        return self.result.report.summary


@dataclass(slots=True, frozen=True)
class SessionTakeSummary:
    """Stable reference to one take inside a session-level summary."""

    rank: int
    take_path: Path
    overall_score: float


@dataclass(slots=True, frozen=True)
class SessionPracticeLoopSummary:
    """Practice loop selected for session-level follow-up."""

    take_rank: int
    take_path: Path
    section_index: int
    start_s: float
    end_s: float
    focus: MetricName
    instruction: str


@dataclass(slots=True, frozen=True)
class BatchSessionSummary:
    """Stable session-level summary across all compared takes."""

    compared_takes: int
    best_take: SessionTakeSummary
    weakest_take: SessionTakeSummary
    recurring_weakness: MetricName
    recurring_weakness_count: int
    strongest_stable_area: MetricName
    strongest_stable_area_average_score: float
    next_recording_target: str
    practice_loops: tuple[SessionPracticeLoopSummary, ...] = ()
    schema_version: int = 1


@dataclass(slots=True, frozen=True)
class BatchCompareResult:
    """Result envelope for one batch comparison run."""

    reference_path: Path
    entries: tuple[BatchCompareEntry, ...]
    overview: BatchCompareOverview = BatchCompareOverview()
    artifacts: tuple[tuple[ArtifactKind, Path], ...] = ()
    summary: str | None = None
    session_summary: BatchSessionSummary | None = None

    @property
    def best_entry(self) -> BatchCompareEntry:
        return self.entries[0]