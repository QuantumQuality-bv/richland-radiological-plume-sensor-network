ifeq ($(OS),Windows_NT)
ifneq ("$(wildcard .venv/Scripts/python.exe)","")
PYTHON ?= .\\.venv\\Scripts\\python.exe
else
PYTHON ?= python
endif
else
ifneq ("$(wildcard .venv/bin/python)","")
PYTHON ?= .venv/bin/python
else
PYTHON ?= python
endif
endif

.PHONY: inputs core plume detectors networks reconstruction sensitivity montecarlo-quick-check montecarlo-final matlab-exports figures-main figures-plume figures-detector figures-network figures-reconstruction figures-uncertainty figures figures-extra report-tables test package all clean clean-outputs

inputs:
	$(PYTHON) scripts/00_create_synthetic_inputs.py

core:
	$(PYTHON) scripts/01_run_core_validation.py

plume:
	$(PYTHON) scripts/02_run_plume_models.py

detectors:
	$(PYTHON) scripts/03_run_detector_simulation.py

networks:
	$(PYTHON) scripts/04_run_network_comparison.py

reconstruction:
	$(PYTHON) scripts/05_run_source_reconstruction.py

sensitivity:
	$(PYTHON) scripts/06_run_sensitivity.py

montecarlo-quick-check:
	$(PYTHON) scripts/07_run_monte_carlo.py --n-samples 500 --run-name quick_check

montecarlo-final:
	$(PYTHON) scripts/07_run_monte_carlo.py --n-samples 5000 --run-name final

matlab-exports:
	$(PYTHON) scripts/08_export_matlab_inputs.py

figures-main:
	$(PYTHON) -u scripts/10_generate_figures.py --profile main

figures-plume:
	@$(MAKE) figures-main PYTHON="$(PYTHON)"

figures-detector:
	@$(MAKE) figures-main PYTHON="$(PYTHON)"

figures-network:
	@$(MAKE) figures-main PYTHON="$(PYTHON)"

figures-reconstruction:
	@$(MAKE) figures-main PYTHON="$(PYTHON)"

figures-uncertainty:
	@$(MAKE) figures-main PYTHON="$(PYTHON)"

figures: figures-main

figures-extra:
	$(PYTHON) -u scripts/10_generate_figures.py --profile all

report-tables:
	$(PYTHON) scripts/09_build_report_tables.py

test:
	$(PYTHON) -m pytest -q

package:
	$(PYTHON) scripts/11_create_release_zip.py

all: inputs core plume detectors networks reconstruction sensitivity montecarlo-quick-check montecarlo-final matlab-exports figures report-tables test

clean:
	$(PYTHON) -c "import pathlib, shutil; root=pathlib.Path('.'); [shutil.rmtree(root/p, ignore_errors=True) for p in ['data/processed','report/tables','report/appendices','figures','images','.pytest_cache']]; [shutil.rmtree(p, ignore_errors=True) for p in root.rglob('__pycache__') if '.venv' not in p.parts]; [p.unlink() for p in root.rglob('*.pyc') if '.venv' not in p.parts]; [p.unlink() for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.aux','.log','.out','.toc','.fls'} and '.venv' not in p.parts]; [p.unlink() for p in root.rglob('*.fdb_latexmk') if '.venv' not in p.parts]; [p.unlink() for p in root.rglob('*.synctex.gz') if '.venv' not in p.parts]"

clean-outputs:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(pathlib.Path(p), ignore_errors=True) for p in ['data/processed','report/tables','report/appendices','figures','images']]"
