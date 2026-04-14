import json
from pathlib import Path

from practicelens.domain.enums import AnalysisMode, ArtifactKind, MetricName, Severity
from practicelens.domain.models import (
    AnalysisInput,
    AnalysisOverview,
    AnalysisReport,
    ArtifactLink,
    ComponentScore,
    FeatureFlags,
    MetricResult,
    SectionFinding,
    SectionReport,
)
from practicelens.reporting.json_report import report_to_json_payload, report_to_json_text


def _sample_report() -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path("take.wav")),
        feature_flags=FeatureFlags(),
        scores=(ComponentScore(MetricName.PITCH_FIDELITY, 92.0, 1.0),),
        metrics=(MetricResult(MetricName.PITCH_FIDELITY, 0.92, 92.0, Severity.INFO),),
        sections=(
            SectionReport(
                index=0,
                start_s=0.0,
                end_s=8.0,
                component_scores=(ComponentScore(MetricName.PITCH_FIDELITY, 92.0, 1.0),),
                findings=(SectionFinding(0.0, 8.0, Severity.INFO, "Opening phrase is stable."),),
            ),
        ),
        top_strengths=("Pitch Fidelity is a clear current strength at 92.0/100; keep preserving that control.",),
        top_weaknesses=("Pitch Fidelity is the main weakness at 92.0/100. Keep preserving that control.",),
        next_practice_step="Next practice step: keep the current pitch control steady through the full phrase.",
        feedback=("Keep the current pitch stability.",),
        artifacts=(ArtifactLink(ArtifactKind.JSON_REPORT, "report.json", "Structured analysis report."),),
        summary="Strong reference match overall.",
    )


def test_report_json_payload_has_stable_top_level_contract() -> None:
    payload = report_to_json_payload(_sample_report())
    json.loads(report_to_json_text(_sample_report()))

    assert tuple(payload) == (
        "overview",
        "inputs",
        "feature_flags",
        "overall_score",
        "scores",
        "metrics",
        "sections",
        "top_strengths",
        "top_weaknesses",
        "next_practice_step",
        "feedback",
        "artifacts",
        "summary",
    )
    assert tuple(payload["overview"]) == ("kind", "schema_version", "status", "ok", "mode")
    assert payload["overview"] == {
        "kind": "analysis_report",
        "schema_version": 1,
        "status": "completed",
        "ok": True,
        "mode": "reference",
    }
    assert payload["top_strengths"] == [
        "Pitch Fidelity is a clear current strength at 92.0/100; keep preserving that control."
    ]
    assert payload["top_weaknesses"] == [
        "Pitch Fidelity is the main weakness at 92.0/100. Keep preserving that control."
    ]
    assert payload["next_practice_step"] == (
        "Next practice step: keep the current pitch control steady through the full phrase."
    )
    assert payload["artifacts"][0] == {
        "kind": "json_report",
        "path": "report.json",
        "description": "Structured analysis report.",
    }
