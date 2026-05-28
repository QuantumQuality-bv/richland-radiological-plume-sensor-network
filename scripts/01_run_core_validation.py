from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.decay import decay_constant, remaining_fraction
from src.geometry import classify_receptor, wind_coordinates, wind_unit_vector
from src.source_term import radiological_source_term, release_rate
from src.units import days_to_seconds

def main():
    """Run Phase 2 validation and write values with units to CSV."""
    out_path = ROOT / 'data' / 'processed' / 'core_validation_results.csv'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    half_life_s = days_to_seconds(8.0)
    q_rel = radiological_source_term(1.0e9, 0.10, 1.0e-3, 0.50, 0.10)
    q_dot = release_rate(q_rel, 600.0)
    rows = [
        {'module':'decay.py','quantity':'half_life_s','value':half_life_s,'expected':691200.0,'units':'s'},
        {'module':'decay.py','quantity':'lambda','value':decay_constant(half_life_s),'expected':1.003e-6,'units':'1/s'},
        {'module':'decay.py','quantity':'remaining_fraction_600_s','value':remaining_fraction(half_life_s,600.0),'expected':0.9994,'units':'dimensionless'},
        {'module':'source_term.py','quantity':'Q_rel','value':q_rel,'expected':5000.0,'units':'Bq'},
        {'module':'source_term.py','quantity':'Q_dot','value':q_dot,'expected':8.3333333333,'units':'Bq/s'},
    ]
    source = (0.0,0.0); wind = wind_unit_vector(0.0)
    receptors = {'R001':(1000.0,0.0),'R002':(1000.0,200.0),'R003':(-500.0,0.0),'R004':(500.0,0.0)}
    for rid, xy in receptors.items():
        g = wind_coordinates(source, xy, wind)
        rows += [
            {'module':'geometry.py','quantity':f'{rid}_x_downwind','value':g['x_downwind_m'],'expected':'','units':'m'},
            {'module':'geometry.py','quantity':f'{rid}_y_crosswind','value':g['y_crosswind_m'],'expected':'','units':'m'},
            {'module':'geometry.py','quantity':f'{rid}_classification','value':classify_receptor(g['x_downwind_m']),'expected':'','units':'text'},
        ]
    with out_path.open('w', newline='', encoding='utf-8') as fp:
        w = csv.DictWriter(fp, fieldnames=['module','quantity','value','expected','units']); w.writeheader(); w.writerows(rows)
    print('Phase 2 core validation complete.')
    print(f'Wrote: {out_path.relative_to(ROOT)}')
if __name__ == '__main__': main()
