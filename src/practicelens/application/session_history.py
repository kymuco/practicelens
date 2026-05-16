from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from practicelens.application.contracts import BatchCompareResult, SessionTakeSummary

DEFAULT_SESSION_HISTORY_INDEX = Path(".practicelens") / "sessions" / "index.jsonl"


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


def read_session_history_entries(index_path: Path) -> tuple[dict[str, object], ...]:
    """Read valid JSONL session history entries from an index path."""

    if not index_path.exists():
        return ()

    entries: list[dict[str, object]] = []
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid session history JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"invalid session history entry on line {line_number}: expected object")
        entries.append(payload)
    return tuple(entries)


def format_session_history_entry(entry: dict[str, object]) -> str:
    """Format one compact CLI line for a session history entry."""

    created_at = _date_part(entry.get("created_at"))
    session_dir = _string_or_dash(entry.get("session_dir"))
    best_take = _path_name(entry.get("best_take"))
    score = _score(entry.get("best_score"))
    focus = _string_or_dash(entry.get("recurring_weakness"))
    return f"{created_at}  {session_dir}  best={best_take}  score={score}  focus={focus}"


def _date_part(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return "-"
    return value.split("T", maxsplit=1)[0]


def _path_name(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return "-"
    return Path(value).name


def _score(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.1f}"
    return "-"


def _string_or_dash(value: Any) -> str:
    if isinstance(value, str) and value:
        return value
    return "-"


def _take_path(take: SessionTakeSummary) -> str:
    return str(take.take_path)
