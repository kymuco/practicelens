"""Application-facing PracticeLens contracts."""

from practicelens.application.contracts import AnalyzeRequest, AnalyzeResult
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
from practicelens.application.pipeline import AnalysisPipeline, PipelineDependencies

__all__ = [
    "AnalysisPipeline",
    "AnalyzeRequest",
    "AnalyzeResult",
    "OfflineReferenceAnalysisPipeline",
    "PipelineDependencies",
]
