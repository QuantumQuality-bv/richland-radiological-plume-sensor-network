import pytest

from src.plume_puff import arrival_time, puff_centroid, puff_concentration_proxy


def test_arrival_time_targets():
    assert arrival_time(500.0, 3.0) == pytest.approx(166.7, rel=1e-3)
    assert arrival_time(1000.0, 3.0) == pytest.approx(333.3, rel=1e-3)
    assert arrival_time(2000.0, 3.0) == pytest.approx(666.7, rel=1e-3)
    assert arrival_time(-500.0, 3.0) is None


def test_puff_centroid():
    assert puff_centroid((0.0, 0.0), (1.0, 0.0), 3.0, 100.0) == pytest.approx((300.0, 0.0))


def test_puff_proxy_largest_at_centroid():
    at_centroid = puff_concentration_proxy((300.0, 0.0), (300.0, 0.0), 200.0, 1.0)
    off_centroid = puff_concentration_proxy((500.0, 0.0), (300.0, 0.0), 200.0, 1.0)
    assert at_centroid > off_centroid


def test_puff_validation():
    with pytest.raises(ValueError):
        arrival_time(1.0, 0.0)
    with pytest.raises(ValueError):
        puff_centroid((0.0, 0.0), (1.0, 0.0), 0.0, 100.0)
    with pytest.raises(ValueError):
        puff_concentration_proxy((0.0, 0.0), (0.0, 0.0), 0.0, 1.0)
