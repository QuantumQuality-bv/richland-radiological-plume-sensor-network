"""Unit conversion helpers."""
from __future__ import annotations
from .constants import CI_TO_BQ, BQ_TO_CI, SV_TO_MREM, MREM_TO_SV

def ci_to_bq(activity_ci: float) -> float:
    """Convert activity from curies to becquerels."""
    return float(activity_ci) * CI_TO_BQ

def bq_to_ci(activity_bq: float) -> float:
    """Convert activity from becquerels to curies."""
    return float(activity_bq) * BQ_TO_CI

def sv_to_mrem(dose_sv: float) -> float:
    """Convert dose from sieverts to millirem."""
    return float(dose_sv) * SV_TO_MREM

def mrem_to_sv(dose_mrem: float) -> float:
    """Convert dose from millirem to sieverts."""
    return float(dose_mrem) * MREM_TO_SV

def minutes_to_seconds(minutes: float) -> float:
    """Convert time from minutes to seconds."""
    return float(minutes) * 60.0

def hours_to_seconds(hours: float) -> float:
    """Convert time from hours to seconds."""
    return float(hours) * 3600.0

def days_to_seconds(days: float) -> float:
    """Convert time from days to seconds."""
    return float(days) * 86400.0

def ppm_to_mg_m3(ppm: float, molecular_weight_g_mol: float) -> float:
    """Convert concentration from ppm to milligrams per cubic meter."""
    if molecular_weight_g_mol <= 0:
        raise ValueError('molecular_weight_g_mol must be positive.')
    return float(ppm) * float(molecular_weight_g_mol) / 24.45

def mg_m3_to_ppm(mg_m3: float, molecular_weight_g_mol: float) -> float:
    """Convert concentration from milligrams per cubic meter to ppm."""
    if molecular_weight_g_mol <= 0:
        raise ValueError('molecular_weight_g_mol must be positive.')
    return float(mg_m3) * 24.45 / float(molecular_weight_g_mol)
