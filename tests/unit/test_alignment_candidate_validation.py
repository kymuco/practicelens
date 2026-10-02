from __future__ import annotations

from practicelens.measurement.alignment_candidate_validation import (
    _directional_verdict,
    _monotonicity_verdict,
    _no_measurement_regression,
    _safe_ratio,
)
from practicelens.measurement.alignment_substrate_ablation import (
    CURRENT_POSITIONAL_PROFILE,
)
from practicelens.measurement.baseline_audit import AUDITED_MEASUREMENTS


def test_candidate_profile_is_frozen_from_r0_5d() -> None:
    assert CURRENT_POSITIONAL_PROFILE.name == "current_positional_0p10"
    assert CURRENT_POSITIONAL_PROFILE.pitch_weight == 0.55
    assert CURRENT_POSITIONAL_PROFILE.energy_weight == 0.25
    assert CURRENT_POSITIONAL_PROFILE.zcr_weight == 0.20
    assert CURRENT_POSITIONAL_PROFILE.voiced_mismatch_penalty == 0.40
    assert CURRENT_POSITIONAL_PROFILE.position_penalty_weight == 0.10


def test_directional_and_monotonicity_verdicts_remain_strict() -> None:
    assert _directional_verdict([100.0, 99.0, 98.0]) == "PASS"
    assert _directional_verdict([100.0, 100.0]) == "UNRESOLVED"
    assert _directional_verdict([100.0, 101.0]) == "FAIL"

    assert _monotonicity_verdict([100.0, 99.0, 98.0]) == "PASS"
    assert _monotonicity_verdict([100.0, 98.0, 99.0, 97.0]) == "PARTIAL"
    assert _monotonicity_verdict([100.0, 100.0]) == "UNRESOLVED"


def test_nuisance_no_regression_requires_every_measurement_not_worse() -> None:
    production = {
        name: float(index)
        for index, name in enumerate(AUDITED_MEASUREMENTS, start=1)
    }
    candidate = dict(production)
    assert _no_measurement_regression(
        production=production,
        candidate=candidate,
    )

    candidate[AUDITED_MEASUREMENTS[-1]] += 0.01
    assert not _no_measurement_regression(
        production=production,
        candidate=candidate,
    )


def test_safe_ratio_handles_zero_baseline_without_hiding_new_movement() -> None:
    assert _safe_ratio(0.0, 0.0) == 1.0
    assert _safe_ratio(2.0, 4.0) == 0.5
    assert _safe_ratio(0.1, 0.0) is None
