from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Simple string enum base for stable serialized contracts."""


class AnalysisMode(StrEnum):
    """Supported high-level analysis modes."""

    REFERENCE = "reference"


class Severity(StrEnum):
    """Normalized severity scale for findings and metrics."""

    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricName(StrEnum):
    """Stable metric identifiers for v0.1 reports."""

    PITCH_FIDELITY = "pitch_fidelity"
    RHYTHM_FIDELITY = "rhythm_fidelity"
    TIMING_CONSISTENCY = "timing_consistency"
    SECTION_STABILITY = "section_stability"
    ALIGNMENT_COVERAGE = "alignment_coverage"


class ArtifactKind(StrEnum):
    """Structured report artifact kinds."""

    JSON_REPORT = "json_report"
    MARKDOWN_REPORT = "markdown_report"
    CSV_REPORT = "csv_report"
    SVG_REPORT = "svg_report"
    DEBUG_PAYLOAD = "debug_payload"
