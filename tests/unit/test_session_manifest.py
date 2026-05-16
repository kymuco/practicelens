import json
from pathlib import Path

from practicelens.application.contracts import (
    AnalyzeResult,
    BatchCompareEntry,
    BatchCompareResult,
    BatchSessionSummary,
    SessionTakeSummary,
)
from practicelens.domain.enums import AnalysisMode, ArtifactKind, MetricName
from practicelens.domain.models import AnalysisInput, AnalysisOverview, AnalysisReport, ComponentScore, FeatureFlags
from practicelens.reporting.session_manifest import (
    batch_compare_result_to_session_manifest_payload,
    batch_compare_result_to_session_manifest_text,
)


def _sample_report(path: str, score: float) -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path(path)),
        feature_flags=FeatureFlags(),
        scores=(ComponentScore(MetricName.PITCH_FIDELITY, score, 1.0),),
        summary=f"Score {score:.1f}",
    )


def test_batch_session_manifest_payload_is_serializable() -> None:
    result = BatchCompareResult(
        reference_path=Path("reference.wav"),
        entries=(
            BatchCompareEntry(1, Path("take_a.wav"), 91.0, AnalyzeResult(_sample_report("take_a.wav", 91.0))),
            BatchCompareEntry(2, Path("take_b.wav"), 77.0, AnalyzeResult(_sample_report("take_b.wav", 77.0))),
        ),
        artifacts=(
            (ArtifactKind.JSON_REPORT, Path("batch_report.json")),
            (ArtifactKind.MARKDOWN_REPORT, Path("batch_report.md")),
            (ArtifactKind.CSV_REPORT, Path("batch_report.csv")),
            (ArtifactKind.SVG_REPORT, Path("batch_report.svg")),
            (ArtifactKind.PRACTICE_PLAN, Path("practice_plan.md")),
            (ArtifactKind.SESSION_MANIFEST, Path("session_manifest.json")),
        ),
        summary="Best take: take_a.wav with 91.0/100 across 2 compared takes.",
        session_summary=BatchSessionSummary(
            compared_takes=2,
            best_take=SessionTakeSummary(rank=1, take_path=Path("take_a.wav"), overall_score=91.0),
            weakest_take=SessionTakeSummary(rank=2, take_path=Path("take_b.wav"), overall_score=77.0),
            recurring_weakness=MetricName.PITCH_FIDELITY,
            recurring_weakness_count=2,
            strongest_stable_area=MetricName.PITCH_FIDELITY,
            strongest_stable_area_average_score=84.0,
            next_recording_target="Record one new take focused on improving Pitch Fidelity.",
        ),
    )

    payload = batch_compare_result_to_session_manifest_payload(result)
    text = batch_compare_result_to_session_manifest_text(result)

    assert json.loads(text) == payload
    assert payload == {
        "schema_version": 1,
        "kind": "practice_session_manifest",
        "reference_path": "reference.wav",
        "compared_takes": 2,
        "take_paths": ["take_a.wav", "take_b.wav"],
        "best_take": {"rank": 1, "take_path": "take_a.wav", "overall_score": 91.0},
        "weakest_take": {"rank": 2, "take_path": "take_b.wav", "overall_score": 77.0},
        "recurring_weakness": "pitch_fidelity",
        "strongest_stable_area": "pitch_fidelity",
        "next_recording_target": "Record one new take focused on improving Pitch Fidelity.",
        "entrypoints": {
            "batch_json": "batch_report.json",
            "batch_markdown": "batch_report.md",
            "batch_csv": "batch_report.csv",
            "batch_svg": "batch_report.svg",
            "practice_plan": "practice_plan.md",
            "session_manifest": "session_manifest.json",
        },
        "artifacts": [
            {"kind": "json_report", "path": "batch_report.json"},
            {"kind": "markdown_report", "path": "batch_report.md"},
            {"kind": "csv_report", "path": "batch_report.csv"},
            {"kind": "svg_report", "path": "batch_report.svg"},
            {"kind": "practice_plan", "path": "practice_plan.md"},
            {"kind": "session_manifest", "path": "session_manifest.json"},
        ],
    }
