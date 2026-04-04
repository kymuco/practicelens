from practicelens.alignment import align_feature_bundles
from practicelens.features.models import FeatureBundle


def _bundle(*, pitch=(220.0, 220.0, 220.0, 220.0), onsets=(1.0, 3.0)) -> FeatureBundle:
    frame_count = len(pitch)
    return FeatureBundle(
        time_axis_s=tuple(float(index) for index in range(frame_count)),
        energy_curve=tuple(0.5 for _ in range(frame_count)),
        zero_crossing_rate=tuple(0.1 for _ in range(frame_count)),
        pitch_contour_hz=tuple(pitch),
        voiced_mask=tuple(value > 0.0 for value in pitch),
        onset_times_s=tuple(onsets),
        estimated_tempo_bpm=120.0,
    )


def test_align_feature_bundles_prefers_diagonal_for_identical_inputs() -> None:
    reference = _bundle()
    take = _bundle()

    alignment = align_feature_bundles(reference, take)

    assert alignment.coverage_ratio == 1.0
    assert alignment.pairs[0].reference_index == 0
    assert alignment.pairs[0].take_index == 0
    assert alignment.pairs[-1].reference_index == reference.frame_count - 1
    assert alignment.pairs[-1].take_index == take.frame_count - 1


def test_align_feature_bundles_handles_length_mismatch() -> None:
    reference = _bundle(pitch=(220.0, 220.0, 220.0, 220.0))
    take = _bundle(pitch=(220.0, 220.0, 220.0, 220.0, 220.0))

    alignment = align_feature_bundles(reference, take)

    assert alignment.coverage_ratio >= 0.8
    assert alignment.pair_count >= reference.frame_count
