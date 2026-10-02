from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from practicelens.alignment.models import AlignmentPair, AlignmentPath
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
from practicelens.domain.enums import MetricName
from practicelens.domain.errors import AlignmentError
from practicelens.domain.models import AnalysisConfig, ComponentScore
from practicelens.features import FeatureBundle, extract_feature_bundle
from practicelens.io import load_wav_audio
from practicelens.measurement.controlled_perturbations import (
    ControlledPerturbationCase,
    generate_controlled_perturbation_harness,
)
from practicelens.measurement.cross_talk_attribution import alignment_diagnostics
from practicelens.scoring import score_aligned_features

ALIGNMENT_SUBSTRATE_ABLATION_SCHEMA_VERSION = 1
ALIGNMENT_SUBSTRATE_ABLATION_EXPERIMENT_ID = "r0.5d-alignment-substrate-ablation-v1"
ALIGNMENT_SUBSTRATE_ABLATION_EPSILON = 1e-9
ALIGNMENT_SUBSTRATE_ABLATION_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)


@dataclass(slots=True, frozen=True)
class AlignmentCostProfile:
    """One diagnostic DTW cost profile. Not a production configuration."""

    name: str
    pitch_weight: float
    energy_weight: float
    zcr_weight: float
    voiced_mismatch_penalty: float
    position_penalty_weight: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.pitch_weight,
            self.energy_weight,
            self.zcr_weight,
            self.voiced_mismatch_penalty,
            self.position_penalty_weight,
        )
        if not self.name:
            raise ValueError("alignment profile name must not be empty")
        if any(not math.isfinite(value) or value < 0.0 for value in values):
            raise ValueError("alignment profile weights must be finite and non-negative")
        feature_weight_sum = self.pitch_weight + self.energy_weight + self.zcr_weight
        if not math.isclose(feature_weight_sum, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("pitch + energy + zcr weights must sum to 1")


CURRENT_PROFILE = AlignmentCostProfile(
    name="current",
    pitch_weight=0.55,
    energy_weight=0.25,
    zcr_weight=0.20,
    voiced_mismatch_penalty=0.40,
)

PITCH_HALF_PROFILE = AlignmentCostProfile(
    name="pitch_half",
    pitch_weight=0.275,
    energy_weight=0.4027777777777778,
    zcr_weight=0.3222222222222222,
    voiced_mismatch_penalty=0.20,
)

PITCH_FREE_STRUCTURAL_PROFILE = AlignmentCostProfile(
    name="pitch_free_structural",
    pitch_weight=0.0,
    energy_weight=5.0 / 9.0,
    zcr_weight=4.0 / 9.0,
    voiced_mismatch_penalty=0.0,
)

CURRENT_POSITIONAL_PROFILE = AlignmentCostProfile(
    name="current_positional_0p10",
    pitch_weight=0.55,
    energy_weight=0.25,
    zcr_weight=0.20,
    voiced_mismatch_penalty=0.40,
    position_penalty_weight=0.10,
)

PITCH_HALF_POSITIONAL_PROFILE = AlignmentCostProfile(
    name="pitch_half_positional_0p10",
    pitch_weight=0.275,
    energy_weight=0.4027777777777778,
    zcr_weight=0.3222222222222222,
    voiced_mismatch_penalty=0.20,
    position_penalty_weight=0.10,
)

ALIGNMENT_ABLATION_PROFILES = (
    CURRENT_PROFILE,
    PITCH_HALF_PROFILE,
    PITCH_FREE_STRUCTURAL_PROFILE,
    CURRENT_POSITIONAL_PROFILE,
    PITCH_HALF_POSITIONAL_PROFILE,
)


@dataclass(slots=True, frozen=True)
class AlignmentAblationCondition:
    """Scores and path evidence for one profile x controlled condition."""

    profile_name: str
    case: ControlledPerturbationCase
    scores: dict[str, float]
    alignment: dict[str, float | int]


@dataclass(slots=True, frozen=True)
class AlignmentSubstrateAblationResult:
    out_dir: Path
    summary_path: Path
    conditions: tuple[AlignmentAblationCondition, ...]
    summary: dict[str, object]


def run_alignment_substrate_ablation(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    config: AnalysisConfig = ALIGNMENT_SUBSTRATE_ABLATION_CONFIG,
) -> AlignmentSubstrateAblationResult:
    """Compare preregistered alignment substrates on frozen controlled targets."""

    out_dir.mkdir(parents=True, exist_ok=True)
    harness = generate_controlled_perturbation_harness(
        out_dir / "harness",
        sample_rate=config.target_sample_rate,
    )
    pipeline = OfflineReferenceAnalysisPipeline()
    reference_audio = pipeline._prepare_audio(load_wav_audio(harness.reference_path), config)
    reference_features = extract_feature_bundle(reference_audio, config)

    target_cases = tuple(
        case
        for case in harness.cases
        if case.condition.intervention.family in {"pitch_drift", "local_timing_warp"}
    )
    prepared_features = {
        case.condition.condition_id: extract_feature_bundle(
            pipeline._prepare_audio(load_wav_audio(case.path), config),
            config,
        )
        for case in target_cases
    }

    conditions: list[AlignmentAblationCondition] = []
    for profile in ALIGNMENT_ABLATION_PROFILES:
        for case in target_cases:
            take_features = prepared_features[case.condition.condition_id]
            alignment = align_with_profile(reference_features, take_features, profile)
            scoring = score_aligned_features(
                reference_features,
                take_features,
                alignment,
                config,
            )
            conditions.append(
                AlignmentAblationCondition(
                    profile_name=profile.name,
                    case=case,
                    scores=_score_map(scoring.component_scores),
                    alignment=alignment_diagnostics(
                        reference_features,
                        take_features,
                        alignment,
                    ),
                )
            )

    summary = alignment_substrate_ablation_payload(
        tuple(conditions),
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return AlignmentSubstrateAblationResult(
        out_dir=out_dir,
        summary_path=summary_path,
        conditions=tuple(conditions),
        summary=summary,
    )


def align_with_profile(
    reference: FeatureBundle,
    take: FeatureBundle,
    profile: AlignmentCostProfile,
) -> AlignmentPath:
    """Run diagnostic DTW with an explicit cost profile."""

    if reference.frame_count == 0 or take.frame_count == 0:
        raise AlignmentError("feature bundles must both contain at least one frame")

    ref_vectors = tuple(_feature_vector(reference, index) for index in range(reference.frame_count))
    take_vectors = tuple(_feature_vector(take, index) for index in range(take.frame_count))

    rows = reference.frame_count
    cols = take.frame_count
    costs = [[float("inf")] * cols for _ in range(rows)]
    backpointers: list[list[tuple[int, int] | None]] = [[None] * cols for _ in range(rows)]

    for row in range(rows):
        for col in range(cols):
            local_cost = _profile_distance(
                ref_vectors[row],
                take_vectors[col],
                row=row,
                col=col,
                rows=rows,
                cols=cols,
                profile=profile,
            )
            if row == 0 and col == 0:
                costs[row][col] = local_cost
                continue

            candidates: list[tuple[float, tuple[int, int]]] = []
            if row > 0:
                candidates.append((costs[row - 1][col], (row - 1, col)))
            if col > 0:
                candidates.append((costs[row][col - 1], (row, col - 1)))
            if row > 0 and col > 0:
                candidates.append((costs[row - 1][col - 1], (row - 1, col - 1)))

            previous_cost, previous = min(candidates, key=lambda item: item[0])
            costs[row][col] = local_cost + previous_cost
            backpointers[row][col] = previous

    row = rows - 1
    col = cols - 1
    reversed_pairs: list[AlignmentPair] = []
    while True:
        local_cost = _profile_distance(
            ref_vectors[row],
            take_vectors[col],
            row=row,
            col=col,
            rows=rows,
            cols=cols,
            profile=profile,
        )
        reversed_pairs.append(
            AlignmentPair(
                reference_index=row,
                take_index=col,
                local_cost=local_cost,
            )
        )
        previous = backpointers[row][col]
        if previous is None:
            break
        row, col = previous

    pairs = tuple(reversed(reversed_pairs))
    unique_reference = {pair.reference_index for pair in pairs}
    unique_take = {pair.take_index for pair in pairs}
    coverage_ratio = min(
        len(unique_reference) / float(reference.frame_count),
        len(unique_take) / float(take.frame_count),
    )
    return AlignmentPath(
        pairs=pairs,
        total_cost=costs[rows - 1][cols - 1],
        coverage_ratio=coverage_ratio,
    )


def alignment_substrate_ablation_payload(
    conditions: tuple[AlignmentAblationCondition, ...],
    *,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    """Build the machine-readable R0.5d comparison."""

    by_profile: dict[str, list[AlignmentAblationCondition]] = {}
    for condition in conditions:
        by_profile.setdefault(condition.profile_name, []).append(condition)

    profile_payloads = {
        profile.name: _profile_payload(profile, tuple(by_profile[profile.name]))
        for profile in ALIGNMENT_ABLATION_PROFILES
    }
    current = profile_payloads[CURRENT_PROFILE.name]
    current_cross_talk = float(
        current["pitch_drift"]["timing_cross_talk_max_abs_delta"]
    )
    current_min_coverage = float(current["path_geometry"]["min_coverage_ratio"])

    for profile in ALIGNMENT_ABLATION_PROFILES:
        payload = profile_payloads[profile.name]
        payload["strict_narrow_hypothesis"] = _strict_narrow_hypothesis(
            profile_name=profile.name,
            payload=payload,
            current_cross_talk=current_cross_talk,
            current_min_coverage=current_min_coverage,
        )

    successful = [
        profile.name
        for profile in ALIGNMENT_ABLATION_PROFILES
        if profile_payloads[profile.name]["strict_narrow_hypothesis"]["meets"]
    ]

    return {
        "kind": "alignment_substrate_ablation",
        "schema_version": ALIGNMENT_SUBSTRATE_ABLATION_SCHEMA_VERSION,
        "experiment_id": ALIGNMENT_SUBSTRATE_ABLATION_EXPERIMENT_ID,
        "code_revision": code_revision,
        "epsilon": ALIGNMENT_SUBSTRATE_ABLATION_EPSILON,
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
        },
        "profiles": profile_payloads,
        "profiles_meeting_strict_narrow_hypothesis": successful,
        "strict_narrow_hypothesis": {
            "question": (
                "Does a preregistered non-production alignment profile strictly reduce "
                "pitch-drift timing cross-talk, make local-timing response monotonic, "
                "preserve directional/monotonic pitch sensitivity, and preserve minimum coverage?"
            ),
            "current_timing_cross_talk": current_cross_talk,
            "current_min_coverage": current_min_coverage,
        },
        "interpretation_boundary": [
            "Ablation profiles are diagnostic counterfactuals, not production candidates.",
            "The experiment does not tune weights after observing results.",
            "A profile meeting the narrow hypothesis shows that the timing defect is solvable within alignment-space.",
            "Production admission requires a separate validation step and broader failure-boundary checks.",
        ],
    }


def render_alignment_substrate_ablation_text(summary: dict[str, object]) -> str:
    lines = [
        "PracticeLens R0.5d Alignment Substrate Ablation v1",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
    ]
    for name, payload in summary["profiles"].items():
        pitch = payload["pitch_drift"]
        timing = payload["local_timing_warp"]
        hypothesis = payload["strict_narrow_hypothesis"]
        lines.append(
            f"{name}: pitch->timing={pitch['timing_cross_talk_max_abs_delta']:.6f} "
            f"timing_monotonicity={timing['timing_monotonicity']} "
            f"timing_endpoint={timing['timing_endpoint_delta']:+.6f} "
            f"pitch_monotonicity={pitch['pitch_monotonicity']} "
            f"meets={hypothesis['meets']}"
        )
    return "\n".join(lines)


def _profile_payload(
    profile: AlignmentCostProfile,
    conditions: tuple[AlignmentAblationCondition, ...],
) -> dict[str, object]:
    by_family: dict[str, list[AlignmentAblationCondition]] = {}
    for condition in conditions:
        family = condition.case.condition.intervention.family
        by_family.setdefault(family, []).append(condition)

    pitch = _ordered_family(by_family["pitch_drift"])
    timing = _ordered_family(by_family["local_timing_warp"])

    pitch_scores = [item.scores[MetricName.PITCH_FIDELITY.value] for item in pitch]
    pitch_timing_scores = [item.scores[MetricName.TIMING_CONSISTENCY.value] for item in pitch]
    timing_scores = [item.scores[MetricName.TIMING_CONSISTENCY.value] for item in timing]
    timing_pitch_scores = [item.scores[MetricName.PITCH_FIDELITY.value] for item in timing]

    all_conditions = (*pitch, *timing)
    return {
        "profile": {
            "pitch_weight": profile.pitch_weight,
            "energy_weight": profile.energy_weight,
            "zcr_weight": profile.zcr_weight,
            "voiced_mismatch_penalty": profile.voiced_mismatch_penalty,
            "position_penalty_weight": profile.position_penalty_weight,
        },
        "pitch_drift": {
            "strengths": [
                item.case.condition.intervention.strength
                for item in pitch
            ],
            "pitch_scores": pitch_scores,
            "pitch_directional_sensitivity": _directional_sensitivity_verdict(pitch_scores),
            "pitch_monotonicity": _nonincreasing_monotonicity_verdict(pitch_scores),
            "timing_scores": pitch_timing_scores,
            "timing_cross_talk_max_abs_delta": _max_abs_delta_from_control(
                pitch_timing_scores
            ),
        },
        "local_timing_warp": {
            "strengths": [
                item.case.condition.intervention.strength
                for item in timing
            ],
            "timing_scores": timing_scores,
            "timing_directional_sensitivity": _directional_sensitivity_verdict(timing_scores),
            "timing_monotonicity": _nonincreasing_monotonicity_verdict(timing_scores),
            "timing_endpoint_delta": timing_scores[-1] - timing_scores[0],
            "pitch_scores": timing_pitch_scores,
            "pitch_cross_talk_max_abs_delta": _max_abs_delta_from_control(
                timing_pitch_scores
            ),
        },
        "path_geometry": {
            "min_coverage_ratio": min(
                float(item.alignment["coverage_ratio"])
                for item in all_conditions
            ),
            "max_mean_normalized_position_error": max(
                float(item.alignment["mean_normalized_position_error"])
                for item in all_conditions
            ),
            "max_warp_step_fraction": max(
                float(item.alignment["warp_step_fraction"])
                for item in all_conditions
            ),
        },
        "conditions": [
            {
                "condition_id": item.case.condition.condition_id,
                "family": item.case.condition.intervention.family,
                "strength": item.case.condition.intervention.strength,
                "scores": item.scores,
                "alignment": item.alignment,
            }
            for item in all_conditions
        ],
    }


def _strict_narrow_hypothesis(
    *,
    profile_name: str,
    payload: dict[str, object],
    current_cross_talk: float,
    current_min_coverage: float,
) -> dict[str, object]:
    pitch = payload["pitch_drift"]
    timing = payload["local_timing_warp"]
    geometry = payload["path_geometry"]

    checks = {
        "non_current_profile": profile_name != CURRENT_PROFILE.name,
        "strictly_lower_pitch_to_timing_cross_talk": (
            float(pitch["timing_cross_talk_max_abs_delta"])
            < current_cross_talk - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        ),
        "local_timing_directional_sensitivity_pass": (
            timing["timing_directional_sensitivity"] == "PASS"
        ),
        "local_timing_monotonicity_pass": timing["timing_monotonicity"] == "PASS",
        "pitch_directional_sensitivity_pass": (
            pitch["pitch_directional_sensitivity"] == "PASS"
        ),
        "pitch_monotonicity_pass": pitch["pitch_monotonicity"] == "PASS",
        "minimum_coverage_preserved": (
            float(geometry["min_coverage_ratio"])
            >= current_min_coverage - ALIGNMENT_SUBSTRATE_ABLATION_EPSILON
        ),
    }
    return {
        "meets": all(checks.values()),
        "checks": checks,
    }


def _ordered_family(
    conditions: list[AlignmentAblationCondition],
) -> tuple[AlignmentAblationCondition, ...]:
    return tuple(
        sorted(
            conditions,
            key=lambda item: item.case.condition.intervention.strength,
        )
    )


def _feature_vector(
    bundle: FeatureBundle,
    index: int,
) -> tuple[float, float, float, float]:
    pitch = bundle.pitch_contour_hz[index]
    voiced = 1.0 if bundle.voiced_mask[index] else 0.0
    normalized_pitch = 0.0
    if pitch > 0.0 and math.isfinite(pitch):
        normalized_pitch = min(1.0, pitch / 500.0)
    return (
        normalized_pitch,
        min(1.0, max(0.0, bundle.energy_curve[index])),
        min(1.0, max(0.0, bundle.zero_crossing_rate[index] * 4.0)),
        voiced,
    )


def _profile_distance(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
    *,
    row: int,
    col: int,
    rows: int,
    cols: int,
    profile: AlignmentCostProfile,
) -> float:
    pitch_diff = abs(left[0] - right[0])
    energy_diff = abs(left[1] - right[1])
    zcr_diff = abs(left[2] - right[2])
    voiced_penalty = (
        profile.voiced_mismatch_penalty
        if left[3] != right[3]
        else 0.0
    )
    ref_position = row / float(max(1, rows - 1))
    take_position = col / float(max(1, cols - 1))
    position_penalty = profile.position_penalty_weight * abs(
        ref_position - take_position
    )
    return (
        pitch_diff * profile.pitch_weight
        + energy_diff * profile.energy_weight
        + zcr_diff * profile.zcr_weight
        + voiced_penalty
        + position_penalty
    )


def _score_map(component_scores: tuple[ComponentScore, ...]) -> dict[str, float]:
    return {
        score.name.value: float(score.score)
        for score in component_scores
    }


def _max_abs_delta_from_control(values: list[float]) -> float:
    control = values[0]
    return max(abs(value - control) for value in values)


def _directional_sensitivity_verdict(values: list[float]) -> str:
    endpoint_delta = values[-1] - values[0]
    if endpoint_delta < -ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
        return "PASS"
    if endpoint_delta > ALIGNMENT_SUBSTRATE_ABLATION_EPSILON:
        return "FAIL"
    return "UNRESOLVED"


def _nonincreasing_monotonicity_verdict(values: list[float]) -> str:
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
