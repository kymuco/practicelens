from practicelens.domain.enums import MetricName
from practicelens.domain.models import ComponentScore
from practicelens.scoring.engine import _feedback, _summary


def _sample_component_scores() -> tuple[ComponentScore, ...]:
    return (
        ComponentScore(MetricName.PITCH_FIDELITY, 90.0, 0.35),
        ComponentScore(MetricName.RHYTHM_FIDELITY, 80.0, 0.30),
        ComponentScore(MetricName.TIMING_CONSISTENCY, 75.0, 0.20),
        ComponentScore(MetricName.SECTION_STABILITY, 85.0, 0.15),
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
