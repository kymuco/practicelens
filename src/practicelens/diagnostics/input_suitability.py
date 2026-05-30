from __future__ import annotations

from practicelens.alignment import AlignmentPath
from practicelens.domain.models import InputSuitabilitySummary
from practicelens.domain.types import Seconds
from practicelens.features import FeatureBundle

_DURATION_RATIO_WARNING_MIN = 0.75
_DURATION_RATIO_WARNING_MAX = 1.35
_DURATION_RATIO_LOW_MIN = 0.50
_DURATION_RATIO_LOW_MAX = 2.00
_ALIGNMENT_WARNING_MIN = 0.85
_ALIGNMENT_LOW_MIN = 0.60
_VOICED_WARNING_MIN = 0.35
_VOICED_LOW_MIN = 0.15
_ONSET_PRESENT_MIN = 2
_SCORE_DIGITS = 6


def summarize_input_suitability(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
) -> InputSuitabilitySummary:
    """Build a deterministic evidence summary for the analyzed input pair."""

    reference_duration_s = _duration_s(reference)
    take_duration_s = _duration_s(take)
    duration_ratio = _duration_ratio(reference_duration_s, take_duration_s)
    alignment_coverage = _round_ratio(alignment.coverage_ratio)
    reference_voiced_coverage = _round_ratio(_voiced_ratio(reference))
    take_voiced_coverage = _round_ratio(_voiced_ratio(take))
    voiced_frame_coverage = _round_ratio(min(reference_voiced_coverage, take_voiced_coverage))
    reference_onset_count = len(reference.onset_times_s)
    take_onset_count = len(take.onset_times_s)
    onset_evidence = _onset_evidence(reference_onset_count, take_onset_count)

    risk_points = 0
    low_confidence = False
    reasons: list[str] = []

    if reference_duration_s <= 0.0 or take_duration_s <= 0.0:
        low_confidence = True
        reasons.append("Reference or take duration is unavailable.")
    elif _DURATION_RATIO_WARNING_MIN <= duration_ratio <= _DURATION_RATIO_WARNING_MAX:
        reasons.append("Take duration is comparable to the reference.")
    else:
        reasons.append("Take duration differs from the reference.")
        risk_points += 1
        if duration_ratio < _DURATION_RATIO_LOW_MIN or duration_ratio > _DURATION_RATIO_LOW_MAX:
            low_confidence = True

    if alignment_coverage >= _ALIGNMENT_WARNING_MIN:
        reasons.append("Alignment coverage is broad.")
    else:
        reasons.append("Alignment coverage is limited.")
        risk_points += 1
        if alignment_coverage < _ALIGNMENT_LOW_MIN:
            low_confidence = True

    if voiced_frame_coverage >= _VOICED_WARNING_MIN:
        reasons.append("Voiced-frame coverage is sufficient.")
    else:
        reasons.append("Voiced-frame coverage is limited.")
        risk_points += 1
        if voiced_frame_coverage < _VOICED_LOW_MIN:
            low_confidence = True

    if onset_evidence == "present":
        reasons.append("Onset evidence is present.")
    elif onset_evidence == "sparse":
        reasons.append("Onset evidence is sparse.")
        risk_points += 1
    else:
        reasons.append("Onset evidence is absent.")
        risk_points += 1

    status = _status(low_confidence=low_confidence, risk_points=risk_points)
    return InputSuitabilitySummary(
        status=status,
        reference_duration_s=Seconds(_round_ratio(reference_duration_s)),
        take_duration_s=Seconds(_round_ratio(take_duration_s)),
        duration_ratio=duration_ratio,
        alignment_coverage=alignment_coverage,
        voiced_frame_coverage=voiced_frame_coverage,
        reference_voiced_frame_coverage=reference_voiced_coverage,
        take_voiced_frame_coverage=take_voiced_coverage,
        onset_evidence=onset_evidence,
        reference_onset_count=reference_onset_count,
        take_onset_count=take_onset_count,
        reasons=tuple(reasons),
    )


def _duration_s(bundle: FeatureBundle) -> float:
    if not bundle.time_axis_s:
        return 0.0
    if len(bundle.time_axis_s) == 1:
        return max(0.0, bundle.time_axis_s[0])
    return max(0.0, bundle.time_axis_s[-1] - bundle.time_axis_s[0])


def _duration_ratio(reference_duration_s: float, take_duration_s: float) -> float:
    if reference_duration_s <= 0.0:
        return 0.0
    return _round_ratio(take_duration_s / reference_duration_s)


def _voiced_ratio(bundle: FeatureBundle) -> float:
    if not bundle.voiced_mask:
        return 0.0
    return sum(1 for voiced in bundle.voiced_mask if voiced) / float(len(bundle.voiced_mask))


def _onset_evidence(reference_onset_count: int, take_onset_count: int) -> str:
    shared_onset_count = min(reference_onset_count, take_onset_count)
    if shared_onset_count >= _ONSET_PRESENT_MIN:
        return "present"
    if shared_onset_count == 1:
        return "sparse"
    return "absent"


def _status(*, low_confidence: bool, risk_points: int) -> str:
    if low_confidence or risk_points >= 3:
        return "low_confidence"
    if risk_points > 0:
        return "warning"
    return "ok"


def _round_ratio(value: float) -> float:
    return round(float(value), _SCORE_DIGITS)
