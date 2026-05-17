from __future__ import annotations

import argparse
import sys
from pathlib import Path

from practicelens.application import (
    AnalyzeRequest,
    BatchCompareRequest,
    BatchCompareResult,
    OfflineBatchComparePipeline,
    OfflineReferenceAnalysisPipeline,
)
from practicelens.application.session_history import (
    DEFAULT_SESSION_HISTORY_INDEX,
    append_session_history_entry,
    build_session_history_entry,
    format_session_compare,
    format_session_history_entry,
    format_session_show,
    read_session_history_entries,
    read_session_manifest,
    resolve_session_manifest_path,
)
from practicelens.domain.enums import ArtifactKind
from practicelens.domain.models import AnalysisConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="practicelens")
    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze", help="Analyze a take against a reference WAV.")
    analyze.add_argument("--reference", required=True, help="Path to the reference WAV file.")
    analyze.add_argument("--take", required=True, help="Path to the user take WAV file.")
    analyze.add_argument("--out", required=True, help="Output directory for report artifacts.")
    _add_common_analysis_args(analyze)

    compare_batch = subparsers.add_parser(
        "compare-batch",
        help="Compare multiple takes against one reference WAV.",
    )
    _add_batch_args(compare_batch, out_help="Output directory for batch artifacts.")
    _add_common_analysis_args(compare_batch)

    practice_session = subparsers.add_parser(
        "practice-session",
        help="Run a practice-session review across multiple takes.",
    )
    _add_batch_args(practice_session, out_help="Output directory for practice-session artifacts.")
    practice_session.add_argument(
        "--history-index",
        help="Optional JSONL path where a compact practice-session history entry should be appended.",
    )
    _add_common_analysis_args(practice_session)

    sessions = subparsers.add_parser("sessions", help="Inspect local practice-session history.")
    sessions_subparsers = sessions.add_subparsers(dest="sessions_command")
    sessions_list = sessions_subparsers.add_parser("list", help="List indexed practice sessions.")
    sessions_list.add_argument(
        "--history-index",
        default=str(DEFAULT_SESSION_HISTORY_INDEX),
        help="JSONL session history index path to read.",
    )
    sessions_show = sessions_subparsers.add_parser(
        "show",
        help="Show one practice session from a manifest path, session directory, or history id.",
    )
    sessions_show.add_argument(
        "session",
        help=(
            "Session directory, session_manifest.json path, indexed session id, "
            "or indexed session path."
        ),
    )
    sessions_show.add_argument(
        "--history-index",
        default=str(DEFAULT_SESSION_HISTORY_INDEX),
        help="JSONL session history index path to use when resolving an indexed session.",
    )
    sessions_compare = sessions_subparsers.add_parser(
        "compare",
        help="Compare two practice sessions for first-pass progress tracking.",
    )
    sessions_compare.add_argument("old_session", help="Older session directory, manifest path, or indexed session id.")
    sessions_compare.add_argument("new_session", help="Newer session directory, manifest path, or indexed session id.")
    sessions_compare.add_argument(
        "--history-index",
        default=str(DEFAULT_SESSION_HISTORY_INDEX),
        help="JSONL session history index path to use when resolving indexed sessions.",
    )

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _run_analyze(args)
    if args.command == "compare-batch":
        return _run_compare_batch(args)
    if args.command == "practice-session":
        return _run_practice_session(args)
    if args.command == "sessions":
        return _run_sessions(args)

    parser.print_help()
    return 1


def _run_analyze(args: argparse.Namespace) -> int:
    request = AnalyzeRequest(
        reference_path=Path(args.reference),
        take_path=Path(args.take),
        out_dir=Path(args.out),
        config=_build_config(args),
    )
    try:
        result = OfflineReferenceAnalysisPipeline().analyze(request)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.report.summary or "Analysis completed.")
    for artifact in result.report.artifacts:
        print(f"{artifact.kind.value}: {artifact.path}")
    return 0


def _run_compare_batch(args: argparse.Namespace) -> int:
    try:
        result = _run_batch_compare_pipeline(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary or "Batch comparison completed.")
    for kind, path in result.artifacts:
        print(f"{kind.value}: {path}")
    return 0


def _run_practice_session(args: argparse.Namespace) -> int:
    try:
        result = _run_batch_compare_pipeline(args)
        history_index_path = Path(args.history_index) if args.history_index else None
        if history_index_path is not None:
            manifest_path = _find_batch_artifact_path(result, ArtifactKind.SESSION_MANIFEST)
            if manifest_path is None:
                raise RuntimeError("practice-session history requires session_manifest.json")
            history_entry = build_session_history_entry(
                result,
                session_dir=Path(args.out),
                manifest_path=manifest_path,
            )
            append_session_history_entry(history_index_path, history_entry)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary or "Practice session completed.")
    if result.session_summary is not None:
        summary = result.session_summary
        print(f"best_take: {summary.best_take.take_path}")
        print(f"weakest_take: {summary.weakest_take.take_path}")
        print(f"recurring_weakness: {summary.recurring_weakness.value}")
        print(f"next_recording_target: {summary.next_recording_target}")
    practice_plan_path = _find_batch_artifact_path(result, ArtifactKind.PRACTICE_PLAN)
    if practice_plan_path is not None:
        print(f"practice_plan: {practice_plan_path}")
    if args.history_index:
        print(f"history_index: {args.history_index}")
    return 0


def _run_sessions(args: argparse.Namespace) -> int:
    if args.sessions_command == "list":
        return _run_sessions_list(args)
    if args.sessions_command == "show":
        return _run_sessions_show(args)
    if args.sessions_command == "compare":
        return _run_sessions_compare(args)
    print("error: missing sessions command", file=sys.stderr)
    return 1


def _run_sessions_list(args: argparse.Namespace) -> int:
    try:
        entries = read_session_history_entries(Path(args.history_index))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not entries:
        print("No practice sessions found.")
        return 0

    for entry in entries:
        print(format_session_history_entry(entry))
    return 0


def _run_sessions_show(args: argparse.Namespace) -> int:
    try:
        manifest_path = resolve_session_manifest_path(args.session, history_index_path=Path(args.history_index))
        manifest = read_session_manifest(manifest_path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_session_show(manifest, manifest_path=manifest_path))
    return 0


def _run_sessions_compare(args: argparse.Namespace) -> int:
    try:
        history_index_path = Path(args.history_index)
        old_manifest_path = resolve_session_manifest_path(args.old_session, history_index_path=history_index_path)
        new_manifest_path = resolve_session_manifest_path(args.new_session, history_index_path=history_index_path)
        old_manifest = read_session_manifest(old_manifest_path)
        new_manifest = read_session_manifest(new_manifest_path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_session_compare(old_manifest, new_manifest))
    return 0


def _run_batch_compare_pipeline(args: argparse.Namespace) -> BatchCompareResult:
    request = BatchCompareRequest(
        reference_path=Path(args.reference),
        take_paths=tuple(Path(value) for value in args.takes),
        out_dir=Path(args.out),
        config=_build_config(args),
    )
    return OfflineBatchComparePipeline().compare(request)


def _find_batch_artifact_path(result: BatchCompareResult, kind: ArtifactKind) -> Path | None:
    for artifact_kind, path in result.artifacts:
        if artifact_kind == kind:
            return path
    return None


def _build_config(args: argparse.Namespace) -> AnalysisConfig:
    return AnalysisConfig(
        target_sample_rate=args.sample_rate,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        segment_duration_s=args.segment_duration,
    )


def _add_batch_args(parser: argparse.ArgumentParser, *, out_help: str) -> None:
    parser.add_argument("--reference", required=True, help="Path to the reference WAV file.")
    parser.add_argument(
        "--take",
        dest="takes",
        action="append",
        required=True,
        help="Path to one take WAV file. Repeat for multiple takes.",
    )
    parser.add_argument("--out", required=True, help=out_help)


def _add_common_analysis_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sample-rate", type=int, default=16_000)
    parser.add_argument("--frame-length", type=int, default=2_048)
    parser.add_argument("--hop-length", type=int, default=512)
    parser.add_argument("--segment-duration", type=float, default=8.0)


if __name__ == "__main__":
    raise SystemExit(run())