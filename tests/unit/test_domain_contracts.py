from pathlib import Path

import pytest

from practicelens.application.contracts import AnalyzeRequest
from practicelens.domain.errors import InvalidAnalysisConfigError
from practicelens.domain.models import AnalysisConfig


def test_analysis_config_rejects_invalid_weight_sum() -> None:
    with pytest.raises(InvalidAnalysisConfigError):
        AnalysisConfig(
            pitch_weight=0.40,
            rhythm_weight=0.30,
            timing_weight=0.20,
            stability_weight=0.20,
        )


def test_analyze_request_converts_to_analysis_input() -> None:
    request = AnalyzeRequest(
        reference_path=Path("reference.wav"),
        take_path=Path("take.wav"),
    )

    analysis_input = request.to_analysis_input()

    assert analysis_input.reference_path == Path("reference.wav")
    assert analysis_input.take_path == Path("take.wav")
    assert analysis_input.mode.value == "reference"
