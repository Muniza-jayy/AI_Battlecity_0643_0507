"""Helpers for aligning tanks to tile lanes during movement."""

from __future__ import annotations


def lane_center_delta(coordinate: float, tile_size: int) -> float:
    """Return the distance from the current coordinate to the nearest tile center."""
    center = (round((coordinate - tile_size / 2) / tile_size) * tile_size) + tile_size / 2
    return center - coordinate


def is_near_lane_center(coordinate: float, tile_size: int, threshold: float) -> bool:
    """Return whether the coordinate is close enough to turn into a perpendicular lane."""
    return abs(lane_center_delta(coordinate, tile_size)) <= threshold


def step_toward_lane_center(coordinate: float, tile_size: int, max_step: float) -> float:
    """Move a coordinate toward the nearest lane center by at most one movement step."""
    delta = lane_center_delta(coordinate, tile_size)
    if abs(delta) <= max_step:
        return coordinate + delta
    return coordinate + max_step * (1 if delta > 0 else -1)


def align_toward_lane_center(
    coordinate: float,
    tile_size: int,
    max_step: float,
    threshold: float,
) -> float:
    """Nudge a coordinate toward the nearest tile center when already close."""
    delta = lane_center_delta(coordinate, tile_size)
    if abs(delta) > threshold:
        return coordinate

    if abs(delta) <= max_step:
        return coordinate + delta

    return coordinate + max_step * (1 if delta > 0 else -1)
