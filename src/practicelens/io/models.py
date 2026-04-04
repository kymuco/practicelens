from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LoadedAudio:
    """Normalized mono audio loaded from a bounded local asset."""

    samples: tuple[float, ...]
    sample_rate: int
    source_channels: int = 1
    sample_width_bytes: int = 2

    @property
    def duration_s(self) -> float:
        if self.sample_rate <= 0:
            return 0.0
        return len(self.samples) / float(self.sample_rate)
