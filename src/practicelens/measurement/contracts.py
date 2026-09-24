from __future__ import annotations

import json
import math
from dataclasses import dataclass

from practicelens.domain.enums import StrEnum
from practicelens.domain.models import AnalysisConfig

MEASUREMENT_EXPERIMENT_SCHEMA_VERSION = 1


class InterventionRole(StrEnum):
    """Role of a controlled intervention in a measurement experiment."""

    CONTROL = "control"
    NUISANCE = "nuisance"
    TARGET = "target"


ParameterValue = str | int | float | bool


@dataclass(slots=True, frozen=True)
class InterventionParameter:
    """One explicit parameter used to construct an intervention."""

    name: str
    value: ParameterValue
    unit: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("intervention parameter name must not be empty")
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("intervention parameter float value must be finite")
        if self.unit is not None and not self.unit.strip():
            raise ValueError("intervention parameter unit must not be empty when provided")


@dataclass(slots=True, frozen=True)
class InterventionSpec:
    """Controlled change applied to one experiment condition."""

    family: str
    role: InterventionRole
    strength: float
    unit: str | None = None
    parameters: tuple[InterventionParameter, ...] = ()

    def __post_init__(self) -> None:
        if not self.family.strip():
            raise ValueError("intervention family must not be empty")
        if not math.isfinite(self.strength):
            raise ValueError("intervention strength must be finite")
        if self.role is InterventionRole.CONTROL and self.strength != 0.0:
            raise ValueError("control intervention strength must be zero")
        if self.unit is not None and not self.unit.strip():
            raise ValueError("intervention unit must not be empty when provided")

        names = tuple(parameter.name for parameter in self.parameters)
        if len(names) != len(set(names)):
            raise ValueError("intervention parameter names must be unique")


@dataclass(slots=True, frozen=True)
class AnalysisConfigSnapshot:
    """Exact analysis configuration used for a measurement experiment."""

    schema_version: int
    target_sample_rate: int
    frame_length: int
    hop_length: int
    segment_duration_s: float
    pitch_weight: float
    rhythm_weight: float
    timing_weight: float
    stability_weight: float

    @classmethod
    def from_config(cls, config: AnalysisConfig) -> AnalysisConfigSnapshot:
        return cls(
            schema_version=int(config.schema_version),
            target_sample_rate=config.target_sample_rate,
            frame_length=config.frame_length,
            hop_length=config.hop_length,
            segment_duration_s=float(config.segment_duration_s),
            pitch_weight=config.pitch_weight,
            rhythm_weight=config.rhythm_weight,
            timing_weight=config.timing_weight,
            stability_weight=config.stability_weight,
        )


@dataclass(slots=True, frozen=True)
class ExperimentCondition:
    """Identity and controlled intervention for one experiment condition."""

    condition_id: str
    reference_case: str
    take_case: str
    intervention: InterventionSpec

    def __post_init__(self) -> None:
        if not self.condition_id.strip():
            raise ValueError("condition_id must not be empty")
        if not self.reference_case.strip():
            raise ValueError("reference_case must not be empty")
        if not self.take_case.strip():
            raise ValueError("take_case must not be empty")


@dataclass(slots=True, frozen=True)
class MeasurementRunProvenance:
    """Reproducibility information for one measurement run."""

    generator: str
    generator_version: str
    analysis_config: AnalysisConfigSnapshot
    code_revision: str | None = None
    source_manifest: str | None = None

    def __post_init__(self) -> None:
        if not self.generator.strip():
            raise ValueError("generator must not be empty")
        if not self.generator_version.strip():
            raise ValueError("generator_version must not be empty")
        if self.code_revision is not None and not self.code_revision.strip():
            raise ValueError("code_revision must not be empty when provided")
        if self.source_manifest is not None and not self.source_manifest.strip():
            raise ValueError("source_manifest must not be empty when provided")


@dataclass(slots=True, frozen=True)
class CandidateMeasurementResult:
    """One candidate measurement output captured without claiming validity."""

    name: str
    value: float
    unit: str
    source: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("measurement name must not be empty")
        if not math.isfinite(self.value):
            raise ValueError("measurement value must be finite")
        if not self.unit.strip():
            raise ValueError("measurement unit must not be empty")
        if not self.source.strip():
            raise ValueError("measurement source must not be empty")


@dataclass(slots=True, frozen=True)
class MeasurementExperimentRecord:
    """Stable machine-readable record for one controlled measurement condition."""

    experiment_id: str
    condition: ExperimentCondition
    provenance: MeasurementRunProvenance
    measurements: tuple[CandidateMeasurementResult, ...]
    schema_version: int = MEASUREMENT_EXPERIMENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != MEASUREMENT_EXPERIMENT_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported measurement experiment schema_version: {self.schema_version}"
            )
        if not self.experiment_id.strip():
            raise ValueError("experiment_id must not be empty")
        if not self.measurements:
            raise ValueError("measurement experiment record must contain at least one measurement")

        names = tuple(measurement.name for measurement in self.measurements)
        if len(names) != len(set(names)):
            raise ValueError("measurement names must be unique within one experiment record")


def measurement_experiment_record_to_payload(
    record: MeasurementExperimentRecord,
) -> dict[str, object]:
    """Serialize one experiment record into the canonical schema-v1 payload."""

    return {
        "kind": "measurement_experiment_record",
        "schema_version": record.schema_version,
        "experiment_id": record.experiment_id,
        "condition": {
            "condition_id": record.condition.condition_id,
            "reference_case": record.condition.reference_case,
            "take_case": record.condition.take_case,
            "intervention": {
                "family": record.condition.intervention.family,
                "role": record.condition.intervention.role.value,
                "strength": record.condition.intervention.strength,
                "unit": record.condition.intervention.unit,
                "parameters": [
                    {
                        "name": parameter.name,
                        "value": parameter.value,
                        "unit": parameter.unit,
                    }
                    for parameter in record.condition.intervention.parameters
                ],
            },
        },
        "provenance": {
            "generator": record.provenance.generator,
            "generator_version": record.provenance.generator_version,
            "code_revision": record.provenance.code_revision,
            "source_manifest": record.provenance.source_manifest,
            "analysis_config": {
                "schema_version": record.provenance.analysis_config.schema_version,
                "target_sample_rate": record.provenance.analysis_config.target_sample_rate,
                "frame_length": record.provenance.analysis_config.frame_length,
                "hop_length": record.provenance.analysis_config.hop_length,
                "segment_duration_s": record.provenance.analysis_config.segment_duration_s,
                "pitch_weight": record.provenance.analysis_config.pitch_weight,
                "rhythm_weight": record.provenance.analysis_config.rhythm_weight,
                "timing_weight": record.provenance.analysis_config.timing_weight,
                "stability_weight": record.provenance.analysis_config.stability_weight,
            },
        },
        "measurements": [
            {
                "name": measurement.name,
                "value": measurement.value,
                "unit": measurement.unit,
                "source": measurement.source,
            }
            for measurement in record.measurements
        ],
    }


def measurement_experiment_record_to_json(record: MeasurementExperimentRecord) -> str:
    """Serialize one experiment record deterministically for artifacts and snapshots."""

    return json.dumps(
        measurement_experiment_record_to_payload(record),
        indent=2,
        sort_keys=True,
    )
