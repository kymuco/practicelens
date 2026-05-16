from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from practicelens.application.contracts import BatchCompareResult, SessionTakeSummary


def build_session_history_entry(
    result: BatchCompareResult,
    *,
    session_dir: Path,
    manifest_path: Path,
    created_at: datetime | None = None,
) -> dict[str, object]:
    """Build one append-only session history index entry."""

    timestamp = created_at or datetime.now(UTC)
    summary = result.session_summary
    return {
        "schema_version": 1,
        "kind": "practice_session_index_entry",
        "created_at": timestamp.isoformat(),
        "session_dir": str(session_dir),
        "manifest_path": str(manifest_path),
        "reference_path": str(result.reference_path),
        "compared_takes": len(result.entries),
        "best_take": _take_path(summary.best_take) if summary is not None else None,
        "best_score": summary.best_take.overall_score if summary is not None else None,
        "weakest_take": _take_path(summary.weakest_take) if summary is not None else None,
        "weakest_score": summary.weakest_take.overall_score if summary is not None else None,
        "recurring_weakness": summary.recurring_weakness.value if summary is not None else None,
        "strongest_stable_area": summary.strongest_stable_area.value if summary is not None else None,
        "next_recording_target": summary.next_recording_target if summary is not None else None,
    }


def append_session_history_entry(index_path: Path, entry: dict[str, object]) -> None:
    """Append one JSONL session history entry, creating parent directories when needed."""

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, sort_keys=True))
        file.write("\n")


def _take_path(take: SessionTakeSummary) -> str:
    return str(take.take_path)
