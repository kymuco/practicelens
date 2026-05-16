from __future__ import annotations

from practicelens.reporting.batch_report import (
    batch_compare_result_to_csv_text,
    batch_compare_result_to_json_payload,
    batch_compare_result_to_json_text,
    batch_compare_result_to_markdown,
)
from practicelens.reporting.batch_svg_report import batch_compare_result_to_svg
from practicelens.reporting.csv_report import report_to_csv_text
from practicelens.reporting.debug_payload import report_to_debug_payload, report_to_debug_payload_text
from practicelens.reporting.json_report import report_to_json_payload, report_to_json_text
from practicelens.reporting.markdown_report import report_to_markdown
from practicelens.reporting.session_manifest import (
    batch_compare_result_to_session_manifest_payload,
    batch_compare_result_to_session_manifest_text,
)
from practicelens.reporting.svg_report import report_to_svg

__all__ = [
    "batch_compare_result_to_csv_text",
    "batch_compare_result_to_json_payload",
    "batch_compare_result_to_json_text",
    "batch_compare_result_to_markdown",
    "batch_compare_result_to_session_manifest_payload",
    "batch_compare_result_to_session_manifest_text",
    "batch_compare_result_to_svg",
    "report_to_csv_text",
    "report_to_debug_payload",
    "report_to_debug_payload_text",
    "report_to_json_payload",
    "report_to_json_text",
    "report_to_markdown",
    "report_to_svg",
]