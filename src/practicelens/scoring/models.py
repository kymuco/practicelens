from __future__ import annotations

from dataclasses import dataclass

from practicelens.domain.models import ComponentScore, MetricResult, SectionReport


@dataclass(slots=True, frozen=True)
class ScoringBundle:
    """Structured scoring result produced from aligned feature bundles."""

    overall_score: float
    component_scores: tuple[ComponentScore, ...]
    metrics: tuple[MetricResult, ...]
    sections: tuple[SectionReport, ...]
    feedback: tuple[str, ...] = ()
    summary: str | None = None
