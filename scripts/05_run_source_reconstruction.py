from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.source_reconstruction import (
    candidate_source_grid,
    estimate_source_location,
    least_squares_source_grid,
    likelihood_map,
    localization_error,
    simulate_observations,
)
from src.source_term import evaluate_source_table


def main() -> None:
    """Run Phase 6 synthetic inverse modeling and write source-location CSV outputs."""
    synthetic_dir = ROOT / "data" / "synthetic"
    out_dir = ROOT / "data" / "processed" / "source_reconstruction_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = evaluate_source_table(pd.read_csv(synthetic_dir / "synthetic_sources.csv"))
    weather = pd.read_csv(synthetic_dir / "weather_cases.csv")
    detectors = pd.read_csv(synthetic_dir / "candidate_detectors.csv")

    true_source = sources[sources["scenario_id"] == "S6"].iloc[0].to_dict()
    weather_case = weather[weather["scenario_id"] == "S6"].iloc[0].to_dict()
    observations = simulate_observations(true_source, detectors, weather_case, true_source["Q_dot_Bq_s"], seed=None)
    observations.to_csv(out_dir / "synthetic_observations.csv", index=False)

    candidate_grid = candidate_source_grid(-500.0, 500.0, -500.0, 500.0, 50.0)
    candidate_grid.to_csv(out_dir / "candidate_source_grid.csv", index=False)

    least_squares = least_squares_source_grid(observations, candidate_grid)
    least_squares.to_csv(out_dir / "least_squares_grid.csv", index=False)

    likelihood = likelihood_map(least_squares)
    likelihood.to_csv(out_dir / "likelihood_grid.csv", index=False)

    estimate = estimate_source_location(likelihood)
    pd.DataFrame([estimate]).to_csv(out_dir / "source_estimate.csv", index=False)

    error_m = localization_error(
        (true_source["x_m"], true_source["y_m"]),
        (estimate["estimated_x_m"], estimate["estimated_y_m"]),
    )
    pd.DataFrame(
        [
            {
                "true_x_m": true_source["x_m"],
                "true_y_m": true_source["y_m"],
                "estimated_x_m": estimate["estimated_x_m"],
                "estimated_y_m": estimate["estimated_y_m"],
                "localization_error_m": error_m,
                "description": "synthetic inverse modeling localization error",
            }
        ]
    ).to_csv(out_dir / "localization_error_summary.csv", index=False)

    display_noise_seed = 20260519
    display_noise_level = 0.25
    display_detectors = detectors[detectors["detector_id"].isin(["D001", "D002", "D003", "D004", "D005"])].copy()
    noisy_observations = simulate_observations(
        true_source,
        display_detectors,
        weather_case,
        true_source["Q_dot_Bq_s"],
        seed=display_noise_seed,
        noise_fraction=display_noise_level,
    )
    noisy_observations.to_csv(out_dir / "noisy_display_observations.csv", index=False)
    noisy_least_squares = least_squares_source_grid(noisy_observations, candidate_grid)
    noisy_least_squares.to_csv(out_dir / "noisy_least_squares_grid.csv", index=False)
    noisy_likelihood = likelihood_map(noisy_least_squares)
    noisy_likelihood.to_csv(out_dir / "noisy_likelihood_grid.csv", index=False)
    noisy_estimate = estimate_source_location(noisy_likelihood)
    pd.DataFrame([noisy_estimate]).to_csv(out_dir / "noisy_source_estimate.csv", index=False)
    noisy_error_m = localization_error(
        (true_source["x_m"], true_source["y_m"]),
        (noisy_estimate["estimated_x_m"], noisy_estimate["estimated_y_m"]),
    )
    pd.DataFrame(
        [
            {
                "true_x_m": true_source["x_m"],
                "true_y_m": true_source["y_m"],
                "estimated_x_m": noisy_estimate["estimated_x_m"],
                "estimated_y_m": noisy_estimate["estimated_y_m"],
                "estimated_Q_Bq_s": noisy_estimate["estimated_Q_Bq_s"],
                "localization_error_m": noisy_error_m,
                "mismatch_J": noisy_estimate["J"],
                "relative_likelihood_max": noisy_estimate["relative_likelihood"],
                "noise_seed": display_noise_seed,
                "noise_level": display_noise_level,
                "description": "fixed-seed noisy synthetic display case",
            }
        ]
    ).to_csv(out_dir / "noisy_loc_error_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "true_x": true_source["x_m"],
                "true_y": true_source["y_m"],
                "estimated_x": noisy_estimate["estimated_x_m"],
                "estimated_y": noisy_estimate["estimated_y_m"],
                "estimated_Q": noisy_estimate["estimated_Q_Bq_s"],
                "localization_error_m": noisy_error_m,
                "mismatch_J": noisy_estimate["J"],
                "relative_likelihood_max": noisy_estimate["relative_likelihood"],
                "noise_seed": display_noise_seed,
                "noise_level": display_noise_level,
                "description": "fixed-seed noisy synthetic display case for figures",
            }
        ]
    ).to_csv(out_dir / "src_recon_noisy_summary.csv", index=False)

    print("Phase 6 source reconstruction complete.")
    print(f"Wrote: {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
