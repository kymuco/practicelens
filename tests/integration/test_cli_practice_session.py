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


def test_cli_sessions_list_reports_empty_history(tmp_path: Path, capsys) -> None:
    history_index = tmp_path / "missing-index.jsonl"

    exit_code = run(["sessions", "list", "--history-index", str(history_index)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == f"No practice sessions found in {history_index}.\n"


def test_cli_sessions_list_rejects_non_positive_limit(capsys) -> None:
    exit_code = run(["sessions", "list", "--limit", "0"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.err == "error: --limit must be greater than 0\n"


def test_cli_sessions_list_prints_indexed_sessions(tmp_path: Path, capsys) -> None:
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"
    _write_history_index(history_index)

    exit_code = run(["sessions", "list", "--history-index", str(history_index)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == (
        "1  2026-05-16  out/session-a  best=take_02.wav  score=88.4  focus=rhythm_fidelity\n"
        "2  2026-05-17  out/session-b  best=take_03.wav  score=90.1  focus=timing_consistency\n"
    )


def test_cli_sessions_list_can_limit_to_most_recent_sessions(tmp_path: Path, capsys) -> None:
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"
    _write_history_index(history_index)

    exit_code = run(["sessions", "list", "--history-index", str(history_index), "--limit", "1"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "2  2026-05-17  out/session-b  best=take_03.wav  score=90.1  focus=timing_consistency\n"


def test_cli_practice_session_history_can_be_listed(tmp_path: Path, capsys) -> None:
    reference = tmp_path / "reference.wav"
    take_a = tmp_path / "take_a.wav"
    take_b = tmp_path / "take_b.wav"
    out_dir = tmp_path / "practice-session-out"
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"

    _write_wav(reference, 220.0)
    _write_wav(take_a, 220.0)
    _write_wav(take_b, 246.94)

    session_exit_code = run(
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
    capsys.readouterr()

    list_exit_code = run(["sessions", "list", "--history-index", str(history_index)])
    captured = capsys.readouterr()

    assert session_exit_code == 0
    assert list_exit_code == 0
    assert captured.out.startswith("1  ")
    assert str(out_dir) in captured.out
    assert "best=" in captured.out
    assert "score=" in captured.out
    assert "focus=" in captured.out


def test_cli_sessions_show_can_read_session_directory(tmp_path: Path, capsys) -> None:
    out_dir = _run_practice_session_fixture(tmp_path, capsys)

    exit_code = run(["sessions", "show", str(out_dir)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"Session manifest: {out_dir / 'session_manifest.json'}" in captured.out
    assert "Best take:" in captured.out
    assert "Weakest take:" in captured.out
    assert "Recurring weakness:" in captured.out
    assert "Next recording target:" in captured.out
    assert f"Practice plan: {out_dir / 'practice_plan.md'}" in captured.out
    assert f"Batch report: {out_dir / 'batch_report.md'}" in captured.out


def test_cli_sessions_show_can_read_manifest_file(tmp_path: Path, capsys) -> None:
    out_dir = _run_practice_session_fixture(tmp_path, capsys)

    exit_code = run(["sessions", "show", str(out_dir / "session_manifest.json")])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"Session manifest: {out_dir / 'session_manifest.json'}" in captured.out
    assert "Best take:" in captured.out
    assert f"Practice plan: {out_dir / 'practice_plan.md'}" in captured.out
    assert f"Batch report: {out_dir / 'batch_report.md'}" in captured.out


def test_cli_sessions_show_can_resolve_history_id(tmp_path: Path, capsys) -> None:
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"
    out_dir = _run_practice_session_fixture(tmp_path, capsys, history_index=history_index)

    exit_code = run(["sessions", "show", "1", "--history-index", str(history_index)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"Session manifest: {out_dir / 'session_manifest.json'}" in captured.out
    assert "Best take:" in captured.out
    assert "Weakest take:" in captured.out
    assert "Recurring weakness:" in captured.out
    assert "Next recording target:" in captured.out


def test_cli_sessions_compare_can_read_manifest_files(tmp_path: Path, capsys) -> None:
    old_dir = tmp_path / "old-session"
    new_dir = tmp_path / "new-session"
    _write_manifest(old_dir, best_score=88.4, recurring_weakness="rhythm_fidelity")
    _write_manifest(new_dir, best_score=91.6, recurring_weakness="timing_consistency")

    exit_code = run(
        [
            "sessions",
            "compare",
            str(old_dir / "session_manifest.json"),
            str(new_dir / "session_manifest.json"),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == (
        "Overall score: +3.2\n"
        "Recurring weakness: rhythm_fidelity -> timing_consistency\n"
        "Best take: improved\n"
        "Stable area: preserved (section_stability)\n"
    )


def test_cli_sessions_compare_can_resolve_history_ids(tmp_path: Path, capsys) -> None:
    old_dir = tmp_path / "old-session"
    new_dir = tmp_path / "new-session"
    history_index = tmp_path / ".practicelens" / "sessions" / "index.jsonl"
    _write_manifest(old_dir, best_score=91.0, strongest_stable_area="section_stability")
    _write_manifest(new_dir, best_score=90.0, strongest_stable_area="pitch_fidelity")
    history_index.parent.mkdir(parents=True)
    history_index.write_text(
        json.dumps({"session_dir": str(old_dir), "manifest_path": str(old_dir / "session_manifest.json")})
        + "\n"
        + json.dumps({"session_dir": str(new_dir), "manifest_path": str(new_dir / "session_manifest.json")})
        + "\n",
        encoding="utf-8",
    )

    exit_code = run(["sessions", "compare", "1", "2", "--history-index", str(history_index)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == (
        "Overall score: -1.0\n"
        "Recurring weakness: pitch_fidelity -> pitch_fidelity\n"
        "Best take: declined\n"
        "Stable area: changed (section_stability -> pitch_fidelity)\n"
    )


def _run_practice_session_fixture(tmp_path: Path, capsys, *, history_index: Path | None = None) -> Path:
    reference = tmp_path / "reference.wav"
    take_a = tmp_path / "take_a.wav"
    take_b = tmp_path / "take_b.wav"
    out_dir = tmp_path / "practice-session-out"

    _write_wav(reference, 220.0)
    _write_wav(take_a, 220.0)
    _write_wav(take_b, 246.94)

    args = [
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
    if history_index is not None:
        args.extend(["--history-index", str(history_index)])

    assert run(args) == 0
    capsys.readouterr()
    return out_dir


def _write_history_index(history_index: Path) -> None:
    history_index.parent.mkdir(parents=True)
    history_index.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "created_at": "2026-05-16T10:00:00+00:00",
                        "session_dir": "out/session-a",
                        "best_take": "samples/take_02.wav",
                        "best_score": 88.4,
                        "recurring_weakness": "rhythm_fidelity",
                    },
                    sort_keys=True,
                ),
                json.dumps(
                    {
                        "created_at": "2026-05-17T10:00:00+00:00",
                        "session_dir": "out/session-b",
                        "best_take": "samples/take_03.wav",
                        "best_score": 90.1,
                        "recurring_weakness": "timing_consistency",
                    },
                    sort_keys=True,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_manifest(
    session_dir: Path,
    *,
    best_score: float,
    recurring_weakness: str = "pitch_fidelity",
    strongest_stable_area: str = "section_stability",
) -> Path:
    session_dir.mkdir(parents=True)
    manifest_path = session_dir / "session_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "practice_session_manifest",
                "best_take": {
                    "rank": 1,
                    "take_path": str(session_dir / "take_best.wav"),
                    "overall_score": best_score,
                },
                "weakest_take": {
                    "rank": 2,
                    "take_path": str(session_dir / "take_weak.wav"),
                    "overall_score": 77.0,
                },
                "recurring_weakness": recurring_weakness,
                "strongest_stable_area": strongest_stable_area,
                "next_recording_target": "Record one new take.",
                "entrypoints": {
                    "practice_plan": str(session_dir / "practice_plan.md"),
                    "batch_markdown": str(session_dir / "batch_report.md"),
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return manifest_path
