from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisConfig
from practicelens.features import extract_feature_bundle
from practicelens.io import load_wav_audio
from practicelens.measurement.alignment_substrate_ablation import (
    ALIGNMENT_SUBSTRATE_ABLATION_EPSILON,
    CURRENT_POSITIONAL_PROFILE,
    align_with_profile,
)
from practicelens.measurement.baseline_audit import AUDITED_MEASUREMENTS
from practicelens.measurement.controlled_perturbations import (
    ControlledPerturbationCase,
    generate_controlled_perturbation_harness,
)
from practicelens.measurement.cross_talk_attribution import alignment_diagnostics
from practicelens.scoring import score_aligned_features

ALIGNMENT_CANDIDATE_VALIDATION_SCHEMA_VERSION = 1
ALIGNMENT_CANDIDATE_VALIDATION_EXPERIMENT_ID = "r0.5e-alignment-candidate-validation-v1"
ALIGNMENT_CANDIDATE_VALIDATION_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)

_TARGET_PRIMARY: dict[str, str] = {
    "pitch_drift": MetricName.PITCH_FIDELITY.value,
    "local_timing_warp": MetricName.TIMING_CONSISTENCY.value,
}

_TARGET_PROTECTED: dict[str, tuple[str, ...]] = {
    "pitch_drift": (
        MetricName.RHYTHM_FIDELITY.value,
        MetricName.TIMING_CONSISTENCY.value,
    ),
    "local_timing_warp": (MetricName.PITCH_FIDELITY.value,),
}


@dataclass(slots=True, frozen=True)
class CandidateValidationCondition:
    case: ControlledPerturbationCase
    production_scores: dict[str, float]
    candidate_scores: dict[str, float]
    production_alignment_coverage: float
    candidate_alignment: dict[str, float | int]


@dataclass(slots=True, frozen=True)
class AlignmentCandidateValidationResult:
    out_dir: Path
    summary_path: Path
    conditions: tuple[CandidateValidationCondition, ...]
    summary: dict[str, object]


def run_alignment_candidate_validation(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    config: AnalysisConfig = ALIGNMENT_CANDIDATE_VALIDATION_CONFIG,
) -> AlignmentCandidateValidationResult:
    """Validate the frozen positional candidate across all existing R0.3 families."""

    out_dir.mkdir(parents=True, exist_ok=True)
    harness = generate_controlled_perturbation_harness(
        out_dir / "harness",
        sample_rate=config.target_sample_rate,
    )
    pipeline = OfflineReferenceAnalysisPipeline()
    reference_audio = pipeline._prepare_audio(load_wav_audio(harness.reference_path), config)
    reference_features = extract_feature_bundle(reference_audio, config)

    conditions: list[CandidateValidationCondition] = []
    for case in harness.cases:
        production_report = pipeline.analyze(
            AnalyzeRequest(
                reference_path=harness.reference_path,
                take_path=case.path,
                config=config,
            )
        ).report
        production_score_map = production_report.score_map()

        take_audio = pipeline._prepare_audio(load_wav_audio(case.path), config)
        take_features = extract_feature_bundle(take_audio, config)
        candidate_alignment = align_with_profile(
            reference_features,
            take_features,
            CURRENT_POSITIONAL_PROFILE,
        )
        candidate_scoring = score_aligned_features(
            reference_features,
            take_features,
            candidate_alignment,
            config,
        )

        conditions.append(
            CandidateValidationCondition(
                case=case,
                production_scores={
                    measurement_name: float(production_score_map[measurement_name].score)
                    for measurement_name in AUDITED_MEASUREMENTS
                },
                candidate_scores={
                    score.name.value: float(score.score)
                    for score in candidate_scoring.component_scores
                },
                production_alignment_coverage=float(
                    production_report.input_suitability.alignment_coverage
                ),
                candidate_alignment=alignment_diagnostics(
                    reference_features,
                    take_features,
                    candidate_alignment,
                ),
            )
        )

    summary = alignment_candidate_validation_payload(
        tuple(conditions),
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return AlignmentCandidateValidationResult(
        out_dir=out_dir,
        summary_path=summary_path,
        conditions=tuple(conditions),
        summary=summary,
    )


def alignment_candidate_validation_payload(
    conditions: tuple[CandidateValidationCondition, ...],
    *,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    by_family: dict[str, list[CandidateValidationCondition]] = {}
    for condition in conditions:
        family = condition.case.condition.intervention.family
        by_family.setdefault(family, []).append(condition)

    families = {
        family: _family_payload(family, tuple(items))
        for family, items in sorted(by_family.items())
    }
    checks = _validation_checks(families)
    return {
        "kind": "alignment_candidate_validation",
        "schema_version": ALIGNMENT_CANDIDATE_VALIDATION_SCHEMA_VERSION,
        "experiment_id": ALIGNMENT_CANDIDATE_VALIDATION_EXPERIMENT_ID,
        "code_revision": code_revision,
        "candidate_profile": {
            "name": CURRENT_POSITIONAL_PROFILE.name,
            "pitch_weight": CURRENT_POSITIONAL_PROFILE.pitch_weight,
            "energy_weight": CURRENT_POSITIONAL_PROFILE.energy_weight,
            "zcr_weight": CURRENT_POSITIONAL_PROFILE.zcr_weight,
            "voiced_mismatch_penalty": CURRENT_POSITIONAL_PROFILE.voiced_mismatch_penalty,
            "position_penalty_weight": CURRENT_POSITIONAL_PROFILE.position_penalty_weight,
        },
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
        },
        "families": families,
        "validation_checks": checks,
        "passes_all_preregistered_checks": all(checks.values()),
        "interpretation_boundary": [
            "The candidate profile is frozen from R0.5d; R0.5e performs no weight search.",
            "Passing the synthetic checks does not admit a production DTW change.",
            "Response magnitude is reported but not thresholded because R0.5b human repeatability evidence is still pending.",
            "A protected-dimension regression is recorded as a failed synthetic check even if the primary target improves.",
        ],
    }


def render_alignment_candidate_validation_text(summary: dict[str, object]) -> str:
    lines = [
        "PracticeLens R0.5e Alignment Candidate Validation v1",
        f"candidate: {summary['candidate_profile']['name']}",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
    ]
    for family_name, family in summary["families"].items():
        lines.append(f"{family_name}:")
        for measurement_name in AUDITED_MEASUREMENTS:
            production = family["production"]["max_abs_deltas"][measurement_name]
            candidate = family["candidate"]["max_abs_deltas"][measurement_name]
            lines.append(
                f"  {measurement_name}: production={production:.6f} "
                f"candidate={candidate:.6f}"
            )
        if family["role"] == "target":
            lines.append(
                f"  candidate primary monotonicity: "
                f"{family['candidate']['primary_monotonicity']}"
            )
    lines.extend(
        (
            "",
            "checks:",
            *[
                f"  {name}: {'PASS' if passed else 'FAIL'}"
                for name, passed in summary["validation_checks"].items()
            ],
        )
    )
    return "\n".join(lines)


def _family_payload(
    family: str,
    conditions: tuple[CandidateValidationCondition, ...],
) -> dict[str, object]:
    ordered = tuple(
        sorted(
            conditions,
            key=lambda item: item.case.condition.intervention.strength,
        )
    )
    roles = {
        item.case.condition.intervention.role.value
        for item in ordered
        if item.case.condition.intervention.role.value != "control"
    }
    if len(roles) != 1:
        raise ValueError(f"family {family!r} must have one non-control role")
    role = next(iter(roles))

    production = _series_payload(
        ordered,
        source="production",
        primary_measurement=_TARGET_PRIMARY.get(family),
    )
    candidate = _series_payload(
        ordered,
        source="candidate",
        primary_measurement=_TARGET_PRIMARY.get(family),
    )
    return {
        "family": family,
        "role": role,
        "strengths": [
            item.case.condition.intervention.strength
            for item in ordered
        ],
        "condition_ids": [
            item.case.condition.condition_id
            for item in ordered
        ],
        "primary_measurement": _TARGET_PRIMARY.get(family),
        "protected_measurements": list(_TARGET_PROTECTED.get(family, AUDITED_MEASUREMENTS)),
        "production": production,
        "candidate": candidate,
        "comparison": {
            "max_abs_delta_ratios_candidate_over_production": {
                measurement_name: _safe_ratio(
                    candidate["max_abs_deltas"][measurement_name],
                    production["max_abs_deltas"][measurement_name],
                )
                for measurement_name in AUDITED_MEASUREMENTS
            },
            "endpoint_delta_ratios_candidate_over_production": {
                measurement_name: _safe_ratio(
                    abs(candidate["endpoint_deltas"][measurement_name]),
                    abs(production["endpoint_deltas"][measurement_name]),
                )
                for measurement_name in AUDITED_MEASUREMENTS
            },
            "candidate_min_coverage": min(
                float(item.candidate_alignment["coverage_ratio"])
                for item in ordered
            ),
            "production_min_coverage": min(
                item.production_alignment_coverage
                for item in ordered
            ),
        },
        "conditions": [
            {
                "condition_id": item.case.condition.condition_id,
                "strength": item.case.condition.intervention.strength,
                "production_scores": item.production_scores,
                "candidate_scores": item.candidate_scores,
                "production_alignment_coverage": item.production_alignment_coverage,
                "candidate_alignment": item.candidate_alignment,
            }
            for item in ordered
        ],
    }


def _series_payload(
    conditions: tuple[CandidateValidationCondition, ...],
    *,
    source: str,
    primary_measurement: str | None,
) -> dict[str, object]:
    if source not in {"production", "candidate"}:
        raise ValueError(f"unsupported series source: {source!r}")

    values: dict[str, list[float]] = {}
    for measurement_name in AUDITED_MEASUREMENTS:
        values[measurement_name] = [
            (
                item.production_scores[measurement_name]
                if source == "production"
                else item.candidate_scores[measurement_name]
            )
            for item in conditions
        ]

    deltas = {
        measurement_name: [
            value - measurement_values[0]
            for value in measurement_values
        ]
        for measurement_name, measurement_values in values.items()
    }
    payload: dict[str, object] = {
        "values": values,
        "deltas_from_control": deltas,
        "max_abs_deltas": {
            measurement_name: max(abs(delta) for delta in measurement_deltas)
            for measurement_name, measurement_deltas in deltas.items()
        },
        "endpoint_deltas": {
            measurement_name: measurement_deltas[-1]
            for measurement_name, measurement_deltas in deltas.items()
        },
    }
    if primary_measurement is not None:
        primary_values = values[primary_measurement]
        payload["primary_directional_sensitivity"] = _directional_verdict(primary_values)
        payload["primary_monotonicity"] = _monotonicity_verdict(primary_values)
    return payload


def _validation_checks(families: dict[str, dict[str, object]]) -> dict[str, bool]:
    amplitude = families["amplitude_gain"]
    noise = families["deterministic_additive_noise"]
    pitch = families["pitch_drift"]
    timing = families["local_timing_warp"]

    return {
        "amplitude_gain_strict_invariance": _all_zero(
            amplitude["candidate"]["max_abs_deltas"]
        ),
        "additive_noise_no_measurement_regression": _no_measurement_regression(
            production=noise["production"]["max_abs_deltas"],
            candidate=noise["candidate"]["max_abs_deltas"],
        ),
        "pitch_drift_directional_sensitivity_preserved": (
            pitch["candidate"]["primary_directional_sensitivity"] == "PASS"
        ),
        "pitch_drift_monotonicity_preserved": (
            pitch["candidate"]["primary_monotonicity"] == "PASS"
        ),
        "pitch_drift_protected_cross_talk_no_worse": _protected_no_worse(
            pitch,
            _TARGET_PROTECTED["pitch_drift"],
        ),
        "local_timing_directional_sensitivity_preserved": (
            timing["candidate"]["primary_directional_sensitivity"] == "PASS"
        ),
        "local_timing_monotonicity_improved_to_pass": (
            timing["candidate"]["primary_monotonicity"] == "PASS"
        ),
        "local_timing_protected_cross_talk_no_worse": _protected_no_worse(
            timing,
            _TARGET_PROTECTED["local_timing_warp"],
        ),
        "minimum_alignment_coverage_preserved": all(
            family["comparison"]["candidate_min_coverage"]
            >= family["comparison"]["production_min_coverage"]
            - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
            for family in families.values()
        ),
    }


def _all_zero(max_abs_deltas: dict[str, float]) -> bool:
    return all(
        value <= ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        for value in max_abs_deltas.values()
    )


def _no_measurement_regression(
    *,
    production: dict[str, float],
    candidate: dict[str, float],
) -> bool:
    return all(
        candidate[name] <= production[name] + ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        for name in AUDITED_MEASUREMENTS
    )


def _protected_no_worse(
    family: dict[str, object],
    protected_measurements: tuple[str, ...],
) -> bool:
    production = family["production"]["max_abs_deltas"]
    candidate = family["candidate"]["max_abs_deltas"]
    return all(
        candidate[name] <= production[name] + ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        for name in protected_measurements
    )


def _directional_verdict(values: list[float]) -> str:
    endpoint_delta = values[-1] - values[0]
    if endpoint_delta < -ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
        return "PASS"
    if endpoint_delta > ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
        return "FAIL"
    return "UNRESOLVED"


def _monotonicity_verdict(values: list[float]) -> str:
    has_decrease = False
    has_increase = False
    for left, right in zip(values, values[1:], strict=False):
        delta = right - left
        if delta < -ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
            has_decrease = True
        elif delta > ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
            has_increase = True

    if not has_decrease and not has_increase:
        return "UNRESOLVED"
    if not has_increase:
        return "PASS"
    if values[-1] < values[0] - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
        return "PARTIAL"
    return "FAIL"


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if abs(denominator) <= ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
        if abs(numerator) <= ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
            return 1.0
        return None
    return numerator / denominator
