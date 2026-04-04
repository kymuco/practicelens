import math
import wave
from pathlib import Path

from practicelens.io import load_wav_audio
from practicelens.preprocessing import peak_normalize, resample_linear, trim_silence


def _write_wav(path: Path, samples: list[float], *, sample_rate: int = 16_000, channels: int = 1) -> None:
    ints = [max(-32767, min(32767, int(sample * 32767))) for sample in samples]
    frames = bytearray()
    for value in ints:
        chunk = int(value).to_bytes(2, byteorder="little", signed=True)
        if channels == 1:
            frames.extend(chunk)
        else:
            frames.extend(chunk * channels)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


def test_load_wav_audio_reads_mono_signal(tmp_path: Path) -> None:
    path = tmp_path / "mono.wav"
    samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(1600)]
    _write_wav(path, samples, channels=1)

    audio = load_wav_audio(path)

    assert audio.sample_rate == 16_000
    assert audio.source_channels == 1
    assert len(audio.samples) == 1600
    assert audio.duration_s > 0.09


def test_load_wav_audio_mixes_multichannel_to_mono(tmp_path: Path) -> None:
    path = tmp_path / "stereo.wav"
    samples = [0.25] * 64
    _write_wav(path, samples, channels=2)

    audio = load_wav_audio(path)

    assert audio.source_channels == 2
    assert len(audio.samples) == 64
    assert max(audio.samples) > 0.2


def test_preprocessing_helpers_stay_deterministic() -> None:
    normalized = peak_normalize((0.0, 0.5, -1.0, 0.25))
    trimmed = trim_silence((0.0, 0.0, 0.2, 0.1, 0.0), threshold=0.05)
    resampled = resample_linear((0.0, 1.0, 0.0), 3, 5)

    assert normalized == (0.0, 0.5, -1.0, 0.25)
    assert trimmed == (0.2, 0.1)
    assert len(resampled) == 5
    assert resampled[1] > 0.0
