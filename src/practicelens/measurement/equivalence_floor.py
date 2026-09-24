from __future__ import annotations

import hashlib
import json
import math
import shutil
import wave
from dataclasses import dataclass
from pathlib import Path

from practicelens.application import AnalyzeRequest, OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.io import load_wav_audio
from practicelens.measurement.baseline_audit import AUDITED_MEASUREMENTS
from practicelens.measurement.controlled_perturbations import (
    generate_controlled_perturbation_harness,
)

SYNTHETIC_EQUIVALENCE_FLOOR_SCHEMA_VERSION = 1
SYNTHETIC_EQUIVALENCE_FLOOR_EXPERIMENT_ID = "r0.5a-synthetic-equivalence-floor-v1"
SYNTHETIC_EQUIVALENCE_CONFIG = AnalysisConfig(
    target_sample_rate=16_000,
    frame_length=1_024,
    hop_length=256,
    segment_duration_s=1.0,
)


@dataclass(slots=True, frozen=True)
class EquivalentRecordingCase:
    case_id: str
    family: str
    path: Path
    sha256: str
    parameters: tuple[tuple[str, str], ...] = ()


@dataclass(slots=True, frozen=True)
class SyntheticEquivalenceFloorResult:
    out_dir: Path
    source_reference_path: Path
    cases_dir: Path
    summary_path: Path
    cases: tuple[EquivalentRecordingCase, ...]
    summary: dict[str, object]


def generate_equivalent_recording_cases(
    out_dir: Path,
    *,
    sample_rate: int = 16_000,
) -> tuple[Path, tuple[EquivalentRecordingCase, ...]]:
    """Generate deterministic recordings intended to preserve performance semantics."""

    out_dir.mkdir(parents=True, exist_ok=True)
    source = generate_controlled_perturbation_harness(
        out_dir / "_r0_3_source",
        sample_rate=sample_rate,
    )
    reference_path = source.reference_path
    loaded = load_wav_audio(reference_path)
    samples = list(loaded.samples)

    cases_dir = out_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    cases: list[EquivalentRecordingCase] = []
    cases.append(
        _copy_case(
            reference_path,
            cases_dir / "exact_byte_copy.wav",
            case_id="exact_byte_copy",
            family="exact_copy",
        )
    )
    cases.append(
        _write_case(
            samples,
            cases_dir / "pcm_roundtrip.wav",
            sample_rate=sample_rate,
            case_id="pcm_roundtrip",
            family="pcm_roundtrip",
        )
    )
    cases.append(
        _write_case(
            [-sample for sample in samples],
            cases_dir / "polarity_inverted.wav",
            sample_rate=sample_rate,
            case_id="polarity_inverted",
            family="polarity",
        )
    )
    for magnitude_db in (6.0, 12.0):
        gain_db = -magnitude_db
        scale = 10.0 ** (gain_db / 20.0)
        cases.append(
            _write_case(
                [_clamp(sample * scale) for sample in samples],
                cases_dir / f"gain_minus_{int(magnitude_db)}db.wav",
                sample_rate=sample_rate,
                case_id=f"gain_minus_{int(magnitude_db)}db",
                family="gain",
                parameters=(("gain_db", f"{gain_db:.1f}"),),
            )
        )
    for offset in (-0.01, 0.01):
        token = "minus" if offset < 0.0 else "plus"
        cases.append(
            _write_case(
                [_clamp(sample + offset) for sample in samples],
                cases_dir / f"dc_offset_{token}_0p01.wav",
                sample_rate=sample_rate,
                case_id=f"dc_offset_{token}_0p01",
                family="dc_offset",
                parameters=(("offset_full_scale", f"{offset:.2f}"),),
            )
        )
    for padding_ms in (16, 64):
        padding = [0.0] * int(round(sample_rate * padding_ms / 1_000.0))
        cases.append(
            _write_case(
                [*padding, *samples],
                cases_dir / f"leading_silence_{padding_ms}ms.wav",
                sample_rate=sample_rate,
                case_id=f"leading_silence_{padding_ms}ms",
                family="recording_window",
                parameters=(("leading_silence_ms", str(padding_ms)),),
            )
        )
        cases.append(
            _write_case(
                [*samples, *padding],
                cases_dir / f"trailing_silence_{padding_ms}ms.wav",
                sample_rate=sample_rate,
                case_id=f"trailing_silence_{padding_ms}ms",
                family="recording_window",
                parameters=(("trailing_silence_ms", str(padding_ms)),),
            )
        )

    return reference_path, tuple(cases)


def run_synthetic_equivalence_floor(
    out_dir: Path,
    *,
    code_revision: str | None = None,
    repeat_count: int = 3,
    config: AnalysisConfig = SYNTHETIC_EQUIVALENCE_CONFIG,
) -> SyntheticEquivalenceFloorResult:
    """Measure exact rerun stability and tested equivalence variation."""

    if repeat_count < 2:
        raise ValueError("repeat_count must be at least 2")

    out_dir.mkdir(parents=True, exist_ok=True)
    reference_path, cases = generate_equivalent_recording_cases(
        out_dir,
        sample_rate=config.target_sample_rate,
    )

    repeat_values: list[dict[str, float]] = []
    for _ in range(repeat_count):
        pipeline = OfflineReferenceAnalysisPipeline()
        repeat_values.append(
            _score_values(
                pipeline,
                reference_path=reference_path,
                take_path=reference_path,
                config=config,
            )
        )

    baseline = repeat_values[0]
    case_values: dict[str, dict[str, float]] = {}
    case_deltas: dict[str, dict[str, float]] = {}

    pipeline = OfflineReferenceAnalysisPipeline()
    for case in cases:
        values = _score_values(
            pipeline,
            reference_path=reference_path,
            take_path=case.path,
            config=config,
        )
        case_values[case.case_id] = values
        case_deltas[case.case_id] = {
            name: values[name] - baseline[name]
            for name in AUDITED_MEASUREMENTS
        }

    summary = synthetic_equivalence_floor_payload(
        baseline=baseline,
        repeat_values=tuple(repeat_values),
        cases=cases,
        case_values=case_values,
        case_deltas=case_deltas,
        code_revision=code_revision,
        config=config,
    )
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return SyntheticEquivalenceFloorResult(
        out_dir=out_dir,
        source_reference_path=reference_path,
        cases_dir=out_dir / "cases",
        summary_path=summary_path,
        cases=cases,
        summary=summary,
    )


def synthetic_equivalence_floor_payload(
    *,
    baseline: dict[str, float],
    repeat_values: tuple[dict[str, float], ...],
    cases: tuple[EquivalentRecordingCase, ...],
    case_values: dict[str, dict[str, float]],
    case_deltas: dict[str, dict[str, float]],
    code_revision: str | None,
    config: AnalysisConfig,
) -> dict[str, object]:
    exact_repeat_floor = {
        name: max(abs(values[name] - baseline[name]) for values in repeat_values)
        for name in AUDITED_MEASUREMENTS
    }

    equivalence_floor: dict[str, float] = {}
    floor_source: dict[str, str] = {}
    for name in AUDITED_MEASUREMENTS:
        source_id, max_delta = max(
            (
                (case.case_id, abs(case_deltas[case.case_id][name]))
                for case in cases
            ),
            key=lambda item: item[1],
        )
        equivalence_floor[name] = max(max_delta, exact_repeat_floor[name])
        floor_source[name] = (
            "exact_repeat"
            if exact_repeat_floor[name] > max_delta
            else source_id
        )

    by_family: dict[str, dict[str, float]] = {}
    for case in cases:
        family_floor = by_family.setdefault(
            case.family,
            {name: 0.0 for name in AUDITED_MEASUREMENTS},
        )
        for name in AUDITED_MEASUREMENTS:
            family_floor[name] = max(
                family_floor[name],
                abs(case_deltas[case.case_id][name]),
            )

    return {
        "kind": "synthetic_equivalence_floor",
        "schema_version": SYNTHETIC_EQUIVALENCE_FLOOR_SCHEMA_VERSION,
        "experiment_id": SYNTHETIC_EQUIVALENCE_FLOOR_EXPERIMENT_ID,
        "code_revision": code_revision,
        "analysis_config": {
            "schema_version": int(config.schema_version),
            "target_sample_rate": config.target_sample_rate,
            "frame_length": config.frame_length,
            "hop_length": config.hop_length,
            "segment_duration_s": float(config.segment_duration_s),
        },
        "audited_measurements": list(AUDITED_MEASUREMENTS),
        "baseline_values": baseline,
        "repeat_values": list(repeat_values),
        "exact_repeat_floor": exact_repeat_floor,
        "cases": [
            {
                "case_id": case.case_id,
                "family": case.family,
                "sha256": case.sha256,
                "parameters": [
                    {"name": name, "value": value}
                    for name, value in case.parameters
                ],
                "values": case_values[case.case_id],
                "deltas_from_baseline": case_deltas[case.case_id],
            }
            for case in cases
        ],
        "family_max_abs_deltas": by_family,
        "tested_equivalence_floor": equivalence_floor,
        "tested_equivalence_floor_source": floor_source,
        "limitations": [
            "This is a deterministic synthetic equivalence floor, not a human repeatability estimate.",
            "The tested transformations preserve intended performance semantics but do not cover room, microphone, performer, or day-to-day variation.",
            "R0.5b remains necessary before longitudinal human-development thresholds are admitted.",
        ],
    }


def render_synthetic_equivalence_floor_text(summary: dict[str, object]) -> str:
    lines = [
        "PracticeLens R0.5a Synthetic Equivalence Floor v1",
        f"revision: {summary['code_revision'] or 'unknown'}",
        "",
        "exact repeat floor:",
    ]
    for name, value in summary["exact_repeat_floor"].items():
        lines.append(f"  {name}: {value:.6f}")
    lines.append("")
    lines.append("tested equivalence floor:")
    for name, value in summary["tested_equivalence_floor"].items():
        source = summary["tested_equivalence_floor_source"][name]
        lines.append(f"  {name}: {value:.6f} ({source})")
    return "\n".join(lines)


def _score_values(
    pipeline: OfflineReferenceAnalysisPipeline,
    *,
    reference_path: Path,
    take_path: Path,
    config: AnalysisConfig,
) -> dict[str, float]:
    report = pipeline.analyze(
        AnalyzeRequest(
            reference_path=reference_path,
            take_path=take_path,
            config=config,
        )
    ).report
    score_map = report.score_map()
    return {
        name: float(score_map[name].score)
        for name in AUDITED_MEASUREMENTS
    }


def _copy_case(
    source_path: Path,
    destination_path: Path,
    *,
    case_id: str,
    family: str,
) -> EquivalentRecordingCase:
    shutil.copyfile(source_path, destination_path)
    return EquivalentRecordingCase(
        case_id=case_id,
        family=family,
        path=destination_path,
        sha256=_sha256_file(destination_path),
    )


def _write_case(
    samples: list[float],
    path: Path,
    *,
    sample_rate: int,
    case_id: str,
    family: str,
    parameters: tuple[tuple[str, str], ...] = (),
) -> EquivalentRecordingCase:
    _write_wav(path, samples, sample_rate=sample_rate)
    return EquivalentRecordingCase(
        case_id=case_id,
        family=family,
        path=path,
        sha256=_sha256_file(path),
        parameters=parameters,
    )


def _write_wav(path: Path, samples: list[float], *, sample_rate: int) -> None:
    ints = [
        max(-32768, min(32767, int(round(_clamp(sample) * 32768))))
        for sample in samples
    ]
    frames = bytearray()
    for value in ints:
        frames.extend(value.to_bytes(2, byteorder="little", signed=True))

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clamp(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("equivalence sample must be finite")
    return max(-1.0, min(1.0, value))
