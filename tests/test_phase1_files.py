from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def test_phase1_files_exist():
    for rel in ['data/synthetic/synthetic_sources.csv','data/synthetic/weather_cases.csv','data/synthetic/synthetic_receptors.csv','data/synthetic/candidate_detectors.csv','data/synthetic/detector_backgrounds.csv','scripts/00_create_synthetic_inputs.py']:
        assert (ROOT / rel).exists(), rel
