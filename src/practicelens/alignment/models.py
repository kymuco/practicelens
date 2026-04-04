from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AlignmentPair:
    """One aligned reference/take frame pair."""

    reference_index: int
    take_index: int
    local_cost: float


@dataclass(slots=True, frozen=True)
class AlignmentPath:
    """Stable alignment result for one reference-aware comparison."""

    pairs: tuple[AlignmentPair, ...]
    total_cost: float
    coverage_ratio: float

    @property
    def pair_count(self) -> int:
        return len(self.pairs)
