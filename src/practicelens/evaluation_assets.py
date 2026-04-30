from __future__ import annotations

import json
import math
import wave
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_OUT_DIR = Path("examples/evaluation_assets/generated")
REFERENCE_CASE = "reference_phrase"


@dataclass(slots=True, frozen=True)
class EvaluationCaseSpec:
    """One deterministic synthetic audio case for evaluation and demos."""

    name: str
    filename: str
    role: str
    expected_strength: str
    expected_weakness: str
    description: str


CASE_SPECS: tuple[EvaluationCaseSpec, ...] = (
    EvaluationCaseSpec(
        name=REFERENCE_CASE,
        filename="reference_phrase.wav",
        role="reference",
        expected_strength="baseline",
        expected_weakness="none",
        description="Clean monophonic reference phrase with simple note changes and phrase-level dynamics.",
    ),
    EvaluationCaseSpec(
        name="exact_take",
        filename="exact_take.wav",
        role="take",
        expected_strength="pitch_fidelity",
        expected_weakness="none",
        description="Near-exact copy of the reference phrase used as the high-score control case.",
    ),
    EvaluationCaseSpec(
        name="pitch_drift_take",
        filename="pitch_drift_take.wav",
        role="take",
        expected_strength="timing_consistency",
        expected_weakness="pitch_fidelity",
        description="The phrase follows the reference timing but drifts upward in pitch over the take.",
    ),
    EvaluationCaseSpec(
        name="timing_drift_take",
        filename="timing_drift_take.wav",
        role="take",
        expected_strength="pitch_fidelity",
        expected_weakness="timing_consistency",
        description="The phrase keeps the same notes but gradually stretches timing against the reference.",
    ),
    EvaluationCaseSpec(
        name="rhythm_mistake_take",
        filename="rhythm_mistake_take.wav",
        role="take",
        expected_strength="pitch_fidelity",
        expected_weakness="rhythm_fidelity",
        description="The phrase keeps pitch mostly intact but drops and shifts attacks in the middle.",
    ),
    EvaluationCaseSpec(
        name="noisy_take",
        filename="noisy_take.wav",
        role="take",
        expected_strength="timing_consistency",
        expected_weakness="pitch_fidelity",
        description="The reference phrase with deterministic broadband-like noise mixed in.",
    ),
    EvaluationCaseSpec(
        name="silence_mismatch_take",
        filename="silence_mismatch_take.wav",
        role="take",
        expected_strength="section_stability",
        expected_weakness="rhythm_fidelity",
        description="The phrase contains an inserted silent gap that should disturb local evidence.",
    ),
    EvaluationCaseSpec(
        name="vibrato_take",
        filename="vibrato_take.wav",
        role="take",
        expected_strength="rhythm_fidelity",
        expected_weakness="pitch_fidelity",
        description="The phrase adds a strong deterministic vibrato-like modulation to sustained notes.",
    ),
    EvaluationCaseSpec(
        name="pluck_take",
        filename="pluck_take.wav",
        role="take",
        expected_strength="rhythm_fidelity",
        expected_weakness="section_stability",
        description="A guitar-like plucked envelope version of the same phrase, useful for instrument-like smoke coverage.",
    ),
    EvaluationCaseSpec(
        name="tempo_mismatch_take",
        filename="tempo_mismatch_take.wav",
        role="take",
        expected_strength="pitch_fidelity",
        expected_weakness="timing_consistency",
        description="The phrase is rendered faster than the reference and padded back to a comparable duration.",
    ),
)

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


def generate_evaluation_assets(
    out_dir: Path = DEFAULT_OUT_DIR,
    *,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> dict[str, Path]:
    """Generate deterministic synthetic evaluation WAV files plus a manifest."""

    out_dir.mkdir(parents=True, exist_ok=True)
    reference = _phrase_samples(sample_rate=sample_rate)
    assets: dict[str, list[float]] = {
        REFERENCE_CASE: reference,
        "exact_take": list(reference),
        "pitch_drift_take": _phrase_samples(sample_rate=sample_rate, pitch_ramp=0.09),
        "timing_drift_take": _stretch_to_length(_phrase_samples(sample_rate=sample_rate, duration_scale=1.12), len(reference)),
        "rhythm_mistake_take": _with_muted_window(_phrase_samples(sample_rate=sample_rate), sample_rate, 1.25, 1.55),
        "noisy_take": _with_noise(reference, amount=0.08),
        "silence_mismatch_take": _with_inserted_silence(reference, sample_rate, start_s=1.8, duration_s=0.22),
        "vibrato_take": _phrase_samples(sample_rate=sample_rate, vibrato_depth=0.035),
        "pluck_take": _phrase_samples(sample_rate=sample_rate, envelope="pluck"),
        "tempo_mismatch_take": _stretch_to_length(_phrase_samples(sample_rate=sample_rate, duration_scale=0.86), len(reference)),
    }

    paths: dict[str, Path] = {}
    for spec in CASE_SPECS:
        path = out_dir / spec.filename
        _write_wav(path, assets[spec.name], sample_rate=sample_rate)
        paths[spec.name] = path

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sample_rate": sample_rate,
                "reference_case": REFERENCE_CASE,
                "cases": [
                    {
                        "name": spec.name,
                        "filename": spec.filename,
                        "path": str(paths[spec.name]),
                        "role": spec.role,
                        "expected_strength": spec.expected_strength,
                        "expected_weakness": spec.expected_weakness,
                        "description": spec.description,
                    }
                    for spec in CASE_SPECS
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    paths["manifest"] = manifest_path
    return paths


def _phrase_samples(
    *,
    sample_rate: int,
    duration_scale: float = 1.0,
    pitch_ramp: float = 0.0,
    vibrato_depth: float = 0.0,
    envelope: str = "phrase",
) -> list[float]:
    samples: list[float] = []
    total_duration = sum(duration for _, duration in _NOTE_PLAN) * duration_scale
    elapsed_s = 0.0
    for note_index, (base_freq, duration_s) in enumerate(_NOTE_PLAN):
        scaled_duration = duration_s * duration_scale
        frame_count = max(1, int(round(scaled_duration * sample_rate)))
        for index in range(frame_count):
            local_t = index / sample_rate
            global_t = elapsed_s + local_t
            progress = min(1.0, global_t / max(total_duration, 1e-9))
            freq = base_freq * (1.0 + pitch_ramp * progress)
            if vibrato_depth:
                freq *= 1.0 + vibrato_depth * math.sin(2.0 * math.pi * 5.8 * local_t)
            amp = _amplitude(index, frame_count, note_index=note_index, envelope=envelope)
            samples.append(math.sin(2.0 * math.pi * freq * local_t) * amp)
        elapsed_s += scaled_duration
    return samples


def _amplitude(index: int, frame_count: int, *, note_index: int, envelope: str) -> float:
    progress = index / max(frame_count - 1, 1)
    attack = min(1.0, progress / 0.08)
    release = min(1.0, (1.0 - progress) / 0.12)
    phrase_shape = 0.75 + 0.12 * math.sin(note_index * 0.9)
    if envelope == "pluck":
        return max(0.0, min(0.95, math.exp(-progress * 4.5) * attack * 0.95))
    return max(0.0, min(0.95, attack * release * phrase_shape))


def _stretch_to_length(samples: list[float], target_length: int) -> list[float]:
    if not samples:
        return [0.0] * target_length
    if target_length <= 1:
        return [samples[0]]
    stretched: list[float] = []
    for index in range(target_length):
        source_position = index * (len(samples) - 1) / max(target_length - 1, 1)
        left_index = int(math.floor(source_position))
        right_index = min(len(samples) - 1, left_index + 1)
        fraction = source_position - left_index
        stretched.append(samples[left_index] * (1.0 - fraction) + samples[right_index] * fraction)
    return stretched


def _with_noise(samples: list[float], *, amount: float) -> list[float]:
    noisy: list[float] = []
    for index, sample in enumerate(samples):
        deterministic_noise = math.sin(index * 12.9898) * math.sin(index * 78.233)
        noisy.append(_clamp_sample(sample + deterministic_noise * amount))
    return noisy


def _with_muted_window(samples: list[float], sample_rate: int, start_s: float, end_s: float) -> list[float]:
    start = max(0, int(start_s * sample_rate))
    end = min(len(samples), int(end_s * sample_rate))
    return [sample if index < start or index >= end else sample * 0.08 for index, sample in enumerate(samples)]


def _with_inserted_silence(samples: list[float], sample_rate: int, *, start_s: float, duration_s: float) -> list[float]:
    start = max(0, min(len(samples), int(start_s * sample_rate)))
    silence = [0.0] * max(1, int(duration_s * sample_rate))
    inserted = samples[:start] + silence + samples[start:]
    return inserted[: len(samples)]


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


def _clamp_sample(value: float) -> float:
    return max(-1.0, min(1.0, value))
