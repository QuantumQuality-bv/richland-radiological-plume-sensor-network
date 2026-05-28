import pandas as pd

from src.network_optimization import greedy_network_selection, score_network, wind_sector_coverage


def test_wind_sector_coverage():
    detectors = pd.DataFrame({"detector_id": ["A", "B"], "x_m": [1.0, 0.0], "y_m": [0.0, 1.0], "cost_proxy": [1.0, 1.0]})
    assert wind_sector_coverage(detectors, {"n_sectors": 4}) == 0.5


def test_score_network_prefers_detecting_detector():
    detectors = pd.DataFrame({"detector_id": ["D1"], "x_m": [1000.0], "y_m": [0.0], "cost_proxy": [1.0]})
    results = pd.DataFrame(
        {
            "scenario_id": ["S1"],
            "detector_id": ["D1"],
            "n_sigma": [3.0],
            "first_threshold_crossing_s": [300.0],
        }
    )
    score = score_network(detectors, results, None, {"T_max_s": 1200.0, "C_max": 5.0, "sector_definition": {"n_sectors": 8}})
    assert score["P_detect"] == 1.0
    assert score["T_detect_s"] == 300.0
    assert score["score"] > 0.0


def test_greedy_selection_returns_history():
    candidates = pd.DataFrame({"detector_id": ["D1", "D2"], "x_m": [1.0, 2.0], "y_m": [0.0, 0.0], "cost_proxy": [1.0, 1.0]})

    def objective(subset):
        return {"score": float(len(subset))}

    history = greedy_network_selection(candidates, 2, objective)
    assert list(history["step"]) == [1, 2]
