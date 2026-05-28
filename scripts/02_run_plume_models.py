from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.geometry import wind_coordinates, wind_unit_vector
from src.plume_gaussian import (
    centerline_ground_concentration,
    evaluate_concentration_grid,
    evaluate_receptor_grid,
    gaussian_plume_concentration,
    sigma_y,
    sigma_z,
)
from src.plume_puff import arrival_time, evaluate_detector_time_series
from src.source_term import evaluate_source_table


def _add_concentration_alias(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with the legacy mixed-case concentration alias."""
    out = df.copy()
    out["concentration_Bq_m3"] = out["concentration_bq_m3"]
    return out


def _add_metadata(df: pd.DataFrame, source_id: str, scenario_id: str, weather_id: str) -> pd.DataFrame:
    """Return a copy with baseline synthetic scenario metadata columns."""
    out = df.copy()
    out.insert(0, "weather_id", weather_id)
    out.insert(0, "scenario_id", scenario_id)
    out.insert(0, "source_id", source_id)
    return out


def _steady_detector_concentration(
    source_xy: tuple[float, float],
    detector_xy: tuple[float, float],
    wind_vector: tuple[float, float],
    q_dot_bq_s: float,
    wind_speed_mps: float,
    stability_class: str,
    H_m: float,
) -> float:
    """Return ground-level steady concentration used for Phase 4 compatibility."""
    coords = wind_coordinates(source_xy, detector_xy, wind_vector)
    if coords["x_downwind_m"] <= 0.0:
        return 0.0
    sy = sigma_y(coords["x_downwind_m"], stability_class)
    sz = sigma_z(coords["x_downwind_m"], stability_class)
    return gaussian_plume_concentration(
        q_dot_bq_s,
        wind_speed_mps,
        sy,
        sz,
        coords["y_crosswind_m"],
        0.0,
        H_m,
    )


def main() -> None:
    """Run Phase 3 plume models and write synthetic CSV outputs."""
    synthetic_dir = ROOT / "data" / "synthetic"
    out_dir = ROOT / "data" / "processed" / "plume_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = evaluate_source_table(pd.read_csv(synthetic_dir / "synthetic_sources.csv"))
    weather = pd.read_csv(synthetic_dir / "weather_cases.csv")
    receptors = pd.read_csv(synthetic_dir / "synthetic_receptors.csv")
    detectors = pd.read_csv(synthetic_dir / "candidate_detectors.csv")

    source = sources.loc[sources["source_id"] == "SRC_001"].iloc[0]
    weather_case = weather.loc[weather["weather_id"] == "W1"].iloc[0]
    source_xy = (float(source.x_m), float(source.y_m))
    source_id = str(source.source_id)
    scenario_id = str(source.scenario_id)
    weather_id = str(weather_case.weather_id)
    wind_speed = float(weather_case.wind_speed_mps)
    wind_vector = wind_unit_vector(float(weather_case.wind_dir_deg))
    stability_class = str(weather_case.stability_class)
    release_height = float(source.z_m)
    q_dot = float(source.Q_dot_Bq_s)

    written: list[Path] = []

    plume_receptors = evaluate_receptor_grid(
        source_xy,
        receptors,
        wind_vector,
        q_dot,
        wind_speed,
        H_m=release_height,
        stability_class=stability_class,
    )
    plume_receptors = _add_concentration_alias(plume_receptors)
    plume_receptors = _add_metadata(plume_receptors, source_id, scenario_id, weather_id)
    plume_receptor_cols = [
        "source_id",
        "scenario_id",
        "weather_id",
        "receptor_id",
        "x_m",
        "y_m",
        "z_m",
        "x_downwind_m",
        "y_crosswind_m",
        "sigma_y_m",
        "sigma_z_m",
        "concentration_bq_m3",
        "classification",
        "concentration_Bq_m3",
    ]
    path = out_dir / "plume_receptors.csv"
    plume_receptors[plume_receptor_cols].to_csv(path, index=False)
    written.append(path)

    plume_grid = evaluate_concentration_grid(
        source_xy,
        np.arange(-500.0, 4000.0 + 100.0, 100.0),
        np.arange(-1000.0, 1000.0 + 100.0, 100.0),
        wind_vector,
        q_dot,
        wind_speed,
        z_m=0.0,
        H_m=release_height,
        stability_class=stability_class,
    )
    plume_grid = _add_concentration_alias(plume_grid)
    plume_grid = _add_metadata(plume_grid, source_id, scenario_id, weather_id)
    path = out_dir / "plume_grid.csv"
    plume_grid.to_csv(path, index=False)
    written.append(path)

    centerline = evaluate_concentration_grid(
        source_xy,
        np.arange(100.0, 4000.0 + 100.0, 100.0),
        [0.0],
        wind_vector,
        q_dot,
        wind_speed,
        z_m=0.0,
        H_m=release_height,
        stability_class=stability_class,
    )
    centerline = _add_concentration_alias(centerline)
    centerline = _add_metadata(centerline, source_id, scenario_id, weather_id)
    path = out_dir / "centerline_profile.csv"
    centerline.to_csv(path, index=False)
    written.append(path)

    crosswind = evaluate_concentration_grid(
        source_xy,
        [1000.0],
        np.arange(-1000.0, 1000.0 + 50.0, 50.0),
        wind_vector,
        q_dot,
        wind_speed,
        z_m=0.0,
        H_m=release_height,
        stability_class=stability_class,
    )
    crosswind = _add_concentration_alias(crosswind)
    crosswind = _add_metadata(crosswind, source_id, scenario_id, weather_id)
    path = out_dir / "crosswind_profile.csv"
    crosswind.to_csv(path, index=False)
    written.append(path)

    comparison_rows = []
    for multiplier in [0.65, 1.00, 1.50]:
        for x_m in [500.0, 1000.0, 2000.0, 3000.0]:
            sy = sigma_y(x_m, stability_class) * multiplier
            sz = sigma_z(x_m, stability_class) * multiplier
            concentration = centerline_ground_concentration(q_dot, wind_speed, sy, sz)
            comparison_rows.append(
                {
                    "source_id": source_id,
                    "scenario_id": scenario_id,
                    "weather_id": weather_id,
                    "sigma_multiplier": multiplier,
                    "x_m": x_m,
                    "y_m": 0.0,
                    "z_m": 0.0,
                    "sigma_y_m": sy,
                    "sigma_z_m": sz,
                    "concentration_bq_m3": concentration,
                    "concentration_Bq_m3": concentration,
                }
            )
    path = out_dir / "dispersion_comparison.csv"
    pd.DataFrame(comparison_rows).to_csv(path, index=False)
    written.append(path)

    arrival_rows = []
    steady_concentrations = {}
    for det in detectors.itertuples(index=False):
        detector_xy = (float(det.x_m), float(det.y_m))
        coords = wind_coordinates(source_xy, detector_xy, wind_vector)
        t_arrival = arrival_time(coords["x_downwind_m"], wind_speed)
        steady_concentrations[det.detector_id] = _steady_detector_concentration(
            source_xy,
            detector_xy,
            wind_vector,
            q_dot,
            wind_speed,
            stability_class,
            release_height,
        )
        arrival_rows.append(
            {
                "source_id": source_id,
                "scenario_id": scenario_id,
                "weather_id": weather_id,
                "detector_id": det.detector_id,
                "x_downwind_m": coords["x_downwind_m"],
                "y_crosswind_m": coords["y_crosswind_m"],
                "arrival_time_s": t_arrival,
                "classification": "upwind" if t_arrival is None else "downwind",
            }
        )
    path = out_dir / "puff_arrival_times.csv"
    pd.DataFrame(arrival_rows).to_csv(path, index=False)
    written.append(path)

    finite_arrivals = [
        row["arrival_time_s"]
        for row in arrival_rows
        if row["arrival_time_s"] is not None and row["arrival_time_s"] <= 1200.0
    ]
    time_grid_s = np.array(
        sorted(set(np.round(np.concatenate([np.arange(0.0, 1200.0 + 60.0, 60.0), finite_arrivals]), 6)))
    )
    puff_timeseries = evaluate_detector_time_series(
        source_xy,
        detectors,
        wind_vector,
        wind_speed,
        time_grid_s,
        spread_m=200.0,
        strength=1.0,
    )
    puff_timeseries["source_id"] = source_id
    puff_timeseries["scenario_id"] = scenario_id
    puff_timeseries["weather_id"] = weather_id
    puff_timeseries["x_m"] = puff_timeseries["detector_x_m"]
    puff_timeseries["y_m"] = puff_timeseries["detector_y_m"]
    detector_z = detectors.set_index("detector_id")["z_m"].astype(float).to_dict()
    puff_timeseries["z_m"] = puff_timeseries["detector_id"].map(detector_z)
    puff_timeseries["concentration_Bq_m3"] = [
        row.concentration_proxy * steady_concentrations[row.detector_id]
        for row in puff_timeseries.itertuples(index=False)
    ]
    path = out_dir / "puff_detector_timeseries.csv"
    puff_timeseries.to_csv(path, index=False)
    written.append(path)

    print("Phase 3 plume modeling complete.")
    for output in written:
        print(f"Wrote: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
