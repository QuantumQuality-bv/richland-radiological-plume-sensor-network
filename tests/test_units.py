import pytest
from src.units import bq_to_ci, ci_to_bq, days_to_seconds, mg_m3_to_ppm, ppm_to_mg_m3, mrem_to_sv, sv_to_mrem

def test_activity_conversions():
    assert ci_to_bq(1.0) == pytest.approx(3.7e10)
    assert bq_to_ci(3.7e10) == pytest.approx(1.0)
def test_dose_conversions():
    assert sv_to_mrem(1.0) == pytest.approx(100000.0)
    assert mrem_to_sv(100000.0) == pytest.approx(1.0)
def test_days_to_seconds():
    assert days_to_seconds(8.0) == pytest.approx(691200.0)
def test_ppm_round_trip():
    x = ppm_to_mg_m3(100.0, 28.0)
    assert mg_m3_to_ppm(x, 28.0) == pytest.approx(100.0)
