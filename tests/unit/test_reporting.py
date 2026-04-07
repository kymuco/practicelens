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
from practicelens.reporting import (
    report_to_csv_text,
    report_to_json_payload,
    report_to_json_text,
    report_to_markdown,
    report_to_svg,
)


def _sample_report() -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path("take.wav")),
        feature_flags=FeatureFlags(),
        scores=(
            ComponentScore(MetricName.PITCH_FIDELITY, 90.0, 0.35),
            ComponentScore(MetricName.RHYTHM_FIDELITY, 80.0, 0.30),
            ComponentScore(MetricName.TIMING_CONSISTENCY, 75.0, 0.20),
            ComponentScore(MetricName.SECTION_STABILITY, 85.0, 0.15),
        ),
        metrics=(
            MetricResult(MetricName.PITCH_FIDELITY, 0.9, 90.0, Severity.INFO, "Pitch detail"),
        ),
        sections=(
            SectionReport(
                index=0,
                start_s=0.0,
                end_s=8.0,
                component_scores=(
                    ComponentScore(MetricName.PITCH_FIDELITY, 90.0, 0.35),
                    ComponentScore(MetricName.RHYTHM_FIDELITY, 80.0, 0.30),
                    ComponentScore(MetricName.TIMING_CONSISTENCY, 75.0, 0.20),
                    ComponentScore(MetricName.SECTION_STABILITY, 85.0, 0.15),
                ),
                findings=(SectionFinding(0.0, 8.0, Severity.NOTICE, "Stable section"),),
            ),
        ),
        feedback=("Good baseline.",),
        artifacts=(
            ArtifactLink(ArtifactKind.JSON_REPORT, "report.json", "Structured report."),
            ArtifactLink(ArtifactKind.CSV_REPORT, "report.csv", "Section export."),
            ArtifactLink(ArtifactKind.SVG_REPORT, "report.svg", "Visual summary."),
        ),
        summary="Overall score 84.0/100.",
    )


def test_report_to_json_payload_is_serializable() -> None:
    payload = report_to_json_payload(_sample_report())

    assert payload["overview"]["mode"] == "reference"
    assert payload["scores"][0]["name"] == "pitch_fidelity"
    assert payload["artifacts"][1]["kind"] == "csv_report"


def test_report_text_renderers_include_expected_sections() -> None:
    report = _sample_report()

    json_text = report_to_json_text(report)
    markdown_text = report_to_markdown(report)
    csv_text = report_to_csv_text(report)
    svg_text = report_to_svg(report)
    json.loads(json_text)

    assert "# PracticeLens Report" in markdown_text
    assert "## At a glance" in markdown_text
    assert "| Component | Score | Weight |" in markdown_text
    assert "Pitch Fidelity" in markdown_text
    assert "Section average" in markdown_text
    assert "section_index,start_s,end_s" in csv_text
    assert "<svg" in svg_text
    assert "PracticeLens Summary" in svg_text
    assert "Performance band" in svg_text
    assert "Pitch Fidelity" in svg_text
    assert "Section trend" in svg_text
