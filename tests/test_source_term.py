import pytest
from src.source_term import radiological_source_term, release_rate

def test_source_term_baseline():
    assert radiological_source_term(1.0e9, 0.10, 1.0e-3, 0.50, 0.10) == pytest.approx(5000.0)
def test_release_rate_baseline():
    assert release_rate(5000.0, 600.0) == pytest.approx(8.3333333333)
def test_bad_fraction():
    with pytest.raises(ValueError): radiological_source_term(1.0e9, 1.2, 1.0e-3, 0.50, 0.10)
