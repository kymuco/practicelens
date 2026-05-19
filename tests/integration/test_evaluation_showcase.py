import json
from pathlib import Path

from practicelens.evaluation_showcase import generate_evaluation_showcase


def test_generate_evaluation_showcase_writes_session_history_workflow(tmp_path: Path) -> None:
    result = generate_evaluation_showcase(out_dir=tmp_path / "showcase")

    assert result.history_index_path.exists()
    assert result.session_history_dir.exists()

    sessions_list_path = result.session_history_dir / "outputs" / "sessions_list.txt"
    sessions_show_1_path = result.session_history_dir / "outputs" / "sessions_show_1.txt"
    sessions_compare_1_2_path = result.session_history_dir / "outputs" / "sessions_compare_1_2.txt"

    assert sessions_list_path.exists()
    assert sessions_show_1_path.exists()
    assert sessions_compare_1_2_path.exists()

    history_lines = result.history_index_path.read_text(encoding="utf-8").splitlines()
    assert len(history_lines) == 2
    assert "1  2026-05-16" in sessions_list_path.read_text(encoding="utf-8")
    assert "2  2026-05-17" in sessions_list_path.read_text(encoding="utf-8")
    assert "Session manifest:" in sessions_show_1_path.read_text(encoding="utf-8")
    assert "Overall score:" in sessions_compare_1_2_path.read_text(encoding="utf-8")

    summary = json.loads(result.summary_path.read_text(encoding="utf-8"))
    assert summary["session_history"]["history_index_path"] == str(result.history_index_path)
    assert summary["session_history"]["outputs"] == {
        "sessions_compare_1_2": str(sessions_compare_1_2_path),
        "sessions_list": str(sessions_list_path),
        "sessions_show_1": str(sessions_show_1_path),
    }
