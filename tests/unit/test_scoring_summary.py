from practicelens.domain.enums import MetricName, Severity
from practicelens.domain.models import ComponentScore, SectionFinding, SectionReport
from practicelens.scoring.engine import (
    _feedback,
    _next_practice_step,
    _section_findings,
    _summary,
    _top_strengths,
    _top_weaknesses,
)


def _sample_component_scores() -> tuple[ComponentScore, ...]:
    return (
        ComponentScore(MetricName.PITCH_FIDELITY, 90.0, 0.35),
        ComponentScore(MetricName.RHYTHM_FIDELITY, 80.0, 0.30),
        ComponentScore(MetricName.TIMING_CONSISTENCY, 75.0, 0.20),
        ComponentScore(MetricName.SECTION_STABILITY, 85.0, 0.15),
    )


def _sample_sections() -> tuple[SectionReport, ...]:
    return (
        SectionReport(
            index=0,
            start_s=0.0,
            end_s=8.0,
            component_scores=(
                ComponentScore(MetricName.PITCH_FIDELITY, 92.0, 0.35),
                ComponentScore(MetricName.RHYTHM_FIDELITY, 84.0, 0.30),
                ComponentScore(MetricName.TIMING_CONSISTENCY, 82.0, 0.20),
                ComponentScore(MetricName.SECTION_STABILITY, 87.0, 0.15),
            ),
        ),
        SectionReport(
            index=1,
            start_s=8.0,
            end_s=16.0,
            component_scores=(
                ComponentScore(MetricName.PITCH_FIDELITY, 88.0, 0.35),
                ComponentScore(MetricName.RHYTHM_FIDELITY, 78.0, 0.30),
                ComponentScore(MetricName.TIMING_CONSISTENCY, 60.0, 0.20),
                ComponentScore(MetricName.SECTION_STABILITY, 80.0, 0.15),
            ),
        ),
    )


def test_summary_uses_human_readable_best_and_weakest_areas() -> None:
    component_scores = _sample_component_scores()
    overall_score = sum(score.score * score.weight for score in component_scores)

    summary = _summary(component_scores, overall_score)

    assert summary.startswith("Strong reference match overall.")
    assert "Best area: Pitch Fidelity (90.0/100)." in summary
    assert "Main improvement area: Timing Consistency (75.0/100)." in summary


def test_feedback_balances_strength_focus_and_overall_guidance() -> None:
    feedback = _feedback(_sample_component_scores())

    assert feedback[0] == (
        "Keep leaning on Pitch Fidelity; it is currently the clearest strength in the take."
    )
    assert feedback[1] == (
        "Primary focus area: Timing Consistency. Tighten phrase timing so the take stops drifting "
        "across the section."
    )
    assert feedback[2] == (
        "Overall the take is strong; preserve the current strengths while improving one weaker "
        "area at a time."
    )


def test_top_strengths_and_weaknesses_surface_multiple_ranked_takeaways() -> None:
    strengths = _top_strengths(_sample_component_scores())
    weaknesses = _top_weaknesses(_sample_component_scores())

    assert strengths == (
        "Pitch Fidelity is a clear current strength at 90.0/100; keep preserving that control.",
        "Section Stability is a clear current strength at 85.0/100; keep repeating that steadiness across the full take.",
    )
    assert weaknesses == (
        "Timing Consistency is the main weakness at 75.0/100. Tighten phrase timing so the take stops drifting across the section.",
        "Rhythm Fidelity is the next weakness at 80.0/100. Rehearse the onset pattern slower and re-lock attacks against the reference.",
    )


def test_next_practice_step_points_to_weakest_metric_in_weakest_section() -> None:
    next_step = _next_practice_step(_sample_component_scores(), _sample_sections())

    assert next_step == (
        "Next practice step: loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency. "
        "Tighten phrase timing so the take stops drifting across the section."
    )


def test_section_findings_add_actionable_focus_hints() -> None:
    findings = _section_findings(8.0, 16.0, 88.0, 78.0, 74.0)

    assert findings == (
        SectionFinding(
            8.0,
            16.0,
            Severity.NOTICE,
            "Best focus here: Timing Consistency. Tighten phrase timing so the take stops drifting across the section.",
        ),
    )
