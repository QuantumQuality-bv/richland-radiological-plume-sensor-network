import pytest
from src.geometry import classify_receptor, distance_2d, wind_coordinates, wind_unit_vector

def test_distance_2d():
    assert distance_2d((0.0,0.0),(3.0,4.0)) == pytest.approx(5.0)
def test_wind_unit_vector():
    ux, uy = wind_unit_vector(0.0)
    assert ux == pytest.approx(1.0)
    assert uy == pytest.approx(0.0)
def test_centerline():
    g = wind_coordinates((0.0,0.0),(1000.0,0.0),(1.0,0.0))
    assert g['x_downwind_m'] == pytest.approx(1000.0)
    assert g['y_crosswind_m'] == pytest.approx(0.0)
    assert classify_receptor(g['x_downwind_m']) == 'downwind'
def test_off_centerline():
    g = wind_coordinates((0.0,0.0),(1000.0,200.0),(1.0,0.0))
    assert g['x_downwind_m'] == pytest.approx(1000.0)
    assert g['y_crosswind_m'] == pytest.approx(200.0)
def test_upwind():
    g = wind_coordinates((0.0,0.0),(-500.0,0.0),(1.0,0.0))
    assert g['x_downwind_m'] == pytest.approx(-500.0)
    assert classify_receptor(g['x_downwind_m']) == 'upwind'
