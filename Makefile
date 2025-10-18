.PHONY: help install install-dev install-wheel test lint format clean build run-api run-ui ui docs-check metrics feedback-summary

help:
	@echo "SentinelDF - Available commands:"
	@echo "  make install          - Install dependencies from requirements.txt"
	@echo "  make install-dev      - Install with dev dependencies"
	@echo "  make install-wheel    - Install from built wheel"
	@echo "  make build            - Build wheel and sdist"
	@echo "  make test             - Run test suite with pytest"
	@echo "  make lint             - Run linters (ruff, mypy)"
	@echo "  make format           - Format code with black and isort"
	@echo "  make clean            - Remove build artifacts and cache"
	@echo "  make run-api          - Start FastAPI backend server"
	@echo "  make run-ui           - Start Streamlit frontend"
	@echo "  make ui               - Alias for run-ui"
	@echo "  make docs-check       - Check documentation links"
	@echo "  make metrics          - Generate metrics report from scan logs"
	@echo "  make feedback-summary - Aggregate user feedback JSONs"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

install-wheel:
	@python -c "import glob; wheels=sorted(glob.glob('dist/*.whl')); print(f'Installing {wheels[-1] if wheels else \"No wheel found\"}'); exit(0 if wheels else 1)"
	pip install --force-reinstall $$(python -c "import glob; print(sorted(glob.glob('dist/*.whl'))[-1])")

build: clean
	python -m pip install --upgrade build
	python -m build

test:
	pytest -q

lint:
	ruff check backend/ frontend/ cli/ tests/
	mypy backend/ --ignore-missing-imports

format:
	black backend/ frontend/ cli/ tests/
	isort backend/ frontend/ cli/ tests/

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	python -c "import shutil; shutil.rmtree('build', ignore_errors=True); shutil.rmtree('dist', ignore_errors=True); shutil.rmtree('.pytest_cache', ignore_errors=True); shutil.rmtree('.mypy_cache', ignore_errors=True); shutil.rmtree('.ruff_cache', ignore_errors=True)"

run-api:
	uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

run-ui:
	streamlit run frontend/streamlit_app.py

ui: run-ui

docs-check:
	@echo "📖 Checking documentation..."
	@python -c "import pathlib; docs=['README.md','CHANGELOG.md','CONTRIBUTING.md','LICENSE','docs/DEMO.md','docs/SECURITY.md','docs/ROADMAP.md','docs/RELEASE.md','docs/CI.md']; missing=[d for d in docs if not pathlib.Path(d).exists()]; print('✅ All docs present' if not missing else f'⚠️  Missing: {missing}')"

metrics:
	@echo "📊 Generating metrics report..."
	@python scripts/metrics_report.py

feedback-summary:
	@echo "📝 Aggregating feedback..."
	@python scripts/feedback_summary.py
