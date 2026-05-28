"""Synthetic grid-search source reconstruction helpers."""
from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from .geometry import wind_unit_vector
from .plume_gaussian import (
    _signed_wind_coordinates,
    gaussian_plume_concentration,
    sigma_y,
    sigma_z,
)


def _value(record: Any, name: str, default: Any = None) -> Any:
    """Return a named field from a mapping or pandas row; units depend on field."""
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _weather_from_observations(observations_df: pd.DataFrame) -> dict[str, Any]:
    """Return weather fields from an observation table; units follow column names."""
    first = observations_df.iloc[0]
    return {
        "wind_speed_mps": float(first.get("wind_speed_mps", 3.0)),
        "wind_dir_deg": float(first.get("wind_dir_deg", 0.0)),
        "stability_class": first.get("stability_class", "D"),
        "sigma_multiplier": float(first.get("sigma_multiplier", 1.0)),
    }


def simulate_observations(
    true_source: Mapping[str, Any],
    detectors_df: pd.DataFrame,
    weather_case: Mapping[str, Any],
    source_strength: float,
    seed: int | None = None,
    noise_fraction: float = 0.05,
    noise_floor_Bq_m3: float = 1.0e-8,
) -> pd.DataFrame:
    """Return synthetic detector observations in becquerels per cubic meter."""
    if noise_fraction < 0.0:
        raise ValueError("noise_fraction must be nonnegative.")
    if noise_floor_Bq_m3 <= 0.0:
        raise ValueError("noise_floor_Bq_m3 must be positive.")
    predicted = predict_detector_response_for_candidate(true_source, detectors_df, weather_case, source_strength)
    sigma = np.maximum(predicted["modeled_concentration_Bq_m3"].to_numpy() * noise_fraction, noise_floor_Bq_m3)
    if seed is None:
        noise = np.zeros(len(predicted), dtype=float)
    else:
        noise = np.random.default_rng(seed).normal(0.0, sigma)
    observed = np.clip(predicted["modeled_concentration_Bq_m3"].to_numpy() + noise, 0.0, None)
    out = predicted.rename(columns={"modeled_concentration_Bq_m3": "true_concentration_Bq_m3"}).copy()
    out["observed_concentration_Bq_m3"] = observed
    out["sigma_Bq_m3"] = sigma
    out["source_strength_Bq_s"] = float(source_strength)
    out["noise_fraction"] = float(noise_fraction)
    out["noise_floor_Bq_m3"] = float(noise_floor_Bq_m3)
    out["description"] = "synthetic inverse modeling observation"
    return out


def candidate_source_grid(x_min: float, x_max: float, y_min: float, y_max: float, spacing_m: float) -> pd.DataFrame:
    """Return candidate source grid coordinates in meters."""
    spacing = float(spacing_m)
    if spacing <= 0.0:
        raise ValueError("spacing_m must be positive.")
    if x_max < x_min or y_max < y_min:
        raise ValueError("grid maximums must be greater than or equal to minimums.")
    xs = np.arange(float(x_min), float(x_max) + spacing * 0.5, spacing)
    ys = np.arange(float(y_min), float(y_max) + spacing * 0.5, spacing)
    rows = []
    for x in xs:
        for y in ys:
            rows.append({"candidate_source_id": f"CS_{len(rows) + 1:05d}", "x_m": float(x), "y_m": float(y)})
    return pd.DataFrame(rows)


def predict_detector_response_for_candidate(
    candidate_source: Mapping[str, Any],
    detectors_df: pd.DataFrame,
    weather_case: Mapping[str, Any],
    Q: float,
) -> pd.DataFrame:
    """Return modeled detector concentration response in becquerels per cubic meter."""
    q = float(Q)
    if q < 0.0:
        raise ValueError("Q must be nonnegative.")
    wind_speed = float(_value(weather_case, "wind_speed_mps", 3.0))
    if wind_speed <= 0.0:
        raise ValueError("wind_speed_mps must be positive.")
    sigma_multiplier = float(_value(weather_case, "sigma_multiplier", 1.0))
    if sigma_multiplier <= 0.0:
        raise ValueError("sigma_multiplier must be positive.")
    wind_vector = wind_unit_vector(float(_value(weather_case, "wind_dir_deg", 0.0)))
    stability_class = str(_value(weather_case, "stability_class", "D"))
    source_xy = (float(_value(candidate_source, "x_m")), float(_value(candidate_source, "y_m")))

    rows: list[dict[str, Any]] = []
    for det in detectors_df.itertuples(index=False):
        coords = _signed_wind_coordinates(source_xy, (det.x_m, det.y_m), wind_vector)
        if coords["x_downwind_m"] <= 0.0:
            concentration = 0.0
            sy = float("nan")
            sz = float("nan")
        else:
            sy = sigma_y(coords["x_downwind_m"], stability_class) * sigma_multiplier
            sz = sigma_z(coords["x_downwind_m"], stability_class) * sigma_multiplier
            concentration = gaussian_plume_concentration(q, wind_speed, sy, sz, coords["y_crosswind_m"], det.z_m, 0.0)
        rows.append(
            {
                "candidate_source_id": _value(candidate_source, "candidate_source_id", ""),
                "source_x_m": source_xy[0],
                "source_y_m": source_xy[1],
                "detector_id": det.detector_id,
                "x_m": float(det.x_m),
                "y_m": float(det.y_m),
                "z_m": float(det.z_m),
                "x_downwind_m": coords["x_downwind_m"],
                "y_crosswind_m": coords["y_crosswind_m"],
                "sigma_y_m": sy,
                "sigma_z_m": sz,
                "response_per_Bq_s": concentration / q if q > 0.0 else 0.0,
                "modeled_concentration_Bq_m3": concentration,
                "wind_speed_mps": wind_speed,
                "wind_dir_deg": float(_value(weather_case, "wind_dir_deg", 0.0)),
                "stability_class": stability_class,
                "sigma_multiplier": sigma_multiplier,
            }
        )
    return pd.DataFrame(rows)


def estimate_Q_for_candidate(observations_df: pd.DataFrame, response_factors: Any, sigma: Any) -> float:
    """Return weighted least-squares source strength estimate in becquerels per second."""
    if observations_df.empty:
        raise ValueError("observations_df must not be empty.")
    y_col = "observed_concentration_Bq_m3" if "observed_concentration_Bq_m3" in observations_df.columns else "observation"
    y = np.asarray(observations_df[y_col], dtype=float)
    g = np.asarray(response_factors, dtype=float)
    s = np.asarray(sigma, dtype=float)
    if len(y) != len(g):
        raise ValueError("observations and response_factors must have the same length.")
    if np.any(s <= 0.0):
        raise ValueError("sigma values must be positive.")
    weights = 1.0 / (s * s)
    denominator = float(np.sum(weights * g * g))
    if denominator <= 0.0:
        return 0.0
    estimate = float(np.sum(weights * g * y) / denominator)
    return max(0.0, estimate)


def least_squares_source_grid(observations_df: pd.DataFrame, candidate_sources_df: pd.DataFrame) -> pd.DataFrame:
    """Return least-squares source grid with J values in squared normalized residual units."""
    if observations_df.empty:
        raise ValueError("observations_df must not be empty.")
    if candidate_sources_df.empty:
        raise ValueError("candidate_sources_df must not be empty.")
    weather = _weather_from_observations(observations_df)
    detector_cols = ["detector_id", "x_m", "y_m", "z_m"]
    detectors = observations_df[detector_cols].drop_duplicates("detector_id").copy()
    y = observations_df["observed_concentration_Bq_m3"].to_numpy(dtype=float)
    sigma = observations_df["sigma_Bq_m3"].to_numpy(dtype=float)

    rows: list[dict[str, Any]] = []
    for candidate in candidate_sources_df.itertuples(index=False):
        candidate_record = candidate._asdict()
        predicted_unit = predict_detector_response_for_candidate(candidate_record, detectors, weather, 1.0)
        response = predicted_unit["response_per_Bq_s"].to_numpy(dtype=float)
        q_hat = estimate_Q_for_candidate(observations_df, response, sigma)
        residual = y - q_hat * response
        j_value = float(np.sum((residual / sigma) ** 2))
        rows.append(
            {
                "candidate_source_id": candidate.candidate_source_id,
                "x_m": float(candidate.x_m),
                "y_m": float(candidate.y_m),
                "Q_hat_Bq_s": q_hat,
                "J": j_value,
                "description": "synthetic inverse modeling grid point",
            }
        )
    return pd.DataFrame(rows)


def likelihood_map(reconstruction_grid_df: pd.DataFrame) -> pd.DataFrame:
    """Return relative likelihood values from least-squares J with dimensionless likelihood."""
    if reconstruction_grid_df.empty:
        raise ValueError("reconstruction_grid_df must not be empty.")
    out = reconstruction_grid_df.copy()
    j_min = float(out["J"].min())
    out["relative_likelihood"] = np.exp(-0.5 * (out["J"] - j_min))
    total = float(out["relative_likelihood"].sum())
    out["normalized_likelihood"] = out["relative_likelihood"] / total if total > 0.0 else 0.0
    return out


def estimate_source_location(likelihood_df: pd.DataFrame) -> dict[str, Any]:
    """Return maximum-likelihood source estimate with coordinates in meters."""
    if likelihood_df.empty:
        raise ValueError("likelihood_df must not be empty.")
    row = likelihood_df.sort_values(["relative_likelihood", "J"], ascending=[False, True]).iloc[0]
    return {
        "candidate_source_id": row["candidate_source_id"],
        "estimated_x_m": float(row["x_m"]),
        "estimated_y_m": float(row["y_m"]),
        "estimated_Q_Bq_s": float(row["Q_hat_Bq_s"]),
        "J": float(row["J"]),
        "relative_likelihood": float(row["relative_likelihood"]),
        "description": "synthetic inverse modeling estimate",
    }


def localization_error(true_source_xy: tuple[float, float], estimated_source_xy: tuple[float, float]) -> float:
    """Return source localization error in meters."""
    dx = float(estimated_source_xy[0]) - float(true_source_xy[0])
    dy = float(estimated_source_xy[1]) - float(true_source_xy[1])
    return math.hypot(dx, dy)
