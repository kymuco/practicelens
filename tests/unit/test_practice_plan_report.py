from dataclasses import replace
from pathlib import Path

from practicelens.domain.enums import AnalysisMode, MetricName, Severity
from practicelens.domain.models import (
    AnalysisInput,
    AnalysisOverview,
    AnalysisReport,
    ComponentScore,
    FeatureFlags,
    MetricResult,
    PracticeLoop,
    SectionReport,
)
from practicelens.reporting.practice_plan_report import report_to_practice_plan_markdown


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
        metrics=(MetricResult(MetricName.TIMING_CONSISTENCY, 0.75, 75.0, Severity.NOTICE, "Timing detail"),),
        sections=(SectionReport(index=0, start_s=0.0, end_s=8.0),),
        practice_loops=(
            PracticeLoop(
                section_index=0,
                start_s=0.0,
                end_s=8.0,
                focus=MetricName.TIMING_CONSISTENCY,
                instruction="Loop Section 0 and focus on Timing Consistency.",
            ),
        ),
        top_strengths=("Pitch Fidelity is the strongest stable area in this take.",),
        top_weaknesses=("Timing Consistency should be fixed before changing the arrangement.",),
        summary="Overall score 83.2/100.",
    )


def test_practice_plan_starts_with_goal_heading_and_action_guidance() -> None:
    text = report_to_practice_plan_markdown(_sample_report())

    assert text.startswith("# PracticeLens Practice Plan\n\n## Goal for the next take")
    assert "Record one new take focused on improving Timing Consistency while preserving Pitch Fidelity." in text
    assert "- **Fix first:** Timing Consistency (75.0/100)" in text
    assert "- **Keep:** Pitch Fidelity (90.0/100)" in text
    assert "- **Current take:** `take.wav`" in text
    assert "- **Overall score:** 83.2/100" in text


def test_practice_plan_includes_before_next_take_near_top() -> None:
    text = report_to_practice_plan_markdown(_sample_report())

    assert "## Before next take" in text
    assert text.index("## Before next take") < text.index("## What to keep")
    assert "1. Loop Section 0 (0.00s - 8.00s) and focus on Timing Consistency." in text
    assert "2. Keep attention on Timing Consistency before changing anything else." in text
    assert "3. Record one clean complete attempt:" in text


def test_practice_plan_before_next_take_without_loops_stays_useful() -> None:
    report = replace(_sample_report(), practice_loops=())

    text = report_to_practice_plan_markdown(report)

    assert "## Before next take" in text
    assert "1. Run one clean full-take pass before section-level loop work." in text
    assert "2. Keep attention on Timing Consistency before changing anything else." in text
    assert "3. Record one clean complete attempt:" in text


def test_practice_plan_makes_strength_and_weakness_easy_to_find() -> None:
    text = report_to_practice_plan_markdown(_sample_report())

    assert "## What to keep" in text
    assert "- Pitch Fidelity is the strongest stable area in this take." in text
    assert "## What to fix first" in text
    assert "- Timing Consistency should be fixed before changing the arrangement." in text
    assert "## Why this matters" in text
    assert "Timing Consistency is the lowest-scoring area right now." in text
    assert "protecting Pitch Fidelity" in text


def test_practice_plan_keeps_loops_and_next_recording_target() -> None:
    text = report_to_practice_plan_markdown(_sample_report())

    assert "## Practice loops" in text
    assert "### Loop 1: Section 0" in text
    assert "- **Focus:** Timing Consistency" in text
    assert "- **Instruction:** Loop Section 0 and focus on Timing Consistency." in text
    assert "## Next recording target" in text
    assert "Record one new take focused on improving Timing Consistency while preserving Pitch Fidelity." in text
    assert "## Confidence notes" in text
