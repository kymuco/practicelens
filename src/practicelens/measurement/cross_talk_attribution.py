from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

from practicelens.alignment import AlignmentPair, AlignmentPath, align_feature_bundles
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisConfig
from practicelens.features import FeatureBundle, extract_feature_bundle
from practicelens.io import load_wav_audio
from practicelens.measurement.controlled_perturbations import (
    ControlledPerturbationCase,
    generate_controlled_perturbation_harness,
)
from practicelens.scoring import score_aligned_features

CROSS_TALK_ATTRIBUTION_SCHEMA_VERSION = 1
CROSS_TALK_ATTRIBUTION_EXPERIMENT_ID = "r0.5c-cross-talk-attribution-v1"
CROSS_TALK_ATTRIBUTION_EPSILON = 1e-9
CROSS_TALK_ATTRIBUTION_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
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

_SCORE_DEPENDENCIES: dict[str, dict[str, object]] = {
    MetricName.PITCH_FIDELITY.value: {
        "feature_inputs": ["pitch_contour_hz", "voiced_mask"],
        "uses_alignment": True,
        "cross_metric_score_inputs": [],
    },
    MetricName.RHYTHM_FIDELITY.value: {
        "feature_inputs": ["onset_times_s", "time_axis_s"],
        "uses_alignment": False,
        "cross_metric_score_inputs": [],
    },
    MetricName.TIMING_CONSISTENCY.value: {
        "feature_inputs": ["frame_count"],
        "uses_alignment": True,
        "cross_metric_score_inputs": [],
    },
}


@dataclass(slots=True, frozen=True)
class CrossTalkConditionObservation:
    case: ControlledPerturbationCase
    feature_diagnostics: dict[str, float | int | None]
    alignment_diagnostics: dict[str, float | int]
    observed_scores: dict[str, float]
    linear_alignment_scores: dict[str, float]


@dataclass(slots=True, frozen=True)
class CrossTalkAttributionResult:
    out_dir: Path
    summary_path: Path
    observations: tuple[CrossTalkConditionObservation, ...]
    summary: dict[str, object]


def run_cross_talk_attribution_audit(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    config: AnalysisConfig = CROSS_TALK_ATTRIBUTION_CONFIG,
) -> CrossTalkAttributionResult:
    """Localize protected-dimension movement across feature, alignment, and scoring boundaries."""

    out_dir.mkdir(parents=True, exist_ok=True)
    harness = generate_controlled_perturbation_harness(
        out_dir / "harness",
        sample_rate=config.target_sample_rate,
    )
    pipeline = OfflineReferenceAnalysisPipeline()
    reference_audio = pipeline._prepare_audio(load_wav_audio(harness.reference_path), config)
    reference_features = extract_feature_bundle(reference_audio, config)

    observations: list[CrossTalkConditionObservation] = []
    for case in harness.cases:
        family = case.condition.intervention.family
        if family not in _TARGET_RULES:
            continue

        take_audio = pipeline._prepare_audio(load_wav_audio(case.path), config)
        take_features = extract_feature_bundle(take_audio, config)
        observed_alignment = align_feature_bundles(reference_features, take_features)
        linear_alignment = build_linear_alignment(reference_features, take_features)

        observed_scoring = score_aligned_features(
            reference_features,
            take_features,
            observed_alignment,
            config,
        )
        linear_scoring = score_aligned_features(
            reference_features,
            take_features,
            linear_alignment,
            config,
        )
        observations.append(
            CrossTalkConditionObservation(
                case=case,
                feature_diagnostics=feature_diagnostics(
                    reference_features,
                    take_features,
                    linear_alignment,
                ),
                alignment_diagnostics=alignment_diagnostics(
                    reference_features,
                    take_features,
                    observed_alignment,
                ),
                observed_scores=_score_map(observed_scoring.component_scores),
                linear_alignment_scores=_score_map(linear_scoring.component_scores),
            )
        )

    summary = cross_talk_attribution_payload(
        tuple(observations),
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return CrossTalkAttributionResult(
        out_dir=out_dir,
        summary_path=summary_path,
        observations=tuple(observations),
        summary=summary,
    )


def cross_talk_attribution_payload(
    observations: tuple[CrossTalkConditionObservation, ...],
    *,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    by_family: dict[str, list[CrossTalkConditionObservation]] = {}
    for observation in observations:
        family = observation.case.condition.intervention.family
        by_family.setdefault(family, []).append(observation)

    family_payloads = [
        _family_attribution_payload(family, tuple(items))
        for family, items in sorted(by_family.items())
    ]
    return {
        "kind": "cross_talk_attribution_audit",
        "schema_version": CROSS_TALK_ATTRIBUTION_SCHEMA_VERSION,
        "experiment_id": CROSS_TALK_ATTRIBUTION_EXPERIMENT_ID,
        "code_revision": code_revision,
        "epsilon": CROSS_TALK_ATTRIBUTION_EPSILON,
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
        },
        "score_dependencies": _SCORE_DEPENDENCIES,
        "families": family_payloads,
        "interpretation_boundary": [
            "Linear-alignment scoring is a counterfactual diagnostic, not an alternative production scorer.",
            "Pre-alignment attribution means movement is already present before the observed DTW path is applied.",
            "Alignment attribution means the observed DTW geometry adds protected-score movement beyond the linear counterfactual.",
            "The audit localizes current deterministic cross-talk; it does not establish practical human significance.",
        ],
    }


def build_linear_alignment(reference: FeatureBundle, take: FeatureBundle) -> AlignmentPath:
    """Build a monotonic relative-position alignment independent of feature similarity."""

    if reference.frame_count <= 0 or take.frame_count <= 0:
        raise ValueError("feature bundles must contain frames")

    ref_denominator = max(1, reference.frame_count - 1)
    take_denominator = max(1, take.frame_count - 1)
    pairs = tuple(
        AlignmentPair(
            reference_index=reference_index,
            take_index=int(round((reference_index / ref_denominator) * take_denominator)),
            local_cost=0.0,
        )
        for reference_index in range(reference.frame_count)
    )
    return AlignmentPath(
        pairs=pairs,
        total_cost=0.0,
        coverage_ratio=min(
            1.0,
            len({pair.take_index for pair in pairs}) / float(take.frame_count),
        ),
    )


def feature_diagnostics(
    reference: FeatureBundle,
    take: FeatureBundle,
    linear_alignment: AlignmentPath,
) -> dict[str, float | int | None]:
    """Describe pre-DTW feature movement relevant to protected scores."""

    pitch_errors: list[float] = []
    voiced_mismatches = 0
    energy_deltas: list[float] = []
    zcr_deltas: list[float] = []

    for pair in linear_alignment.pairs:
        ref_index = pair.reference_index
        take_index = pair.take_index
        ref_pitch = reference.pitch_contour_hz[ref_index]
        take_pitch = take.pitch_contour_hz[take_index]
        ref_voiced = reference.voiced_mask[ref_index]
        take_voiced = take.voiced_mask[take_index]

        if ref_voiced and take_voiced and ref_pitch > 0.0 and take_pitch > 0.0:
            pitch_errors.append(abs(1200.0 * math.log2(ref_pitch / take_pitch)))
        elif ref_voiced != take_voiced:
            voiced_mismatches += 1

        energy_deltas.append(
            abs(reference.energy_curve[ref_index] - take.energy_curve[take_index])
        )
        zcr_deltas.append(
            abs(reference.zero_crossing_rate[ref_index] - take.zero_crossing_rate[take_index])
        )

    onset_distance = _normalized_onset_mean_nearest_distance(reference, take)
    return {
        "reference_frame_count": reference.frame_count,
        "take_frame_count": take.frame_count,
        "frame_count_delta": take.frame_count - reference.frame_count,
        "reference_voiced_ratio": _voiced_ratio(reference),
        "take_voiced_ratio": _voiced_ratio(take),
        "voiced_ratio_delta": _voiced_ratio(take) - _voiced_ratio(reference),
        "reference_onset_count": len(reference.onset_times_s),
        "take_onset_count": len(take.onset_times_s),
        "onset_count_delta": len(take.onset_times_s) - len(reference.onset_times_s),
        "reference_tempo_bpm": reference.estimated_tempo_bpm,
        "take_tempo_bpm": take.estimated_tempo_bpm,
        "tempo_delta_bpm": _optional_delta(
            reference.estimated_tempo_bpm,
            take.estimated_tempo_bpm,
        ),
        "linear_pitch_mean_cents_error": (
            float(statistics.fmean(pitch_errors)) if pitch_errors else 0.0
        ),
        "linear_pitch_voiced_mismatch_fraction": (
            voiced_mismatches / float(max(1, len(linear_alignment.pairs)))
        ),
        "linear_energy_mean_abs_delta": float(statistics.fmean(energy_deltas)),
        "linear_zcr_mean_abs_delta": float(statistics.fmean(zcr_deltas)),
        "normalized_onset_mean_nearest_distance": onset_distance,
    }


def alignment_diagnostics(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
) -> dict[str, float | int]:
    """Describe observed DTW path geometry without scoring it."""

    ref_denominator = max(1, reference.frame_count - 1)
    take_denominator = max(1, take.frame_count - 1)
    position_errors = [
        abs(
            pair.reference_index / float(ref_denominator)
            - pair.take_index / float(take_denominator)
        )
        for pair in alignment.pairs
    ]
    warp_steps = 0
    for left, right in zip(alignment.pairs, alignment.pairs[1:], strict=False):
        if (
            right.reference_index == left.reference_index
            or right.take_index == left.take_index
        ):
            warp_steps += 1
    step_count = max(1, len(alignment.pairs) - 1)
    return {
        "pair_count": alignment.pair_count,
        "coverage_ratio": alignment.coverage_ratio,
        "total_cost": alignment.total_cost,
        "mean_local_cost": float(
            statistics.fmean(pair.local_cost for pair in alignment.pairs)
        ),
        "mean_normalized_position_error": float(statistics.fmean(position_errors)),
        "max_normalized_position_error": float(max(position_errors)),
        "warp_step_fraction": warp_steps / float(step_count),
    }


def classify_protected_cross_talk(
    *,
    observed_max_abs_delta: float,
    linear_max_abs_delta: float,
    alignment_max_abs_contribution: float,
) -> str:
    """Classify where protected-score movement is already present."""

    observed = observed_max_abs_delta > CROSS_TALK_ATTRIBUTION_EPSILON
    pre_alignment = linear_max_abs_delta > CROSS_TALK_ATTRIBUTION_EPSILON
    alignment = alignment_max_abs_contribution > CROSS_TALK_ATTRIBUTION_EPSILON

    if not observed:
        return "none"
    if pre_alignment and alignment:
        return "mixed_pre_alignment_and_alignment"
    if pre_alignment:
        return "pre_alignment_feature_or_score_path"
    if alignment:
        return "alignment_path"
    return "unresolved"


def render_cross_talk_attribution_text(summary: dict[str, object]) -> str:
    lines = [
        "PracticeLens R0.5c Cross-Talk Attribution Audit v1",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
    ]
    for family in summary["families"]:
        lines.append(f"{family['family']}:")
        for metric_name, attribution in family["protected_attribution"].items():
            lines.append(
                f"  {metric_name}: {attribution['classification']} "
                f"observed={attribution['observed_max_abs_delta']:.6f} "
                f"linear={attribution['linear_max_abs_delta']:.6f} "
                f"alignment={attribution['alignment_max_abs_contribution']:.6f}"
            )
    return "\n".join(lines)


def _family_attribution_payload(
    family: str,
    observations: tuple[CrossTalkConditionObservation, ...],
) -> dict[str, object]:
    if family not in _TARGET_RULES:
        raise ValueError(f"unsupported target family: {family!r}")

    ordered = tuple(
        sorted(
            observations,
            key=lambda observation: observation.case.condition.intervention.strength,
        )
    )
    controls = [
        observation
        for observation in ordered
        if observation.case.condition.intervention.strength == 0.0
    ]
    if len(controls) != 1:
        raise ValueError(f"family {family!r} must contain exactly one zero control")
    control = controls[0]

    primary_measurement, protected_measurements = _TARGET_RULES[family]
    protected_attribution: dict[str, dict[str, object]] = {}
    for measurement_name in protected_measurements:
        observed_deltas = [
            observation.observed_scores[measurement_name]
            - control.observed_scores[measurement_name]
            for observation in ordered
        ]
        linear_deltas = [
            observation.linear_alignment_scores[measurement_name]
            - control.linear_alignment_scores[measurement_name]
            for observation in ordered
        ]
        alignment_contributions = [
            observed_delta - linear_delta
            for observed_delta, linear_delta in zip(
                observed_deltas,
                linear_deltas,
                strict=True,
            )
        ]
        observed_max = max(abs(value) for value in observed_deltas)
        linear_max = max(abs(value) for value in linear_deltas)
        alignment_max = max(abs(value) for value in alignment_contributions)

        protected_attribution[measurement_name] = {
            "classification": classify_protected_cross_talk(
                observed_max_abs_delta=observed_max,
                linear_max_abs_delta=linear_max,
                alignment_max_abs_contribution=alignment_max,
            ),
            "observed_score_deltas": observed_deltas,
            "linear_alignment_score_deltas": linear_deltas,
            "alignment_contribution_deltas": alignment_contributions,
            "observed_max_abs_delta": observed_max,
            "linear_max_abs_delta": linear_max,
            "alignment_max_abs_contribution": alignment_max,
            "score_dependencies": _SCORE_DEPENDENCIES[measurement_name],
            "feature_evidence": _protected_feature_evidence(
                measurement_name,
                ordered,
                control,
            ),
        }

    return {
        "family": family,
        "primary_measurement": primary_measurement,
        "protected_measurements": list(protected_measurements),
        "strengths": [
            observation.case.condition.intervention.strength
            for observation in ordered
        ],
        "conditions": [
            {
                "condition_id": observation.case.condition.condition_id,
                "strength": observation.case.condition.intervention.strength,
                "feature_diagnostics": observation.feature_diagnostics,
                "alignment_diagnostics": observation.alignment_diagnostics,
                "observed_scores": observation.observed_scores,
                "linear_alignment_scores": observation.linear_alignment_scores,
            }
            for observation in ordered
        ],
        "protected_attribution": protected_attribution,
    }


def _protected_feature_evidence(
    measurement_name: str,
    observations: tuple[CrossTalkConditionObservation, ...],
    control: CrossTalkConditionObservation,
) -> dict[str, object]:
    if measurement_name == MetricName.PITCH_FIDELITY.value:
        keys = (
            "linear_pitch_mean_cents_error",
            "linear_pitch_voiced_mismatch_fraction",
            "voiced_ratio_delta",
        )
    elif measurement_name == MetricName.RHYTHM_FIDELITY.value:
        keys = (
            "normalized_onset_mean_nearest_distance",
            "onset_count_delta",
            "tempo_delta_bpm",
        )
    elif measurement_name == MetricName.TIMING_CONSISTENCY.value:
        return {
            "note": (
                "timing_consistency has no independent pre-alignment timing feature; "
                "the score is defined from alignment path geometry"
            )
        }
    else:
        return {"note": "no protected feature evidence mapping"}

    evidence: dict[str, object] = {}
    for key in keys:
        control_value = control.feature_diagnostics[key]
        values = [observation.feature_diagnostics[key] for observation in observations]
        evidence[key] = {
            "control": control_value,
            "values": values,
            "max_abs_delta": _max_abs_optional_delta(control_value, values),
        }
    return evidence


def _score_map(component_scores: tuple[object, ...]) -> dict[str, float]:
    return {
        score.name.value: float(score.score)
        for score in component_scores
    }


def _normalized_onset_mean_nearest_distance(
    reference: FeatureBundle,
    take: FeatureBundle,
) -> float:
    reference_onsets = _normalize_onsets(reference)
    take_onsets = _normalize_onsets(take)
    if not reference_onsets and not take_onsets:
        return 0.0
    if not reference_onsets or not take_onsets:
        return 1.0
    distances = [
        min(abs(ref_onset - take_onset) for take_onset in take_onsets)
        for ref_onset in reference_onsets
    ]
    return float(statistics.fmean(distances))


def _normalize_onsets(bundle: FeatureBundle) -> tuple[float, ...]:
    if not bundle.onset_times_s:
        return ()
    duration = max(bundle.time_axis_s[-1] if bundle.time_axis_s else 0.0, 1e-9)
    return tuple(value / duration for value in bundle.onset_times_s)


def _voiced_ratio(bundle: FeatureBundle) -> float:
    if not bundle.voiced_mask:
        return 0.0
    return sum(1 for value in bundle.voiced_mask if value) / float(len(bundle.voiced_mask))


def _optional_delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return float(right - left)


def _max_abs_optional_delta(
    control_value: float | int | None,
    values: list[float | int | None],
) -> float | None:
    if control_value is None or any(value is None for value in values):
        return None
    return max(abs(float(value) - float(control_value)) for value in values)
