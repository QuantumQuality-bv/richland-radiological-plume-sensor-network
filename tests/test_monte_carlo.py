import pandas as pd
import pytest

from src.monte_carlo import (
    compute_percentile_summary,
    estimate_detection_probability,
    run_monte_carlo,
    sample_uncertain_inputs,
)


def test_sampling_is_seeded():
    config = {"wind_speed_mps": 3.0}
    a = sample_uncertain_inputs(config, 5, seed=123)
    b = sample_uncertain_inputs(config, 5, seed=123)
    assert a["source_multiplier"].tolist() == pytest.approx(b["source_multiplier"].tolist())


def test_monte_carlo_summary_and_probability():
    samples = sample_uncertain_inputs({"wind_speed_mps": 3.0}, 10, seed=2)
    results = run_monte_carlo(samples)
    summary = compute_percentile_summary(results, percentiles=[5, 50, 95])
    assert {"variable", "percentile", "value"}.issubset(summary.columns)
    probability = estimate_detection_probability(pd.DataFrame({"detected": [True, False, True]}))
    assert probability == pytest.approx(2.0 / 3.0)
