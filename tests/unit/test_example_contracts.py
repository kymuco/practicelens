from __future__ import annotations

from pathlib import Path

from .._helpers import read_json


def test_api_example_payload_files_match_supported_request_keys() -> None:
    examples_dir = Path("examples/api")

    analyze_payload = read_json(examples_dir / "analyze_payload.json")
    batch_payload = read_json(examples_dir / "compare_batch_payload.json")

    assert set(analyze_payload) == {
        "reference_path",
        "take_path",
        "out_dir",
        "sample_rate",
        "frame_length",
        "hop_length",
        "segment_duration",
    }
    assert set(batch_payload) == {
        "reference_path",
        "take_paths",
        "out_dir",
        "sample_rate",
        "frame_length",
        "hop_length",
        "segment_duration",
    }


def test_single_example_result_matches_current_contract_shape() -> None:
    payload = read_json(Path("examples/results/single/report.json"))

    assert tuple(payload) == (
        "analysis_confidence",
        "artifacts",
        "feature_flags",
        "feedback",
        "inputs",
        "metrics",
        "next_practice_step",
        "overall_score",
        "overview",
        "practice_loops",
        "scores",
        "sections",
        "summary",
        "top_strengths",
        "top_weaknesses",
    )
    assert payload["overview"] == {
        "kind": "analysis_report",
        "mode": "reference",
        "ok": True,
        "schema_version": 1,
        "status": "completed",
    }
    assert payload["analysis_confidence"]["level"] in {"high", "medium", "low"}
    assert payload["analysis_confidence"]["reasons"]
    assert payload["analysis_confidence"]["limitations"]
    assert isinstance(payload["practice_loops"], list)
    assert payload["top_strengths"]
    assert payload["top_weaknesses"]
    assert payload["next_practice_step"] is not None
    assert [artifact["kind"] for artifact in payload["artifacts"]] == [
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
    ]


def test_batch_example_result_matches_current_contract_shape() -> None:
    payload = read_json(Path("examples/results/batch/batch_report.json"))

    assert tuple(payload) == (
        "artifacts",
        "entries",
        "overview",
        "reference_path",
        "summary",
    )
    assert payload["overview"] == {
        "kind": "batch_compare_report",
        "ok": True,
        "schema_version": 1,
        "status": "completed",
    }
    assert [artifact["kind"] for artifact in payload["artifacts"]] == [
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
    ]
    first_entry = payload["entries"][0]
    assert [artifact["kind"] for artifact in first_entry["artifacts"]] == [
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
    ]
