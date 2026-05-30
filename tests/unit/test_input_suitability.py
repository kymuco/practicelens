from practicelens.alignment import AlignmentPath
from practicelens.diagnostics import summarize_input_suitability
from practicelens.features import FeatureBundle


def test_input_suitability_summary_reports_ok_when_evidence_is_strong() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.0), voiced_mask=(True, True, True, True), onset_times_s=(0.5, 1.5)),
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.0), voiced_mask=(True, True, True, True), onset_times_s=(0.5, 1.5)),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "ok"
    assert summary.reference_duration_s == 3.0
    assert summary.take_duration_s == 3.0
    assert summary.duration_ratio == 1.0
    assert summary.duration_diagnostic == "duration_ratio_ok"
    assert summary.duration_diagnostic_message is None
    assert summary.start_diagnostic == "start_region_ok"
    assert summary.start_diagnostic_message is None
    assert summary.alignment_coverage == 0.9
    assert summary.voiced_frame_coverage == 1.0
    assert summary.onset_evidence == "present"


def test_input_suitability_summary_reports_warning_when_duration_differs() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.0), voiced_mask=(True, True, True, True), onset_times_s=(0.5, 1.5)),
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0), voiced_mask=(True, True, True), onset_times_s=(0.5, 1.5)),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "warning"
    assert summary.duration_ratio == 0.666667
    assert summary.duration_diagnostic == "take_much_shorter_than_reference"
    assert summary.duration_diagnostic_message is not None
    assert "extra silence" in summary.duration_diagnostic_message
    assert "restart" in summary.duration_diagnostic_message
    assert "missing section" in summary.duration_diagnostic_message
    assert "unrelated material" in summary.duration_diagnostic_message
    assert summary.duration_diagnostic_message in summary.reasons


def test_input_suitability_summary_reports_low_confidence_when_evidence_is_thin() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.0), voiced_mask=(True, False, False, False), onset_times_s=()),
        _feature_bundle(time_axis_s=(0.0, 0.5), voiced_mask=(False, False), onset_times_s=()),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.4),
    )

    assert summary.status == "low_confidence"
    assert summary.duration_diagnostic == "take_much_shorter_than_reference"
    assert summary.alignment_coverage == 0.4
    assert summary.voiced_frame_coverage == 0.0
    assert summary.onset_evidence == "absent"


def test_input_suitability_duration_diagnostic_reports_much_longer_take() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0), voiced_mask=(True, True, True), onset_times_s=(0.5, 1.5)),
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.0, 4.0), voiced_mask=(True, True, True, True, True), onset_times_s=(0.5, 1.5)),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "warning"
    assert summary.duration_ratio == 2.0
    assert summary.duration_diagnostic == "take_much_longer_than_reference"
    assert summary.duration_diagnostic_message is not None
    assert "extra silence" in summary.duration_diagnostic_message


def test_input_suitability_duration_diagnostic_reports_acceptable_duration() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.0), voiced_mask=(True, True, True, True), onset_times_s=(0.5, 1.5)),
        _feature_bundle(time_axis_s=(0.0, 1.0, 2.0, 3.2), voiced_mask=(True, True, True, True), onset_times_s=(0.5, 1.5)),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "ok"
    assert summary.duration_ratio == 1.066667
    assert summary.duration_diagnostic == "duration_ratio_ok"
    assert summary.duration_diagnostic_message is None


def test_input_suitability_start_diagnostic_reports_delayed_take_start() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(
            time_axis_s=(0.0, 0.25, 0.5, 0.75, 1.0),
            voiced_mask=(True, True, True, True, True),
            onset_times_s=(0.1, 0.6),
            energy_curve=(1.0, 1.0, 1.0, 1.0, 1.0),
        ),
        _feature_bundle(
            time_axis_s=(0.0, 0.25, 0.5, 0.75, 1.0),
            voiced_mask=(False, False, True, True, True),
            onset_times_s=(0.55, 0.8),
            energy_curve=(0.0, 0.0, 1.0, 1.0, 1.0),
        ),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "warning"
    assert summary.reference_activity_start_s == 0.0
    assert summary.take_activity_start_s == 0.5
    assert summary.start_offset_s == 0.5
    assert summary.start_diagnostic == "take_activity_starts_late"
    assert summary.start_diagnostic_message is not None
    assert "may indicate" in summary.start_diagnostic_message
    assert summary.start_diagnostic_message in summary.reasons


def test_input_suitability_start_diagnostic_reports_noisy_leading_start() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(
            time_axis_s=(0.0, 0.25, 0.5, 0.75, 1.0),
            voiced_mask=(True, True, True, True, True),
            onset_times_s=(0.1, 0.6),
            energy_curve=(1.0, 1.0, 1.0, 1.0, 1.0),
        ),
        _feature_bundle(
            time_axis_s=(0.0, 0.25, 0.5, 0.75, 1.0),
            voiced_mask=(False, False, True, True, True),
            onset_times_s=(0.55, 0.8),
            energy_curve=(0.3, 0.3, 1.0, 1.0, 1.0),
        ),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "warning"
    assert summary.leading_noise_duration_s == 0.5
    assert summary.start_diagnostic == "take_leading_noise_before_activity"
    assert summary.start_diagnostic_message is not None
    assert "may contain leading noise" in summary.start_diagnostic_message
    assert "Possible causes" in summary.start_diagnostic_message
    assert summary.start_diagnostic_message in summary.reasons


def test_input_suitability_start_diagnostic_reports_normal_start() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(time_axis_s=(0.0, 0.25, 0.5, 0.75, 1.0), voiced_mask=(True, True, True, True, True), onset_times_s=(0.1, 0.6)),
        _feature_bundle(time_axis_s=(0.0, 0.25, 0.5, 0.75, 1.0), voiced_mask=(True, True, True, True, True), onset_times_s=(0.1, 0.6)),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "ok"
    assert summary.start_offset_s == 0.0
    assert summary.leading_noise_duration_s == 0.0
    assert summary.start_diagnostic == "start_region_ok"
    assert summary.start_diagnostic_message is None


def _feature_bundle(
    *,
    time_axis_s: tuple[float, ...],
    voiced_mask: tuple[bool, ...],
    onset_times_s: tuple[float, ...],
    energy_curve: tuple[float, ...] | None = None,
) -> FeatureBundle:
    frame_count = len(time_axis_s)
    return FeatureBundle(
        time_axis_s=time_axis_s,
        energy_curve=energy_curve or (1.0,) * frame_count,
        zero_crossing_rate=(0.1,) * frame_count,
        pitch_contour_hz=tuple(220.0 if voiced else 0.0 for voiced in voiced_mask),
        voiced_mask=voiced_mask,
        onset_times_s=onset_times_s,
        estimated_tempo_bpm=120.0 if len(onset_times_s) >= 2 else None,
    )
