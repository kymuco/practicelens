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
    """Trim silence while preserving a fixed-width context around active audio.

    Unlike :func:`trim_silence`, missing context at a file boundary is
    represented by explicit zeros. Equivalent performances therefore keep the
    same pre/post context even when the recorded WAV begins or ends closer to
    the active signal.
    """

    if pad_samples < 0:
        raise ValueError("pad_samples must not be negative")

    values = tuple(samples)
    if not values:
        return ()

    active_start = 0
    active_end = len(values)

    while active_start < active_end and abs(values[active_start]) < threshold:
        active_start += 1

    if active_start == active_end:
        return ()

    while active_end > active_start and abs(values[active_end - 1]) < threshold:
        active_end -= 1

    context_start = max(0, active_start - pad_samples)
    context_end = min(len(values), active_end + pad_samples)

    available_left = active_start - context_start
    available_right = context_end - active_end
    missing_left = pad_samples - available_left
    missing_right = pad_samples - available_right

    return (
        (0.0,) * missing_left
        + values[context_start:context_end]
        + (0.0,) * missing_right
    )
