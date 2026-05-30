from practicelens.alignment import AlignmentPath
from practicelens.diagnostics import summarize_input_suitability
from practicelens.features import FeatureBundle


def test_input_suitability_summary_reports_ok_when_evidence_is_strong() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(
            time_axis_s=(0.0, 1.0, 2.0, 3.0),
            voiced_mask=(True, True, True, True),
            onset_times_s=(0.5, 1.5),
        ),
        _feature_bundle(
            time_axis_s=(0.0, 1.0, 2.0, 3.0),
            voiced_mask=(True, True, True, True),
            onset_times_s=(0.5, 1.5),
        ),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "ok"
    assert summary.reference_duration_s == 3.0
    assert summary.take_duration_s == 3.0
    assert summary.duration_ratio == 1.0
    assert summary.alignment_coverage == 0.9
    assert summary.voiced_frame_coverage == 1.0
    assert summary.onset_evidence == "present"


def test_input_suitability_summary_reports_warning_when_duration_differs() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(
            time_axis_s=(0.0, 1.0, 2.0, 3.0),
            voiced_mask=(True, True, True, True),
            onset_times_s=(0.5, 1.5),
        ),
        _feature_bundle(
            time_axis_s=(0.0, 1.0, 2.0),
            voiced_mask=(True, True, True),
            onset_times_s=(0.5, 1.5),
        ),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.9),
    )

    assert summary.status == "warning"
    assert summary.duration_ratio == 0.666667
    assert "Take duration differs from the reference." in summary.reasons


def test_input_suitability_summary_reports_low_confidence_when_evidence_is_thin() -> None:
    summary = summarize_input_suitability(
        _feature_bundle(
            time_axis_s=(0.0, 1.0, 2.0, 3.0),
            voiced_mask=(True, False, False, False),
            onset_times_s=(),
        ),
        _feature_bundle(
            time_axis_s=(0.0, 0.5),
            voiced_mask=(False, False),
            onset_times_s=(),
        ),
        AlignmentPath(pairs=(), total_cost=0.0, coverage_ratio=0.4),
    )

    assert summary.status == "low_confidence"
    assert summary.alignment_coverage == 0.4
    assert summary.voiced_frame_coverage == 0.0
    assert summary.onset_evidence == "absent"


def _feature_bundle(
    *,
    time_axis_s: tuple[float, ...],
    voiced_mask: tuple[bool, ...],
    onset_times_s: tuple[float, ...],
) -> FeatureBundle:
    frame_count = len(time_axis_s)
    return FeatureBundle(
        time_axis_s=time_axis_s,
        energy_curve=(1.0,) * frame_count,
        zero_crossing_rate=(0.1,) * frame_count,
        pitch_contour_hz=tuple(220.0 if voiced else 0.0 for voiced in voiced_mask),
        voiced_mask=voiced_mask,
        onset_times_s=onset_times_s,
        estimated_tempo_bpm=120.0 if len(onset_times_s) >= 2 else None,
    )
