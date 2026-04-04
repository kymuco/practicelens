from __future__ import annotations

from math import isfinite

from practicelens.alignment.models import AlignmentPair, AlignmentPath
from practicelens.domain.errors import AlignmentError
from practicelens.features.models import FeatureBundle


def align_feature_bundles(reference: FeatureBundle, take: FeatureBundle) -> AlignmentPath:
    """Align two feature bundles with a bounded DTW path."""

    if reference.frame_count == 0 or take.frame_count == 0:
        raise AlignmentError("feature bundles must both contain at least one frame")

    ref_vectors = [_feature_vector(reference, index) for index in range(reference.frame_count)]
    take_vectors = [_feature_vector(take, index) for index in range(take.frame_count)]

    rows = reference.frame_count
    cols = take.frame_count
    costs = [[float("inf")] * cols for _ in range(rows)]
    backpointers: list[list[tuple[int, int] | None]] = [[None] * cols for _ in range(rows)]

    for row in range(rows):
        for col in range(cols):
            local_cost = _distance(ref_vectors[row], take_vectors[col])
            if row == 0 and col == 0:
                costs[row][col] = local_cost
                continue

            candidates: list[tuple[float, tuple[int, int]]] = []
            if row > 0:
                candidates.append((costs[row - 1][col], (row - 1, col)))
            if col > 0:
                candidates.append((costs[row][col - 1], (row, col - 1)))
            if row > 0 and col > 0:
                candidates.append((costs[row - 1][col - 1], (row - 1, col - 1)))

            previous_cost, previous = min(candidates, key=lambda item: item[0])
            costs[row][col] = local_cost + previous_cost
            backpointers[row][col] = previous

    row = rows - 1
    col = cols - 1
    reversed_pairs: list[AlignmentPair] = []
    while True:
        local_cost = _distance(ref_vectors[row], take_vectors[col])
        reversed_pairs.append(
            AlignmentPair(reference_index=row, take_index=col, local_cost=local_cost)
        )
        previous = backpointers[row][col]
        if previous is None:
            break
        row, col = previous

    pairs = tuple(reversed(reversed_pairs))
    unique_reference = {pair.reference_index for pair in pairs}
    unique_take = {pair.take_index for pair in pairs}
    coverage_ratio = min(
        len(unique_reference) / float(reference.frame_count),
        len(unique_take) / float(take.frame_count),
    )

    return AlignmentPath(
        pairs=pairs,
        total_cost=costs[rows - 1][cols - 1],
        coverage_ratio=coverage_ratio,
    )


def _feature_vector(bundle: FeatureBundle, index: int) -> tuple[float, float, float, float]:
    pitch = bundle.pitch_contour_hz[index]
    voiced = 1.0 if bundle.voiced_mask[index] else 0.0
    normalized_pitch = 0.0
    if pitch > 0.0 and isfinite(pitch):
        normalized_pitch = min(1.0, pitch / 500.0)
    return (
        normalized_pitch,
        min(1.0, max(0.0, bundle.energy_curve[index])),
        min(1.0, max(0.0, bundle.zero_crossing_rate[index] * 4.0)),
        voiced,
    )


def _distance(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> float:
    pitch_diff = abs(left[0] - right[0])
    energy_diff = abs(left[1] - right[1])
    zcr_diff = abs(left[2] - right[2])
    voiced_penalty = 0.4 if left[3] != right[3] else 0.0
    return pitch_diff * 0.55 + energy_diff * 0.25 + zcr_diff * 0.20 + voiced_penalty
