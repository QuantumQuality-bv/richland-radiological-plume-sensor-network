"""Geometry and wind-coordinate helpers."""
from __future__ import annotations
import math
import pandas as pd

def distance_2d(source: tuple[float, float], receptor: tuple[float, float]) -> float:
    """Return two-dimensional distance in meters."""
    return math.hypot(float(receptor[0])-float(source[0]), float(receptor[1])-float(source[1]))

def distance_3d(source: tuple[float, float, float], receptor: tuple[float, float, float]) -> float:
    """Return three-dimensional distance in meters."""
    dx = float(receptor[0])-float(source[0])
    dy = float(receptor[1])-float(source[1])
    dz = float(receptor[2])-float(source[2])
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def wind_unit_vector(theta_degrees: float) -> tuple[float, float]:
    """Return a dimensionless wind-direction unit vector from degrees."""
    theta = math.radians(float(theta_degrees))
    return (math.cos(theta), math.sin(theta))

def wind_coordinates(source: tuple[float, float], receptor: tuple[float, float], wind_vector: tuple[float, float]) -> dict[str, float]:
    """Return downwind and crosswind coordinates in meters."""
    dx = float(receptor[0])-float(source[0])
    dy = float(receptor[1])-float(source[1])
    ux, uy = wind_vector
    n = math.hypot(ux, uy)
    if n <= 0:
        raise ValueError('wind_vector must be nonzero.')
    ux, uy = ux/n, uy/n
    x_downwind = dx*ux + dy*uy
    d2 = dx*dx + dy*dy
    y_crosswind = math.sqrt(max(0.0, d2 - x_downwind*x_downwind))
    return {'dx_m': dx, 'dy_m': dy, 'x_downwind_m': x_downwind, 'y_crosswind_m': y_crosswind, 'distance_m': math.sqrt(d2)}

def classify_receptor(x_downwind: float, tolerance: float = 1e-9) -> str:
    """Return receptor class from downwind distance in meters."""
    if x_downwind > tolerance:
        return 'downwind'
    if x_downwind < -tolerance:
        return 'upwind'
    return 'crosswind'

def evaluate_receptor_geometry(source_xy: tuple[float, float], receptors_df: pd.DataFrame, wind_vector: tuple[float, float]) -> pd.DataFrame:
    """Return receptor geometry table with distances in meters."""
    rows = []
    for row in receptors_df.itertuples(index=False):
        out = wind_coordinates(source_xy, (row.x_m, row.y_m), wind_vector)
        out['receptor_id'] = row.receptor_id
        out['classification'] = classify_receptor(out['x_downwind_m'])
        rows.append(out)
    return pd.DataFrame(rows)
