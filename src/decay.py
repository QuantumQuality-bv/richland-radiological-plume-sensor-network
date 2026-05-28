"""Radioactive decay helpers."""
from __future__ import annotations
import math

def decay_constant(half_life_s: float) -> float:
    """Return radioactive decay constant in inverse seconds from half-life in seconds."""
    if half_life_s <= 0:
        raise ValueError('half_life_s must be positive.')
    return math.log(2.0) / float(half_life_s)

def activity_after_time(A0: float, half_life_s: float, time_s: float) -> float:
    """Return activity in becquerels after elapsed time in seconds."""
    if A0 < 0:
        raise ValueError('A0 must be nonnegative.')
    if time_s < 0:
        raise ValueError('time_s must be nonnegative.')
    return float(A0) * math.exp(-decay_constant(half_life_s) * float(time_s))

def remaining_fraction(half_life_s: float, time_s: float) -> float:
    """Return dimensionless remaining activity fraction after elapsed time in seconds."""
    if time_s < 0:
        raise ValueError('time_s must be nonnegative.')
    return math.exp(-decay_constant(half_life_s) * float(time_s))
