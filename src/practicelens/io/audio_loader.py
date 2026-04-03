from __future__ import annotations

import math
import wave
from pathlib import Path

from practicelens.domain.errors import AudioLoadError
from practicelens.io.models import LoadedAudio


def load_wav_audio(path: str | Path) -> LoadedAudio:
    """Load a PCM WAV file as bounded mono float samples in [-1.0, 1.0]."""

    wav_path = Path(path)
    if not wav_path.exists():
        raise AudioLoadError(f"audio file does not exist: {wav_path}")

    try:
        with wave.open(str(wav_path), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            frame_count = wav_file.getnframes()
            raw_frames = wav_file.readframes(frame_count)
    except wave.Error as exc:
        raise AudioLoadError(f"failed to read wav file: {wav_path}") from exc

    if channels <= 0:
        raise AudioLoadError("wav file must have at least one channel")
    if sample_rate <= 0:
        raise AudioLoadError("wav file must have a positive sample rate")
    if sample_width not in (1, 2, 4):
        raise AudioLoadError(f"unsupported sample width: {sample_width}")

    samples = _pcm_bytes_to_floats(raw_frames, sample_width)
    if channels > 1:
        samples = _mix_to_mono(samples, channels)

    if not samples:
        raise AudioLoadError("wav file contains no audio samples")

    return LoadedAudio(
        samples=tuple(samples),
        sample_rate=sample_rate,
        source_channels=channels,
        sample_width_bytes=sample_width,
    )


def _pcm_bytes_to_floats(raw_frames: bytes, sample_width: int) -> list[float]:
    samples: list[float] = []

    if sample_width == 1:
        for value in raw_frames:
            samples.append((float(value) - 128.0) / 128.0)
        return samples

    signed = True
    scale = float(2 ** (8 * sample_width - 1))
    for index in range(0, len(raw_frames), sample_width):
        chunk = raw_frames[index : index + sample_width]
        if len(chunk) != sample_width:
            break
        integer = int.from_bytes(chunk, byteorder="little", signed=signed)
        samples.append(max(-1.0, min(1.0, integer / scale)))
    return samples


def _mix_to_mono(samples: list[float], channels: int) -> list[float]:
    mono: list[float] = []
    for index in range(0, len(samples), channels):
        frame = samples[index : index + channels]
        if len(frame) != channels:
            break
        mono.append(sum(frame) / float(channels))
    return mono


def ensure_finite_audio(audio: LoadedAudio) -> LoadedAudio:
    """Reject NaN or infinite sample payloads early."""

    if not audio.samples:
        raise AudioLoadError("audio sample payload is empty")
    if any(not math.isfinite(sample) for sample in audio.samples):
        raise AudioLoadError("audio samples must all be finite")
    return audio
