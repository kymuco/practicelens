from __future__ import annotations

import pytest

from practicelens.preprocessing import trim_silence, trim_silence_fixed_padding


def test_trim_silence_keeps_existing_boundary_clipping_behavior() -> None:
    samples = (0.0, 0.0, 0.02, 0.5, 0.02, 0.0)

    assert trim_silence(samples, threshold=0.01, pad_samples=3) == samples


def test_fixed_padding_canonicalizes_equivalent_recording_windows() -> None:
    phrase = (0.001, 0.004, 0.02, 0.5, 0.02, 0.004, 0.001)
    padded = (0.0,) * 20 + phrase + (0.0,) * 30

    reference = trim_silence_fixed_padding(
        phrase,
        threshold=0.01,
        pad_samples=4,
    )
    shifted = trim_silence_fixed_padding(
        padded,
        threshold=0.01,
        pad_samples=4,
    )

    assert shifted == reference


def test_fixed_padding_zero_fills_missing_file_boundary_context() -> None:
    samples = (0.001, 0.02, 0.5, 0.02, 0.001)

    trimmed = trim_silence_fixed_padding(
        samples,
        threshold=0.01,
        pad_samples=3,
    )

    assert trimmed == (
        0.0,
        0.0,
        0.001,
        0.02,
        0.5,
        0.02,
        0.001,
        0.0,
        0.0,
    )


def test_fixed_padding_returns_empty_for_all_silence() -> None:
    assert (
        trim_silence_fixed_padding(
            (0.0, 0.001, -0.001, 0.0),
            threshold=0.01,
            pad_samples=3,
        )
        == ()
    )


def test_fixed_padding_rejects_negative_padding() -> None:
    with pytest.raises(ValueError, match="pad_samples must not be negative"):
        trim_silence_fixed_padding(
            (0.0, 0.5, 0.0),
            threshold=0.01,
            pad_samples=-1,
        )
