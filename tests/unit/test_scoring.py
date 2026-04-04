from practicelens.alignment.models import AlignmentPair, AlignmentPath
from practicelens.domain.models import AnalysisConfig
from practicelens.features.models import FeatureBundle
from practicelens.scoring import score_aligned_features


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


def _diagonal_alignment(frame_count: int) -> AlignmentPath:
    pairs = tuple(
        AlignmentPair(reference_index=index, take_index=index, local_cost=0.0)
        for index in range(frame_count)
    )
    return AlignmentPath(pairs=pairs, total_cost=0.0, coverage_ratio=1.0)


def test_score_aligned_features_rewards_matching_inputs() -> None:
    reference = _bundle()
    take = _bundle()

    scoring = score_aligned_features(reference, take, _diagonal_alignment(4), AnalysisConfig())

    assert scoring.overall_score >= 90.0
    assert all(score.score >= 85.0 for score in scoring.component_scores)
    assert scoring.sections


def test_score_aligned_features_penalizes_detuned_pitch() -> None:
    reference = _bundle(pitch=(220.0, 220.0, 220.0, 220.0))
    take = _bundle(pitch=(246.94, 246.94, 246.94, 246.94))

    scoring = score_aligned_features(reference, take, _diagonal_alignment(4), AnalysisConfig())
    pitch_score = next(score.score for score in scoring.component_scores if score.name.value == "pitch_fidelity")

    assert pitch_score < 90.0


def test_score_aligned_features_penalizes_timing_and_rhythm_drift() -> None:
    reference = _bundle(pitch=(220.0, 220.0, 220.0, 220.0), onsets=(1.0, 3.0))
    take = _bundle(pitch=(220.0, 220.0, 220.0, 220.0, 220.0), onsets=(1.8, 3.8))
    alignment = AlignmentPath(
        pairs=(
            AlignmentPair(0, 0, 0.0),
            AlignmentPair(1, 2, 0.0),
            AlignmentPair(2, 3, 0.0),
            AlignmentPair(3, 4, 0.0),
        ),
        total_cost=0.0,
        coverage_ratio=0.8,
    )

    scoring = score_aligned_features(reference, take, alignment, AnalysisConfig())
    score_map = {score.name.value: score.score for score in scoring.component_scores}

    assert score_map["rhythm_fidelity"] < 80.0
    assert score_map["timing_consistency"] < 80.0
