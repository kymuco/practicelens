from __future__ import annotations

import json

import pytest

from practicelens.domain.models import AnalysisConfig
from practicelens.measurement import (
    MEASUREMENT_EXPERIMENT_SCHEMA_VERSION,
    AnalysisConfigSnapshot,
    CandidateMeasurementResult,
    ExperimentCondition,
    InterventionParameter,
    InterventionRole,
    InterventionSpec,
    MeasurementExperimentRecord,
    MeasurementRunProvenance,
    measurement_experiment_record_to_json,
    measurement_experiment_record_to_payload,
)


def _record() -> MeasurementExperimentRecord:
    config = AnalysisConfig(
        target_sample_rate=16_000,
        frame_length=1_024,
        hop_length=256,
        segment_duration_s=1.0,
    )
    return MeasurementExperimentRecord(
        experiment_id="r0.3-pitch-drift-v1",
        condition=ExperimentCondition(
            condition_id="pitch_drift_0.02",
            reference_case="reference_phrase",
            take_case="pitch_drift_0.02",
            intervention=InterventionSpec(
                family="pitch_drift",
                role=InterventionRole.TARGET,
                strength=0.02,
                unit="fraction",
                parameters=(
                    InterventionParameter(
                        name="curve",
                        value="linear",
                    ),
                ),
            ),
        ),
        provenance=MeasurementRunProvenance(
            generator="practicelens.controlled_perturbations",
            generator_version="1",
            code_revision="abc123",
            source_manifest="controlled/manifest.json",
            analysis_config=AnalysisConfigSnapshot.from_config(config),
        ),
        measurements=(
            CandidateMeasurementResult(
                name="pitch_fidelity",
                value=83.25,
                unit="score_0_100",
                source="component_score",
            ),
            CandidateMeasurementResult(
                name="timing_consistency",
                value=96.5,
                unit="score_0_100",
                source="component_score",
            ),
        ),
    )


def test_analysis_config_snapshot_preserves_exact_analysis_settings() -> None:
    config = AnalysisConfig(
        target_sample_rate=22_050,
        frame_length=1_024,
        hop_length=128,
        segment_duration_s=2.5,
        pitch_weight=0.4,
        rhythm_weight=0.25,
        timing_weight=0.2,
        stability_weight=0.15,
    )

    snapshot = AnalysisConfigSnapshot.from_config(config)

    assert snapshot == AnalysisConfigSnapshot(
        schema_version=1,
        target_sample_rate=22_050,
        frame_length=1_024,
        hop_length=128,
        segment_duration_s=2.5,
        pitch_weight=0.4,
        rhythm_weight=0.25,
        timing_weight=0.2,
        stability_weight=0.15,
    )


def test_control_intervention_requires_zero_strength() -> None:
    with pytest.raises(ValueError, match="control intervention strength must be zero"):
        InterventionSpec(
            family="gain",
            role=InterventionRole.CONTROL,
            strength=1.0,
            unit="db",
        )


def test_intervention_parameter_names_must_be_unique() -> None:
    with pytest.raises(ValueError, match="parameter names must be unique"):
        InterventionSpec(
            family="pitch_drift",
            role=InterventionRole.TARGET,
            strength=0.02,
            unit="fraction",
            parameters=(
                InterventionParameter(name="curve", value="linear"),
                InterventionParameter(name="curve", value="quadratic"),
            ),
        )


def test_measurement_values_must_be_finite() -> None:
    with pytest.raises(ValueError, match="measurement value must be finite"):
        CandidateMeasurementResult(
            name="pitch_fidelity",
            value=float("nan"),
            unit="score_0_100",
            source="component_score",
        )


def test_measurement_names_must_be_unique_within_record() -> None:
    record = _record()

    with pytest.raises(ValueError, match="measurement names must be unique"):
        MeasurementExperimentRecord(
            experiment_id=record.experiment_id,
            condition=record.condition,
            provenance=record.provenance,
            measurements=(
                record.measurements[0],
                record.measurements[0],
            ),
        )


def test_measurement_record_serializes_to_stable_schema_v1_payload() -> None:
    record = _record()

    payload = measurement_experiment_record_to_payload(record)

    assert payload == {
        "kind": "measurement_experiment_record",
        "schema_version": MEASUREMENT_EXPERIMENT_SCHEMA_VERSION,
        "experiment_id": "r0.3-pitch-drift-v1",
        "condition": {
            "condition_id": "pitch_drift_0.02",
            "reference_case": "reference_phrase",
            "take_case": "pitch_drift_0.02",
            "intervention": {
                "family": "pitch_drift",
                "role": "target",
                "strength": 0.02,
                "unit": "fraction",
                "parameters": [
                    {
                        "name": "curve",
                        "value": "linear",
                        "unit": None,
                    }
                ],
            },
        },
        "provenance": {
            "generator": "practicelens.controlled_perturbations",
            "generator_version": "1",
            "code_revision": "abc123",
            "source_manifest": "controlled/manifest.json",
            "analysis_config": {
                "schema_version": 1,
                "target_sample_rate": 16_000,
                "frame_length": 1_024,
                "hop_length": 256,
                "segment_duration_s": 1.0,
                "pitch_weight": 0.35,
                "rhythm_weight": 0.30,
                "timing_weight": 0.20,
                "stability_weight": 0.15,
            },
        },
        "measurements": [
            {
                "name": "pitch_fidelity",
                "value": 83.25,
                "unit": "score_0_100",
                "source": "component_score",
            },
            {
                "name": "timing_consistency",
                "value": 96.5,
                "unit": "score_0_100",
                "source": "component_score",
            },
        ],
    }


def test_measurement_record_json_is_deterministic_and_round_trippable() -> None:
    record = _record()

    first = measurement_experiment_record_to_json(record)
    second = measurement_experiment_record_to_json(record)

    assert first == second
    assert json.loads(first) == measurement_experiment_record_to_payload(record)
