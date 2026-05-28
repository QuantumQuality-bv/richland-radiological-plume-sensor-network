import pytest

from src.geometry import wind_unit_vector
from src.plume_gaussian import (
    centerline_ground_concentration,
    concentration_at_receptor,
    crosswind_factor,
    gaussian_plume_concentration,
    sigma_y,
    sigma_z,
    vertical_factor,
)


def test_dispersion_targets():
    assert sigma_y(500.0) == pytest.approx(39.04, rel=1e-3)
    assert sigma_z(500.0) == pytest.approx(22.68, rel=1e-3)
    assert sigma_y(1000.0) == pytest.approx(76.28, rel=1e-3)
    assert sigma_z(1000.0) == pytest.approx(37.95, rel=1e-3)


def test_gaussian_concentration_targets():
    sy = sigma_y(1000.0)
    sz = sigma_z(1000.0)
    centerline = centerline_ground_concentration(8.333333333333334, 3.0, sy, sz)
    crosswind = gaussian_plume_concentration(8.333333333333334, 3.0, sy, sz, 200.0, 0.0, 0.0)
    assert centerline == pytest.approx(3.05e-4, rel=2e-2)
    assert crosswind == pytest.approx(9.82e-6, rel=3e-2)
    assert crosswind_factor(0.0, sy) == pytest.approx(1.0)


def test_upwind_receptor_returns_zero_concentration():
    result = concentration_at_receptor(
        (0.0, 0.0),
        (-500.0, 0.0, 0.0),
        wind_unit_vector(0.0),
        8.333333333333334,
        3.0,
    )
    assert result["classification"] == "upwind"
    assert result["concentration_bq_m3"] == 0.0


def test_invalid_wind_speed_raises():
    with pytest.raises(ValueError):
        gaussian_plume_concentration(1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0)


def test_invalid_sigma_values_raise():
    with pytest.raises(ValueError):
        centerline_ground_concentration(1.0, 3.0, 0.0, 1.0)
    with pytest.raises(ValueError):
        crosswind_factor(0.0, -1.0)
    with pytest.raises(ValueError):
        vertical_factor(0.0, 0.0, 0.0)
