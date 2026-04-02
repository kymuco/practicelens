from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from practicelens.application.contracts import AnalyzeRequest, AnalyzeResult


class AnalysisPipeline(Protocol):
    """Stable application pipeline protocol for v0.1 vertical slices."""

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResult:
        """Execute one bounded offline analysis request."""


@dataclass(slots=True)
class PipelineDependencies:
    """Placeholder dependency bundle for future concrete pipeline wiring."""

    pipeline_name: str = "offline_reference_analysis_v0"
