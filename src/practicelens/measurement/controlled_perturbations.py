from __future__ import annotations

import hashlib
import json
import math
import wave
from dataclasses import dataclass
from pathlib import Path

from practicelens.measurement.contracts import (
    ExperimentCondition,
    InterventionParameter,
    InterventionRole,
    InterventionSpec,
)

CONTROLLED_PERTURBATION_SCHEMA_VERSION = 1
CONTROLLED_PERTURBATION_GENERATOR_VERSION = "1"
DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_OUT_DIR = Path("examples/measurement/controlled_v1")

_NOTE_PLAN: tuple[tuple[float, float], ...] = (
    (220.00, 0.45),
    (246.94, 0.35),
    (261.63, 0.50),
    (293.66, 0.40),
    (329.63, 0.55),
    (293.66, 0.35),
    (261.63, 0.50),
    (246.94, 0.35),
    (220.00, 0.65),
)

_GAIN_DB_MAGNITUDES = (0.0, 3.0, 6.0, 12.0)
_NOISE_AMOUNTS = (0.0, 0.01, 0.03, 0.06)
_PITCH_DRIFT_FRACTIONS = (0.0, 0.01, 0.03, 0.06)
_LOCAL_TIMING_WARP_MS = (0.0, 20.0, 40.0, 80.0)


@dataclass(slots=True, frozen=True)
class ControlledPerturbationCase:
    """One generated controlled condition and its audio artifact."""

    condition: ExperimentCondition
    path: Path
    sha256: str


@dataclass(slots=True, frozen=True)
class ControlledPerturbationHarnessResult:
    """Output locations and generated conditions for controlled perturbation v1."""

    out_dir: Path
    reference_path: Path
    reference_sha256: str
    manifest_path: Path
    cases: tuple[ControlledPerturbationCase, ...]


def generate_controlled_perturbation_harness(
    out_dir: Path = DEFAULT_OUT_DIR,
    *,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> ControlledPerturbationHarnessResult:
    """Generate deterministic one-factor-at-a-time perturbation families."""

    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")

    out_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = out_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    reference = _canonical_phrase_samples(sample_rate=sample_rate)
    reference_path = out_dir / "reference.wav"
    _write_wav(reference_path, reference, sample_rate=sample_rate)
    reference_sha256 = _sha256_file(reference_path)

    generated: list[ControlledPerturbationCase] = []
    generated.extend(
        _generate_gain_family(
            cases_dir=cases_dir,
            reference=reference,
            reference_sha256=reference_sha256,
            sample_rate=sample_rate,
        )
    )
    generated.extend(
        _generate_noise_family(
            cases_dir=cases_dir,
            reference=reference,
            reference_sha256=reference_sha256,
            sample_rate=sample_rate,
        )
    )
    generated.extend(
        _generate_pitch_drift_family(
            cases_dir=cases_dir,
            reference_sha256=reference_sha256,
            sample_rate=sample_rate,
        )
    )
    generated.extend(
        _generate_local_timing_warp_family(
            cases_dir=cases_dir,
            reference=reference,
            reference_sha256=reference_sha256,
            sample_rate=sample_rate,
        )
    )

    result = ControlledPerturbationHarnessResult(
        out_dir=out_dir,
        reference_path=reference_path,
        reference_sha256=reference_sha256,
        manifest_path=out_dir / "manifest.json",
        cases=tuple(generated),
    )
    result.manifest_path.write_text(
        json.dumps(
            controlled_perturbation_manifest_payload(result, sample_rate=sample_rate),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return result


def controlled_perturbation_manifest_payload(
    result: ControlledPerturbationHarnessResult,
    *,
    sample_rate: int,
) -> dict[str, object]:
    """Return the canonical machine-readable controlled-harness manifest."""

    return {
        "kind": "controlled_perturbation_manifest",
        "schema_version": CONTROLLED_PERTURBATION_SCHEMA_VERSION,
        "generator_version": CONTROLLED_PERTURBATION_GENERATOR_VERSION,
        "sample_rate": sample_rate,
        "reference": {
            "case_id": "reference_phrase",
            "path": str(result.reference_path),
            "sha256": result.reference_sha256,
        },
        "cases": [
            {
                "condition": _condition_payload(case.condition),
                "path": str(case.path),
                "sha256": case.sha256,
            }
            for case in result.cases
        ],
    }


def _generate_gain_family(
    *,
    cases_dir: Path,
    reference: list[float],
    reference_sha256: str,
    sample_rate: int,
) -> list[ControlledPerturbationCase]:
    cases: list[ControlledPerturbationCase] = []
    for magnitude_db in _GAIN_DB_MAGNITUDES:
        role = InterventionRole.CONTROL if magnitude_db == 0.0 else InterventionRole.NUISANCE
        gain_db = -magnitude_db
        samples = list(reference) if magnitude_db == 0.0 else _apply_gain_db(reference, gain_db)
        cases.append(
            _write_case(
                cases_dir=cases_dir,
                family="amplitude_gain",
                strength=magnitude_db,
                unit="db_magnitude",
                role=role,
                samples=samples,
                sample_rate=sample_rate,
                reference_sha256=reference_sha256,
                parameters=(
                    InterventionParameter(name="gain_db", value=gain_db, unit="db"),
                ),
            )
        )
    return cases


def _generate_noise_family(
    *,
    cases_dir: Path,
    reference: list[float],
    reference_sha256: str,
    sample_rate: int,
) -> list[ControlledPerturbationCase]:
    cases: list[ControlledPerturbationCase] = []
    for amount in _NOISE_AMOUNTS:
        role = InterventionRole.CONTROL if amount == 0.0 else InterventionRole.NUISANCE
        samples = list(reference) if amount == 0.0 else _with_deterministic_noise(reference, amount=amount)
        cases.append(
            _write_case(
                cases_dir=cases_dir,
                family="broadband_noise",
                strength=amount,
                unit="full_scale_fraction",
                role=role,
                samples=samples,
                sample_rate=sample_rate,
                reference_sha256=reference_sha256,
            )
        )
    return cases


def _generate_pitch_drift_family(
    *,
    cases_dir: Path,
    reference_sha256: str,
    sample_rate: int,
) -> list[ControlledPerturbationCase]:
    cases: list[ControlledPerturbationCase] = []
    for fraction in _PITCH_DRIFT_FRACTIONS:
        role = InterventionRole.CONTROL if fraction == 0.0 else InterventionRole.TARGET
        samples = _canonical_phrase_samples(sample_rate=sample_rate, pitch_drift_fraction=fraction)
        cases.append(
            _write_case(
                cases_dir=cases_dir,
                family="pitch_drift",
                strength=fraction,
                unit="terminal_fraction",
                role=role,
                samples=samples,
                sample_rate=sample_rate,
                reference_sha256=reference_sha256,
                parameters=(
                    InterventionParameter(name="curve", value="linear"),
                ),
            )
        )
    return cases


def _generate_local_timing_warp_family(
    *,
    cases_dir: Path,
    reference: list[float],
    reference_sha256: str,
    sample_rate: int,
) -> list[ControlledPerturbationCase]:
    cases: list[ControlledPerturbationCase] = []
    window_start_s = 1.20
    window_end_s = 2.80
    for max_shift_ms in _LOCAL_TIMING_WARP_MS:
        role = InterventionRole.CONTROL if max_shift_ms == 0.0 else InterventionRole.TARGET
        samples = (
            list(reference)
            if max_shift_ms == 0.0
            else _with_local_timing_warp(
                reference,
                sample_rate=sample_rate,
                window_start_s=window_start_s,
                window_end_s=window_end_s,
                max_shift_ms=max_shift_ms,
            )
        )
        cases.append(
            _write_case(
                cases_dir=cases_dir,
                family="local_timing_warp",
                strength=max_shift_ms,
                unit="ms_max_shift",
                role=role,
                samples=samples,
                sample_rate=sample_rate,
                reference_sha256=reference_sha256,
                parameters=(
                    InterventionParameter(name="window_start_s", value=window_start_s, unit="s"),
                    InterventionParameter(name="window_end_s", value=window_end_s, unit="s"),
                    InterventionParameter(name="curve", value="sine"),
                ),
            )
        )
    return cases


def _write_case(
    *,
    cases_dir: Path,
    family: str,
    strength: float,
    unit: str,
    role: InterventionRole,
    samples: list[float],
    sample_rate: int,
    reference_sha256: str,
    parameters: tuple[InterventionParameter, ...] = (),
) -> ControlledPerturbationCase:
    strength_token = _strength_token(strength)
    condition_id = f"{family}__{strength_token}"
    family_dir = cases_dir / family
    family_dir.mkdir(parents=True, exist_ok=True)
    path = family_dir / f"{strength_token}.wav"
    _write_wav(path, samples, sample_rate=sample_rate)
    sha256 = _sha256_file(path)

    condition = ExperimentCondition(
        condition_id=condition_id,
        reference_case="reference_phrase",
        take_case=condition_id,
        intervention=InterventionSpec(
            family=family,
            role=role,
            strength=strength,
            unit=unit,
            parameters=(
                InterventionParameter(
                    name="reference_sha256",
                    value=reference_sha256,
                ),
                *parameters,
            ),
        ),
    )
    return ControlledPerturbationCase(
        condition=condition,
        path=path,
        sha256=sha256,
    )


def _canonical_phrase_samples(
    *,
    sample_rate: int,
    pitch_drift_fraction: float = 0.0,
) -> list[float]:
    samples: list[float] = []
    total_duration = sum(duration for _, duration in _NOTE_PLAN)
    elapsed_s = 0.0
    phase = 0.0

    for note_index, (base_frequency, duration_s) in enumerate(_NOTE_PLAN):
        frame_count = max(1, int(round(duration_s * sample_rate)))
        for index in range(frame_count):
            local_t = index / sample_rate
            global_t = elapsed_s + local_t
            progress = min(1.0, global_t / max(total_duration, 1e-12))
            frequency = base_frequency * (1.0 + pitch_drift_fraction * progress)
            phase += 2.0 * math.pi * frequency / sample_rate
            amplitude = _phrase_amplitude(index, frame_count, note_index=note_index)
            samples.append(math.sin(phase) * amplitude)
        elapsed_s += duration_s
    return samples


def _phrase_amplitude(index: int, frame_count: int, *, note_index: int) -> float:
    progress = index / max(frame_count - 1, 1)
    attack = min(1.0, progress / 0.08)
    release = min(1.0, (1.0 - progress) / 0.12)
    phrase_shape = 0.75 + 0.12 * math.sin(note_index * 0.9)
    return max(0.0, min(0.95, attack * release * phrase_shape))


def _apply_gain_db(samples: list[float], gain_db: float) -> list[float]:
    scale = 10.0 ** (gain_db / 20.0)
    return [_clamp_sample(sample * scale) for sample in samples]


def _with_deterministic_noise(samples: list[float], *, amount: float) -> list[float]:
    noisy: list[float] = []
    for index, sample in enumerate(samples):
        noise = math.sin(index * 12.9898) * math.sin(index * 78.233)
        noisy.append(_clamp_sample(sample + noise * amount))
    return noisy


def _with_local_timing_warp(
    samples: list[float],
    *,
    sample_rate: int,
    window_start_s: float,
    window_end_s: float,
    max_shift_ms: float,
) -> list[float]:
    start = max(0, int(round(window_start_s * sample_rate)))
    end = min(len(samples) - 1, int(round(window_end_s * sample_rate)))
    if end <= start:
        raise ValueError("timing warp window must contain at least two samples")

    max_shift_samples = max_shift_ms * sample_rate / 1_000.0
    warped: list[float] = []
    for output_index in range(len(samples)):
        if output_index <= start or output_index >= end:
            source_position = float(output_index)
        else:
            progress = (output_index - start) / (end - start)
            shift = max_shift_samples * math.sin(math.pi * progress)
            source_position = min(float(end), max(float(start), output_index + shift))
        warped.append(_sample_linear(samples, source_position))
    return warped


def _sample_linear(samples: list[float], position: float) -> float:
    left = int(math.floor(position))
    right = min(len(samples) - 1, left + 1)
    fraction = position - left
    return samples[left] * (1.0 - fraction) + samples[right] * fraction


def _write_wav(path: Path, samples: list[float], *, sample_rate: int) -> None:
    ints = [max(-32767, min(32767, int(_clamp_sample(sample) * 32767))) for sample in samples]
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


def _strength_token(strength: float) -> str:
    if strength == 0.0:
        return "0"
    return f"{strength:.6g}".replace("-", "m").replace(".", "p")


def _condition_payload(condition: ExperimentCondition) -> dict[str, object]:
    return {
        "condition_id": condition.condition_id,
        "reference_case": condition.reference_case,
        "take_case": condition.take_case,
        "intervention": {
            "family": condition.intervention.family,
            "role": condition.intervention.role.value,
            "strength": condition.intervention.strength,
            "unit": condition.intervention.unit,
            "parameters": [
                {
                    "name": parameter.name,
                    "value": parameter.value,
                    "unit": parameter.unit,
                }
                for parameter in condition.intervention.parameters
            ],
        },
    }


def _clamp_sample(value: float) -> float:
    return max(-1.0, min(1.0, value))
