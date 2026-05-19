import json
from pathlib import Path

from practicelens.application.contracts import (
    AnalyzeResult,
    BatchCompareEntry,
    BatchCompareResult,
    BatchSessionSummary,
    SessionPracticeLoopSummary,
    SessionTakeSummary,
)
from practicelens.domain.enums import AnalysisMode, ArtifactKind, MetricName, Severity
from practicelens.domain.models import (
    AnalysisInput,
    AnalysisOverview,
    AnalysisReport,
    ArtifactLink,
    ComponentScore,
    FeatureFlags,
    MetricResult,
    PracticeLoop,
    SectionFinding,
    SectionReport,
)
from practicelens.reporting.batch_report import (
    batch_compare_result_to_csv_text,
    batch_compare_result_to_json_payload,
    batch_compare_result_to_json_text,
    batch_compare_result_to_markdown,
)
from practicelens.reporting.batch_svg_report import batch_compare_result_to_svg


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
        practice_loops=(
            PracticeLoop(
                section_index=0,
                start_s=0.0,
                end_s=8.0,
                focus=MetricName.PITCH_FIDELITY,
                instruction=f"Loop Section 0 for {path} and focus on Pitch Fidelity.",
            ),
        ),
        feedback=("Feedback.",),
        artifacts=(ArtifactLink(ArtifactKind.JSON_REPORT, f"{path}.json"),),
        summary=f"Score {score:.1f}",
    )


def _sample_session_summary() -> BatchSessionSummary:
    return BatchSessionSummary(
        compared_takes=2,
        best_take=SessionTakeSummary(rank=1, take_path=Path("take_a.wav"), overall_score=91.0),
        weakest_take=SessionTakeSummary(rank=2, take_path=Path("take_b.wav"), overall_score=77.0),
        recurring_weakness=MetricName.PITCH_FIDELITY,
        recurring_weakness_count=2,
        strongest_stable_area=MetricName.PITCH_FIDELITY,
        strongest_stable_area_average_score=84.0,
        next_recording_target="Record one new take focused on improving Pitch Fidelity.",
        practice_loops=(
            SessionPracticeLoopSummary(
                take_rank=2,
                take_path=Path("take_b.wav"),
                section_index=0,
                start_s=0.0,
                end_s=8.0,
                focus=MetricName.PITCH_FIDELITY,
                instruction="Loop Section 0 for take_b.wav and focus on Pitch Fidelity.",
            ),
        ),
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
        session_summary=_sample_session_summary(),
    )

    payload = batch_compare_result_to_json_payload(result)
    json.loads(batch_compare_result_to_json_text(result))
    markdown_text = batch_compare_result_to_markdown(result)
    csv_text = batch_compare_result_to_csv_text(result)
    svg_text = batch_compare_result_to_svg(result)

    assert tuple(payload) == ("overview", "reference_path", "summary", "session_summary", "entries", "artifacts")
    assert payload["overview"] == {
        "kind": "batch_compare_report",
        "schema_version": 1,
        "status": "completed",
        "ok": True,
    }
    assert payload["session_summary"] == {
        "schema_version": 1,
        "compared_takes": 2,
        "best_take": {"rank": 1, "take_path": "take_a.wav", "overall_score": 91.0},
        "weakest_take": {"rank": 2, "take_path": "take_b.wav", "overall_score": 77.0},
        "recurring_weakness": "pitch_fidelity",
        "recurring_weakness_count": 2,
        "strongest_stable_area": "pitch_fidelity",
        "strongest_stable_area_average_score": 84.0,
        "next_recording_target": "Record one new take focused on improving Pitch Fidelity.",
        "practice_loops": [
            {
                "take_rank": 2,
                "take_path": "take_b.wav",
                "section_index": 0,
                "start_s": 0.0,
                "end_s": 8.0,
                "focus": "pitch_fidelity",
                "instruction": "Loop Section 0 for take_b.wav and focus on Pitch Fidelity.",
            }
        ],
    }
    assert payload["entries"][0]["rank"] == 1
    assert payload["entries"][0]["take_path"] == "take_a.wav"
    assert payload["entries"][0]["practice_loops"] == [
        {
            "section_index": 0,
            "start_s": 0.0,
            "end_s": 8.0,
            "focus": "pitch_fidelity",
            "instruction": "Loop Section 0 for take_a.wav and focus on Pitch Fidelity.",
        }
    ]
    assert payload["artifacts"][0] == {
        "kind": "json_report",
        "path": "batch_report.json",
        "description": "Structured batch comparison report.",
    }
    assert "# PracticeLens Batch Compare" in markdown_text
    assert "## At a glance" in markdown_text
    assert "**Recurring weakness:** Pitch Fidelity" in markdown_text
    assert "**Next target:** Record one new take focused on improving Pitch Fidelity." in markdown_text
    assert "## What to do next" in markdown_text
    assert "1. Keep `take_a.wav` as the current best take." in markdown_text
    assert "2. Practice Pitch Fidelity first." in markdown_text
    assert "3. Record next: Record one new take focused on improving Pitch Fidelity." in markdown_text
    assert "4. Start with `take_b.wav` section 0 (0.00s - 8.00s)." in markdown_text
    assert "## Why this take won" in markdown_text
    assert "`take_a.wav` has the highest overall score in this session." in markdown_text
    assert "It is 14.0 points ahead of `take_b.wav`." in markdown_text
    assert "Evidence: Score 91.0" in markdown_text
    assert "## Session decision" in markdown_text
    assert "**Keep:** `take_a.wav` (91.0/100)." in markdown_text
    assert "**Review weakest take:** `take_b.wav` (77.0/100)." in markdown_text
    assert "**Main recurring weakness:** Pitch Fidelity (2/2 takes)." in markdown_text
    assert "**Protect stable area:** Pitch Fidelity (84.0/100 average)." in markdown_text
    assert "**Record next:** Record one new take focused on improving Pitch Fidelity." in markdown_text
    assert "## Recommended session loops" in markdown_text
    assert "1. `take_b.wav` section 0 (0.00s - 8.00s): Loop Section 0" in markdown_text
    assert "| Rank | Take | Score | Delta vs best | Output dir |" in markdown_text
    assert "First practice loop: Loop Section 0 for take_a.wav and focus on Pitch Fidelity." in markdown_text
    assert "rank,take_name,take_path,overall_score,delta_from_best,first_practice_loop,summary,output_dir" in csv_text
    assert "Loop Section 0 for take_a.wav and focus on Pitch Fidelity." in csv_text
    assert "<svg" in svg_text
    assert "PracticeLens Batch Compare" in svg_text
    assert "Take ranking" in svg_text
    assert "take_a.wav" in svg_text
