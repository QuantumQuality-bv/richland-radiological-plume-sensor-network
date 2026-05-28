import pandas as pd
import pytest

from src.source_reconstruction import (
    candidate_source_grid,
    estimate_source_location,
    least_squares_source_grid,
    likelihood_map,
    localization_error,
    simulate_observations,
)


def test_noise_free_reconstruction_recovers_true_source():
    detectors = pd.DataFrame(
        {
            "detector_id": ["D1", "D2", "D3"],
            "x_m": [500.0, 1000.0, 1000.0],
            "y_m": [0.0, 0.0, 200.0],
            "z_m": [0.0, 0.0, 0.0],
        }
    )
    weather = {"wind_speed_mps": 3.0, "wind_dir_deg": 0.0, "stability_class": "D", "sigma_multiplier": 1.0}
    true_source = {"x_m": 0.0, "y_m": 0.0}
    observations = simulate_observations(true_source, detectors, weather, 8.333333333333334, seed=None)
    grid = candidate_source_grid(-50.0, 50.0, -50.0, 50.0, 50.0)
    least_squares = least_squares_source_grid(observations, grid)
    estimate = estimate_source_location(likelihood_map(least_squares))
    assert estimate["estimated_x_m"] == pytest.approx(0.0)
    assert estimate["estimated_y_m"] == pytest.approx(0.0)
    assert estimate["estimated_Q_Bq_s"] == pytest.approx(8.333333333333334, rel=1e-6)
    assert localization_error((0.0, 0.0), (estimate["estimated_x_m"], estimate["estimated_y_m"])) == pytest.approx(0.0)
