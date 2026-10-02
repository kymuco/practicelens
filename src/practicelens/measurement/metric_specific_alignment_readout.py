from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from practicelens.alignment import align_feature_bundles
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
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

METRIC_SPECIFIC_READOUT_SCHEMA_VERSION = 1
METRIC_SPECIFIC_READOUT_EXPERIMENT_ID = "r0.5f-metric-specific-alignment-readout-v1"
METRIC_SPECIFIC_READOUT_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)

READOUT_MEASUREMENTS: tuple[str, ...] = (
    MetricName.PITCH_FIDELITY.value,
    MetricName.RHYTHM_FIDELITY.value,
    MetricName.TIMING_CONSISTENCY.value,
)

_TARGET_PRIMARY: dict[str, str] = {
    "pitch_drift": MetricName.PITCH_FIDELITY.value,
    "local_timing_warp": MetricName.TIMING_CONSISTENCY.value,
}


@dataclass(slots=True, frozen=True)
class MetricSpecificReadoutCondition:
    case: ControlledPerturbationCase
    production_scores: dict[str, float]
    positional_scores: dict[str, float]
    readout_scores: dict[str, float]
    production_alignment: dict[str, float | int]
    positional_alignment: dict[str, float | int]


@dataclass(slots=True, frozen=True)
class MetricSpecificReadoutResult:
    out_dir: Path
    summary_path: Path
    conditions: tuple[MetricSpecificReadoutCondition, ...]
    summary: dict[str, object]


def run_metric_specific_alignment_readout_ablation(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    config: AnalysisConfig = METRIC_SPECIFIC_READOUT_CONFIG,
) -> MetricSpecificReadoutResult:
    """Evaluate metric-specific alignment ownership without changing production behavior."""

    out_dir.mkdir(parents=True, exist_ok=True)
    harness = generate_controlled_perturbation_harness(
        out_dir / "harness",
        sample_rate=config.target_sample_rate,
    )
    pipeline = OfflineReferenceAnalysisPipeline()
    reference_audio = pipeline._prepare_audio(load_wav_audio(harness.reference_path), config)
    reference_features = extract_feature_bundle(reference_audio, config)

    observations: list[MetricSpecificReadoutCondition] = []
    for case in harness.cases:
        take_audio = pipeline._prepare_audio(load_wav_audio(case.path), config)
        take_features = extract_feature_bundle(take_audio, config)

        production_alignment = align_feature_bundles(reference_features, take_features)
        positional_alignment = align_with_profile(
            reference_features,
            take_features,
            CURRENT_POSITIONAL_PROFILE,
        )
        production_scoring = score_aligned_features(
            reference_features,
            take_features,
            production_alignment,
            config,
        )
        positional_scoring = score_aligned_features(
            reference_features,
            take_features,
            positional_alignment,
            config,
        )

        production_scores = _score_map(production_scoring.component_scores)
        positional_scores = _score_map(positional_scoring.component_scores)
        readout_scores = {
            MetricName.PITCH_FIDELITY.value: production_scores[
                MetricName.PITCH_FIDELITY.value
            ],
            MetricName.RHYTHM_FIDELITY.value: production_scores[
                MetricName.RHYTHM_FIDELITY.value
            ],
            MetricName.TIMING_CONSISTENCY.value: positional_scores[
                MetricName.TIMING_CONSISTENCY.value
            ],
        }

        observations.append(
            MetricSpecificReadoutCondition(
                case=case,
                production_scores=production_scores,
                positional_scores=positional_scores,
                readout_scores=readout_scores,
                production_alignment=alignment_diagnostics(
                    reference_features,
                    take_features,
                    production_alignment,
                ),
                positional_alignment=alignment_diagnostics(
                    reference_features,
                    take_features,
                    positional_alignment,
                ),
            )
        )

    summary = metric_specific_alignment_readout_payload(
        tuple(observations),
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return MetricSpecificReadoutResult(
        out_dir=out_dir,
        summary_path=summary_path,
        conditions=tuple(observations),
        summary=summary,
    )


def metric_specific_alignment_readout_payload(
    conditions: tuple[MetricSpecificReadoutCondition, ...],
    *,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    by_family: dict[str, list[MetricSpecificReadoutCondition]] = {}
    for condition in conditions:
        family = condition.case.condition.intervention.family
        by_family.setdefault(family, []).append(condition)

    families = {
        family: _family_payload(family, tuple(items))
        for family, items in sorted(by_family.items())
    }
    checks = _validation_checks(families)
    return {
        "kind": "metric_specific_alignment_readout_ablation",
        "schema_version": METRIC_SPECIFIC_READOUT_SCHEMA_VERSION,
        "experiment_id": METRIC_SPECIFIC_READOUT_EXPERIMENT_ID,
        "code_revision": code_revision,
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
        },
        "readout_ownership": {
            MetricName.PITCH_FIDELITY.value: "production_flexible_alignment",
            MetricName.RHYTHM_FIDELITY.value: "alignment_independent_onset_time_path",
            MetricName.TIMING_CONSISTENCY.value: CURRENT_POSITIONAL_PROFILE.name,
            MetricName.SECTION_STABILITY.value: "not_redefined_in_r0.5f",
        },
        "families": families,
        "validation_checks": checks,
        "passes_all_preregistered_checks": all(checks.values()),
        "interpretation_boundary": [
            "R0.5f is a counterfactual readout ablation; production still uses one shared alignment path.",
            "Section stability is reported as context but is not redefined from two alignment paths.",
            "A successful result supports shared-alignment coupling as the narrower defect.",
            "Timing response magnitude remains descriptive until R0.5b human repeatability evidence exists.",
        ],
    }


def render_metric_specific_alignment_readout_text(summary: dict[str, object]) -> str:
    lines = [
        "PracticeLens R0.5f Metric-Specific Alignment Readout Ablation v1",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
    ]
    for family_name, family in summary["families"].items():
        lines.append(f"{family_name}:")
        for measurement_name in READOUT_MEASUREMENTS:
            production = family["production"]["max_abs_deltas"][measurement_name]
            readout = family["metric_specific_readout"]["max_abs_deltas"][measurement_name]
            lines.append(
                f"  {measurement_name}: production={production:.6f} "
                f"readout={readout:.6f}"
            )
        if family["primary_measurement"] is not None:
            lines.append(
                "  readout primary monotonicity: "
                f"{family['metric_specific_readout']['primary_monotonicity']}"
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
    conditions: tuple[MetricSpecificReadoutCondition, ...],
) -> dict[str, object]:
    ordered = tuple(
        sorted(
            conditions,
            key=lambda item: item.case.condition.intervention.strength,
        )
    )
    production = _series_payload(
        ordered,
        source="production",
        primary_measurement=_TARGET_PRIMARY.get(family),
    )
    positional = _series_payload(
        ordered,
        source="positional",
        primary_measurement=_TARGET_PRIMARY.get(family),
    )
    readout = _series_payload(
        ordered,
        source="readout",
        primary_measurement=_TARGET_PRIMARY.get(family),
    )

    return {
        "family": family,
        "role": _family_role(ordered),
        "strengths": [
            item.case.condition.intervention.strength
            for item in ordered
        ],
        "condition_ids": [
            item.case.condition.condition_id
            for item in ordered
        ],
        "primary_measurement": _TARGET_PRIMARY.get(family),
        "production": production,
        "positional_context": positional,
        "metric_specific_readout": readout,
        "section_stability_context": {
            "production_max_abs_delta": production["max_abs_deltas"][
                MetricName.SECTION_STABILITY.value
            ],
            "positional_max_abs_delta": positional["max_abs_deltas"][
                MetricName.SECTION_STABILITY.value
            ],
            "note": (
                "R0.5f does not define hybrid section_stability because the current "
                "section score aggregates pitch and timing over one alignment path."
            ),
        },
        "alignment_context": {
            "production_min_coverage": min(
                float(item.production_alignment["coverage_ratio"])
                for item in ordered
            ),
            "positional_min_coverage": min(
                float(item.positional_alignment["coverage_ratio"])
                for item in ordered
            ),
        },
        "conditions": [
            {
                "condition_id": item.case.condition.condition_id,
                "strength": item.case.condition.intervention.strength,
                "production_scores": item.production_scores,
                "positional_scores": item.positional_scores,
                "readout_scores": item.readout_scores,
                "production_alignment": item.production_alignment,
                "positional_alignment": item.positional_alignment,
            }
            for item in ordered
        ],
    }


def _series_payload(
    conditions: tuple[MetricSpecificReadoutCondition, ...],
    *,
    source: str,
    primary_measurement: str | None,
) -> dict[str, object]:
    if source not in {"production", "positional", "readout"}:
        raise ValueError(f"unsupported score source: {source!r}")

    measurement_names = (
        AUDITED_MEASUREMENTS if source != "readout" else READOUT_MEASUREMENTS
    )
    values: dict[str, list[float]] = {}
    for measurement_name in measurement_names:
        values[measurement_name] = [
            _score_source(item, source)[measurement_name]
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
        "amplitude_gain_readouts_strictly_invariant": _all_zero(
            amplitude["metric_specific_readout"]["max_abs_deltas"]
        ),
        "additive_noise_readouts_no_worse_than_production": _no_worse(
            production=noise["production"]["max_abs_deltas"],
            readout=noise["metric_specific_readout"]["max_abs_deltas"],
            measurements=READOUT_MEASUREMENTS,
        ),
        "pitch_drift_pitch_sensitivity_preserved": (
            pitch["metric_specific_readout"]["primary_directional_sensitivity"] == "PASS"
        ),
        "pitch_drift_pitch_monotonicity_preserved": (
            pitch["metric_specific_readout"]["primary_monotonicity"] == "PASS"
        ),
        "pitch_drift_timing_cross_talk_strictly_lower": (
            pitch["metric_specific_readout"]["max_abs_deltas"][
                MetricName.TIMING_CONSISTENCY.value
            ]
            < pitch["production"]["max_abs_deltas"][
                MetricName.TIMING_CONSISTENCY.value
            ]
            - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        ),
        "pitch_drift_rhythm_cross_talk_no_worse": _no_worse(
            production=pitch["production"]["max_abs_deltas"],
            readout=pitch["metric_specific_readout"]["max_abs_deltas"],
            measurements=(MetricName.RHYTHM_FIDELITY.value,),
        ),
        "local_timing_directional_sensitivity_preserved": (
            timing["metric_specific_readout"]["primary_directional_sensitivity"] == "PASS"
        ),
        "local_timing_monotonicity_improved_to_pass": (
            timing["metric_specific_readout"]["primary_monotonicity"] == "PASS"
        ),
        "local_timing_pitch_cross_talk_no_worse": _no_worse(
            production=timing["production"]["max_abs_deltas"],
            readout=timing["metric_specific_readout"]["max_abs_deltas"],
            measurements=(MetricName.PITCH_FIDELITY.value,),
        ),
        "both_alignment_coverages_preserved": all(
            family["alignment_context"]["production_min_coverage"]
            >= 1.0 - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
            and family["alignment_context"]["positional_min_coverage"]
            >= family["alignment_context"]["production_min_coverage"]
            - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
            for family in families.values()
        ),
    }


def _score_source(
    condition: MetricSpecificReadoutCondition,
    source: str,
) -> dict[str, float]:
    if source == "production":
        return condition.production_scores
    if source == "positional":
        return condition.positional_scores
    if source == "readout":
        return condition.readout_scores
    raise ValueError(f"unsupported score source: {source!r}")


def _score_map(component_scores: tuple[object, ...]) -> dict[str, float]:
    return {
        score.name.value: float(score.score)
        for score in component_scores
    }


def _family_role(
    conditions: tuple[MetricSpecificReadoutCondition, ...],
) -> str:
    roles = {
        item.case.condition.intervention.role.value
        for item in conditions
        if item.case.condition.intervention.role.value != "control"
    }
    if len(roles) != 1:
        raise ValueError("family must contain one non-control role")
    return next(iter(roles))


def _all_zero(values: dict[str, float]) -> bool:
    return all(
        value <= ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        for value in values.values()
    )


def _no_worse(
    *,
    production: dict[str, float],
    readout: dict[str, float],
    measurements: tuple[str, ...],
) -> bool:
    return all(
        readout[name] <= production[name] + ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        for name in measurements
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
