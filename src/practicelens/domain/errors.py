from __future__ import annotations


class PracticeLensError(Exception):
    """Base exception for PracticeLens domain and application errors."""


class InvalidAnalysisConfigError(PracticeLensError):
    """Raised when an analysis configuration is invalid."""


class InvalidAnalysisInputError(PracticeLensError):
    """Raised when an analysis request is incomplete or inconsistent."""


class ReportContractError(PracticeLensError):
    """Raised when a report contract cannot be built safely."""


class AudioLoadError(PracticeLensError):
    """Raised when an audio asset cannot be loaded safely."""


class FeatureExtractionError(PracticeLensError):
    """Raised when feature extraction fails or receives invalid input."""


class AlignmentError(PracticeLensError):
    """Raised when feature alignment cannot be computed safely."""


class ScoringError(PracticeLensError):
    """Raised when scoring cannot be synthesized from aligned features."""
