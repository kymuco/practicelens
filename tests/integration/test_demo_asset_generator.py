import json
from pathlib import Path

from practicelens.api import compare_batch_payload
from practicelens.cli.main import run
from practicelens.demo_assets import generate_demo_assets


def test_generated_demo_assets_support_cli_and_api_demo_flows(tmp_path: Path) -> None:
    assets_dir = tmp_path / "assets"
    cli_single_out = tmp_path / "cli-single-out"
    api_batch_out = tmp_path / "api-batch-out"

    assets = generate_demo_assets(assets_dir)

    exit_code = run(
        [
            "analyze",
            "--reference",
            str(assets["reference"]),
            "--take",
            str(assets["take"]),
            "--out",
            str(cli_single_out),
            "--frame-length",
            "1024",
            "--hop-length",
            "256",
            "--segment-duration",
            "2.0",
        ]
    )
    assert exit_code == 0
    assert (cli_single_out / "report.json").exists()

    batch_payload = compare_batch_payload(
        {
            "reference_path": str(assets["reference"]),
            "take_paths": [
                str(assets["take_01"]),
                str(assets["take_02"]),
                str(assets["take_03"]),
            ],
            "out_dir": str(api_batch_out),
            "frame_length": 1024,
            "hop_length": 256,
            "segment_duration": 2.0,
        }
    )

    assert batch_payload["entries"]
    assert batch_payload["entries"][0]["take_path"].endswith("take_02.wav")
    assert (api_batch_out / "batch_report.json").exists()
    manifest = json.loads((assets_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["assets"]["take_02"]["role"] == "Strongest batch-comparison demo take."
