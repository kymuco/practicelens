from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from practicelens.application.contracts import BatchCompareResult, SessionTakeSummary

DEFAULT_SESSION_HISTORY_INDEX = Path(".practicelens") / "sessions" / "index.jsonl"
SESSION_MANIFEST_FILENAME = "session_manifest.json"


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


def resolve_session_manifest_path(target: str, *, history_index_path: Path) -> Path:
    """Resolve a session target to a concrete session_manifest.json path."""

    target_path = Path(target)
    if target_path.is_dir():
        return target_path / SESSION_MANIFEST_FILENAME
    if target_path.is_file():
        return target_path

    entries = read_session_history_entries(history_index_path)
    if target.isdigit():
        index = int(target)
        if index < 1 or index > len(entries):
            raise ValueError(f"session id {target} not found in {history_index_path}")
        return _manifest_path_from_entry(entries[index - 1])

    for entry in entries:
        if entry.get("session_dir") == target or entry.get("manifest_path") == target:
            return _manifest_path_from_entry(entry)

    raise ValueError(f"session {target!r} not found")


def read_session_manifest(manifest_path: Path) -> dict[str, object]:
    """Read one practice session manifest JSON file."""

    if not manifest_path.exists():
        raise FileNotFoundError(f"session manifest not found: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid session manifest: expected object at {manifest_path}")
    if payload.get("kind") != "practice_session_manifest":
        raise ValueError(f"invalid session manifest kind at {manifest_path}")
    return payload


def format_session_show(manifest: dict[str, object], *, manifest_path: Path) -> str:
    """Format a session manifest as a compact human-readable CLI summary."""

    best_take = _take_summary(manifest.get("best_take"))
    weakest_take = _take_summary(manifest.get("weakest_take"))
    recurring_weakness = _string_or_dash(manifest.get("recurring_weakness"))
    next_target = _string_or_dash(manifest.get("next_recording_target"))
    entrypoints = manifest.get("entrypoints") if isinstance(manifest.get("entrypoints"), dict) else {}
    practice_plan = _string_or_dash(entrypoints.get("practice_plan"))
    batch_report = _string_or_dash(entrypoints.get("batch_markdown"))

    return "\n".join(
        (
            f"Session manifest: {manifest_path}",
            f"Best take: {best_take}",
            f"Weakest take: {weakest_take}",
            f"Recurring weakness: {recurring_weakness}",
            f"Next recording target: {next_target}",
            f"Practice plan: {practice_plan}",
            f"Batch report: {batch_report}",
        )
    )


def format_session_compare(old_manifest: dict[str, object], new_manifest: dict[str, object]) -> str:
    """Format a first-pass progress comparison between two session manifests."""

    old_best_score = _take_score(old_manifest.get("best_take"))
    new_best_score = _take_score(new_manifest.get("best_take"))
    old_weakness = _string_or_dash(old_manifest.get("recurring_weakness"))
    new_weakness = _string_or_dash(new_manifest.get("recurring_weakness"))
    old_stable_area = _string_or_dash(old_manifest.get("strongest_stable_area"))
    new_stable_area = _string_or_dash(new_manifest.get("strongest_stable_area"))

    return "\n".join(
        (
            f"Overall score: {_score_delta(old_best_score, new_best_score)}",
            f"Recurring weakness: {old_weakness} -> {new_weakness}",
            f"Best take: {_best_take_change(old_best_score, new_best_score)}",
            f"Stable area: {_stable_area_change(old_stable_area, new_stable_area)}",
        )
    )


def format_session_history_entry(entry: dict[str, object]) -> str:
    """Format one compact CLI line for a session history entry."""

    created_at = _date_part(entry.get("created_at"))
    session_dir = _string_or_dash(entry.get("session_dir"))
    best_take = _path_name(entry.get("best_take"))
    score = _score(entry.get("best_score"))
    focus = _string_or_dash(entry.get("recurring_weakness"))
    return f"{created_at}  {session_dir}  best={best_take}  score={score}  focus={focus}"


def _manifest_path_from_entry(entry: dict[str, object]) -> Path:
    manifest_path = entry.get("manifest_path")
    if isinstance(manifest_path, str) and manifest_path:
        return Path(manifest_path)
    session_dir = entry.get("session_dir")
    if isinstance(session_dir, str) and session_dir:
        return Path(session_dir) / SESSION_MANIFEST_FILENAME
    raise ValueError("session history entry does not include manifest_path or session_dir")


def _take_summary(value: Any) -> str:
    if not isinstance(value, dict):
        return "-"
    take_path = _string_or_dash(value.get("take_path"))
    score = _score(value.get("overall_score"))
    if score == "-":
        return take_path
    return f"{take_path} ({score}/100)"


def _take_score(value: Any) -> float | None:
    if not isinstance(value, dict):
        return None
    score = value.get("overall_score")
    if isinstance(score, int | float):
        return float(score)
    return None


def _score_delta(old_score: float | None, new_score: float | None) -> str:
    if old_score is None or new_score is None:
        return "unknown"
    delta = new_score - old_score
    return f"{delta:+.1f}"


def _best_take_change(old_score: float | None, new_score: float | None) -> str:
    if old_score is None or new_score is None:
        return "unknown"
    if new_score > old_score:
        return "improved"
    if new_score < old_score:
        return "declined"
    return "unchanged"


def _stable_area_change(old_value: str, new_value: str) -> str:
    if old_value == "-" or new_value == "-":
        return "unknown"
    if old_value == new_value:
        return f"preserved ({new_value})"
    return f"changed ({old_value} -> {new_value})"


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
