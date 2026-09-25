from __future__ import annotations

import hashlib
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.measurement.baseline_audit import AUDITED_MEASUREMENTS

LOCAL_SESSION_REPEATABILITY_SCHEMA_VERSION = 1
LOCAL_SESSION_REPEATABILITY_PROTOCOL_VERSION = "1"
LOCAL_SESSION_REPEATABILITY_MIN_TAKES = 5
LOCAL_SESSION_REPEATABILITY_RECOMMENDED_TAKES = 8
LOCAL_SESSION_REPEATABILITY_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)


@dataclass(slots=True, frozen=True)
class LocalSessionTakeObservation:
    """One private local take reduced to compact measurement evidence."""

    take_id: str
    measurements: dict[str, float]
    confidence_level: str
    suitability_status: str
    alignment_coverage: float


@dataclass(slots=True, frozen=True)
class LocalSessionRepeatabilityResult:
    """Local R0.5b result without raw-audio paths in the exported payload."""

    summary_path: Path
    observations: tuple[LocalSessionTakeObservation, ...]
    summary: dict[str, object]


def run_local_session_repeatability(
    reference_path: Path,
    take_paths: tuple[Path, ...],
    *,
    out_path: Path,
    session_label: str | None = None,
    code_revision: str | None = None,
    config: AnalysisConfig = LOCAL_SESSION_REPEATABILITY_CONFIG,
) -> LocalSessionRepeatabilityResult:
    """Analyze independent within-session takes and write privacy-bounded evidence."""

    _validate_local_repeatability_sources(reference_path, take_paths)

    pipeline = OfflineReferenceAnalysisPipeline()
    observations: list[LocalSessionTakeObservation] = []
    for index, take_path in enumerate(take_paths, start=1):
        report = pipeline.analyze(
            AnalyzeRequest(
                reference_path=reference_path,
                take_path=take_path,
                config=config,
            )
        ).report
        score_map = report.score_map()
        observations.append(
            LocalSessionTakeObservation(
                take_id=f"take_{index:02d}",
                measurements={
                    measurement_name: float(score_map[measurement_name].score)
                    for measurement_name in AUDITED_MEASUREMENTS
                },
                confidence_level=report.analysis_confidence.level,
                suitability_status=report.input_suitability.status,
                alignment_coverage=float(report.input_suitability.alignment_coverage),
            )
        )

    summary = local_session_repeatability_payload(
        tuple(observations),
        session_label=session_label,
        code_revision=code_revision,
        config=config,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return LocalSessionRepeatabilityResult(
        summary_path=out_path,
        observations=tuple(observations),
        summary=summary,
    )


def local_session_repeatability_payload(
    observations: tuple[LocalSessionTakeObservation, ...],
    *,
    session_label: str | None,
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    """Build the R0.5b compact evidence payload from analyzed takes."""

    if len(observations) < LOCAL_SESSION_REPEATABILITY_MIN_TAKES:
        raise ValueError(
            "local session repeatability requires at least "
            f"{LOCAL_SESSION_REPEATABILITY_MIN_TAKES} independent takes"
        )

    stats = {
        measurement_name: _measurement_repeatability_stats(
            [observation.measurements[measurement_name] for observation in observations]
        )
        for measurement_name in AUDITED_MEASUREMENTS
    }

    suitability_counts: dict[str, int] = {}
    confidence_counts: dict[str, int] = {}
    for observation in observations:
        suitability_counts[observation.suitability_status] = (
            suitability_counts.get(observation.suitability_status, 0) + 1
        )
        confidence_counts[observation.confidence_level] = (
            confidence_counts.get(observation.confidence_level, 0) + 1
        )

    min_alignment_coverage = min(observation.alignment_coverage for observation in observations)
    quality_flags: list[str] = []
    if any(status != "ok" for status in suitability_counts):
        quality_flags.append("non_ok_input_suitability_present")
    if any(level == "low" for level in confidence_counts):
        quality_flags.append("low_analysis_confidence_present")
    if min_alignment_coverage < 0.85:
        quality_flags.append("alignment_coverage_below_0_85")

    return {
        "kind": "local_session_repeatability",
        "schema_version": LOCAL_SESSION_REPEATABILITY_SCHEMA_VERSION,
        "protocol_version": LOCAL_SESSION_REPEATABILITY_PROTOCOL_VERSION,
        "session_label": session_label,
        "code_revision": code_revision,
        "take_count": len(observations),
        "recommended_take_count": LOCAL_SESSION_REPEATABILITY_RECOMMENDED_TAKES,
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
        "takes": [
            {
                "take_id": observation.take_id,
                "measurements": observation.measurements,
                "confidence_level": observation.confidence_level,
                "suitability_status": observation.suitability_status,
                "alignment_coverage": observation.alignment_coverage,
            }
            for observation in observations
        ],
        "repeatability": stats,
        "quality_summary": {
            "suitability_counts": suitability_counts,
            "confidence_counts": confidence_counts,
            "min_alignment_coverage": min_alignment_coverage,
            "flags": quality_flags,
        },
        "privacy": {
            "audio_embedded": False,
            "source_paths_embedded": False,
            "source_fingerprints_embedded": False,
        },
        "interpretation_boundary": [
            "This artifact estimates one within-session sample of observed measurement variation.",
            "It is not a population-level human repeatability distribution.",
            "It does not prove that between-session score changes are skill changes.",
            "Multiple sessions are required before a longitudinal minimum detectable change is admitted.",
        ],
    }


def render_local_session_repeatability_text(summary: dict[str, object]) -> str:
    """Render a compact terminal summary without local file paths."""

    lines = [
        "PracticeLens R0.5b Local Session Repeatability v1",
        f"takes: {summary['take_count']}",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
    ]
    for name, stats in summary["repeatability"].items():
        lines.append(
            f"{name}: median={stats['median']:.3f} "
            f"MAD={stats['median_abs_deviation']:.3f} "
            f"pairwise_median={stats['median_pairwise_abs_delta']:.3f} "
            f"span={stats['observed_span']:.3f}"
        )
    flags = summary["quality_summary"]["flags"]
    if flags:
        lines.extend(("", "quality flags: " + ", ".join(flags)))
    return "\n".join(lines)


def _measurement_repeatability_stats(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("repeatability values must not be empty")

    median = float(statistics.median(values))
    deviations = [abs(value - median) for value in values]
    pairwise = [
        abs(values[left] - values[right])
        for left in range(len(values))
        for right in range(left + 1, len(values))
    ]
    return {
        "median": median,
        "minimum": float(min(values)),
        "maximum": float(max(values)),
        "observed_span": float(max(values) - min(values)),
        "median_abs_deviation": float(statistics.median(deviations)),
        "max_abs_deviation_from_median": float(max(deviations)),
        "median_pairwise_abs_delta": float(statistics.median(pairwise)),
        "max_pairwise_abs_delta": float(max(pairwise)),
    }


def _validate_local_repeatability_sources(
    reference_path: Path,
    take_paths: tuple[Path, ...],
) -> None:
    if len(take_paths) < LOCAL_SESSION_REPEATABILITY_MIN_TAKES:
        raise ValueError(
            "local session repeatability requires at least "
            f"{LOCAL_SESSION_REPEATABILITY_MIN_TAKES} independent takes"
        )
    if not reference_path.is_file():
        raise FileNotFoundError(f"reference WAV not found: {reference_path}")

    reference_digest = _sha256_file(reference_path)
    seen: dict[str, int] = {}
    for index, take_path in enumerate(take_paths, start=1):
        if not take_path.is_file():
            raise FileNotFoundError(f"take WAV not found: {take_path}")
        digest = _sha256_file(take_path)
        if digest == reference_digest:
            raise ValueError(
                f"take {index} is byte-identical to the reference; "
                "R0.5b requires independent performances"
            )
        if digest in seen:
            raise ValueError(
                f"take {index} duplicates take {seen[digest]}; "
                "R0.5b requires independent performances"
            )
        seen[digest] = index


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
