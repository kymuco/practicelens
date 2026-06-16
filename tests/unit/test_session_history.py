import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from practicelens.application.contracts import (
    AnalyzeResult,
    BatchCompareEntry,
    BatchCompareResult,
    BatchSessionSummary,
    SessionTakeSummary,
)
from practicelens.application.session_history import (
    append_session_history_entry,
    build_session_history_entry,
    format_session_compare,
    format_session_history_entry,
    format_session_show,
    read_session_history_entries,
    read_session_manifest,
    resolve_session_manifest_path,
)
from practicelens.domain.enums import AnalysisMode, MetricName
from practicelens.domain.models import AnalysisInput, AnalysisOverview, AnalysisReport, ComponentScore, FeatureFlags


def _normalize_path_separators(value: object) -> object:
    """Normalize platform-native paths when tests assert path identity, not slash style."""

    if isinstance(value, str):
        return value.replace("\\", "/")
    if isinstance(value, dict):
        return {key: _normalize_path_separators(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_path_separators(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_normalize_path_separators(item) for item in value)
    return value


def _sample_report(path: str, score: float) -> AnalysisReport:
    return AnalysisReport(
        overview=AnalysisOverview(mode=AnalysisMode.REFERENCE),
        inputs=AnalysisInput(Path("reference.wav"), Path(path)),
        feature_flags=FeatureFlags(),
        scores=(ComponentScore(MetricName.PITCH_FIDELITY, score, 1.0),),
        metrics=(),
        sections=(),
        summary=f"Score {score:.1f}",
    )


def _sample_result() -> BatchCompareResult:
    return BatchCompareResult(
        reference_path=Path("reference.wav"),
        entries=(
            BatchCompareEntry(1, Path("take_a.wav"), 91.0, AnalyzeResult(_sample_report("take_a.wav", 91.0))),
            BatchCompareEntry(2, Path("take_b.wav"), 77.0, AnalyzeResult(_sample_report("take_b.wav", 77.0))),
        ),
        summary="Best take: take_a.wav with 91.0/100 across 2 compared takes.",
        session_summary=BatchSessionSummary(
            compared_takes=2,
            best_take=SessionTakeSummary(rank=1, take_path=Path("take_a.wav"), overall_score=91.0),
            weakest_take=SessionTakeSummary(rank=2, take_path=Path("take_b.wav"), overall_score=77.0),
            recurring_weakness=MetricName.PITCH_FIDELITY,
            recurring_weakness_count=2,
            strongest_stable_area=MetricName.PITCH_FIDELITY,
            strongest_stable_area_average_score=84.0,
            next_recording_target="Record one new take focused on improving Pitch Fidelity.",
        ),
    )


def _sample_manifest(
    *,
    best_score: float = 91.0,
    recurring_weakness: str = "pitch_fidelity",
    strongest_stable_area: str = "section_stability",
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "kind": "practice_session_manifest",
        "best_take": {"rank": 1, "take_path": "samples/take_a.wav", "overall_score": best_score},
        "weakest_take": {"rank": 2, "take_path": "samples/take_b.wav", "overall_score": 77.0},
        "recurring_weakness": recurring_weakness,
        "strongest_stable_area": strongest_stable_area,
        "next_recording_target": "Record one new take focused on improving Pitch Fidelity.",
        "entrypoints": {
            "practice_plan": "out/session/practice_plan.md",
            "batch_markdown": "out/session/batch_report.md",
        },
    }


def test_build_session_history_entry_has_stable_shape() -> None:
    entry = build_session_history_entry(
        _sample_result(),
        session_dir=Path("out/session"),
        manifest_path=Path("out/session/session_manifest.json"),
        created_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
    )

    assert _normalize_path_separators(entry) == {
        "schema_version": 1,
        "kind": "practice_session_index_entry",
        "created_at": "2026-05-16T10:00:00+00:00",
        "session_dir": "out/session",
        "manifest_path": "out/session/session_manifest.json",
        "reference_path": "reference.wav",
        "compared_takes": 2,
        "best_take": "take_a.wav",
        "best_score": 91.0,
        "weakest_take": "take_b.wav",
        "weakest_score": 77.0,
        "recurring_weakness": "pitch_fidelity",
        "strongest_stable_area": "pitch_fidelity",
        "next_recording_target": "Record one new take focused on improving Pitch Fidelity.",
    }


def test_append_and_read_session_history_entry_writes_jsonl(tmp_path: Path) -> None:
    index_path = tmp_path / ".practicelens" / "sessions" / "index.jsonl"
    entry = build_session_history_entry(
        _sample_result(),
        session_dir=Path("out/session"),
        manifest_path=Path("out/session/session_manifest.json"),
        created_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
    )

    append_session_history_entry(index_path, entry)
    append_session_history_entry(index_path, entry)

    lines = index_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert read_session_history_entries(index_path) == (entry, entry)


def test_read_session_history_entries_returns_empty_for_missing_index(tmp_path: Path) -> None:
    assert read_session_history_entries(tmp_path / "missing.jsonl") == ()


def test_read_session_history_entries_rejects_invalid_json(tmp_path: Path) -> None:
    index_path = tmp_path / "index.jsonl"
    index_path.write_text("{not-json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid session history JSON on line 1"):
        read_session_history_entries(index_path)


def test_resolve_session_manifest_path_accepts_session_directory(tmp_path: Path) -> None:
    session_dir = tmp_path / "session-a"
    session_dir.mkdir()

    assert resolve_session_manifest_path(
        str(session_dir),
        history_index_path=tmp_path / "missing.jsonl",
    ) == session_dir / "session_manifest.json"


def test_resolve_session_manifest_path_accepts_manifest_file(tmp_path: Path) -> None:
    manifest_path = tmp_path / "session_manifest.json"
    manifest_path.write_text(json.dumps(_sample_manifest()), encoding="utf-8")

    assert resolve_session_manifest_path(str(manifest_path), history_index_path=tmp_path / "missing.jsonl") == manifest_path


def test_resolve_session_manifest_path_accepts_history_id(tmp_path: Path) -> None:
    index_path = tmp_path / "index.jsonl"
    manifest_a = tmp_path / "session-a" / "session_manifest.json"
    manifest_b = tmp_path / "session-b" / "session_manifest.json"
    index_path.write_text(
        json.dumps({"session_dir": str(manifest_a.parent), "manifest_path": str(manifest_a)})
        + "\n"
        + json.dumps({"session_dir": str(manifest_b.parent), "manifest_path": str(manifest_b)})
        + "\n",
        encoding="utf-8",
    )

    assert resolve_session_manifest_path("2", history_index_path=index_path) == manifest_b


def test_resolve_session_manifest_path_accepts_indexed_session_dir(tmp_path: Path) -> None:
    index_path = tmp_path / "index.jsonl"
    manifest_path = tmp_path / "session-a" / "session_manifest.json"
    index_path.write_text(
        json.dumps({"session_dir": str(manifest_path.parent), "manifest_path": str(manifest_path)}) + "\n",
        encoding="utf-8",
    )

    assert resolve_session_manifest_path(str(manifest_path.parent), history_index_path=index_path) == manifest_path


def test_resolve_session_manifest_path_rejects_missing_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="session 'missing-session' not found"):
        resolve_session_manifest_path("missing-session", history_index_path=tmp_path / "missing.jsonl")


def test_read_session_manifest_validates_kind(tmp_path: Path) -> None:
    manifest_path = tmp_path / "session_manifest.json"
    manifest_path.write_text(json.dumps({"kind": "other"}), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid session manifest kind"):
        read_session_manifest(manifest_path)


def test_format_session_show_outputs_human_summary() -> None:
    text = format_session_show(_sample_manifest(), manifest_path=Path("out/session/session_manifest.json"))

    assert _normalize_path_separators(text) == (
        "Session manifest: out/session/session_manifest.json\n"
        "Best take: samples/take_a.wav (91.0/100)\n"
        "Weakest take: samples/take_b.wav (77.0/100)\n"
        "Recurring weakness: pitch_fidelity\n"
        "Next recording target: Record one new take focused on improving Pitch Fidelity.\n"
        "Practice plan: out/session/practice_plan.md\n"
        "Batch report: out/session/batch_report.md"
    )


def test_format_session_compare_outputs_progress_summary() -> None:
    text = format_session_compare(
        _sample_manifest(best_score=88.4, recurring_weakness="rhythm_fidelity"),
        _sample_manifest(best_score=91.6, recurring_weakness="timing_consistency"),
    )

    assert text == (
        "Overall score: +3.2\n"
        "Recurring weakness: rhythm_fidelity -> timing_consistency\n"
        "Best take: improved\n"
        "Stable area: preserved (section_stability)"
    )


def test_format_session_compare_reports_stable_area_change() -> None:
    text = format_session_compare(
        _sample_manifest(best_score=91.0, strongest_stable_area="section_stability"),
        _sample_manifest(best_score=90.0, strongest_stable_area="pitch_fidelity"),
    )

    assert text == (
        "Overall score: -1.0\n"
        "Recurring weakness: pitch_fidelity -> pitch_fidelity\n"
        "Best take: declined\n"
        "Stable area: changed (section_stability -> pitch_fidelity)"
    )


def test_format_session_compare_handles_missing_scores() -> None:
    text = format_session_compare(
        {"kind": "practice_session_manifest"},
        {"kind": "practice_session_manifest"},
    )

    assert text == (
        "Overall score: unknown\n"
        "Recurring weakness: - -> -\n"
        "Best take: unknown\n"
        "Stable area: unknown"
    )


def test_format_session_history_entry_outputs_compact_cli_line() -> None:
    line = format_session_history_entry(
        {
            "created_at": "2026-05-16T10:00:00+00:00",
            "session_dir": "out/session-a",
            "best_take": "samples/take_02.wav",
            "best_score": 88.4,
            "recurring_weakness": "rhythm_fidelity",
        }
    )

    assert line == "2026-05-16  out/session-a  best=take_02.wav  score=88.4  focus=rhythm_fidelity"


def test_format_session_history_entry_can_include_index() -> None:
    line = format_session_history_entry(
        {
            "created_at": "2026-05-16T10:00:00+00:00",
            "session_dir": "out/session-a",
            "best_take": "samples/take_02.wav",
            "best_score": 88.4,
            "recurring_weakness": "rhythm_fidelity",
        },
        index=1,
    )

    assert line == "1  2026-05-16  out/session-a  best=take_02.wav  score=88.4  focus=rhythm_fidelity"


def test_format_session_history_entry_handles_missing_optional_fields() -> None:
    assert format_session_history_entry({}) == "-  -  best=-  score=-  focus=-"
