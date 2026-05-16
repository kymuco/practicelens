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
    format_session_history_entry,
    read_session_history_entries,
)
from practicelens.domain.enums import AnalysisMode, MetricName
from practicelens.domain.models import AnalysisInput, AnalysisOverview, AnalysisReport, ComponentScore, FeatureFlags


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


def test_build_session_history_entry_has_stable_shape() -> None:
    entry = build_session_history_entry(
        _sample_result(),
        session_dir=Path("out/session"),
        manifest_path=Path("out/session/session_manifest.json"),
        created_at=datetime(2026, 5, 16, 10, 0, tzinfo=UTC),
    )

    assert entry == {
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


def test_format_session_history_entry_handles_missing_optional_fields() -> None:
    assert format_session_history_entry({}) == "-  -  best=-  score=-  focus=-"
