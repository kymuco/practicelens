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
    """Return activity with fixed edge context independent of source-file boundaries."""

    if pad_samples < 0:
        raise ValueError("pad_samples must be non-negative")

    values = tuple(samples)
    if not values:
        return ()

    start = 0
    end = len(values)

    while start < end and abs(values[start]) < threshold:
        start += 1
    while end > start and abs(values[end - 1]) < threshold:
        end -= 1

    if start == end:
        return ()

    context_start = max(0, start - pad_samples)
    context_end = min(len(values), end + pad_samples)

    available_before = start - context_start
    available_after = context_end - end
    missing_before = pad_samples - available_before
    missing_after = pad_samples - available_after

    return (
        *((0.0,) * missing_before),
        *values[context_start:context_end],
        *((0.0,) * missing_after),
    )
