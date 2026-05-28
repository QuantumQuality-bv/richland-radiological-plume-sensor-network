"""Steady Gaussian plume calculations for synthetic public study cases."""
from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

import pandas as pd

from .geometry import classify_receptor, wind_coordinates


def _validate_nonnegative(name: str, value: float) -> float:
    """Return value as a float after nonnegative validation."""
    out = float(value)
    if out < 0.0:
        raise ValueError(f"{name} must be nonnegative.")
    return out


def _validate_positive(name: str, value: float) -> float:
    """Return value as a float after positive validation."""
    out = float(value)
    if out <= 0.0:
        raise ValueError(f"{name} must be positive.")
    return out


def _signed_wind_coordinates(
    source_xy: tuple[float, float],
    receptor_xy: tuple[float, float],
    wind_vector: tuple[float, float],
) -> dict[str, float]:
    """Return signed downwind and crosswind coordinates in meters."""
    dx = float(receptor_xy[0]) - float(source_xy[0])
    dy = float(receptor_xy[1]) - float(source_xy[1])
    ux, uy = float(wind_vector[0]), float(wind_vector[1])
    norm = math.hypot(ux, uy)
    if norm <= 0.0:
        raise ValueError("wind_vector must be nonzero.")
    ux, uy = ux / norm, uy / norm
    x_downwind = dx * ux + dy * uy
    y_crosswind = dx * (-uy) + dy * ux
    return {
        "dx_m": dx,
        "dy_m": dy,
        "x_downwind_m": x_downwind,
        "y_crosswind_m": y_crosswind,
        "distance_m": math.hypot(dx, dy),
    }


def sigma_y(x_m: float, stability_class: str = "D") -> float:
    """Return baseline lateral dispersion coefficient sigma_y in meters."""
    x = _validate_positive("x_m", x_m)
    _ = stability_class
    return 0.08 * x * (1.0 + 0.0001 * x) ** -0.5


def sigma_z(x_m: float, stability_class: str = "D") -> float:
    """Return baseline vertical dispersion coefficient sigma_z in meters."""
    x = _validate_positive("x_m", x_m)
    _ = stability_class
    return 0.06 * x * (1.0 + 0.0015 * x) ** -0.5


def centerline_ground_concentration(
    Q_bq_s: float, u_mps: float, sigma_y_m: float, sigma_z_m: float
) -> float:
    """Return ground-level centerline concentration in becquerels per cubic meter."""
    q = _validate_nonnegative("Q_bq_s", Q_bq_s)
    u = _validate_positive("u_mps", u_mps)
    sy = _validate_positive("sigma_y_m", sigma_y_m)
    sz = _validate_positive("sigma_z_m", sigma_z_m)
    return q / (math.pi * u * sy * sz)


def crosswind_factor(y_m: float, sigma_y_m: float) -> float:
    """Return dimensionless Gaussian crosswind attenuation."""
    sy = _validate_positive("sigma_y_m", sigma_y_m)
    return math.exp(-(float(y_m) ** 2) / (2.0 * sy * sy))


def vertical_factor(z_m: float, H_m: float, sigma_z_m: float) -> float:
    """Return dimensionless reflected-plume vertical factor."""
    sz = _validate_positive("sigma_z_m", sigma_z_m)
    z = float(z_m)
    h = float(H_m)
    return math.exp(-((z - h) ** 2) / (2.0 * sz * sz)) + math.exp(-((z + h) ** 2) / (2.0 * sz * sz))


def gaussian_plume_concentration(
    Q_bq_s: float,
    u_mps: float,
    sigma_y_m: float,
    sigma_z_m: float,
    y_m: float,
    z_m: float,
    H_m: float,
) -> float:
    """Return Gaussian plume concentration in becquerels per cubic meter."""
    q = _validate_nonnegative("Q_bq_s", Q_bq_s)
    u = _validate_positive("u_mps", u_mps)
    sy = _validate_positive("sigma_y_m", sigma_y_m)
    sz = _validate_positive("sigma_z_m", sigma_z_m)
    coefficient = q / (2.0 * math.pi * u * sy * sz)
    return coefficient * crosswind_factor(y_m, sy) * vertical_factor(z_m, H_m, sz)


def concentration_at_receptor(
    source_xy: tuple[float, float],
    receptor_xyz: tuple[float, float, float],
    wind_vector: tuple[float, float],
    Q_bq_s: float,
    u_mps: float,
    H_m: float = 0.0,
    stability_class: str = "D",
) -> dict[str, Any]:
    """Return Gaussian plume concentration details for one synthetic receptor."""
    q = _validate_nonnegative("Q_bq_s", Q_bq_s)
    u = _validate_positive("u_mps", u_mps)
    receptor_xy = (float(receptor_xyz[0]), float(receptor_xyz[1]))
    coords = wind_coordinates(source_xy, receptor_xy, wind_vector)
    classification = classify_receptor(coords["x_downwind_m"])
    z = float(receptor_xyz[2])

    if coords["x_downwind_m"] <= 0.0:
        sy = float("nan")
        sz = float("nan")
        concentration = 0.0
    else:
        sy = sigma_y(coords["x_downwind_m"], stability_class)
        sz = sigma_z(coords["x_downwind_m"], stability_class)
        concentration = gaussian_plume_concentration(
            q, u, sy, sz, coords["y_crosswind_m"], z, H_m
        )

    return {
        "x_downwind_m": coords["x_downwind_m"],
        "y_crosswind_m": coords["y_crosswind_m"],
        "z_m": z,
        "sigma_y_m": sy,
        "sigma_z_m": sz,
        "concentration_bq_m3": concentration,
        "classification": classification,
    }


def evaluate_receptor_grid(
    source_xy: tuple[float, float],
    receptors_df: pd.DataFrame,
    wind_vector: tuple[float, float],
    Q_bq_s: float,
    u_mps: float,
    H_m: float = 0.0,
    stability_class: str = "D",
) -> pd.DataFrame:
    """Evaluate Gaussian plume concentrations for a receptor table."""
    rows: list[dict[str, Any]] = []
    for row in receptors_df.itertuples(index=False):
        result = concentration_at_receptor(
            source_xy,
            (row.x_m, row.y_m, row.z_m),
            wind_vector,
            Q_bq_s,
            u_mps,
            H_m=H_m,
            stability_class=stability_class,
        )
        rows.append(
            {
                "receptor_id": row.receptor_id,
                "x_m": float(row.x_m),
                "y_m": float(row.y_m),
                "z_m": float(row.z_m),
                **result,
            }
        )
    return pd.DataFrame(rows)


def evaluate_concentration_grid(
    source_xy: tuple[float, float],
    x_values: Iterable[float],
    y_values: Iterable[float],
    wind_vector: tuple[float, float],
    Q_bq_s: float,
    u_mps: float,
    z_m: float = 0.0,
    H_m: float = 0.0,
    stability_class: str = "D",
) -> pd.DataFrame:
    """Evaluate a long-format Gaussian plume concentration grid."""
    rows: list[dict[str, Any]] = []
    for x in x_values:
        for y in y_values:
            result = concentration_at_receptor(
                source_xy,
                (float(x), float(y), z_m),
                wind_vector,
                Q_bq_s,
                u_mps,
                H_m=H_m,
                stability_class=stability_class,
            )
            rows.append(
                {
                    "x_m": float(x),
                    "y_m": float(y),
                    "z_m": float(z_m),
                    "x_downwind_m": result["x_downwind_m"],
                    "y_crosswind_m": result["y_crosswind_m"],
                    "concentration_bq_m3": result["concentration_bq_m3"],
                    "classification": result["classification"],
                }
            )
    return pd.DataFrame(rows)
