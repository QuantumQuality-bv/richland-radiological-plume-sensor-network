import numpy as np
import pytest

from src.detector_model import (
    detect_threshold_crossing,
    detector_signal,
    false_positive_rate,
    simulate_background,
    threshold_level,
    time_to_first_threshold_crossing,
)


def test_threshold_validation_targets():
    sigma = np.sqrt(7200.0)
    assert sigma == pytest.approx(84.85, rel=5e-4)
    assert threshold_level(7200.0, sigma, 3.0) == pytest.approx(7454.56, rel=5e-5)
    assert threshold_level(7200.0, sigma, 5.0) == pytest.approx(7624.26, rel=5e-5)


def test_signal_crosses_three_sigma_not_five_sigma():
    signal = detector_signal(3.0547e-4, 1.0e6, 7200.0, 0.0)
    assert signal[()] == pytest.approx(7505.47)
    assert detect_threshold_crossing(signal, threshold_level(7200.0, np.sqrt(7200.0), 3.0))[()]
    assert not detect_threshold_crossing(signal, threshold_level(7200.0, np.sqrt(7200.0), 5.0))[()]


def test_background_seed_and_time_to_crossing():
    a = simulate_background(7200.0, 84.85, 3, seed=1)
    b = simulate_background(7200.0, 84.85, 3, seed=1)
    assert np.allclose(a, b)
    assert time_to_first_threshold_crossing([0.0, 60.0], [7200.0, 7500.0], 7454.56) == pytest.approx(60.0)
    assert false_positive_rate([7200.0, 7500.0], 7454.56) == pytest.approx(0.5)
