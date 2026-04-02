from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from practicelens.domain.models import AnalysisConfig, AnalysisInput, AnalysisReport


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
