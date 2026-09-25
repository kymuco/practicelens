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


def remove_dc_offset(samples: Iterable[float], *, floor: float = 1e-12) -> tuple[float, ...]:
    """Remove the constant (zero-frequency) component from an audio sample sequence."""

    values = tuple(samples)
    if not values:
        return ()

    offset = sum(values) / float(len(values))
    if abs(offset) <= floor:
        return values
    return tuple(sample - offset for sample in values)
