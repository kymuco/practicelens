from __future__ import annotations

from practicelens.application import OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.io.models import LoadedAudio
from practicelens.preprocessing import trim_silence_fixed_padding


def test_fixed_padding_is_independent_of_available_leading_silence() -> None:
    phrase = (0.0, 0.004, 0.012, 0.2, 0.1, 0.0)

    base = trim_silence_fixed_padding(
        phrase,
        threshold=0.01,
        pad_samples=3,
    )
    shifted = trim_silence_fixed_padding(
        (0.0,) * 12 + phrase,
        threshold=0.01,
        pad_samples=3,
    )

    assert base == shifted
    assert base[:3] == (0.0, 0.0, 0.0)
    assert base[-3:] == (0.0, 0.0, 0.0)
    assert base[3:-3] == (0.012, 0.2, 0.1)


def test_fixed_padding_is_independent_of_available_trailing_silence() -> None:
    phrase = (0.0, 0.02, 0.3, 0.015, 0.0)

    base = trim_silence_fixed_padding(
        phrase,
        threshold=0.01,
        pad_samples=4,
    )
    shifted = trim_silence_fixed_padding(
        phrase + (0.0,) * 20,
        threshold=0.01,
        pad_samples=4,
    )

    assert base == shifted


def test_pipeline_preparation_has_canonical_recording_start_origin() -> None:
    config = AnalysisConfig(
        target_sample_rate=16_000,
        frame_length=1_024,
        hop_length=256,
        segment_duration_s=1.0,
    )
    pipeline = OfflineReferenceAnalysisPipeline()

    phrase = tuple(
        0.0 if index < 9 else 0.2
        for index in range(2_000)
    )
    base = LoadedAudio(samples=phrase, sample_rate=16_000)
    shifted = LoadedAudio(
        samples=(0.0,) * 1_024 + phrase,
        sample_rate=16_000,
    )

    prepared_base = pipeline._prepare_audio(base, config)
    prepared_shifted = pipeline._prepare_audio(shifted, config)

    assert prepared_base.samples == prepared_shifted.samples
    assert prepared_base.samples[:64] == (0.0,) * 64


def test_fixed_padding_rejects_negative_padding() -> None:
    try:
        trim_silence_fixed_padding(
            (0.0, 0.1, 0.0),
            threshold=0.01,
            pad_samples=-1,
        )
    except ValueError as exc:
        assert str(exc) == "pad_samples must be non-negative"
    else:
        raise AssertionError("expected negative pad_samples to fail")
