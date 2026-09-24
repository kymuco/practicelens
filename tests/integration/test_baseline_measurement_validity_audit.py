from __future__ import annotations

from pathlib import Path

from practicelens.measurement.baseline_audit import (
    AUDITED_MEASUREMENTS,
    AuditVerdict,
    _directional_sensitivity_verdict,
    _nonincreasing_monotonicity_verdict,
    run_baseline_measurement_validity_audit,
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


def test_baseline_audit_runs_frozen_pipeline_and_writes_records(tmp_path: Path) -> None:
    result = run_baseline_measurement_validity_audit(
        tmp_path / "audit",
        code_revision="test-revision",
    )

    assert result.summary_path.is_file()
    assert result.harness.manifest_path.is_file()
    assert len(result.observations) == 16
    assert len(tuple(result.records_dir.glob("*.json"))) == 16

    summary = result.summary
    assert summary["kind"] == "baseline_measurement_validity_audit"
    assert summary["code_revision"] == "test-revision"
    assert summary["audited_measurements"] == list(AUDITED_MEASUREMENTS)
    assert len(summary["series"]) == 4

    families = {series["family"] for series in summary["series"]}
    assert families == {
        "amplitude_gain",
        "deterministic_additive_noise",
        "pitch_drift",
        "local_timing_warp",
    }

    for series in summary["series"]:
        assert len(series["strengths"]) == 4
        assert series["strengths"][0] == 0.0
        assert set(series["values"]) == set(AUDITED_MEASUREMENTS)
        assert set(series["max_abs_deltas"]) == set(AUDITED_MEASUREMENTS)
        assert series["family_verdict"] in {
            "PASS",
            "PARTIAL",
            "FAIL",
            "UNRESOLVED",
        }
