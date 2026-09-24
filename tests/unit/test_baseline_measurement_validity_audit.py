from __future__ import annotations

from pathlib import Path

from practicelens.domain.models import AnalysisConfig
from practicelens.measurement.baseline_audit import (
    AUDITED_MEASUREMENTS,
    AuditVerdict,
    ConditionAuditObservation,
    _audit_family,
    _directional_sensitivity_verdict,
    _nonincreasing_monotonicity_verdict,
)
from practicelens.measurement.contracts import (
    AnalysisConfigSnapshot,
    CandidateMeasurementResult,
    ExperimentCondition,
    InterventionRole,
    InterventionSpec,
    MeasurementExperimentRecord,
    MeasurementRunProvenance,
)
from practicelens.measurement.controlled_perturbations import ControlledPerturbationCase


def _observation(
    *,
    family: str,
    role: InterventionRole,
    strength: float,
    values: tuple[float, float, float, float],
) -> ConditionAuditObservation:
    condition_id = f"{family}__{strength}"
    condition = ExperimentCondition(
        condition_id=condition_id,
        reference_case="reference_phrase",
        take_case=condition_id,
        intervention=InterventionSpec(
            family=family,
            role=role,
            strength=strength,
            unit="test_unit",
        ),
    )
    record = MeasurementExperimentRecord(
        experiment_id="test-audit",
        condition=condition,
        provenance=MeasurementRunProvenance(
            generator="test",
            generator_version="1",
            analysis_config=AnalysisConfigSnapshot.from_config(AnalysisConfig()),
        ),
        measurements=tuple(
            CandidateMeasurementResult(
                name=name,
                value=value,
                unit="score_0_100",
                source="component_score",
            )
            for name, value in zip(AUDITED_MEASUREMENTS, values, strict=True)
        ),
    )
    return ConditionAuditObservation(
        case=ControlledPerturbationCase(
            condition=condition,
            path=Path(f"{condition_id}.wav"),
            sha256="0" * 64,
        ),
        record=record,
        confidence_level="high",
        suitability_status="suitable",
        alignment_coverage=1.0,
    )


def test_directional_sensitivity_uses_endpoint_direction_only() -> None:
    assert _directional_sensitivity_verdict([100.0, 90.0]) is AuditVerdict.PASS
    assert _directional_sensitivity_verdict([90.0, 100.0]) is AuditVerdict.FAIL
    assert _directional_sensitivity_verdict([100.0, 100.0]) is AuditVerdict.UNRESOLVED


def test_nonincreasing_monotonicity_distinguishes_partial_response() -> None:
    assert _nonincreasing_monotonicity_verdict([100.0, 95.0, 90.0]) is AuditVerdict.PASS
    assert _nonincreasing_monotonicity_verdict([100.0, 98.0, 99.0, 90.0]) is AuditVerdict.PARTIAL
    assert _nonincreasing_monotonicity_verdict([100.0, 100.0, 100.0]) is AuditVerdict.UNRESOLVED
    assert _nonincreasing_monotonicity_verdict([100.0, 101.0, 102.0]) is AuditVerdict.FAIL


def test_nuisance_family_fails_strict_invariance_when_any_measurement_moves() -> None:
    series = _audit_family(
        "amplitude_gain",
        (
            _observation(
                family="amplitude_gain",
                role=InterventionRole.CONTROL,
                strength=0.0,
                values=(100.0, 100.0, 100.0, 100.0),
            ),
            _observation(
                family="amplitude_gain",
                role=InterventionRole.NUISANCE,
                strength=6.0,
                values=(99.0, 100.0, 100.0, 100.0),
            ),
        ),
    )

    assert series["family_verdict"] == "FAIL"
    assert series["property_verdicts"]["strict_invariance:pitch_fidelity"] == "FAIL"
    assert series["max_abs_deltas"]["pitch_fidelity"] == 1.0


def test_pitch_target_passes_when_primary_is_monotonic_and_protected_scores_hold() -> None:
    series = _audit_family(
        "pitch_drift",
        (
            _observation(
                family="pitch_drift",
                role=InterventionRole.CONTROL,
                strength=0.0,
                values=(100.0, 100.0, 100.0, 100.0),
            ),
            _observation(
                family="pitch_drift",
                role=InterventionRole.TARGET,
                strength=0.01,
                values=(95.0, 100.0, 100.0, 98.0),
            ),
            _observation(
                family="pitch_drift",
                role=InterventionRole.TARGET,
                strength=0.03,
                values=(85.0, 100.0, 100.0, 94.0),
            ),
        ),
    )

    assert series["family_verdict"] == "PASS"
    assert series["property_verdicts"] == {
        "directional_sensitivity": "PASS",
        "nonincreasing_monotonicity": "PASS",
        "strict_protected_specificity": "PASS",
    }


def test_pitch_target_is_partial_when_protected_measurement_moves() -> None:
    series = _audit_family(
        "pitch_drift",
        (
            _observation(
                family="pitch_drift",
                role=InterventionRole.CONTROL,
                strength=0.0,
                values=(100.0, 100.0, 100.0, 100.0),
            ),
            _observation(
                family="pitch_drift",
                role=InterventionRole.TARGET,
                strength=0.03,
                values=(80.0, 99.0, 100.0, 95.0),
            ),
        ),
    )

    assert series["family_verdict"] == "PARTIAL"
    assert series["property_verdicts"]["strict_protected_specificity"] == "FAIL"
