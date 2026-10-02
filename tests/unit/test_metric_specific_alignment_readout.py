from __future__ import annotations

from practicelens.domain.enums import MetricName
from practicelens.measurement.metric_specific_alignment_readout import (
    READOUT_MEASUREMENTS,
    _directional_verdict,
    _monotonicity_verdict,
    _no_worse,
)


def test_metric_specific_readout_scope_is_explicit() -> None:
    assert READOUT_MEASUREMENTS == (
        MetricName.PITCH_FIDELITY.value,
        MetricName.RHYTHM_FIDELITY.value,
        MetricName.TIMING_CONSISTENCY.value,
    )
    assert MetricName.SECTION_STABILITY.value not in READOUT_MEASUREMENTS


def test_no_worse_is_measurement_specific() -> None:
    production = {
        MetricName.PITCH_FIDELITY.value: 3.0,
        MetricName.RHYTHM_FIDELITY.value: 2.0,
        MetricName.TIMING_CONSISTENCY.value: 4.0,
    }
    readout = {
        MetricName.PITCH_FIDELITY.value: 3.0,
        MetricName.RHYTHM_FIDELITY.value: 1.0,
        MetricName.TIMING_CONSISTENCY.value: 2.0,
    }

    assert _no_worse(
        production=production,
        readout=readout,
        measurements=READOUT_MEASUREMENTS,
    )

    readout[MetricName.PITCH_FIDELITY.value] = 3.1
    assert not _no_worse(
        production=production,
        readout=readout,
        measurements=READOUT_MEASUREMENTS,
    )


def test_readout_verdicts_use_same_strict_directional_semantics() -> None:
    assert _directional_verdict([100.0, 95.0, 90.0]) == "PASS"
    assert _directional_verdict([100.0, 100.0]) == "UNRESOLVED"
    assert _directional_verdict([100.0, 101.0]) == "FAIL"

    assert _monotonicity_verdict([100.0, 95.0, 90.0]) == "PASS"
    assert _monotonicity_verdict([100.0, 95.0, 97.0, 90.0]) == "PARTIAL"
    assert _monotonicity_verdict([100.0, 100.0]) == "UNRESOLVED"
