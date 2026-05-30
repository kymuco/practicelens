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
_START_OFFSET_WARNING_S = 0.35
_LEADING_NOISE_WARNING_S = 0.25
_ENERGY_ACTIVITY_RELATIVE_THRESHOLD = 0.20
_SCORE_DIGITS = 6
_DURATION_WARNING_MESSAGE = (
    "Take duration differs substantially from the reference. Possible causes include extra silence, "
    "a restart, a missing section, or unrelated material."
)
_START_DELAY_MESSAGE = (
    "The take start may be delayed relative to the reference. This may indicate a weak or missing first note, "
    "late playing, or leading silence before the musical activity."
)
_LEADING_NOISE_MESSAGE = (
    "The take may contain leading noise before the first clear musical activity. Possible causes include handling noise, "
    "breath noise, pickup noise, or room noise before the performance starts."
)


def summarize_input_suitability(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
) -> InputSuitabilitySummary:
    """Build a deterministic evidence summary for the analyzed input pair."""

    reference_duration_s = _duration_s(reference)
    take_duration_s = _duration_s(take)
    duration_ratio = _duration_ratio(reference_duration_s, take_duration_s)
    duration_diagnostic = _duration_diagnostic(reference_duration_s, take_duration_s, duration_ratio)
    duration_diagnostic_message = _duration_diagnostic_message(duration_diagnostic)
    reference_activity_start_s = _activity_start_s(reference)
    take_activity_start_s = _activity_start_s(take)
    start_offset_s = _start_offset_s(reference_activity_start_s, take_activity_start_s)
    leading_noise_duration_s = _leading_noise_duration_s(take, take_activity_start_s)
    start_diagnostic = _start_diagnostic(start_offset_s, leading_noise_duration_s)
    start_diagnostic_message = _start_diagnostic_message(start_diagnostic)
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

    if duration_diagnostic == "duration_ratio_unavailable":
        low_confidence = True
        reasons.append("Reference or take duration is unavailable.")
    elif duration_diagnostic == "duration_ratio_ok":
        reasons.append("Take duration is comparable to the reference.")
    else:
        reasons.append(duration_diagnostic_message or "Take duration differs from the reference.")
        risk_points += 1
        if duration_ratio < _DURATION_RATIO_LOW_MIN or duration_ratio > _DURATION_RATIO_LOW_MAX:
            low_confidence = True

    if start_diagnostic == "start_region_unavailable":
        reasons.append("Start-region activity evidence is unavailable.")
    elif start_diagnostic == "start_region_ok":
        reasons.append("Start-region activity appears aligned enough for review.")
    else:
        reasons.append(start_diagnostic_message or "Start-region activity may not align cleanly.")
        risk_points += 1

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
        duration_diagnostic=duration_diagnostic,
        duration_diagnostic_message=duration_diagnostic_message,
        reference_activity_start_s=_seconds_or_none(reference_activity_start_s),
        take_activity_start_s=_seconds_or_none(take_activity_start_s),
        start_offset_s=_seconds_or_none(start_offset_s),
        leading_noise_duration_s=Seconds(_round_ratio(leading_noise_duration_s)),
        start_diagnostic=start_diagnostic,
        start_diagnostic_message=start_diagnostic_message,
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


def _duration_diagnostic(reference_duration_s: float, take_duration_s: float, duration_ratio: float) -> str:
    if reference_duration_s <= 0.0 or take_duration_s <= 0.0:
        return "duration_ratio_unavailable"
    if duration_ratio < _DURATION_RATIO_WARNING_MIN:
        return "take_much_shorter_than_reference"
    if duration_ratio > _DURATION_RATIO_WARNING_MAX:
        return "take_much_longer_than_reference"
    return "duration_ratio_ok"


def _duration_diagnostic_message(duration_diagnostic: str) -> str | None:
    if duration_diagnostic in {"take_much_shorter_than_reference", "take_much_longer_than_reference"}:
        return _DURATION_WARNING_MESSAGE
    return None


def _activity_start_s(bundle: FeatureBundle) -> float | None:
    starts = [_first_voiced_time_s(bundle), _first_onset_time_s(bundle), _first_energy_activity_time_s(bundle)]
    available_starts = [start for start in starts if start is not None]
    if not available_starts:
        return None
    return min(available_starts)


def _first_voiced_time_s(bundle: FeatureBundle) -> float | None:
    for time_s, voiced in zip(bundle.time_axis_s, bundle.voiced_mask, strict=False):
        if voiced:
            return float(time_s)
    return None


def _first_onset_time_s(bundle: FeatureBundle) -> float | None:
    if not bundle.onset_times_s:
        return None
    return float(bundle.onset_times_s[0])


def _first_energy_activity_time_s(bundle: FeatureBundle) -> float | None:
    if not bundle.time_axis_s or not bundle.energy_curve:
        return None
    peak_energy = max(bundle.energy_curve)
    if peak_energy <= 0.0:
        return None
    threshold = peak_energy * _ENERGY_ACTIVITY_RELATIVE_THRESHOLD
    for time_s, energy in zip(bundle.time_axis_s, bundle.energy_curve, strict=False):
        if energy >= threshold:
            return float(time_s)
    return None


def _start_offset_s(reference_activity_start_s: float | None, take_activity_start_s: float | None) -> float | None:
    if reference_activity_start_s is None or take_activity_start_s is None:
        return None
    return _round_ratio(take_activity_start_s - reference_activity_start_s)


def _leading_noise_duration_s(bundle: FeatureBundle, take_activity_start_s: float | None) -> float:
    if take_activity_start_s is None or take_activity_start_s <= 0.0:
        return 0.0
    if not bundle.time_axis_s or not bundle.energy_curve:
        return 0.0

    activity_index = _first_index_at_or_after(bundle.time_axis_s, take_activity_start_s)
    if activity_index <= 0:
        return 0.0

    pre_activity_energy = bundle.energy_curve[:activity_index]
    post_activity_energy = bundle.energy_curve[activity_index:]
    if not pre_activity_energy or not post_activity_energy:
        return 0.0

    max_post_activity_energy = max(post_activity_energy)
    if max_post_activity_energy <= 0.0:
        return 0.0

    noise_threshold = max_post_activity_energy * _ENERGY_ACTIVITY_RELATIVE_THRESHOLD
    noisy_times = [time_s for time_s, energy in zip(bundle.time_axis_s[:activity_index], pre_activity_energy, strict=False) if energy >= noise_threshold]
    if not noisy_times:
        return 0.0
    return _round_ratio(max(0.0, take_activity_start_s - noisy_times[0]))


def _first_index_at_or_after(time_axis_s: tuple[float, ...], start_s: float) -> int:
    for index, time_s in enumerate(time_axis_s):
        if time_s >= start_s:
            return index
    return len(time_axis_s)


def _start_diagnostic(start_offset_s: float | None, leading_noise_duration_s: float) -> str:
    if start_offset_s is None:
        return "start_region_unavailable"
    if leading_noise_duration_s >= _LEADING_NOISE_WARNING_S:
        return "take_leading_noise_before_activity"
    if start_offset_s >= _START_OFFSET_WARNING_S:
        return "take_activity_starts_late"
    return "start_region_ok"


def _start_diagnostic_message(start_diagnostic: str) -> str | None:
    if start_diagnostic == "take_activity_starts_late":
        return _START_DELAY_MESSAGE
    if start_diagnostic == "take_leading_noise_before_activity":
        return _LEADING_NOISE_MESSAGE
    return None


def _seconds_or_none(value: float | None) -> Seconds | None:
    if value is None:
        return None
    return Seconds(_round_ratio(value))


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
