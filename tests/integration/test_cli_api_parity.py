from __future__ import annotations

from pathlib import Path

from practicelens.api import analyze_payload, compare_batch_payload
from practicelens.cli.main import run
from tests._helpers import normalize_batch_payload, normalize_single_payload, read_json, write_sine_wav


def test_cli_and_api_single_analysis_stay_in_contract_parity(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take = tmp_path / "take.wav"
    api_out_dir = tmp_path / "api-single-out"
    cli_out_dir = tmp_path / "cli-single-out"

    write_sine_wav(reference, 220.0)
    write_sine_wav(take, 220.0)

    api_payload = analyze_payload(
        {
            "reference_path": str(reference),
            "take_path": str(take),
            "out_dir": str(api_out_dir),
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.0,
        }
    )

    exit_code = run(
        [
            "analyze",
            "--reference",
            str(reference),
            "--take",
            str(take),
            "--out",
            str(cli_out_dir),
            "--frame-length",
            "1024",
            "--hop-length",
            "256",
            "--segment-duration",
            "2.0",
        ]
    )

    assert exit_code == 0
    cli_payload = read_json(cli_out_dir / "report.json")
    assert normalize_single_payload(api_payload) == normalize_single_payload(cli_payload)


def test_cli_and_api_batch_compare_stay_in_contract_parity(tmp_path: Path) -> None:
    reference = tmp_path / "reference.wav"
    take_best = tmp_path / "take_best.wav"
    take_low = tmp_path / "take_low.wav"
    api_out_dir = tmp_path / "api-batch-out"
    cli_out_dir = tmp_path / "cli-batch-out"

    write_sine_wav(reference, 220.0)
    write_sine_wav(take_best, 220.0)
    write_sine_wav(take_low, 261.63)

    api_payload = compare_batch_payload(
        {
            "reference_path": str(reference),
            "take_paths": [str(take_low), str(take_best)],
            "out_dir": str(api_out_dir),
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.0,
        }
    )

    exit_code = run(
        [
            "compare-batch",
            "--reference",
            str(reference),
            "--take",
            str(take_low),
            "--take",
            str(take_best),
            "--out",
            str(cli_out_dir),
            "--frame-length",
            "1024",
            "--hop-length",
            "256",
            "--segment-duration",
            "2.0",
        ]
    )

    assert exit_code == 0
    cli_payload = read_json(cli_out_dir / "batch_report.json")
    assert normalize_batch_payload(api_payload) == normalize_batch_payload(cli_payload)
