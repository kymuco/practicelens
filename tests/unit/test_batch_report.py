import json
from pathlib import Path

from practicelens.application.contracts import AnalyzeResult, BatchCompareEntry, BatchCompareResult
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
from practicelens.reporting.batch_report import (
    batch_compare_result_to_csv_text,
    batch_compare_result_to_json_payload,
    batch_compare_result_to_json_text,
    batch_compare_result_to_markdown,
)


def _sample_report(path: str, score: float) -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path(path)),
        feature_flags=FeatureFlags(),
        scores=(ComponentScore(MetricName.PITCH_FIDELITY, score, 1.0),),
        metrics=(MetricResult(MetricName.PITCH_FIDELITY, score / 100.0, score, Severity.INFO),),
        sections=(
            SectionReport(
                index=0,
                start_s=0.0,
                end_s=8.0,
                component_scores=(ComponentScore(MetricName.PITCH_FIDELITY, score, 1.0),),
                findings=(SectionFinding(0.0, 8.0, Severity.NOTICE, "Section note"),),
            ),
        ),
        feedback=("Feedback.",),
        artifacts=(ArtifactLink(ArtifactKind.JSON_REPORT, f"{path}.json"),),
        summary=f"Score {score:.1f}",
    )


def test_batch_report_renderers_emit_ranking_outputs() -> None:
    result = BatchCompareResult(
        reference_path=Path("reference.wav"),
        entries=(
            BatchCompareEntry(1, Path("take_a.wav"), 91.0, AnalyzeResult(_sample_report("take_a.wav", 91.0))),
            BatchCompareEntry(2, Path("take_b.wav"), 77.0, AnalyzeResult(_sample_report("take_b.wav", 77.0))),
        ),
        artifacts=((ArtifactKind.JSON_REPORT, Path("batch_report.json")),),
        summary="Best take: take_a.wav with 91.0/100 across 2 compared takes.",
    )

    payload = batch_compare_result_to_json_payload(result)
    json.loads(batch_compare_result_to_json_text(result))
    markdown_text = batch_compare_result_to_markdown(result)
    csv_text = batch_compare_result_to_csv_text(result)

    assert payload["entries"][0]["rank"] == 1
    assert payload["entries"][0]["take_path"] == "take_a.wav"
    assert "# PracticeLens Batch Compare" in markdown_text
    assert "rank,take_path,overall_score,summary,output_dir" in csv_text
