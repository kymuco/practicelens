from __future__ import annotations

import json

from practicelens.domain.models import AnalysisReport


def report_to_json_payload(report: AnalysisReport) -> dict[str, object]:
    """Convert an analysis report into a stable JSON-serializable payload."""

    overall_score = sum(score.score * score.weight for score in report.scores)
    return {
        "overview": {
            "kind": report.overview.kind,
            "schema_version": int(report.overview.schema_version),
            "status": report.overview.status,
            "ok": report.overview.ok,
            "mode": report.overview.mode.value,
        },
        "inputs": {
            "reference_path": str(report.inputs.reference_path),
            "take_path": str(report.inputs.take_path),
            "mode": report.inputs.mode.value,
        },
        "feature_flags": {
            "pitch_enabled": report.feature_flags.pitch_enabled,
            "onset_enabled": report.feature_flags.onset_enabled,
            "tempo_enabled": report.feature_flags.tempo_enabled,
            "energy_enabled": report.feature_flags.energy_enabled,
            "voicing_enabled": report.feature_flags.voicing_enabled,
        },
        "overall_score": overall_score,
        "scores": [
            {
                "name": score.name.value,
                "score": score.score,
                "weight": score.weight,
            }
            for score in report.scores
        ],
        "metrics": [
            {
                "name": metric.name.value,
                "value": metric.value,
                "score": metric.score,
                "severity": metric.severity.value,
                "detail": metric.detail,
            }
            for metric in report.metrics
        ],
        "sections": [
            {
                "index": section.index,
                "start_s": section.start_s,
                "end_s": section.end_s,
                "component_scores": [
                    {
                        "name": score.name.value,
                        "score": score.score,
                        "weight": score.weight,
                    }
                    for score in section.component_scores
                ],
                "findings": [
                    {
                        "start_s": finding.start_s,
                        "end_s": finding.end_s,
                        "severity": finding.severity.value,
                        "message": finding.message,
                    }
                    for finding in section.findings
                ],
            }
            for section in report.sections
        ],
        "analysis_confidence": {
            "level": report.analysis_confidence.level,
            "reasons": list(report.analysis_confidence.reasons),
            "limitations": list(report.analysis_confidence.limitations),
        },
        "top_strengths": list(report.top_strengths),
        "top_weaknesses": list(report.top_weaknesses),
        "next_practice_step": report.next_practice_step,
        "feedback": list(report.feedback),
        "artifacts": [
            {
                "kind": artifact.kind.value,
                "path": artifact.path,
                "description": artifact.description,
            }
            for artifact in report.artifacts
        ],
        "summary": report.summary,
    }


def report_to_json_text(report: AnalysisReport) -> str:
    """Render an analysis report as pretty JSON text."""

    return json.dumps(report_to_json_payload(report), indent=2, sort_keys=True)
