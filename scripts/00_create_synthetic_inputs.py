from __future__ import annotations
import csv, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DIR = ROOT / 'data' / 'synthetic'
PROCESSED_DIR = ROOT / 'data' / 'processed'
FILES = {
    'sources': SYNTHETIC_DIR / 'synthetic_sources.csv',
    'weather': SYNTHETIC_DIR / 'weather_cases.csv',
    'receptors': SYNTHETIC_DIR / 'synthetic_receptors.csv',
    'detectors': SYNTHETIC_DIR / 'candidate_detectors.csv',
    'backgrounds': SYNTHETIC_DIR / 'detector_backgrounds.csv',
}
REQ = {
    'sources':['source_id','scenario_id','x_m','y_m','z_m','MAR_Bq','DR','ARF','RF','LPF','duration_s','half_life_s','release_type','notes'],
    'weather':['weather_id','scenario_id','wind_speed_mps','wind_dir_deg','wind_dir_sigma_deg','stability_class','sigma_multiplier','temperature_C','pressure_kPa','relative_humidity_pct','notes'],
    'receptors':['receptor_id','x_m','y_m','z_m','receptor_type','include_in_validation','notes'],
    'detectors':['detector_id','x_m','y_m','z_m','detector_type','response_factor','cost_proxy','power_option','comm_option','uptime_factor','candidate_group','notes'],
    'backgrounds':['detector_id','scenario_id','background_mean_counts','background_sigma_counts','integration_time_s','noise_model','seed','notes'],
}
BANNED = ['emergency action level','protective action','evacuation','shelter in place','official threshold','operational response','real inventory','tank inventory','vulnerability']
def rows(path):
    """Return CSV rows from path; units are defined by each CSV column."""
    if not path.exists(): raise FileNotFoundError(path)
    with path.open('r', newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def fval(v, name):
    """Return finite floating value; units are defined by the column name."""
    x = float(v)
    if not math.isfinite(x): raise ValueError(name)
    return x
def validate_cols(name, rs):
    """Validate required CSV columns; units are defined by schema names."""
    if not rs: raise ValueError(f'{name} has no rows')
    miss = [c for c in REQ[name] if c not in rs[0]]
    extra = [c for c in rs[0] if c not in REQ[name]]
    if miss or extra: raise ValueError(f'{name} columns missing={miss} extra={extra}')
def main():
    """Validate Phase 1 synthetic inputs and write summary counts to CSV."""
    all_rows = {name: rows(path) for name, path in FILES.items()}
    for name, rs in all_rows.items(): validate_cols(name, rs)
    text = '\n'.join(' '.join(r.values()) for rs in all_rows.values() for r in rs).lower()
    found = [w for w in BANNED if w in text]
    if found: raise ValueError(f'Prohibited terms found: {found}')
    for r in all_rows['sources']:
        for c in ['MAR_Bq','duration_s','half_life_s']:
            if fval(r[c], c) <= 0: raise ValueError(c)
        for c in ['DR','ARF','RF','LPF']:
            x = fval(r[c], c)
            if not 0 <= x <= 1: raise ValueError(c)
    for r in all_rows['weather']:
        if fval(r['wind_speed_mps'], 'wind_speed_mps') <= 0: raise ValueError('wind_speed_mps')
        if fval(r['sigma_multiplier'], 'sigma_multiplier') <= 0: raise ValueError('sigma_multiplier')
    if len(all_rows['detectors']) < 20: raise ValueError('Need at least 20 detectors')
    needed_types = {'centerline','off_centerline','upwind','near_field','far_field','elevated','boundary'}
    have_types = {r['receptor_type'] for r in all_rows['receptors']}
    if not needed_types.issubset(have_types): raise ValueError(f'Missing receptors: {needed_types-have_types}')
    src_scen = {r['scenario_id'] for r in all_rows['sources']}
    met_scen = {r['scenario_id'] for r in all_rows['weather']}
    if src_scen - met_scen: raise ValueError(f'Missing weather: {src_scen-met_scen}')
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / 'input_summary.csv'
    with out.open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=['metric','value']); w.writeheader()
        w.writerows([
            {'metric':'source_rows','value':len(all_rows['sources'])},
            {'metric':'weather_rows','value':len(all_rows['weather'])},
            {'metric':'receptor_rows','value':len(all_rows['receptors'])},
            {'metric':'candidate_detector_rows','value':len(all_rows['detectors'])},
            {'metric':'detector_background_rows','value':len(all_rows['backgrounds'])},
            {'metric':'scenario_count','value':len(src_scen)},
            {'metric':'scope_status','value':'synthetic_public_non_operational'},
        ])
    print('Phase 1 synthetic input validation complete.')
    print(f'Wrote: {out.relative_to(ROOT)}')
if __name__ == '__main__': main()
