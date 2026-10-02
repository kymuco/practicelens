from __future__ import annotations

import pytest

from practicelens.alignment import align_feature_bundles
from practicelens.features.models import FeatureBundle
from practicelens.measurement.alignment_substrate_ablation import (
    CURRENT_PROFILE,
    AlignmentCostProfile,
    _directional_sensitivity_verdict,
    _nonincreasing_monotonicity_verdict,
    align_with_profile,
)


def _bundle(
    pitch: tuple[float, ...],
    energy: tuple[float, ...],
    zcr: tuple[float, ...],
) -> FeatureBundle:
    frame_count = len(pitch)
    return FeatureBundle(
        time_axis_s=tuple(index * 0.1 for index in range(frame_count)),
        energy_curve=energy,
        zero_crossing_rate=zcr,
        pitch_contour_hz=pitch,
        voiced_mask=tuple(value > 0.0 for value in pitch),
        onset_times_s=(0.1, 0.3),
        estimated_tempo_bpm=120.0,
    )


def test_current_profile_reproduces_production_dtw() -> None:
    reference = _bundle(
        (220.0, 220.0, 330.0, 330.0),
        (0.2, 0.6, 0.4, 0.7),
        (0.1, 0.2, 0.3, 0.2),
    )
    take = _bundle(
        (220.0, 225.0, 325.0, 330.0),
        (0.2, 0.5, 0.45, 0.7),
        (0.1, 0.22, 0.28, 0.2),
    )

    production = align_feature_bundles(reference, take)
    diagnostic = align_with_profile(reference, take, CURRENT_PROFILE)

    assert diagnostic.pairs == production.pairs
    assert diagnostic.total_cost == pytest.approx(production.total_cost, abs=1e-12)
    assert diagnostic.coverage_ratio == production.coverage_ratio


def test_profile_requires_normalized_feature_weights() -> None:
    with pytest.raises(ValueError, match="must sum to 1"):
        AlignmentCostProfile(
            name="bad",
            pitch_weight=0.5,
            energy_weight=0.5,
            zcr_weight=0.5,
            voiced_mismatch_penalty=0.0,
        )


def test_position_penalty_changes_off_diagonal_cost_without_changing_diagonal() -> None:
    reference = _bundle(
        (220.0, 220.0, 220.0),
        (0.5, 0.5, 0.5),
        (0.1, 0.1, 0.1),
    )
    take = _bundle(
        (220.0, 220.0, 220.0),
        (0.5, 0.5, 0.5),
        (0.1, 0.1, 0.1),
    )
    positional = AlignmentCostProfile(
        name="position",
        pitch_weight=0.55,
        energy_weight=0.25,
        zcr_weight=0.20,
        voiced_mismatch_penalty=0.40,
        position_penalty_weight=0.10,
    )

    diagnostic = align_with_profile(reference, take, positional)

    assert [(pair.reference_index, pair.take_index) for pair in diagnostic.pairs] == [
        (0, 0),
        (1, 1),
        (2, 2),
    ]
    assert diagnostic.total_cost == 0.0


def test_directional_and_monotonicity_verdicts_match_r0_semantics() -> None:
    assert _directional_sensitivity_verdict([100.0, 95.0, 90.0]) == "PASS"
    assert _directional_sensitivity_verdict([100.0, 100.0]) == "UNRESOLVED"
    assert _directional_sensitivity_verdict([100.0, 101.0]) == "FAIL"

    assert _nonincreasing_monotonicity_verdict([100.0, 95.0, 90.0]) == "PASS"
    assert _nonincreasing_monotonicity_verdict([100.0, 95.0, 97.0, 90.0]) == "PARTIAL"
    assert _nonincreasing_monotonicity_verdict([100.0, 100.0]) == "UNRESOLVED"
    assert _nonincreasing_monotonicity_verdict([100.0, 101.0, 102.0]) == "FAIL"
