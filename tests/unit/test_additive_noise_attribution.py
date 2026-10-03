from __future__ import annotations

from practicelens.alignment.models import AlignmentPair, AlignmentPath
from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisConfig
from practicelens.features.models import FeatureBundle
from practicelens.measurement.additive_noise_attribution import (
    classify_first_noise_stage,
    pitch_score_terms,
    rhythm_score_terms,
)
from practicelens.scoring import score_aligned_features


def _bundle(
    *,
    pitch: tuple[float, ...],
    onsets: tuple[float, ...],
) -> FeatureBundle:
    frame_count = len(pitch)
    return FeatureBundle(
        time_axis_s=tuple(index * 0.1 for index in range(frame_count)),
        energy_curve=tuple(0.5 for _ in range(frame_count)),
        zero_crossing_rate=tuple(0.1 for _ in range(frame_count)),
        pitch_contour_hz=pitch,
        voiced_mask=tuple(value > 0.0 for value in pitch),
        onset_times_s=onsets,
        estimated_tempo_bpm=120.0,
    )


def _identity_alignment(frame_count: int) -> AlignmentPath:
    return AlignmentPath(
        pairs=tuple(
            AlignmentPair(index, index, 0.0)
            for index in range(frame_count)
        ),
        total_cost=0.0,
        coverage_ratio=1.0,
    )


def test_pitch_score_terms_exactly_reconstruct_current_pitch_score() -> None:
    reference = _bundle(
        pitch=(220.0, 220.0, 330.0, 330.0),
        onsets=(0.1, 0.3),
    )
    take = _bundle(
        pitch=(220.0, 225.0, 325.0, 330.0),
        onsets=(0.1, 0.3),
    )
    alignment = _identity_alignment(reference.frame_count)
    scoring = score_aligned_features(
        reference,
        take,
        alignment,
        AnalysisConfig(),
    )
    pitch_score = next(
        score.score
        for score in scoring.component_scores
        if score.name == MetricName.PITCH_FIDELITY
    )

    terms = pitch_score_terms(reference, take, alignment)

    assert terms["final_score"] == pitch_score
    assert terms["mean_cents_error"] > 0.0
    assert terms["voiced_mismatch_count"] == 0


def test_rhythm_score_terms_exactly_reconstruct_current_rhythm_score() -> None:
    reference = _bundle(
        pitch=(220.0, 220.0, 330.0, 330.0),
        onsets=(0.1, 0.3),
    )
    take = _bundle(
        pitch=(220.0, 220.0, 330.0, 330.0),
        onsets=(0.1, 0.2, 0.3),
    )
    alignment = _identity_alignment(reference.frame_count)
    scoring = score_aligned_features(
        reference,
        take,
        alignment,
        AnalysisConfig(),
    )
    rhythm_score = next(
        score.score
        for score in scoring.component_scores
        if score.name == MetricName.RHYTHM_FIDELITY
    )

    terms = rhythm_score_terms(reference, take)

    assert terms["final_score"] == rhythm_score
    assert terms["take_onset_count"] == 3
    assert terms["count_penalty_fraction"] > 0.0


def test_first_stage_classification_distinguishes_feature_and_alignment_paths() -> None:
    assert (
        classify_first_noise_stage(
            feature_movement=1.0,
            linear_score_movement=2.0,
            alignment_contribution=0.0,
        )
        == "feature_extraction"
    )
    assert (
        classify_first_noise_stage(
            feature_movement=1.0,
            linear_score_movement=2.0,
            alignment_contribution=0.5,
        )
        == "feature_extraction_with_alignment_contribution"
    )
    assert (
        classify_first_noise_stage(
            feature_movement=0.0,
            linear_score_movement=0.0,
            alignment_contribution=0.5,
        )
        == "alignment"
    )
    assert (
        classify_first_noise_stage(
            feature_movement=0.0,
            linear_score_movement=2.0,
            alignment_contribution=0.0,
        )
        == "score_construction"
    )
