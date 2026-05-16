from __future__ import annotations

import json
from typing import Any

from practicelens.application.contracts import BatchCompareResult
from practicelens.domain.enums import ArtifactKind


def batch_compare_result_to_session_manifest_payload(result: BatchCompareResult) -> dict[str, object]:
    """Build a compact manifest for opening a batch/practice-session output directory."""

    summary = result.session_summary
    return {
        "schema_version": 1,
        "kind": "practice_session_manifest",
        "reference_path": str(result.reference_path),
        "compared_takes": len(result.entries),
        "take_paths": [str(entry.take_path) for entry in result.entries],
        "best_take": _take_payload(summary.best_take) if summary is not None else None,
        "weakest_take": _take_payload(summary.weakest_take) if summary is not None else None,
        "recurring_weakness": summary.recurring_weakness.value if summary is not None else None,
        "strongest_stable_area": summary.strongest_stable_area.value if summary is not None else None,
        "next_recording_target": summary.next_recording_target if summary is not None else None,
        "entrypoints": _entrypoint_payload(result),
        "artifacts": [
            {
                "kind": kind.value,
                "path": str(path),
            }
            for kind, path in result.artifacts
        ],
    }


def batch_compare_result_to_session_manifest_text(result: BatchCompareResult) -> str:
    """Render a compact practice session manifest as stable pretty JSON."""

    return json.dumps(batch_compare_result_to_session_manifest_payload(result), indent=2, sort_keys=True)


def _take_payload(take: Any) -> dict[str, object]:
    return {
        "rank": take.rank,
        "take_path": str(take.take_path),
        "overall_score": take.overall_score,
    }


def _entrypoint_payload(result: BatchCompareResult) -> dict[str, str | None]:
    return {
        "batch_json": _find_artifact(result, ArtifactKind.JSON_REPORT),
        "batch_markdown": _find_artifact(result, ArtifactKind.MARKDOWN_REPORT),
        "batch_csv": _find_artifact(result, ArtifactKind.CSV_REPORT),
        "batch_svg": _find_artifact(result, ArtifactKind.SVG_REPORT),
        "practice_plan": _find_artifact(result, ArtifactKind.PRACTICE_PLAN),
        "session_manifest": _find_artifact(result, ArtifactKind.SESSION_MANIFEST),
    }


def _find_artifact(result: BatchCompareResult, kind: ArtifactKind) -> str | None:
    for artifact_kind, path in result.artifacts:
        if artifact_kind == kind:
            return str(path)
    return None
