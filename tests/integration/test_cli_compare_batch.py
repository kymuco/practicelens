import math
import wave
from pathlib import Path

from practicelens.cli.main import run


def _write_wav(path: Path, freq_hz: float, *, sample_rate: int = 16_000, duration_samples: int = 8000) -> None:
    ints = [
        max(-32767, min(32767, int(math.sin(2.0 * math.pi * freq_hz * index / sample_rate) * 32767)))
        for index in range(duration_samples)
    ]
    frames = bytearray()
    for value in ints:
        frames.extend(int(value).to_bytes(2, byteorder="little", signed=True))
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


def test_cli_compare_batch_command_writes_batch_reports(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_a = tmp_path / "take_a.wav"
    take_b = tmp_path / "take_b.wav"
    out_dir = tmp_path / "batch-cli-out"

    _write_wav(reference, 220.0)
    _write_wav(take_a, 220.0)
    _write_wav(take_b, 246.94)

    exit_code = run(
        [
            "compare-batch",
            "--reference",
            str(reference),
            "--take",
            str(take_a),
            "--take",
            str(take_b),
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
    assert (out_dir / "batch_report.json").exists()
    assert (out_dir / "batch_report.md").exists()
    assert (out_dir / "batch_report.csv").exists()
    assert (out_dir / "batch_report.svg").exists()
