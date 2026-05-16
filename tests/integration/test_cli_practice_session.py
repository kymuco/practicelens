import json
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


def test_cli_practice_session_command_writes_session_outputs(tmp_path: Path, capsys) -> None:
    reference = tmp_path / "reference.wav"
    take_a = tmp_path / "take_a.wav"
    take_b = tmp_path / "take_b.wav"
    out_dir = tmp_path / "practice-session-out"

    _write_wav(reference, 220.0)
    _write_wav(take_a, 220.0)
    _write_wav(take_b, 246.94)

    exit_code = run(
        [
            "practice-session",
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

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Best take:" in captured.out
    assert "best_take:" in captured.out
    assert "weakest_take:" in captured.out
    assert "recurring_weakness:" in captured.out
    assert "next_recording_target:" in captured.out
    assert "practice_plan:" in captured.out
    assert (out_dir / "batch_report.json").exists()
    assert (out_dir / "batch_report.md").exists()
    assert (out_dir / "practice_plan.md").exists()
    assert (out_dir / "session_manifest.json").exists()
    assert (out_dir / "takes").exists()


def test_cli_practice_session_command_can_append_history_index(tmp_path: Path, capsys) -> None:
    reference = tmp_path / "reference.wav"
    take_a = tmp_path / "take_a.wav"
    take_b = tmp_path / "take_b.wav"
    out_dir = tmp_path / "practice-session-out"
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"

    _write_wav(reference, 220.0)
    _write_wav(take_a, 220.0)
    _write_wav(take_b, 246.94)

    exit_code = run(
        [
            "practice-session",
            "--reference",
            str(reference),
            "--take",
            str(take_a),
            "--take",
            str(take_b),
            "--out",
            str(out_dir),
            "--history-index",
            str(history_index),
            "--frame-length",
            "1024",
            "--hop-length",
            "256",
            "--segment-duration",
            "2.0",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"history_index: {history_index}" in captured.out
    assert history_index.exists()

    lines = history_index.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["kind"] == "practice_session_index_entry"
    assert entry["schema_version"] == 1
    assert entry["session_dir"] == str(out_dir)
    assert entry["manifest_path"].endswith("session_manifest.json")
    assert entry["reference_path"] == str(reference)
    assert entry["compared_takes"] == 2
    assert entry["best_take"]
    assert entry["best_score"] is not None
    assert entry["weakest_take"]
    assert entry["weakest_score"] is not None
    assert entry["recurring_weakness"]
    assert entry["strongest_stable_area"]
    assert entry["next_recording_target"]
