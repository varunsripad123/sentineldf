# Release Checklist

This document provides step-by-step instructions for releasing a new version of SentinelDF.

## Pre-Release Checklist

### 1. Version Bump

Update version in `pyproject.toml`:
```toml
[project]
version = "0.1.0"  # Update to new version
```

Update version string in `cli/sdf.py` if hardcoded:
```python
@click.version_option(version="0.1.0", prog_name="sdf")
```

### 2. Update CHANGELOG.md

Add new version section with date:
```markdown
## [0.1.0] - 2024-10-16

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Bug fix 1
```

### 3. Run Full Test Suite

```bash
# Must be green (172/172 tests passing)
pytest -q
```

**Expected output:**
```
172 passed in ~7-10s
```

**If tests fail:**
1. Fix the failing tests
2. Clear cache if needed: `rm -rf .cache/`
3. Re-run tests

### 4. Run Value Proof Tests

```bash
pytest tests/test_value_proof.py -v -s
```

**Expected:**
- Detection rate: ≥50% (ideally ≥56%)
- False positive rate: 0%
- All assertions pass

## Build & Package

### 5. Clean Previous Builds

```bash
make clean
```

This removes:
- `build/`
- `dist/`
- `*.egg-info`
- `__pycache__`
- `.pytest_cache`

### 6. Build Distribution

```bash
make build
```

**Expected output:**
```
python -m build
* Creating venv in ...
* Installing packages in...
* Building sdist...
* Building wheel from sdist
Successfully built sentineldf-0.1.0.tar.gz and sentineldf-0.1.0-py3-none-any.whl
```

**Verify build artifacts:**
```bash
ls dist/
# Should see:
# sentineldf-0.1.0-py3-none-any.whl
# sentineldf-0.1.0.tar.gz
```

## Installation Testing

### 7. Test Installation in Clean Environment

**Option A: Using pipx (recommended for CLI tools)**

```bash
pipx install --force dist/sentineldf-0.1.0-py3-none-any.whl
```

**Option B: Using pip in fresh venv**

```bash
# Create fresh venv
python -m venv test_venv
# Windows:
test_venv\Scripts\activate
# Unix/macOS:
source test_venv/bin/activate

# Install wheel
pip install dist/sentineldf-0.1.0-py3-none-any.whl

# Verify installation
pip show sentineldf
sdf --version
```

**Expected output:**
```
Name: sentineldf
Version: 0.1.0
...
```

### 8. Smoke Tests

**Test 1: Scan command**
```bash
sdf scan --path data/samples
```

**Expected:**
- Processes 20 documents
- Shows summary with quarantine counts
- Saves report to `reports/scan_*.json`
- Exit code: 1 (if quarantines found) or 0 (if clean)

**Test 2: MBOM generation**
```bash
sdf mbom reports/scan_*.json --approver you@company.com
```

**Expected:**
- Loads most recent scan file
- Creates signed MBOM
- Saves to `reports/mbom_*.json`
- Shows MBOM ID, batch ID, signature
- Exit code: 0

**Test 3: MBOM validation**
```bash
sdf validate reports/mbom_*.json
```

**Expected:**
- Validates all MBOM files
- Shows ✅ for each valid signature
- Exit code: 0 (all valid) or 1 (some invalid)

### 9. Test Streamlit Dashboard

```bash
make ui
# Or: streamlit run frontend/streamlit_app.py
```

**Verify:**
1. Dashboard loads at http://localhost:8501
2. Can scan documents
3. Can view results
4. Can generate MBOM
5. No errors in console

### 10. Test FastAPI Backend

```bash
make run-api
# Or: uvicorn backend.app:app --reload
```

**Verify:**
1. API docs at http://localhost:8000/docs
2. `/scan` endpoint works
3. `/mbom` endpoint works
4. `/health` returns 200

## Git Tagging & Release

### 11. Commit All Changes

```bash
git status  # Review changes
git add .
git commit -m "Release v0.1.0

- Updated version to 0.1.0
- Added CHANGELOG for v0.1.0
- Built and tested distribution"
```

### 12. Create Git Tag

```bash
git tag -a v0.1.0 -m "Release v0.1.0 - MVP with detection, MBOM, and caching"
```

**Verify tag:**
```bash
git tag -l
git show v0.1.0
```

### 13. Push to Remote

```bash
git push origin main
git push origin v0.1.0
# Or push all tags:
git push --tags
```

## PyPI Upload (Optional)

### 14. Upload to Test PyPI (Optional)

```bash
python -m pip install --upgrade twine
python -m twine upload --repository testpypi dist/*
```

### 15. Upload to PyPI (Production)

```bash
python -m twine upload dist/*
```

**Note:** Requires PyPI credentials configured in `~/.pypirc` or via environment variables.

## Post-Release

### 16. Create GitHub Release

1. Go to https://github.com/varunsripad/sentineldf/releases
2. Click "Draft a new release"
3. Select tag: `v0.1.0`
4. Release title: `v0.1.0 - MVP Release`
5. Description: Copy from CHANGELOG.md
6. Attach distribution files (optional):
   - `sentineldf-0.1.0-py3-none-any.whl`
   - `sentineldf-0.1.0.tar.gz`
7. Publish release

### 17. Update Documentation

- Update README badges if applicable (PyPI version, downloads)
- Update installation instructions to reference new version
- Announce release (Twitter, blog, mailing list)

### 18. Verify PyPI Release (if published)

```bash
# In fresh environment
pip install sentineldf==0.1.0
sdf --version
```

## Rollback Procedure

If release has critical issues:

### 19. Yank from PyPI (if published)

```bash
python -m twine yank sentineldf -v 0.1.0 -m "Critical bug: [description]"
```

### 20. Delete Git Tag

```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin :refs/tags/v0.1.0
```

### 21. Revert Commits

```bash
git revert <commit-hash>
git push origin main
```

## Troubleshooting

### Build Fails

**Problem:** `python -m build` fails
**Solution:**
1. Ensure `build` package installed: `pip install --upgrade build`
2. Check `pyproject.toml` syntax
3. Ensure all dependencies in `requirements.txt` are valid

### Tests Fail

**Problem:** `pytest -q` shows failures
**Solution:**
1. Clear cache: `rm -rf .cache/`
2. Re-run tests: `pytest -q`
3. Check for stale imports: `python -m pip install --force-reinstall -e .`

### Import Errors After Install

**Problem:** `ModuleNotFoundError` after installing wheel
**Solution:**
1. Verify installation: `pip show sentineldf`
2. Check entry point: `sdf --help`
3. Reinstall: `pip install --force-reinstall dist/sentineldf-0.1.0-py3-none-any.whl`

### CLI Command Not Found

**Problem:** `sdf: command not found`
**Solution:**
1. Ensure scripts directory in PATH
2. Use `python -m cli.sdf` as fallback
3. Reinstall with pipx: `pipx install --force dist/*.whl`

---

## Quick Reference

**Complete release flow:**
```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Run tests
pytest -q

# 4. Build
make clean
make build

# 5. Test install
pipx install --force dist/sentineldf-0.1.0-py3-none-any.whl

# 6. Smoke test
sdf scan --path data/samples
sdf mbom reports/scan_*.json --approver you@company.com
sdf validate reports/mbom_*.json

# 7. Tag and push
git add .
git commit -m "Release v0.1.0"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main
git push origin v0.1.0

# 8. Upload to PyPI (optional)
python -m twine upload dist/*
```

---

**Version:** 0.1.0  
**Last Updated:** 2024-10-16
