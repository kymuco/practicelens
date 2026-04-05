import math
import wave
from pathlib import Path

from practicelens.cli.main import run


def _write_wav(path: Path, samples: list[float], *, sample_rate: int = 16_000) -> None:
    ints = [max(-32767, min(32767, int(sample * 32767))) for sample in samples]
    frames = bytearray()
    for value in ints:
        frames.extend(int(value).to_bytes(2, byteorder="little", signed=True))
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


def test_cli_analyze_command_writes_reports(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take = tmp_path / "take.wav"
    out_dir = tmp_path / "cli-out"

    reference_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    take_samples = [math.sin(2.0 * math.pi * 220.0 * index / 16_000.0) for index in range(8000)]
    _write_wav(reference, reference_samples)
    _write_wav(take, take_samples)

    exit_code = run(
        [
            "analyze",
            "--reference",
            str(reference),
            "--take",
            str(take),
            "--out",
            str(out_dir),
            "--frame-length",
            "1024",
            "--hop-length",
            "256",
            "--segment-duration",
            "2.0",
        ]
    )

    assert exit_code == 0
    assert (out_dir / "report.json").exists()
    assert (out_dir / "report.md").exists()
    assert (out_dir / "report.csv").exists()
    assert (out_dir / "report.svg").exists()
