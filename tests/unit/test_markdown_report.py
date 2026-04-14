from pathlib import Path

from practicelens.domain.enums import AnalysisMode, MetricName, Severity
from practicelens.domain.models import (
    AnalysisInput,
    AnalysisOverview,
    AnalysisReport,
    ComponentScore,
    FeatureFlags,
    MetricResult,
    SectionFinding,
    SectionReport,
)
from practicelens.reporting.markdown_report import report_to_markdown


def _sample_report() -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path("take.wav")),
        feature_flags=FeatureFlags(),
        scores=(
            ComponentScore(MetricName.PITCH_FIDELITY, 92.0, 0.35),
            ComponentScore(MetricName.TIMING_CONSISTENCY, 74.0, 0.20),
        ),
        metrics=(MetricResult(MetricName.PITCH_FIDELITY, 0.92, 92.0, Severity.INFO),),
        sections=(
            SectionReport(
                index=1,
                start_s=8.0,
                end_s=16.0,
                component_scores=(ComponentScore(MetricName.TIMING_CONSISTENCY, 74.0, 0.20),),
                findings=(
                    SectionFinding(
                        8.0,
                        16.0,
                        Severity.NOTICE,
                        "Best focus here: Timing Consistency. Tighten phrase timing so the take stops drifting across the section.",
                    ),
                ),
            ),
        ),
        top_strengths=("Pitch Fidelity is a clear current strength at 92.0/100; keep preserving that control.",),
        top_weaknesses=(
            "Timing Consistency is the main weakness at 74.0/100. Tighten phrase timing so the take stops drifting across the section.",
        ),
        next_practice_step=(
            "Next practice step: loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency. "
            "Tighten phrase timing so the take stops drifting across the section."
        ),
        feedback=("Keep leaning on Pitch Fidelity.",),
        summary="Strong reference match overall.",
    )


def test_markdown_report_surfaces_strengths_weaknesses_and_next_step() -> None:
    markdown = report_to_markdown(_sample_report())

    assert "## Top Strengths" in markdown
    assert "Pitch Fidelity is a clear current strength at 92.0/100; keep preserving that control." in markdown
    assert "## Top Weaknesses" in markdown
    assert (
        "Timing Consistency is the main weakness at 74.0/100. Tighten phrase timing so the take stops drifting across the section."
        in markdown
    )
    assert "## Next Practice Step" in markdown
    assert "loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency" in markdown
