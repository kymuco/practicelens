from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

from practicelens.alignment import AlignmentPath, align_feature_bundles
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName
from practicelens.domain.models import AnalysisConfig, ComponentScore
from practicelens.features import FeatureBundle, extract_feature_bundle
from practicelens.io import load_wav_audio
from practicelens.measurement.controlled_perturbations import (
    ControlledPerturbationCase,
    generate_controlled_perturbation_harness,
)
from practicelens.measurement.cross_talk_attribution import (
    alignment_diagnostics,
    build_linear_alignment,
    feature_diagnostics,
)
from practicelens.scoring import score_aligned_features

ADDITIVE_NOISE_ATTRIBUTION_SCHEMA_VERSION = 1
ADDITIVE_NOISE_ATTRIBUTION_EXPERIMENT_ID = "r0.5g-additive-noise-attribution-v1"
ADDITIVE_NOISE_ATTRIBUTION_EPSILON = 1e-9
ADDITIVE_NOISE_ATTRIBUTION_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)


@dataclass(slots=True, frozen=True)
class NoiseAttributionCondition:
    case: ControlledPerturbationCase
    feature_diagnostics: dict[str, float | int | None]
    production_alignment: dict[str, float | int]
    production_scores: dict[str, float]
    linear_scores: dict[str, float]
    production_pitch_terms: dict[str, float | int]
    linear_pitch_terms: dict[str, float | int]
    rhythm_terms: dict[str, float | int]


@dataclass(slots=True, frozen=True)
class AdditiveNoiseAttributionResult:
    out_dir: Path
    summary_path: Path
    conditions: tuple[NoiseAttributionCondition, ...]
    summary: dict[str, object]


def run_additive_noise_attribution_audit(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    config: AnalysisConfig = ADDITIVE_NOISE_ATTRIBUTION_CONFIG,
) -> AdditiveNoiseAttributionResult:
    """Localize additive-noise movement in pitch and rhythm measurements."""

    out_dir.mkdir(parents=True, exist_ok=True)
    harness = generate_controlled_perturbation_harness(
        out_dir / "harness",
        sample_rate=config.target_sample_rate,
    )
    pipeline = OfflineReferenceAnalysisPipeline()
    reference_audio = pipeline._prepare_audio(load_wav_audio(harness.reference_path), config)
    reference_features = extract_feature_bundle(reference_audio, config)

    conditions: list[NoiseAttributionCondition] = []
    for case in harness.cases:
        if case.condition.intervention.family != "deterministic_additive_noise":
            continue

        take_audio = pipeline._prepare_audio(load_wav_audio(case.path), config)
        take_features = extract_feature_bundle(take_audio, config)
        production_alignment = align_feature_bundles(reference_features, take_features)
        linear_alignment = build_linear_alignment(reference_features, take_features)

        production_scoring = score_aligned_features(
            reference_features,
            take_features,
            production_alignment,
            config,
        )
        linear_scoring = score_aligned_features(
            reference_features,
            take_features,
            linear_alignment,
            config,
        )

        conditions.append(
            NoiseAttributionCondition(
                case=case,
                feature_diagnostics=feature_diagnostics(
                    reference_features,
                    take_features,
                    linear_alignment,
                ),
                production_alignment=alignment_diagnostics(
                    reference_features,
                    take_features,
                    production_alignment,
                ),
                production_scores=_score_map(production_scoring.component_scores),
                linear_scores=_score_map(linear_scoring.component_scores),
                production_pitch_terms=pitch_score_terms(
                    reference_features,
                    take_features,
                    production_alignment,
                ),
                linear_pitch_terms=pitch_score_terms(
                    reference_features,
                    take_features,
                    linear_alignment,
                ),
                rhythm_terms=rhythm_score_terms(reference_features, take_features),
            )
        )

    summary = additive_noise_attribution_payload(
        tuple(conditions),
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return AdditiveNoiseAttributionResult(
        out_dir=out_dir,
        summary_path=summary_path,
        conditions=tuple(conditions),
        summary=summary,
    )


def additive_noise_attribution_payload(
    conditions: tuple[NoiseAttributionCondition, ...],
    *,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    ordered = tuple(
        sorted(
            conditions,
            key=lambda item: item.case.condition.intervention.strength,
        )
    )
    if len(ordered) < 2:
        raise ValueError("noise attribution requires a control and non-zero conditions")
    if ordered[0].case.condition.intervention.strength != 0.0:
        raise ValueError("first ordered noise condition must be the zero control")

    control = ordered[0]
    pitch = _pitch_attribution_payload(ordered, control)
    rhythm = _rhythm_attribution_payload(ordered, control)
    reconstruction = _reconstruction_payload(ordered)

    return {
        "kind": "additive_noise_attribution_audit",
        "schema_version": ADDITIVE_NOISE_ATTRIBUTION_SCHEMA_VERSION,
        "experiment_id": ADDITIVE_NOISE_ATTRIBUTION_EXPERIMENT_ID,
        "code_revision": code_revision,
        "epsilon": ADDITIVE_NOISE_ATTRIBUTION_EPSILON,
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
        },
        "strengths": [
            item.case.condition.intervention.strength
            for item in ordered
        ],
        "pitch_fidelity": pitch,
        "rhythm_fidelity": rhythm,
        "score_reconstruction": reconstruction,
        "conditions": [
            {
                "condition_id": item.case.condition.condition_id,
                "strength": item.case.condition.intervention.strength,
                "feature_diagnostics": item.feature_diagnostics,
                "production_alignment": item.production_alignment,
                "production_scores": item.production_scores,
                "linear_scores": item.linear_scores,
                "production_pitch_terms": item.production_pitch_terms,
                "linear_pitch_terms": item.linear_pitch_terms,
                "rhythm_terms": item.rhythm_terms,
            }
            for item in ordered
        ],
        "interpretation_boundary": [
            "The audit localizes the first stage where additive-noise movement becomes observable; it does not repair the estimator.",
            "Linear alignment is a diagnostic counterfactual that removes feature-similarity path selection from pitch scoring.",
            (
                "Rhythm fidelity is alignment-independent in the production scorer, so "
                "onset/time feature movement precedes its score movement."
            ),
            "Score-term reconstruction verifies the current score mapping rather than proposing a new score.",
        ],
    }


def pitch_score_terms(
    reference: FeatureBundle,
    take: FeatureBundle,
    alignment: AlignmentPath,
) -> dict[str, float | int]:
    """Reconstruct current pitch-score terms for attribution."""

    cents_errors: list[float] = []
    voiced_mismatches = 0
    aligned_voiced_pairs = 0
    for pair in alignment.pairs:
        ref_pitch = reference.pitch_contour_hz[pair.reference_index]
        take_pitch = take.pitch_contour_hz[pair.take_index]
        ref_voiced = reference.voiced_mask[pair.reference_index]
        take_voiced = take.voiced_mask[pair.take_index]
        if ref_voiced and take_voiced and ref_pitch > 0.0 and take_pitch > 0.0:
            aligned_voiced_pairs += 1
            cents_errors.append(abs(1200.0 * math.log2(ref_pitch / take_pitch)))
        elif ref_voiced != take_voiced:
            voiced_mismatches += 1

    if not cents_errors:
        final_score = max(0.0, 100.0 - voiced_mismatches * 5.0)
        return {
            "aligned_pair_count": alignment.pair_count,
            "aligned_voiced_pair_count": aligned_voiced_pairs,
            "voiced_mismatch_count": voiced_mismatches,
            "mean_cents_error": 0.0,
            "raw_error_score": final_score,
            "mismatch_penalty": 0.0,
            "final_score": final_score,
        }

    mean_error = float(statistics.fmean(cents_errors))
    raw_score = _score_from_error(mean_error, tolerance=200.0)
    mismatch_penalty = min(25.0, voiced_mismatches * 1.5)
    final_score = max(0.0, raw_score - mismatch_penalty)
    return {
        "aligned_pair_count": alignment.pair_count,
        "aligned_voiced_pair_count": aligned_voiced_pairs,
        "voiced_mismatch_count": voiced_mismatches,
        "mean_cents_error": mean_error,
        "raw_error_score": raw_score,
        "mismatch_penalty": mismatch_penalty,
        "final_score": final_score,
    }


def rhythm_score_terms(
    reference: FeatureBundle,
    take: FeatureBundle,
) -> dict[str, float | int]:
    """Reconstruct current rhythm-score terms from onset/time features."""

    reference_onsets = _normalize_onsets(reference)
    take_onsets = _normalize_onsets(take)
    if not reference_onsets and not take_onsets:
        return {
            "reference_onset_count": 0,
            "take_onset_count": 0,
            "mean_nearest_distance": 0.0,
            "count_penalty_fraction": 0.0,
            "distance_score": 100.0,
            "count_score": 100.0,
            "final_score": 100.0,
        }
    if not reference_onsets or not take_onsets:
        return {
            "reference_onset_count": len(reference_onsets),
            "take_onset_count": len(take_onsets),
            "mean_nearest_distance": 1.0,
            "count_penalty_fraction": 1.0,
            "distance_score": 0.0,
            "count_score": 0.0,
            "final_score": 0.0,
        }

    nearest_distances = [
        min(abs(ref_onset - take_onset) for take_onset in take_onsets)
        for ref_onset in reference_onsets
    ]
    mean_distance = float(statistics.fmean(nearest_distances))
    count_penalty = abs(len(reference_onsets) - len(take_onsets)) / max(
        len(reference_onsets),
        1,
    )
    distance_score = _score_from_error(mean_distance, tolerance=0.12)
    count_score = max(0.0, 100.0 * (1.0 - count_penalty))
    final_score = distance_score * 0.75 + count_score * 0.25
    return {
        "reference_onset_count": len(reference_onsets),
        "take_onset_count": len(take_onsets),
        "mean_nearest_distance": mean_distance,
        "count_penalty_fraction": count_penalty,
        "distance_score": distance_score,
        "count_score": count_score,
        "final_score": final_score,
    }


def classify_first_noise_stage(
    *,
    feature_movement: float,
    linear_score_movement: float,
    alignment_contribution: float,
) -> str:
    """Classify the first observable stage of one noise-induced measurement movement."""

    feature_changed = feature_movement > ADDITIVE_NOISE_ATTRIBUTION_EPSILON
    linear_changed = linear_score_movement > ADDITIVE_NOISE_ATTRIBUTION_EPSILON
    alignment_changed = alignment_contribution > ADDITIVE_NOISE_ATTRIBUTION_EPSILON

    if feature_changed and alignment_changed:
        return "feature_extraction_with_alignment_contribution"
    if feature_changed:
        return "feature_extraction"
    if linear_changed and alignment_changed:
        return "score_construction_with_alignment_contribution"
    if linear_changed:
        return "score_construction"
    if alignment_changed:
        return "alignment"
    return "none"


def render_additive_noise_attribution_text(summary: dict[str, object]) -> str:
    pitch = summary["pitch_fidelity"]
    rhythm = summary["rhythm_fidelity"]
    return "\n".join(
        (
            "PracticeLens R0.5g Additive Noise Attribution Audit v1",
            f"revision: {summary['code_revision'] or 'unknown'}",
            "",
            (
                "pitch_fidelity: "
                f"{pitch['classification']} "
                f"production={pitch['production_max_abs_delta']:.6f} "
                f"linear={pitch['linear_max_abs_delta']:.6f} "
                f"alignment={pitch['alignment_max_abs_contribution']:.6f}"
            ),
            (
                "rhythm_fidelity: "
                f"{rhythm['classification']} "
                f"production={rhythm['production_max_abs_delta']:.6f}"
            ),
        )
    )


def _pitch_attribution_payload(
    ordered: tuple[NoiseAttributionCondition, ...],
    control: NoiseAttributionCondition,
) -> dict[str, object]:
    name = MetricName.PITCH_FIDELITY.value
    production_deltas = [
        item.production_scores[name] - control.production_scores[name]
        for item in ordered
    ]
    linear_deltas = [
        item.linear_scores[name] - control.linear_scores[name]
        for item in ordered
    ]
    alignment_contributions = [
        production_delta - linear_delta
        for production_delta, linear_delta in zip(
            production_deltas,
            linear_deltas,
            strict=True,
        )
    ]

    feature_movement = max(
        max(
            abs(float(item.feature_diagnostics["linear_pitch_mean_cents_error"])),
            abs(
                float(
                    item.feature_diagnostics[
                        "linear_pitch_voiced_mismatch_fraction"
                    ]
                )
            ),
            abs(float(item.feature_diagnostics["voiced_ratio_delta"])),
        )
        for item in ordered
    )
    production_max = max(abs(value) for value in production_deltas)
    linear_max = max(abs(value) for value in linear_deltas)
    alignment_max = max(abs(value) for value in alignment_contributions)

    return {
        "classification": classify_first_noise_stage(
            feature_movement=feature_movement,
            linear_score_movement=linear_max,
            alignment_contribution=alignment_max,
        ),
        "production_score_deltas": production_deltas,
        "linear_alignment_score_deltas": linear_deltas,
        "alignment_contribution_deltas": alignment_contributions,
        "production_max_abs_delta": production_max,
        "linear_max_abs_delta": linear_max,
        "alignment_max_abs_contribution": alignment_max,
        "feature_evidence": {
            "linear_pitch_mean_cents_error": [
                item.feature_diagnostics["linear_pitch_mean_cents_error"]
                for item in ordered
            ],
            "linear_pitch_voiced_mismatch_fraction": [
                item.feature_diagnostics["linear_pitch_voiced_mismatch_fraction"]
                for item in ordered
            ],
            "voiced_ratio_delta": [
                item.feature_diagnostics["voiced_ratio_delta"]
                for item in ordered
            ],
        },
        "production_score_terms": [
            item.production_pitch_terms
            for item in ordered
        ],
        "linear_score_terms": [
            item.linear_pitch_terms
            for item in ordered
        ],
    }


def _rhythm_attribution_payload(
    ordered: tuple[NoiseAttributionCondition, ...],
    control: NoiseAttributionCondition,
) -> dict[str, object]:
    name = MetricName.RHYTHM_FIDELITY.value
    production_deltas = [
        item.production_scores[name] - control.production_scores[name]
        for item in ordered
    ]
    production_max = max(abs(value) for value in production_deltas)

    onset_distance_movement = max(
        abs(
            float(item.rhythm_terms["mean_nearest_distance"])
            - float(control.rhythm_terms["mean_nearest_distance"])
        )
        for item in ordered
    )
    onset_count_movement = max(
        abs(
            int(item.rhythm_terms["take_onset_count"])
            - int(control.rhythm_terms["take_onset_count"])
        )
        for item in ordered
    )
    feature_movement = max(onset_distance_movement, float(onset_count_movement))

    return {
        "classification": classify_first_noise_stage(
            feature_movement=feature_movement,
            linear_score_movement=production_max,
            alignment_contribution=0.0,
        ),
        "production_score_deltas": production_deltas,
        "production_max_abs_delta": production_max,
        "uses_alignment": False,
        "feature_evidence": {
            "reference_onset_count": [
                item.rhythm_terms["reference_onset_count"]
                for item in ordered
            ],
            "take_onset_count": [
                item.rhythm_terms["take_onset_count"]
                for item in ordered
            ],
            "mean_nearest_distance": [
                item.rhythm_terms["mean_nearest_distance"]
                for item in ordered
            ],
            "count_penalty_fraction": [
                item.rhythm_terms["count_penalty_fraction"]
                for item in ordered
            ],
            "distance_score": [
                item.rhythm_terms["distance_score"]
                for item in ordered
            ],
            "count_score": [
                item.rhythm_terms["count_score"]
                for item in ordered
            ],
        },
        "score_terms": [
            item.rhythm_terms
            for item in ordered
        ],
    }


def _reconstruction_payload(
    ordered: tuple[NoiseAttributionCondition, ...],
) -> dict[str, object]:
    pitch_production_errors = [
        abs(
            float(item.production_pitch_terms["final_score"])
            - item.production_scores[MetricName.PITCH_FIDELITY.value]
        )
        for item in ordered
    ]
    pitch_linear_errors = [
        abs(
            float(item.linear_pitch_terms["final_score"])
            - item.linear_scores[MetricName.PITCH_FIDELITY.value]
        )
        for item in ordered
    ]
    rhythm_errors = [
        abs(
            float(item.rhythm_terms["final_score"])
            - item.production_scores[MetricName.RHYTHM_FIDELITY.value]
        )
        for item in ordered
    ]
    return {
        "pitch_production_max_abs_error": max(pitch_production_errors),
        "pitch_linear_max_abs_error": max(pitch_linear_errors),
        "rhythm_max_abs_error": max(rhythm_errors),
        "exact_within_epsilon": (
            max(
                *pitch_production_errors,
                *pitch_linear_errors,
                *rhythm_errors,
            )
            <= ADDITIVE_NOISE_ATTRIBUTION_EPSILON
        ),
    }


def _score_map(component_scores: tuple[ComponentScore, ...]) -> dict[str, float]:
    return {
        score.name.value: float(score.score)
        for score in component_scores
    }


def _normalize_onsets(bundle: FeatureBundle) -> tuple[float, ...]:
    if not bundle.onset_times_s:
        return ()
    if not bundle.time_axis_s:
        return bundle.onset_times_s
    duration = max(bundle.time_axis_s[-1], 1e-9)
    return tuple(value / duration for value in bundle.onset_times_s)


def _score_from_error(error: float, *, tolerance: float) -> float:
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    return max(0.0, min(100.0, 100.0 * (1.0 - (error / tolerance))))
