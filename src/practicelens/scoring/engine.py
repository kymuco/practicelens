from __future__ import annotations

import math
import statistics

from practicelens.alignment.models import AlignmentPath
from practicelens.domain.enums import MetricName, Severity
from practicelens.domain.errors import ScoringError
from practicelens.domain.models import (
    AnalysisConfig,
    ComponentScore,
    MetricResult,
    SectionFinding,
    SectionReport,
)
from practicelens.features.models import FeatureBundle
from practicelens.scoring.models import ScoringBundle


def score_aligned_features(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
    config: AnalysisConfig,
) -> ScoringBundle:
    """Compute explainable component scores from aligned feature bundles."""

    if not alignment.pairs:
        raise ScoringError("alignment path must contain at least one pair")

    pitch_score_value = _pitch_score(reference, take, alignment)
    rhythm_score_value = _rhythm_score(reference, take)
    timing_score_value = _timing_score(reference, take, alignment)
    sections = _section_reports(reference, take, alignment, config)
    section_stability_score = _section_stability_score(sections)

    component_scores = (
        ComponentScore(MetricName.PITCH_FIDELITY, pitch_score_value, config.pitch_weight),
        ComponentScore(MetricName.RHYTHM_FIDELITY, rhythm_score_value, config.rhythm_weight),
        ComponentScore(MetricName.TIMING_CONSISTENCY, timing_score_value, config.timing_weight),
        ComponentScore(MetricName.SECTION_STABILITY, section_stability_score, config.stability_weight),
    )

    overall_score = sum(score.score * score.weight for score in component_scores)
    metrics = (
        MetricResult(
            name=MetricName.PITCH_FIDELITY,
            value=pitch_score_value / 100.0,
            score=pitch_score_value,
            severity=_severity_for_score(pitch_score_value),
            detail="Reference-vs-take pitch agreement across aligned voiced frames.",
        ),
        MetricResult(
            name=MetricName.RHYTHM_FIDELITY,
            value=rhythm_score_value / 100.0,
            score=rhythm_score_value,
            severity=_severity_for_score(rhythm_score_value),
            detail="Relative onset agreement after duration normalization.",
        ),
        MetricResult(
            name=MetricName.TIMING_CONSISTENCY,
            value=timing_score_value / 100.0,
            score=timing_score_value,
            severity=_severity_for_score(timing_score_value),
            detail="How closely aligned frames follow the expected monotonic timing path.",
        ),
        MetricResult(
            name=MetricName.SECTION_STABILITY,
            value=section_stability_score / 100.0,
            score=section_stability_score,
            severity=_severity_for_score(section_stability_score),
            detail="How stable section-level scores remain across the full take.",
        ),
        MetricResult(
            name=MetricName.ALIGNMENT_COVERAGE,
            value=alignment.coverage_ratio,
            score=max(0.0, min(100.0, alignment.coverage_ratio * 100.0)),
            severity=_severity_for_score(alignment.coverage_ratio * 100.0),
            detail="Coverage of both frame sequences by the alignment path.",
        ),
    )
    feedback = _feedback(component_scores)
    summary = _summary(component_scores, overall_score)

    return ScoringBundle(
        overall_score=overall_score,
        component_scores=component_scores,
        metrics=metrics,
        sections=sections,
        feedback=feedback,
        summary=summary,
    )


def _pitch_score(reference: FeatureBundle, take: FeatureBundle, alignment: AlignmentPath) -> float:
    cents_errors: list[float] = []
    voiced_mismatches = 0

    for pair in alignment.pairs:
        ref_pitch = reference.pitch_contour_hz[pair.reference_index]
        take_pitch = take.pitch_contour_hz[pair.take_index]
        ref_voiced = reference.voiced_mask[pair.reference_index]
        take_voiced = take.voiced_mask[pair.take_index]

        if ref_voiced and take_voiced and ref_pitch > 0.0 and take_pitch > 0.0:
            cents_errors.append(abs(1200.0 * math.log2(ref_pitch / take_pitch)))
        elif ref_voiced != take_voiced:
            voiced_mismatches += 1

    if not cents_errors:
        return max(0.0, 100.0 - voiced_mismatches * 5.0)

    mean_error = statistics.fmean(cents_errors)
    raw_score = _score_from_error(mean_error, tolerance=200.0)
    mismatch_penalty = min(25.0, voiced_mismatches * 1.5)
    return max(0.0, raw_score - mismatch_penalty)


def _rhythm_score(reference: FeatureBundle, take: FeatureBundle) -> float:
    reference_onsets = _normalize_times(reference.onset_times_s, reference.time_axis_s)
    take_onsets = _normalize_times(take.onset_times_s, take.time_axis_s)

    if not reference_onsets and not take_onsets:
        return 100.0
    if not reference_onsets or not take_onsets:
        return 0.0

    nearest_distances = []
    for ref_onset in reference_onsets:
        nearest_distances.append(min(abs(ref_onset - take_onset) for take_onset in take_onsets))

    mean_distance = statistics.fmean(nearest_distances)
    count_penalty = abs(len(reference_onsets) - len(take_onsets)) / max(len(reference_onsets), 1)
    distance_score = _score_from_error(mean_distance, tolerance=0.12)
    count_score = max(0.0, 100.0 * (1.0 - count_penalty))
    return distance_score * 0.75 + count_score * 0.25


def _timing_score(reference: FeatureBundle, take: FeatureBundle, alignment: AlignmentPath) -> float:
    ref_denominator = max(1, reference.frame_count - 1)
    take_denominator = max(1, take.frame_count - 1)

    position_errors = []
    for pair in alignment.pairs:
        ref_position = pair.reference_index / float(ref_denominator)
        take_position = pair.take_index / float(take_denominator)
        position_errors.append(abs(ref_position - take_position))

    mean_error = statistics.fmean(position_errors)
    return _score_from_error(mean_error, tolerance=0.15)


def _section_reports(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
    config: AnalysisConfig,
) -> tuple[SectionReport, ...]:
    duration_s = reference.time_axis_s[-1] if reference.time_axis_s else 0.0
    if duration_s <= 0.0:
        section_boundaries = [(0.0, float(config.segment_duration_s))]
    else:
        section_boundaries = []
        start_s = 0.0
        while start_s <= duration_s:
            end_s = start_s + float(config.segment_duration_s)
            section_boundaries.append((start_s, end_s))
            start_s = end_s

    reports: list[SectionReport] = []
    for index, (start_s, end_s) in enumerate(section_boundaries):
        pairs = [
            pair
            for pair in alignment.pairs
            if _ref_time(reference, pair.reference_index) >= start_s
            and _ref_time(reference, pair.reference_index) < end_s
        ]
        if not pairs:
            continue

        pitch_score = _pitch_score(reference, take, AlignmentPath(tuple(pairs), 0.0, alignment.coverage_ratio))
        timing_score = _timing_score(reference, take, AlignmentPath(tuple(pairs), 0.0, alignment.coverage_ratio))
        rhythm_score = _section_rhythm_score(reference, take, start_s, end_s)
        local_scores = [pitch_score, rhythm_score, timing_score]
        stability_score = max(0.0, 100.0 - statistics.pstdev(local_scores) * 2.0)
        findings = _section_findings(start_s, end_s, pitch_score, rhythm_score, timing_score)
        reports.append(
            SectionReport(
                index=index,
                start_s=start_s,
                end_s=end_s,
                component_scores=(
                    ComponentScore(MetricName.PITCH_FIDELITY, pitch_score, config.pitch_weight),
                    ComponentScore(MetricName.RHYTHM_FIDELITY, rhythm_score, config.rhythm_weight),
                    ComponentScore(MetricName.TIMING_CONSISTENCY, timing_score, config.timing_weight),
                    ComponentScore(MetricName.SECTION_STABILITY, stability_score, config.stability_weight),
                ),
                findings=findings,
            )
        )
    return tuple(reports)


def _section_rhythm_score(
    reference: FeatureBundle,
    take: FeatureBundle,
    start_s: float,
    end_s: float,
) -> float:
    ref_onsets = [value for value in reference.onset_times_s if start_s <= value < end_s]
    take_onsets = [value for value in take.onset_times_s if start_s <= value < end_s]
    if not ref_onsets and not take_onsets:
        return 100.0
    if not ref_onsets or not take_onsets:
        return 0.0
    ref_norm = _normalize_time_window(ref_onsets, start_s, end_s)
    take_norm = _normalize_time_window(take_onsets, start_s, end_s)
    nearest = [min(abs(left - right) for right in take_norm) for left in ref_norm]
    return _score_from_error(statistics.fmean(nearest), tolerance=0.18)


def _section_stability_score(sections: tuple[SectionReport, ...]) -> float:
    if not sections:
        raise ScoringError("at least one section report is required for section stability")
    section_means = []
    for section in sections:
        section_means.append(statistics.fmean(score.score for score in section.component_scores))
    if len(section_means) == 1:
        return section_means[0]
    return max(
        0.0,
        statistics.fmean(section_means) * 0.6 + (100.0 - statistics.pstdev(section_means) * 2.0) * 0.4,
    )


def _section_findings(
    start_s: float,
    end_s: float,
    pitch_score: float,
    rhythm_score: float,
    timing_score: float,
) -> tuple[SectionFinding, ...]:
    findings: list[SectionFinding] = []
    if pitch_score < 65.0:
        findings.append(
            SectionFinding(start_s, end_s, Severity.WARNING, "Pitch stability drops in this section.")
        )
    if rhythm_score < 65.0:
        findings.append(
            SectionFinding(start_s, end_s, Severity.WARNING, "Onset timing is weak in this section.")
        )
    if timing_score < 65.0:
        findings.append(
            SectionFinding(start_s, end_s, Severity.WARNING, "Reference alignment drifts in this section.")
        )
    return tuple(findings)


def _normalize_times(values: tuple[float, ...], time_axis: tuple[float, ...]) -> tuple[float, ...]:
    if not values:
        return ()
    if not time_axis:
        return values
    duration = max(time_axis[-1], 1e-9)
    return tuple(value / duration for value in values)


def _normalize_time_window(values: list[float], start_s: float, end_s: float) -> tuple[float, ...]:
    duration = max(end_s - start_s, 1e-9)
    return tuple((value - start_s) / duration for value in values)


def _ref_time(reference: FeatureBundle, reference_index: int) -> float:
    if not reference.time_axis_s:
        return float(reference_index)
    return reference.time_axis_s[reference_index]


def _feedback(component_scores: tuple[ComponentScore, ...]) -> tuple[str, ...]:
    strongest = max(component_scores, key=lambda score: score.score)
    weakest = min(component_scores, key=lambda score: score.score)
    overall_score = sum(score.score * score.weight for score in component_scores)

    return (
        f"Keep leaning on {_metric_label(strongest.name.value)}; it is currently the clearest strength in the take.",
        _focus_message(weakest.name),
        _overall_guidance(overall_score),
    )


def _summary(component_scores: tuple[ComponentScore, ...], overall_score: float) -> str:
    weakest = min(component_scores, key=lambda score: score.score)
    strongest = max(component_scores, key=lambda score: score.score)
    return (
        f"{_summary_lead(overall_score)} "
        f"Best area: {_metric_label(strongest.name.value)} ({strongest.score:.1f}/100). "
        f"Main improvement area: {_metric_label(weakest.name.value)} ({weakest.score:.1f}/100)."
    )


def _focus_message(metric_name: MetricName) -> str:
    if metric_name == MetricName.PITCH_FIDELITY:
        return (
            "Primary focus area: Pitch Fidelity. Slow the passage down and match sustained notes "
            "more deliberately against the reference."
        )
    if metric_name == MetricName.RHYTHM_FIDELITY:
        return (
            "Primary focus area: Rhythm Fidelity. Rehearse the passage slower and re-lock the onset "
            "pattern against the reference."
        )
    if metric_name == MetricName.TIMING_CONSISTENCY:
        return (
            "Primary focus area: Timing Consistency. Tighten phrase timing so the take stops drifting "
            "across the section."
        )
    return (
        "Primary focus area: Section Stability. The take quality changes too much between sections, "
        "so isolate weaker segments and repeat them."
    )


def _overall_guidance(score: float) -> str:
    if score >= 85.0:
        return (
            "Overall the take is strong; preserve the current strengths while improving one weaker "
            "area at a time."
        )
    if score >= 70.0:
        return (
            "Overall the take is promising; the fastest win will come from tightening the weakest "
            "area before changing everything else."
        )
    return (
        "Overall the take still diverges noticeably from the reference; reduce tempo and rebuild the "
        "weakest area first."
    )


def _summary_lead(score: float) -> str:
    if score >= 90.0:
        return "Excellent reference match overall."
    if score >= 80.0:
        return "Strong reference match overall."
    if score >= 70.0:
        return "Promising reference match overall."
    return "The take diverges noticeably from the reference overall."


def _metric_label(raw_name: str) -> str:
    return raw_name.replace('_', ' ').title()


def _severity_for_score(score: float) -> Severity:
    if score >= 85.0:
        return Severity.INFO
    if score >= 70.0:
        return Severity.NOTICE
    if score >= 50.0:
        return Severity.WARNING
    return Severity.CRITICAL


def _score_from_error(error: float, *, tolerance: float) -> float:
    if tolerance <= 0.0:
        raise ScoringError("tolerance must be positive")
    return max(0.0, min(100.0, 100.0 * (1.0 - (error / tolerance))))
