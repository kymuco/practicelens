from __future__ import annotations


class PracticeLensError(Exception):
    """Base exception for PracticeLens domain and application errors."""


class InvalidAnalysisConfigError(PracticeLensError):
    """Raised when an analysis configuration is invalid."""


class InvalidAnalysisInputError(PracticeLensError):
    """Raised when an analysis request is incomplete or inconsistent."""


class ReportContractError(PracticeLensError):
    """Raised when a report contract cannot be built safely."""
