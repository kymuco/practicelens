import math
import statistics

from practicelens.domain.models import AnalysisConfig
from practicelens.features import extract_feature_bundle
from practicelens.io.models import LoadedAudio


def test_extract_feature_bundle_produces_frame_aligned_outputs() -> None:
    sample_rate = 16_000
    duration_samples = 4096
    samples = tuple(
        0.4 * math.sin(2.0 * math.pi * 220.0 * index / sample_rate)
        for index in range(duration_samples)
    )
    audio = LoadedAudio(samples=samples, sample_rate=sample_rate)
    config = AnalysisConfig(frame_length=1024, hop_length=256)

    bundle = extract_feature_bundle(audio, config)

    assert bundle.frame_count > 0
    assert len(bundle.energy_curve) == bundle.frame_count
    assert len(bundle.zero_crossing_rate) == bundle.frame_count
    assert len(bundle.pitch_contour_hz) == bundle.frame_count
    assert len(bundle.voiced_mask) == bundle.frame_count
    assert any(bundle.voiced_mask)


def test_extract_feature_bundle_estimates_reasonable_pitch() -> None:
    sample_rate = 16_000
    samples = tuple(
        0.5 * math.sin(2.0 * math.pi * 220.0 * index / sample_rate)
        for index in range(8192)
    )
    audio = LoadedAudio(samples=samples, sample_rate=sample_rate)
    config = AnalysisConfig(frame_length=1024, hop_length=256)

    bundle = extract_feature_bundle(audio, config)
    voiced_pitches = [pitch for pitch in bundle.pitch_contour_hz if pitch > 0.0]

    assert voiced_pitches
    median_pitch = statistics.median(voiced_pitches)
    assert 200.0 <= median_pitch <= 240.0
