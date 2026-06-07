.PHONY: help install install-dev test test-cov lint typecheck format bench figures reproduce package-overleaf clean

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip

help:
	@echo "SEBA-XAI — common developer targets"
	@echo ""
	@echo "  make install       Editable install of the seba package"
	@echo "  make install-dev   Install with dev extras (pytest, ruff, mypy)"
	@echo "  make test          Run the test suite"
	@echo "  make test-cov      Run tests with coverage report (fails if <60%)"
	@echo "  make lint          Run ruff lint checks"
	@echo "  make typecheck     Run mypy strict type checks"
	@echo "  make format        Apply ruff format + isort-style import sort"
	@echo "  make bench         Run the existing 8-step prototype on seed 42"
	@echo "  make figures       Regenerate paper SVG figures from result CSVs"
	@echo "  make reproduce     Run the multi-seed sweep (seeds 7, 21, 42, 99, 123)"
	@echo "  make package-overleaf  Validate and zip the IEEE journal Overleaf project"
	@echo "  make clean         Remove build artifacts and __pycache__ dirs"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest

test-cov:
	$(PYTHON) -m pytest --cov=src/seba --cov-report=term-missing --cov-fail-under=60

lint:
	$(PYTHON) -m ruff check src tests

typecheck:
	$(PYTHON) -m mypy src/seba

format:
	$(PYTHON) -m ruff check --select I --fix src tests
	$(PYTHON) -m ruff format src tests

bench:
	$(PYTHON) prototype/synthetic_access_sim/generate_synthetic_requests.py \
		--run-id 20260528_step1_synthetic_requests_seed42 --seed 42 --num-requests 1000
	$(PYTHON) prototype/synthetic_access_sim/policy_oracle.py \
		--input-run-id 20260528_step1_synthetic_requests_seed42 \
		--run-id 20260528_step2_policy_oracle_seed42

figures:
	$(PYTHON) scripts/generate_paper_figures.py

reproduce:
	bash scripts/run_multi_seed.sh
	$(PYTHON) scripts/aggregate_seeds.py
	$(PYTHON) scripts/run_full_grid.py
	$(PYTHON) scripts/run_ablations.py
	$(PYTHON) scripts/run_nspi_sensitivity.py
	$(PYTHON) scripts/run_nspi_targeted_sensitivity.py
	$(PYTHON) scripts/run_explanation_audit_quality.py
	$(PYTHON) scripts/run_workload_policy_stress.py
	$(PYTHON) scripts/run_seed_confidence_summary.py
	@echo ""
	@echo "Reproduction complete. See results/FINDINGS.md for honest interpretation."

package-overleaf:
	$(PYTHON) scripts/package_overleaf.py

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
