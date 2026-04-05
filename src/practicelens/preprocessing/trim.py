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
