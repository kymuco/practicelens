"""Application-facing PracticeLens contracts."""

from practicelens.application.batch_compare import OfflineBatchComparePipeline
from practicelens.application.contracts import (
    AnalyzeRequest,
    AnalyzeResult,
    BatchCompareEntry,
    BatchCompareRequest,
    BatchCompareResult,
)
from practicelens.application.offline_pipeline import OfflineReferenceAnalysisPipeline
from practicelens.application.pipeline import AnalysisPipeline, PipelineDependencies

__all__ = [
    "AnalysisPipeline",
    "AnalyzeRequest",
    "AnalyzeResult",
    "BatchCompareEntry",
    "BatchCompareRequest",
    "BatchCompareResult",
    "OfflineBatchComparePipeline",
    "OfflineReferenceAnalysisPipeline",
    "PipelineDependencies",
]
