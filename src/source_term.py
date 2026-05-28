"""Synthetic source-term calculations."""
from __future__ import annotations
import pandas as pd

def _check_fraction(name: str, value: float) -> None:
    """Validate a dimensionless fraction between zero and one."""
    if value < 0 or value > 1:
        raise ValueError(f'{name} must be between 0 and 1.')

def radiological_source_term(MAR: float, DR: float, ARF: float, RF: float, LPF: float) -> float:
    """Return synthetic released activity in becquerels."""
    if MAR < 0:
        raise ValueError('MAR must be nonnegative.')
    for name, value in {'DR':DR, 'ARF':ARF, 'RF':RF, 'LPF':LPF}.items():
        _check_fraction(name, float(value))
    return float(MAR) * float(DR) * float(ARF) * float(RF) * float(LPF)

def release_rate(total_release: float, duration_seconds: float) -> float:
    """Return release rate in becquerels per second."""
    if total_release < 0:
        raise ValueError('total_release must be nonnegative.')
    if duration_seconds <= 0:
        raise ValueError('duration_seconds must be positive.')
    return float(total_release) / float(duration_seconds)

def chemical_airborne_mass(total_mass: float, airborne_fraction: float) -> float:
    """Return airborne mass in the same mass units as total_mass."""
    if total_mass < 0:
        raise ValueError('total_mass must be nonnegative.')
    _check_fraction('airborne_fraction', float(airborne_fraction))
    return float(total_mass) * float(airborne_fraction)

def evaluate_source_table(sources_df: pd.DataFrame) -> pd.DataFrame:
    """Return source table with Q_rel in becquerels and Q_dot in becquerels per second."""
    out = sources_df.copy()
    out['Q_rel_Bq'] = [radiological_source_term(row.MAR_Bq, row.DR, row.ARF, row.RF, row.LPF) for row in out.itertuples()]
    out['Q_dot_Bq_s'] = [release_rate(row.Q_rel_Bq, row.duration_s) for row in out.itertuples()]
    return out
