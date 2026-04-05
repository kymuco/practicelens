from __future__ import annotations

from collections.abc import Iterable


def peak_normalize(samples: Iterable[float], *, floor: float = 1e-9) -> tuple[float, ...]:
    """Scale samples by their peak absolute value."""

    values = tuple(samples)
    if not values:
        return ()
    peak = max(abs(sample) for sample in values)
    if peak <= floor:
        return values
    return tuple(sample / peak for sample in values)
