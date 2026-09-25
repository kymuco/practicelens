from __future__ import annotations

import pytest

from practicelens.application import OfflineReferenceAnalysisPipeline
from practicelens.domain.models import AnalysisConfig
from practicelens.io.models import LoadedAudio
from practicelens.preprocessing import remove_dc_offset


def test_pipeline_preparation_has_canonical_recording_start_origin() -> None:
    config = AnalysisConfig(
        target_sample_rate=16_000,
        frame_length=1_024,
        hop_length=256,
        segment_duration_s=1.0,
    )
    pipeline = OfflineReferenceAnalysisPipeline()

    phrase = tuple(
        0.0
        if index < 9 or index == 1_999
        else 0.2 * (-1.0 if (index - 9) % 2 else 1.0)
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
    assert prepared_base.samples
    assert abs(prepared_base.samples[0]) >= 0.01


def test_dc_offset_removal_is_constant_shift_invariant() -> None:
    samples = (-0.3, -0.1, 0.0, 0.2, 0.4)
    shifted = tuple(sample + 0.01 for sample in samples)

    centered = remove_dc_offset(samples)
    centered_shifted = remove_dc_offset(shifted)

    assert centered_shifted == pytest.approx(centered, abs=1e-12)


def test_pipeline_preparation_is_invariant_to_small_dc_sensor_bias() -> None:
    config = AnalysisConfig(
        target_sample_rate=16_000,
        frame_length=1_024,
        hop_length=256,
        segment_duration_s=1.0,
    )
    pipeline = OfflineReferenceAnalysisPipeline()

    phrase = tuple(
        0.2 * (-1.0 if index % 2 else 1.0)
        for index in range(2_000)
    )
    base = LoadedAudio(samples=phrase, sample_rate=16_000)
    biased = LoadedAudio(
        samples=tuple(sample + 0.01 for sample in phrase),
        sample_rate=16_000,
    )

    prepared_base = pipeline._prepare_audio(base, config)
    prepared_biased = pipeline._prepare_audio(biased, config)

    assert prepared_biased.samples == pytest.approx(
        prepared_base.samples,
        abs=1e-12,
    )


def test_dc_offset_removal_preserves_sub_floor_finite_window_mean() -> None:
    samples = (0.10005, -0.09995, 0.10005, -0.09995)

    centered = remove_dc_offset(samples)

    assert centered == samples
