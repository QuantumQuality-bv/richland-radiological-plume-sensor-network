import pytest
from src.decay import decay_constant, remaining_fraction
from src.units import days_to_seconds

def test_decay_constant():
    assert decay_constant(days_to_seconds(8.0)) == pytest.approx(1.003e-6, rel=5e-4)
def test_remaining_fraction():
    assert remaining_fraction(days_to_seconds(8.0), 600.0) == pytest.approx(0.9994, rel=5e-4)
def test_bad_half_life():
    with pytest.raises(ValueError): decay_constant(0.0)
