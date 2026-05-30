from __future__ import annotations

import json

from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisReport, MetricResult
from practicelens.reporting.input_suitability_payload import input_suitability_to_payload

_SCORE_DIGITS = 6


def report_to_debug_payload(report: AnalysisReport) -> dict[str, object]:
    """Build a developer-facing diagnostic payload for one analysis report."""

    overall_score = sum(score.score * score.weight for score in report.scores)
    return {
        "schema_version": 1,
        "kind": "debug_payload",
        "overview": {
            "analysis_kind": report.overview.kind,
            "analysis_schema_version": int(report.overview.schema_version),
            "status": report.overview.status,
            "ok": report.overview.ok,
            "mode": report.overview.mode.value,
        },
        "inputs": {
            "reference_path": str(report.inputs.reference_path),
            "take_path": str(report.inputs.take_path),
        },
        "score_summary": {
            "overall_score": _round_score(overall_score),
            "components": [
                {
                    "name": score.name.value,
                    "score": _round_score(score.score),
                    "weight": _round_score(score.weight),
                    "weighted_contribution": _round_score(score.score * score.weight),
                }
                for score in report.scores
            ],
        },
        "evidence_summary": {
            "alignment_coverage": _metric_score(report, MetricName.ALIGNMENT_COVERAGE),
            "input_suitability": input_suitability_to_payload(report.input_suitability),
            "section_count": len(report.sections),
            "practice_loop_count": len(report.practice_loops),
            "feedback_count": len(report.feedback),
            "artifact_count": len(report.artifacts),
        },
        "confidence": {
            "level": report.analysis_confidence.level,
            "reasons": list(report.analysis_confidence.reasons),
            "limitations": list(report.analysis_confidence.limitations),
        },
        "practice_guidance": {
            "top_strengths": list(report.top_strengths),
            "top_weaknesses": list(report.top_weaknesses),
            "next_practice_step": report.next_practice_step,
            "practice_loops": [
                {
                    "section_index": loop.section_index,
                    "start_s": loop.start_s,
                    "end_s": loop.end_s,
                    "focus": loop.focus.value,
                    "instruction": loop.instruction,
                }
                for loop in report.practice_loops
            ],
        },
        "artifacts": [
            {
                "kind": artifact.kind.value,
                "path": artifact.path,
                "description": artifact.description,
            }
            for artifact in report.artifacts
        ],
    }


def report_to_debug_payload_text(report: AnalysisReport) -> str:
    """Render the developer-facing diagnostic payload as stable pretty JSON."""

    return json.dumps(report_to_debug_payload(report), indent=2, sort_keys=True)


def _metric_score(report: AnalysisReport, metric_name: MetricName) -> dict[str, object] | None:
    metric = _find_metric(report, metric_name)
    if metric is None:
        return None
    return {
        "value": _round_score(metric.value),
        "score": _round_score(metric.score),
        "severity": metric.severity.value,
        "detail": metric.detail,
    }


def _find_metric(report: AnalysisReport, metric_name: MetricName) -> MetricResult | None:
    for metric in report.metrics:
        if metric.name == metric_name:
            return metric
    return None


def _round_score(value: float) -> float:
    return round(value, _SCORE_DIGITS)
