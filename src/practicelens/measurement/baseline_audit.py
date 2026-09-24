from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName, StrEnum
from practicelens.domain.models import AnalysisConfig
from practicelens.measurement.contracts import (
    AnalysisConfigSnapshot,
    CandidateMeasurementResult,
    MeasurementExperimentRecord,
    MeasurementRunProvenance,
    measurement_experiment_record_to_json,
)
from practicelens.measurement.controlled_perturbations import (
    CONTROLLED_PERTURBATION_GENERATOR_VERSION,
    ControlledPerturbationCase,
    ControlledPerturbationHarnessResult,
    generate_controlled_perturbation_harness,
)

BASELINE_VALIDITY_AUDIT_SCHEMA_VERSION = 1
BASELINE_VALIDITY_AUDIT_EXPERIMENT_ID = "r0.4-baseline-measurement-validity-v1"
STRICT_DELTA_EPSILON = 1e-9

BASELINE_VALIDITY_AUDIT_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)

AUDITED_MEASUREMENTS: tuple[str, ...] = (
    MetricName.PITCH_FIDELITY.value,
    MetricName.RHYTHM_FIDELITY.value,
    MetricName.TIMING_CONSISTENCY.value,
    MetricName.SECTION_STABILITY.value,
)

_TARGET_RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "pitch_drift": (
        MetricName.PITCH_FIDELITY.value,
        (
            MetricName.RHYTHM_FIDELITY.value,
            MetricName.TIMING_CONSISTENCY.value,
        ),
    ),
    "local_timing_warp": (
        MetricName.TIMING_CONSISTENCY.value,
        (MetricName.PITCH_FIDELITY.value,),
    ),
}


class AuditVerdict(StrEnum):
    """Screening verdict for one controlled measurement property."""

    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"


@dataclass(slots=True, frozen=True)
class ConditionAuditObservation:
    """One frozen baseline output plus supporting diagnostics."""

    case: ControlledPerturbationCase
    record: MeasurementExperimentRecord
    confidence_level: str
    suitability_status: str
    alignment_coverage: float


@dataclass(slots=True, frozen=True)
class BaselineValidityAuditResult:
    """Generated artifacts for the R0.4 controlled baseline audit."""

    out_dir: Path
    harness: ControlledPerturbationHarnessResult
    records_dir: Path
    summary_path: Path
    observations: tuple[ConditionAuditObservation, ...]
    summary: dict[str, object]


def run_baseline_measurement_validity_audit(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    config: AnalysisConfig = BASELINE_VALIDITY_AUDIT_CONFIG,
) -> BaselineValidityAuditResult:
    """Run the unchanged PracticeLens baseline across every R0.3 condition."""

    out_dir.mkdir(parents=True, exist_ok=True)
    harness_dir = out_dir / "harness"
    records_dir = out_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    harness = generate_controlled_perturbation_harness(
        harness_dir,
        sample_rate=config.target_sample_rate,
    )
    pipeline = OfflineReferenceAnalysisPipeline()
    observations: list[ConditionAuditObservation] = []

    for case in harness.cases:
        report = pipeline.analyze(
            AnalyzeRequest(
                reference_path=harness.reference_path,
                take_path=case.path,
                config=config,
            )
        ).report
        score_map = report.score_map()
        measurements = tuple(
            CandidateMeasurementResult(
                name=measurement_name,
                value=float(score_map[measurement_name].score),
                unit="score_0_100",
                source="component_score",
            )
            for measurement_name in AUDITED_MEASUREMENTS
        )
        record = MeasurementExperimentRecord(
            experiment_id=BASELINE_VALIDITY_AUDIT_EXPERIMENT_ID,
            condition=case.condition,
            provenance=MeasurementRunProvenance(
                generator="practicelens.measurement.controlled_perturbations",
                generator_version=CONTROLLED_PERTURBATION_GENERATOR_VERSION,
                code_revision=code_revision,
                source_manifest="harness/manifest.json",
                analysis_config=AnalysisConfigSnapshot.from_config(config),
            ),
            measurements=measurements,
        )
        record_path = records_dir / f"{case.condition.condition_id}.json"
        record_path.write_text(
            measurement_experiment_record_to_json(record) + "\n",
            encoding="utf-8",
        )
        observations.append(
            ConditionAuditObservation(
                case=case,
                record=record,
                confidence_level=report.analysis_confidence.level,
                suitability_status=report.input_suitability.status,
                alignment_coverage=float(report.input_suitability.alignment_coverage),
            )
        )

    summary = baseline_validity_audit_payload(
        tuple(observations),
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return BaselineValidityAuditResult(
        out_dir=out_dir,
        harness=harness,
        records_dir=records_dir,
        summary_path=summary_path,
        observations=tuple(observations),
        summary=summary,
    )


def baseline_validity_audit_payload(
    observations: tuple[ConditionAuditObservation, ...],
    *,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    """Build the stable R0.4 screening summary from frozen condition outputs."""

    by_family: dict[str, list[ConditionAuditObservation]] = {}
    for observation in observations:
        family = observation.case.condition.intervention.family
        by_family.setdefault(family, []).append(observation)

    series = [
        _audit_family(family, tuple(family_observations))
        for family, family_observations in sorted(by_family.items())
    ]

    verdict_counts = {verdict.value: 0 for verdict in AuditVerdict}
    for item in series:
        verdict_counts[str(item["family_verdict"])] += 1

    return {
        "kind": "baseline_measurement_validity_audit",
        "schema_version": BASELINE_VALIDITY_AUDIT_SCHEMA_VERSION,
        "experiment_id": BASELINE_VALIDITY_AUDIT_EXPERIMENT_ID,
        "code_revision": code_revision,
        "strict_delta_epsilon": STRICT_DELTA_EPSILON,
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
            "pitch_weight": config.pitch_weight,
            "rhythm_weight": config.rhythm_weight,
            "timing_weight": config.timing_weight,
            "stability_weight": config.stability_weight,
        },
        "audited_measurements": list(AUDITED_MEASUREMENTS),
        "screening_semantics": {
            "PASS": "The tested strict property held for this deterministic controlled series.",
            "PARTIAL": "The target moved in the expected endpoint direction but another tested property did not hold.",
            "FAIL": "The tested strict property did not hold.",
            "UNRESOLVED": "The series did not produce enough directional response to resolve the tested property.",
        },
        "series": series,
        "family_verdict_counts": verdict_counts,
        "limitations": [
            "These are strict deterministic synthetic screening verdicts, not final construct-validity claims.",
            "R0.5 is still required to establish practical repeatability and a measurement noise floor.",
            "Real-musician ecological validation is not established by this audit.",
        ],
    }


def render_baseline_validity_audit_text(summary: dict[str, object]) -> str:
    """Render a compact human-readable R0.4 audit summary."""

    lines = [
        "PracticeLens R0.4 Baseline Measurement Validity Audit v1",
        f"experiment: {summary['experiment_id']}",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
    ]
    for series in summary["series"]:
        lines.append(
            f"{series['family']}: {series['family_verdict']} "
            f"({series['role']})"
        )
        for property_name, verdict in series["property_verdicts"].items():
            lines.append(f"  {property_name}: {verdict}")
        primary = series.get("primary_measurement")
        if primary is not None:
            delta = series["endpoint_deltas"][primary]
            lines.append(f"  primary endpoint delta {primary}: {delta:+.6f}")
        max_deltas = series["max_abs_deltas"]
        lines.append(
            "  max abs deltas: "
            + ", ".join(f"{name}={max_deltas[name]:.6f}" for name in AUDITED_MEASUREMENTS)
        )
    return "\n".join(lines)


def _audit_family(
    family: str,
    observations: tuple[ConditionAuditObservation, ...],
) -> dict[str, object]:
    ordered = tuple(
        sorted(
            observations,
            key=lambda observation: observation.case.condition.intervention.strength,
        )
    )
    controls = [
        observation
        for observation in ordered
        if observation.case.condition.intervention.role.value == "control"
    ]
    if len(controls) != 1:
        raise ValueError(f"family {family!r} must contain exactly one control")

    non_controls = [
        observation
        for observation in ordered
        if observation.case.condition.intervention.role.value != "control"
    ]
    if not non_controls:
        raise ValueError(f"family {family!r} must contain at least one non-control")

    family_roles = {
        observation.case.condition.intervention.role.value
        for observation in non_controls
    }
    if len(family_roles) != 1:
        raise ValueError(f"family {family!r} mixes non-control intervention roles")
    role = next(iter(family_roles))

    values = {
        measurement_name: [
            _measurement_value(observation.record, measurement_name)
            for observation in ordered
        ]
        for measurement_name in AUDITED_MEASUREMENTS
    }
    deltas = {
        measurement_name: [
            value - measurement_values[0]
            for value in measurement_values
        ]
        for measurement_name, measurement_values in values.items()
    }
    max_abs_deltas = {
        measurement_name: max(abs(delta) for delta in measurement_deltas)
        for measurement_name, measurement_deltas in deltas.items()
    }
    endpoint_deltas = {
        measurement_name: measurement_deltas[-1]
        for measurement_name, measurement_deltas in deltas.items()
    }

    common = {
        "family": family,
        "role": role,
        "strengths": [
            observation.case.condition.intervention.strength
            for observation in ordered
        ],
        "strength_unit": ordered[0].case.condition.intervention.unit,
        "condition_ids": [
            observation.case.condition.condition_id
            for observation in ordered
        ],
        "values": values,
        "deltas_from_control": deltas,
        "max_abs_deltas": max_abs_deltas,
        "endpoint_deltas": endpoint_deltas,
        "confidence_levels": [
            observation.confidence_level
            for observation in ordered
        ],
        "suitability_statuses": [
            observation.suitability_status
            for observation in ordered
        ],
        "alignment_coverage": [
            observation.alignment_coverage
            for observation in ordered
        ],
    }

    if role == "nuisance":
        per_measurement = {
            measurement_name: _strict_invariance_verdict(max_abs_delta).value
            for measurement_name, max_abs_delta in max_abs_deltas.items()
        }
        family_verdict = (
            AuditVerdict.PASS
            if all(verdict == AuditVerdict.PASS.value for verdict in per_measurement.values())
            else AuditVerdict.FAIL
        )
        return {
            **common,
            "primary_measurement": None,
            "protected_measurements": list(AUDITED_MEASUREMENTS),
            "property_verdicts": {
                "strict_nuisance_invariance": family_verdict.value,
                **{
                    f"strict_invariance:{measurement_name}": verdict
                    for measurement_name, verdict in per_measurement.items()
                },
            },
            "family_verdict": family_verdict.value,
        }

    if role != "target":
        raise ValueError(f"unsupported non-control intervention role: {role!r}")
    if family not in _TARGET_RULES:
        raise ValueError(f"missing target audit rule for family {family!r}")

    primary_measurement, protected_measurements = _TARGET_RULES[family]
    sensitivity = _directional_sensitivity_verdict(
        values[primary_measurement]
    )
    monotonicity = _nonincreasing_monotonicity_verdict(
        values[primary_measurement]
    )
    protected_specificity = _protected_specificity_verdict(
        max_abs_deltas,
        protected_measurements,
    )
    family_verdict = _target_family_verdict(
        sensitivity=sensitivity,
        monotonicity=monotonicity,
        protected_specificity=protected_specificity,
    )

    return {
        **common,
        "primary_measurement": primary_measurement,
        "protected_measurements": list(protected_measurements),
        "property_verdicts": {
            "directional_sensitivity": sensitivity.value,
            "nonincreasing_monotonicity": monotonicity.value,
            "strict_protected_specificity": protected_specificity.value,
        },
        "family_verdict": family_verdict.value,
    }


def _measurement_value(
    record: MeasurementExperimentRecord,
    measurement_name: str,
) -> float:
    for measurement in record.measurements:
        if measurement.name == measurement_name:
            return measurement.value
    raise ValueError(f"missing measurement {measurement_name!r}")


def _strict_invariance_verdict(max_abs_delta: float) -> AuditVerdict:
    if max_abs_delta <= STRICT_DELTA_EPSILON:
        return AuditVerdict.PASS
    return AuditVerdict.FAIL


def _directional_sensitivity_verdict(values: list[float]) -> AuditVerdict:
    endpoint_delta = values[-1] - values[0]
    if endpoint_delta < -STRICT_DELTA_EPSILON:
        return AuditVerdict.PASS
    if endpoint_delta > STRICT_DELTA_EPSILON:
        return AuditVerdict.FAIL
    return AuditVerdict.UNRESOLVED


def _nonincreasing_monotonicity_verdict(values: list[float]) -> AuditVerdict:
    has_decrease = False
    has_increase = False
    for left, right in zip(values, values[1:], strict=True):
        delta = right - left
        if delta < -STRICT_DELTA_EPSILON:
            has_decrease = True
        elif delta > STRICT_DELTA_EPSILON:
            has_increase = True

    if not has_decrease and not has_increase:
        return AuditVerdict.UNRESOLVED
    if not has_increase:
        return AuditVerdict.PASS
    if values[-1] < values[0] - STRICT_DELTA_EPSILON:
        return AuditVerdict.PARTIAL
    return AuditVerdict.FAIL


def _protected_specificity_verdict(
    max_abs_deltas: dict[str, float],
    protected_measurements: tuple[str, ...],
) -> AuditVerdict:
    if all(
        max_abs_deltas[measurement_name] <= STRICT_DELTA_EPSILON
        for measurement_name in protected_measurements
    ):
        return AuditVerdict.PASS
    return AuditVerdict.FAIL


def _target_family_verdict(
    *,
    sensitivity: AuditVerdict,
    monotonicity: AuditVerdict,
    protected_specificity: AuditVerdict,
) -> AuditVerdict:
    if sensitivity is AuditVerdict.FAIL:
        return AuditVerdict.FAIL
    if sensitivity is AuditVerdict.UNRESOLVED:
        return AuditVerdict.UNRESOLVED
    if (
        monotonicity is AuditVerdict.PASS
        and protected_specificity is AuditVerdict.PASS
    ):
        return AuditVerdict.PASS
    return AuditVerdict.PARTIAL
