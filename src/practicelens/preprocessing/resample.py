from __future__ import annotations

from typing import Iterable


def resample_linear(
    samples: Iterable[float],
    original_rate: int,
    target_rate: int,
) -> tuple[float, ...]:
    """Resample 1D audio with simple linear interpolation."""

    values = tuple(samples)
    if not values:
        return ()
    if original_rate <= 0 or target_rate <= 0:
        raise ValueError("sample rates must be positive")
    if original_rate == target_rate:
        return values

    output_length = max(1, round(len(values) * target_rate / float(original_rate)))
    if output_length == 1:
        return (values[0],)

    scale = (len(values) - 1) / float(output_length - 1)
    result: list[float] = []
    for index in range(output_length):
        source_position = index * scale
        left_index = int(source_position)
        right_index = min(left_index + 1, len(values) - 1)
        fraction = source_position - left_index
        interpolated = values[left_index] * (1.0 - fraction) + values[right_index] * fraction
        result.append(interpolated)
    return tuple(result)
