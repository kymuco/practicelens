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
    debug_payload = read_json(Path("examples/results/single/debug_payload.json"))

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
        "practice_plan",
        "debug_payload",
    ]
    assert debug_payload["kind"] == "debug_payload"
    assert debug_payload["schema_version"] == 1
    assert debug_payload["score_summary"]["overall_score"] == payload["overall_score"]
    assert debug_payload["evidence_summary"]["artifact_count"] == len(payload["artifacts"])
    assert [artifact["kind"] for artifact in debug_payload["artifacts"]] == [
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
        "practice_plan",
        "debug_payload",
    ]


def test_batch_example_result_matches_current_contract_shape() -> None:
    payload = read_json(Path("examples/results/batch/batch_report.json"))
    manifest = read_json(Path("examples/results/batch/session_manifest.json"))

    assert tuple(payload) == (
        "artifacts",
        "entries",
        "overview",
        "reference_path",
        "session_summary",
        "summary",
    )
    assert payload["overview"] == {
        "kind": "batch_compare_report",
        "ok": True,
        "schema_version": 1,
        "status": "completed",
    }
    assert payload["session_summary"]["schema_version"] == 1
    assert payload["session_summary"]["compared_takes"] == 3
    assert payload["session_summary"]["best_take"]
    assert payload["session_summary"]["weakest_take"]
    assert payload["session_summary"]["recurring_weakness"]
    assert payload["session_summary"]["strongest_stable_area"]
    assert payload["session_summary"]["next_recording_target"]
    assert payload["session_summary"]["practice_loops"]
    assert [artifact["kind"] for artifact in payload["artifacts"]] == [
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
        "practice_plan",
        "session_manifest",
    ]
    first_entry = payload["entries"][0]
    assert first_entry["practice_loops"]
    assert [artifact["kind"] for artifact in first_entry["artifacts"]] == [
        "json_report",
        "markdown_report",
        "csv_report",
        "svg_report",
        "practice_plan",
        "debug_payload",
    ]
    assert manifest["kind"] == "practice_session_manifest"
    assert manifest["schema_version"] == 1
    assert manifest["best_take"] == payload["session_summary"]["best_take"]
    assert manifest["weakest_take"] == payload["session_summary"]["weakest_take"]
    assert manifest["next_recording_target"] == payload["session_summary"]["next_recording_target"]
    assert manifest["entrypoints"]["batch_json"] == "examples/results/batch/batch_report.json"
    assert manifest["entrypoints"]["practice_plan"] == "examples/results/batch/practice_plan.md"
    assert manifest["entrypoints"]["session_manifest"] == "examples/results/batch/session_manifest.json"