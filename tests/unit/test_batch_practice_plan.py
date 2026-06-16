from dataclasses import replace
from pathlib import Path

from practicelens.application.contracts import (
    AnalyzeResult,
    BatchCompareEntry,
    BatchCompareResult,
    BatchSessionSummary,
    SessionPracticeLoopSummary,
    SessionTakeSummary,
)
from practicelens.domain.enums import AnalysisMode, MetricName
from practicelens.domain.models import AnalysisInput, AnalysisOverview, AnalysisReport, ComponentScore, FeatureFlags, SectionReport
from practicelens.reporting.batch_practice_plan import batch_compare_result_to_practice_plan_markdown


def _sample_report(path: str, score: float) -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path(path)),
        feature_flags=FeatureFlags(),
        scores=(ComponentScore(MetricName.PITCH_FIDELITY, score, 1.0),),
        metrics=(),
        sections=(SectionReport(index=0, start_s=0.0, end_s=8.0),),
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


def _sample_result(summary: BatchSessionSummary | None = None) -> BatchCompareResult:
    return BatchCompareResult(
        reference_path=Path("reference.wav"),
        entries=(
            BatchCompareEntry(1, Path("take_a.wav"), 91.0, AnalyzeResult(_sample_report("take_a.wav", 91.0))),
            BatchCompareEntry(2, Path("take_b.wav"), 77.0, AnalyzeResult(_sample_report("take_b.wav", 77.0))),
        ),
        summary="Best take: take_a.wav with 91.0/100 across 2 compared takes.",
        session_summary=summary or _sample_session_summary(),
    )


def test_batch_practice_plan_includes_before_next_take_near_top() -> None:
    text = batch_compare_result_to_practice_plan_markdown(_sample_result())

    assert "## Before next take" in text
    assert text.index("## Before next take") < text.index("## Keep take")
    assert "1. Loop `take_b.wav` Section 0 (0.00s - 8.00s)." in text
    assert "2. Focus on this loop's target: Pitch Fidelity." in text
    assert "3. Record one clean complete attempt: Record one new take focused on improving Pitch Fidelity." in text


def test_batch_practice_plan_uses_selected_loop_focus_when_it_differs_from_recurring_weakness() -> None:
    summary = replace(_sample_session_summary(), recurring_weakness=MetricName.RHYTHM_FIDELITY)

    text = batch_compare_result_to_practice_plan_markdown(_sample_result(summary))

    assert "1. Loop `take_b.wav` Section 0 (0.00s - 8.00s)." in text
    assert "2. Focus on this loop's target: Pitch Fidelity." in text
    assert "2. Focus on the recurring weakness: Rhythm Fidelity." not in text
    assert "- **Primary recurring weakness:** Rhythm Fidelity" in text


def test_batch_practice_plan_before_next_take_without_loops_stays_useful() -> None:
    summary = replace(_sample_session_summary(), practice_loops=())

    text = batch_compare_result_to_practice_plan_markdown(_sample_result(summary))

    assert "## Before next take" in text
    assert "1. Review the weakest take `take_b.wav` before choosing section-level loop work." in text
    assert "2. Focus on the recurring weakness: Pitch Fidelity." in text
    assert "3. Record one clean complete attempt: Record one new take focused on improving Pitch Fidelity." in text
