from pathlib import Path

from practicelens.domain.enums import AnalysisMode, MetricName, Severity
from practicelens.domain.models import (
    AnalysisConfidence,
    AnalysisInput,
    AnalysisOverview,
    AnalysisReport,
    ComponentScore,
    FeatureFlags,
    InputSuitabilitySummary,
    MetricResult,
    PracticeLoop,
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
        analysis_confidence=AnalysisConfidence(
            level="medium",
            reasons=("Onset evidence is present for rhythm-oriented feedback.",),
            limitations=("Confidence is a sanity note for the current evidence quality, not a scientific accuracy guarantee.",),
        ),
        practice_loops=(
            PracticeLoop(
                section_index=1,
                start_s=8.0,
                end_s=16.0,
                focus=MetricName.TIMING_CONSISTENCY,
                instruction="Loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency.",
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


def _low_confidence_report() -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path("bad-take.wav")),
        feature_flags=FeatureFlags(),
        scores=(ComponentScore(MetricName.PITCH_FIDELITY, 55.0, 1.0),),
        metrics=(MetricResult(MetricName.ALIGNMENT_COVERAGE, 0.4, 40.0, Severity.WARNING, "Limited coverage"),),
        sections=(),
        analysis_confidence=AnalysisConfidence(
            level="low",
            reasons=("Alignment coverage is limited.",),
            limitations=("The recording may not support detailed section feedback.",),
        ),
        input_suitability=InputSuitabilitySummary(
            status="low_confidence",
            reference_duration_s=8.0,
            take_duration_s=3.0,
            duration_ratio=0.375,
            duration_diagnostic="take_much_shorter_than_reference",
            duration_diagnostic_message=(
                "Take duration differs substantially from the reference. Possible causes include extra silence, "
                "a restart, a missing section, or unrelated material."
            ),
            reference_activity_start_s=0.0,
            take_activity_start_s=0.6,
            start_offset_s=0.6,
            leading_noise_duration_s=0.0,
            start_diagnostic="take_activity_starts_late",
            start_diagnostic_message=(
                "The take start may be delayed relative to the reference. This may indicate a weak or missing first note, "
                "late playing, or leading silence before the musical activity."
            ),
            alignment_coverage=0.4,
            voiced_frame_coverage=0.2,
            reference_voiced_frame_coverage=0.9,
            take_voiced_frame_coverage=0.2,
            onset_evidence="absent",
            reference_onset_count=4,
            take_onset_count=0,
            reasons=("Alignment coverage is limited.",),
        ),
        summary="Low confidence input.",
    )


def test_markdown_report_surfaces_strengths_weaknesses_next_step_confidence_and_practice_loops() -> None:
    markdown = report_to_markdown(_sample_report())

    assert "## Analysis Confidence" in markdown
    assert "- **Analysis confidence:** Medium" in markdown
    assert "- Level: **Medium**" in markdown
    assert "Onset evidence is present for rhythm-oriented feedback." in markdown
    assert "Confidence is a sanity note for the current evidence quality" in markdown
    assert "- **Practice loops:** 1 recommended" in markdown
    assert "## Practice Loops" in markdown
    assert "### Section 1 (8.00s - 16.00s)" in markdown
    assert "- Focus: Timing Consistency" in markdown
    assert "Loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency." in markdown
    assert "## Top Strengths" in markdown
    assert "Pitch Fidelity is a clear current strength at 92.0/100; keep preserving that control." in markdown
    assert "## Top Weaknesses" in markdown
    assert (
        "Timing Consistency is the main weakness at 74.0/100. Tighten phrase timing so the take stops drifting across the section."
        in markdown
    )
    assert "## Next Practice Step" in markdown
    assert "loop Section 1 (8.00s - 16.00s) and focus on Timing Consistency" in markdown


def test_markdown_report_surfaces_low_confidence_recording_warnings() -> None:
    markdown = report_to_markdown(_low_confidence_report())

    assert "## Recording Confidence Warnings" in markdown
    assert "review detailed feedback cautiously" in markdown
    assert "Analysis confidence is low; Alignment coverage is limited." in markdown
    assert "Input suitability is low confidence." in markdown
    assert "Take duration differs substantially from the reference." in markdown
    assert "The take start may be delayed relative to the reference." in markdown
    assert "How to improve the next recording:" in markdown
    assert "Record the same musical section as the reference" in markdown
    assert "Use a short count-in" in markdown
    assert "Make the main notes clearer" in markdown
    assert "Play the first attacks clearly" in markdown
