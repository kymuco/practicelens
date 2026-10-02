from __future__ import annotations

from practicelens.alignment.models import AlignmentPair, AlignmentPath
from practicelens.features.models import FeatureBundle
from practicelens.measurement.cross_talk_attribution import (
    alignment_diagnostics,
    build_linear_alignment,
    classify_protected_cross_talk,
    feature_diagnostics,
)


def _bundle(
    *,
    frame_count: int = 4,
    pitch: tuple[float, ...] | None = None,
    onsets: tuple[float, ...] = (0.5, 1.5),
) -> FeatureBundle:
    times = tuple(float(index) for index in range(frame_count))
    pitches = pitch or tuple(220.0 for _ in range(frame_count))
    return FeatureBundle(
        time_axis_s=times,
        energy_curve=tuple(0.5 for _ in range(frame_count)),
        zero_crossing_rate=tuple(0.1 for _ in range(frame_count)),
        pitch_contour_hz=pitches,
        voiced_mask=tuple(value > 0.0 for value in pitches),
        onset_times_s=onsets,
        estimated_tempo_bpm=60.0,
    )


def test_linear_alignment_is_monotonic_and_endpoint_preserving() -> None:
    reference = _bundle(frame_count=5)
    take = _bundle(frame_count=3)

    alignment = build_linear_alignment(reference, take)

    assert alignment.pairs[0].take_index == 0
    assert alignment.pairs[-1].take_index == 2
    assert [pair.take_index for pair in alignment.pairs] == sorted(
        pair.take_index for pair in alignment.pairs
    )


def test_feature_diagnostics_exposes_pitch_and_onset_changes_before_dtw() -> None:
    reference = _bundle()
    take = _bundle(
        pitch=(220.0, 230.0, 220.0, 220.0),
        onsets=(0.5, 2.0),
    )
    linear = build_linear_alignment(reference, take)

    diagnostics = feature_diagnostics(reference, take, linear)

    assert diagnostics["linear_pitch_mean_cents_error"] > 0.0
    assert diagnostics["normalized_onset_mean_nearest_distance"] > 0.0
    assert diagnostics["onset_count_delta"] == 0


def test_alignment_diagnostics_detects_warp_steps() -> None:
    reference = _bundle(frame_count=4)
    take = _bundle(frame_count=4)
    alignment = AlignmentPath(
        pairs=(
            AlignmentPair(0, 0, 0.0),
            AlignmentPair(1, 1, 0.1),
            AlignmentPair(1, 2, 0.2),
            AlignmentPair(2, 3, 0.1),
            AlignmentPair(3, 3, 0.0),
        ),
        total_cost=0.4,
        coverage_ratio=1.0,
    )

    diagnostics = alignment_diagnostics(reference, take, alignment)

    assert diagnostics["warp_step_fraction"] == 0.5
    assert diagnostics["mean_normalized_position_error"] > 0.0


def test_attribution_classifies_alignment_only_cross_talk() -> None:
    assert (
        classify_protected_cross_talk(
            observed_max_abs_delta=2.0,
            linear_max_abs_delta=0.0,
            alignment_max_abs_contribution=2.0,
        )
        == "alignment_path"
    )


def test_attribution_classifies_pre_alignment_cross_talk() -> None:
    assert (
        classify_protected_cross_talk(
            observed_max_abs_delta=2.0,
            linear_max_abs_delta=2.0,
            alignment_max_abs_contribution=0.0,
        )
        == "pre_alignment_feature_or_score_path"
    )


def test_attribution_classifies_mixed_cross_talk() -> None:
    assert (
        classify_protected_cross_talk(
            observed_max_abs_delta=2.0,
            linear_max_abs_delta=3.0,
            alignment_max_abs_contribution=1.0,
        )
        == "mixed_pre_alignment_and_alignment"
    )


def test_attribution_reports_none_when_observed_score_is_invariant() -> None:
    assert (
        classify_protected_cross_talk(
            observed_max_abs_delta=0.0,
            linear_max_abs_delta=4.0,
            alignment_max_abs_contribution=4.0,
        )
        == "none"
    )
