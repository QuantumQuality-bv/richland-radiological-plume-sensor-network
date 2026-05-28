"""Simplified transient puff proxy for synthetic detector time series."""
from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

import pandas as pd

from .geometry import wind_coordinates


def _validate_positive(name: str, value: float) -> float:
    """Return value as a float after positive validation."""
    out = float(value)
    if out <= 0.0:
        raise ValueError(f"{name} must be positive.")
    return out


def puff_centroid(
    source_xy: tuple[float, float],
    wind_vector: tuple[float, float],
    wind_speed_mps: float,
    time_s: float,
) -> tuple[float, float]:
    """Return puff centroid x/y coordinates in meters after time_s seconds."""
    speed = _validate_positive("wind_speed_mps", wind_speed_mps)
    time = float(time_s)
    if time < 0.0:
        raise ValueError("time_s must be nonnegative.")
    ux, uy = float(wind_vector[0]), float(wind_vector[1])
    norm = math.hypot(ux, uy)
    if norm <= 0.0:
        raise ValueError("wind_vector must be nonzero.")
    ux, uy = ux / norm, uy / norm
    return (
        float(source_xy[0]) + speed * time * ux,
        float(source_xy[1]) + speed * time * uy,
    )


def arrival_time(x_downwind_m: float, wind_speed_mps: float) -> float | None:
    """Return downwind puff arrival time in seconds, or None for upwind positions."""
    speed = _validate_positive("wind_speed_mps", wind_speed_mps)
    x = float(x_downwind_m)
    if x < 0.0:
        return None
    return x / speed


def puff_concentration_proxy(
    detector_xy: tuple[float, float],
    centroid_xy: tuple[float, float],
    spread_m: float,
    strength: float,
) -> float:
    """Return a simple two-dimensional Gaussian puff concentration proxy."""
    spread = _validate_positive("spread_m", spread_m)
    source_strength = float(strength)
    if source_strength < 0.0:
        raise ValueError("strength must be nonnegative.")
    dx = float(detector_xy[0]) - float(centroid_xy[0])
    dy = float(detector_xy[1]) - float(centroid_xy[1])
    r2 = dx * dx + dy * dy
    return source_strength * math.exp(-r2 / (2.0 * spread * spread))


def evaluate_detector_time_series(
    source_xy: tuple[float, float],
    detectors_df: pd.DataFrame,
    wind_vector: tuple[float, float],
    wind_speed_mps: float,
    time_grid_s: Iterable[float],
    spread_m: float = 200.0,
    strength: float = 1.0,
) -> pd.DataFrame:
    """Evaluate detector puff proxy concentrations over time."""
    _validate_positive("wind_speed_mps", wind_speed_mps)
    _validate_positive("spread_m", spread_m)
    rows: list[dict[str, Any]] = []
    for det in detectors_df.itertuples(index=False):
        detector_xy = (float(det.x_m), float(det.y_m))
        coords = wind_coordinates(source_xy, detector_xy, wind_vector)
        detector_arrival = arrival_time(coords["x_downwind_m"], wind_speed_mps)
        for time_s in time_grid_s:
            centroid = puff_centroid(source_xy, wind_vector, wind_speed_mps, float(time_s))
            rows.append(
                {
                    "detector_id": det.detector_id,
                    "time_s": float(time_s),
                    "centroid_x_m": centroid[0],
                    "centroid_y_m": centroid[1],
                    "detector_x_m": detector_xy[0],
                    "detector_y_m": detector_xy[1],
                    "concentration_proxy": puff_concentration_proxy(
                        detector_xy, centroid, spread_m, strength
                    ),
                    "arrival_time_s": detector_arrival,
                }
            )
    return pd.DataFrame(rows)
