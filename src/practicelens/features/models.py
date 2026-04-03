from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class FeatureBundle:
    """Deterministic feature bundle extracted from one audio asset."""

    time_axis_s: tuple[float, ...]
    energy_curve: tuple[float, ...]
    zero_crossing_rate: tuple[float, ...]
    pitch_contour_hz: tuple[float, ...]
    voiced_mask: tuple[bool, ...]
    onset_times_s: tuple[float, ...]
    estimated_tempo_bpm: float | None

    @property
    def frame_count(self) -> int:
        return len(self.time_axis_s)
