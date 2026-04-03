from __future__ import annotations

import math
import statistics

from practicelens.domain.errors import FeatureExtractionError
from practicelens.domain.models import AnalysisConfig
from practicelens.features.models import FeatureBundle
from practicelens.io.models import LoadedAudio


def extract_feature_bundle(audio: LoadedAudio, config: AnalysisConfig) -> FeatureBundle:
    """Extract a bounded deterministic feature bundle from one mono signal."""

    if not audio.samples:
        raise FeatureExtractionError("audio sample payload is empty")
    if config.frame_length <= 1:
        raise FeatureExtractionError("frame_length must be greater than one")
    if config.hop_length <= 0:
        raise FeatureExtractionError("hop_length must be positive")

    frames = _frame_signal(audio.samples, config.frame_length, config.hop_length)
    if not frames:
        raise FeatureExtractionError("no frames were produced for feature extraction")

    time_axis = tuple(
        (start + len(frame) / 2.0) / audio.sample_rate for start, frame in frames
    )
    energy_curve = tuple(_frame_rms(frame) for _, frame in frames)
    zcr_curve = tuple(_zero_crossing_rate(frame) for _, frame in frames)

    max_energy = max(energy_curve) if energy_curve else 0.0
    energy_floor = max(0.01, max_energy * 0.1)
    pitch_curve = tuple(
        _estimate_pitch_hz(frame, audio.sample_rate, energy_floor=energy_floor)
        for _, frame in frames
    )
    voiced_mask = tuple(pitch > 0.0 for pitch in pitch_curve)
    onset_times = _detect_onsets(time_axis, energy_curve)
    tempo_bpm = _estimate_tempo_bpm(onset_times)

    return FeatureBundle(
        time_axis_s=time_axis,
        energy_curve=energy_curve,
        zero_crossing_rate=zcr_curve,
        pitch_contour_hz=pitch_curve,
        voiced_mask=voiced_mask,
        onset_times_s=onset_times,
        estimated_tempo_bpm=tempo_bpm,
    )


def _frame_signal(
    samples: tuple[float, ...],
    frame_length: int,
    hop_length: int,
) -> list[tuple[int, tuple[float, ...]]]:
    if len(samples) <= frame_length:
        return [(0, samples)]

    frames: list[tuple[int, tuple[float, ...]]] = []
    for start in range(0, len(samples) - frame_length + 1, hop_length):
        frame = samples[start : start + frame_length]
        frames.append((start, frame))

    last_start = len(samples) - frame_length
    if frames[-1][0] != last_start:
        frames.append((last_start, samples[last_start : last_start + frame_length]))
    return frames


def _frame_rms(frame: tuple[float, ...]) -> float:
    if not frame:
        return 0.0
    mean_square = sum(sample * sample for sample in frame) / float(len(frame))
    return math.sqrt(mean_square)


def _zero_crossing_rate(frame: tuple[float, ...]) -> float:
    if len(frame) < 2:
        return 0.0

    zero_crossings = 0
    previous = frame[0]
    for current in frame[1:]:
        if (previous < 0.0 <= current) or (previous > 0.0 >= current):
            zero_crossings += 1
        previous = current
    return zero_crossings / float(len(frame) - 1)


def _estimate_pitch_hz(
    frame: tuple[float, ...],
    sample_rate: int,
    *,
    min_freq_hz: float = 60.0,
    max_freq_hz: float = 500.0,
    energy_floor: float = 0.01,
) -> float:
    if len(frame) < 8:
        return 0.0
    rms = _frame_rms(frame)
    if rms < energy_floor:
        return 0.0

    centered = [sample - statistics.fmean(frame) for sample in frame]
    min_lag = max(1, int(sample_rate / max_freq_hz))
    max_lag = min(len(centered) - 2, int(sample_rate / min_freq_hz))
    if min_lag >= max_lag:
        return 0.0

    best_lag = 0
    best_corr = 0.0
    for lag in range(min_lag, max_lag + 1):
        corr = 0.0
        for index in range(len(centered) - lag):
            corr += centered[index] * centered[index + lag]
        if corr > best_corr:
            best_corr = corr
            best_lag = lag

    if best_lag <= 0 or best_corr <= 0.0:
        return 0.0
    return sample_rate / float(best_lag)


def _detect_onsets(
    time_axis_s: tuple[float, ...],
    energy_curve: tuple[float, ...],
) -> tuple[float, ...]:
    if len(energy_curve) < 2:
        return ()

    deltas = [
        energy_curve[index] - energy_curve[index - 1]
        for index in range(1, len(energy_curve))
    ]
    positive_deltas = [delta for delta in deltas if delta > 0.0]
    if not positive_deltas:
        return ()

    threshold = statistics.fmean(positive_deltas)
    if len(positive_deltas) > 1:
        threshold += statistics.pstdev(positive_deltas)

    onset_times: list[float] = []
    for index, delta in enumerate(deltas, start=1):
        if delta > threshold:
            onset_times.append(time_axis_s[index])
    return tuple(onset_times)


def _estimate_tempo_bpm(onset_times_s: tuple[float, ...]) -> float | None:
    if len(onset_times_s) < 2:
        return None
    intervals = [
        onset_times_s[index] - onset_times_s[index - 1]
        for index in range(1, len(onset_times_s))
        if onset_times_s[index] > onset_times_s[index - 1]
    ]
    if not intervals:
        return None
    median_interval = statistics.median(intervals)
    if median_interval <= 0.0:
        return None
    return 60.0 / median_interval
