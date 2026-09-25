from __future__ import annotations

from collections.abc import Iterable


def trim_silence(
    samples: Iterable[float],
    *,
    threshold: float = 0.01,
    pad_samples: int = 0,
) -> tuple[float, ...]:
    """Trim leading and trailing silence using an absolute-amplitude threshold."""

    values = tuple(samples)
    if not values:
        return ()

    start = 0
    end = len(values)

    while start < end and abs(values[start]) < threshold:
        start += 1
    while end > start and abs(values[end - 1]) < threshold:
        end -= 1

    start = max(0, start - pad_samples)
    end = min(len(values), end + pad_samples)
    return values[start:end]


def trim_silence_fixed_padding(
    samples: Iterable[float],
    *,
    threshold: float = 0.01,
    pad_samples: int = 0,
) -> tuple[float, ...]:
    """Trim to activity, then add deterministic zero padding independent of file boundaries."""

    if pad_samples < 0:
        raise ValueError("pad_samples must be non-negative")

    trimmed = trim_silence(samples, threshold=threshold, pad_samples=0)
    if not trimmed:
        return ()

    if pad_samples == 0:
        return trimmed

    padding = (0.0,) * pad_samples
    return (*padding, *trimmed, *padding)
