import json
import math
import wave
from pathlib import Path

from practicelens.cli.main import run


def test_cli_progress_tracking_golden_path_contract(tmp_path: Path, capsys) -> None:
    reference = tmp_path / "reference.wav"
    session_a_take_1 = tmp_path / "session-a-take-1.wav"
    session_a_take_2 = tmp_path / "session-a-take-2.wav"
    session_b_take_1 = tmp_path / "session-b-take-1.wav"
    session_b_take_2 = tmp_path / "session-b-take-2.wav"
    session_a_dir = tmp_path / "session-a"
    session_b_dir = tmp_path / "session-b"
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"

    _write_wav(reference, 220.0)
    _write_wav(session_a_take_1, 246.94)
    _write_wav(session_a_take_2, 233.08)
    _write_wav(session_b_take_1, 220.0)
    _write_wav(session_b_take_2, 224.0)

    assert _run_practice_session(
        reference=reference,
        takes=(session_a_take_1, session_a_take_2),
        out_dir=session_a_dir,
        history_index=history_index,
    ) == 0
    session_a_output = capsys.readouterr()
    assert f"history_index: {history_index}" in session_a_output.out

    assert _run_practice_session(
        reference=reference,
        takes=(session_b_take_1, session_b_take_2),
        out_dir=session_b_dir,
        history_index=history_index,
    ) == 0
    session_b_output = capsys.readouterr()
    assert f"history_index: {history_index}" in session_b_output.out

    history_entries = [json.loads(line) for line in history_index.read_text(encoding="utf-8").splitlines()]
    assert len(history_entries) == 2
    assert history_entries[0]["session_dir"] == str(session_a_dir)
    assert history_entries[1]["session_dir"] == str(session_b_dir)
    assert history_entries[0]["manifest_path"] == str(session_a_dir / "session_manifest.json")
    assert history_entries[1]["manifest_path"] == str(session_b_dir / "session_manifest.json")

    assert run(["sessions", "list", "--history-index", str(history_index), "--limit", "2"]) == 0
    sessions_list_output = capsys.readouterr()
    assert sessions_list_output.out.startswith("1  ")
    assert f"  {session_a_dir}  " in sessions_list_output.out
    assert f"\n2  " in sessions_list_output.out
    assert f"  {session_b_dir}  " in sessions_list_output.out
    assert "best=" in sessions_list_output.out
    assert "score=" in sessions_list_output.out
    assert "focus=" in sessions_list_output.out

    assert run(["sessions", "show", "1", "--history-index", str(history_index)]) == 0
    sessions_show_output = capsys.readouterr()
    assert f"Session manifest: {session_a_dir / 'session_manifest.json'}" in sessions_show_output.out
    assert "Best take:" in sessions_show_output.out
    assert "Weakest take:" in sessions_show_output.out
    assert "Recurring weakness:" in sessions_show_output.out
    assert "Next recording target:" in sessions_show_output.out
    assert f"Practice plan: {session_a_dir / 'practice_plan.md'}" in sessions_show_output.out
    assert f"Batch report: {session_a_dir / 'batch_report.md'}" in sessions_show_output.out

    assert run(["sessions", "compare", "1", "2", "--history-index", str(history_index)]) == 0
    sessions_compare_output = capsys.readouterr()
    assert "Overall score:" in sessions_compare_output.out
    assert "Recurring weakness:" in sessions_compare_output.out
    assert "Best take:" in sessions_compare_output.out
    assert "Stable area:" in sessions_compare_output.out


def _run_practice_session(
    *,
    reference: Path,
    takes: tuple[Path, ...],
    out_dir: Path,
    history_index: Path,
) -> int:
    args = [
        "practice-session",
        "--reference",
        str(reference),
    ]
    for take in takes:
        args.extend(["--take", str(take)])
    args.extend(
        [
            "--out",
            str(out_dir),
            "--history-index",
            str(history_index),
            "--frame-length",
            "1024",
            "--hop-length",
            "256",
            "--segment-duration",
            "1.0",
        ]
    )
    return run(args)


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
