# Continuous Integration (CI)

This document provides CI/CD configuration examples for SentinelDF.

## GitHub Actions

### Minimal CI Workflow

Create `.github/workflows/ci.yml` in your repository:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest -q --cov=backend --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.10'
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    name: Build distribution
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install build tools
      run: |
        python -m pip install --upgrade pip
        pip install build
    
    - name: Build distribution
      run: |
        python -m build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  lint:
    name: Lint and format check
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install linting tools
      run: |
        python -m pip install --upgrade pip
        pip install ruff black isort mypy
    
    - name: Run ruff
      run: |
        ruff check backend/ frontend/ cli/ tests/
    
    - name: Check formatting
      run: |
        black --check backend/ frontend/ cli/ tests/
        isort --check-only backend/ frontend/ cli/ tests/
    
    - name: Run mypy
      run: |
        mypy backend/ --ignore-missing-imports
```

### Extended Workflow with Windows/macOS

```yaml
name: CI - Multi-Platform

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Test on ${{ matrix.os }} - Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest -q
    
    - name: Test CLI installation
      run: |
        pip install build
        python -m build
    
    - name: Install from wheel (Unix)
      if: runner.os != 'Windows'
      run: |
        pip install dist/*.whl
        sdf --version
    
    - name: Install from wheel (Windows)
      if: runner.os == 'Windows'
      shell: powershell
      run: |
        $wheel = Get-ChildItem dist/*.whl | Select-Object -First 1
        pip install $wheel.FullName
        sdf --version
```

### Release Workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    name: Build and publish to PyPI
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build distribution
      run: |
        python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m twine upload dist/*
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/*.whl
          dist/*.tar.gz
        body_path: CHANGELOG.md
        draft: false
        prerelease: false
```

## GitLab CI

### `.gitlab-ci.yml`

```yaml
image: python:3.10

stages:
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

before_script:
  - python -m pip install --upgrade pip
  - pip install -r requirements.txt

test:
  stage: test
  script:
    - pip install pytest pytest-cov
    - pytest -q --cov=backend
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

lint:
  stage: test
  script:
    - pip install ruff black isort mypy
    - ruff check backend/ frontend/ cli/ tests/
    - black --check backend/ frontend/ cli/ tests/
    - mypy backend/ --ignore-missing-imports

build:
  stage: build
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy:pypi:
  stage: deploy
  only:
    - tags
  script:
    - pip install twine
    - python -m twine upload dist/*
  environment:
    name: production
```

## Local Pre-commit Hooks

Install pre-commit hooks to run checks locally before pushing:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.10.1
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        args: [-q]
        language: system
        pass_filenames: false
        always_run: true
```

## CI Best Practices

### 1. Cache Dependencies

Speed up CI by caching Python packages:

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.10'
    cache: 'pip'
```

### 2. Fail Fast (or not)

For multi-platform testing:

```yaml
strategy:
  fail-fast: false  # Continue testing other platforms if one fails
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### 3. Artifacts

Save build artifacts for inspection:

```yaml
- uses: actions/upload-artifact@v3
  with:
    name: dist
    path: dist/
    retention-days: 7
```

### 4. Test Coverage

Upload coverage to Codecov or Coveralls:

```bash
pytest --cov=backend --cov-report=xml
```

### 5. Branch Protection

Enable branch protection rules:
- Require status checks to pass before merging
- Require pull request reviews
- Enforce linear history

### 6. Scheduled Runs

Test against latest dependencies weekly:

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Run every Sunday at midnight
```

## Environment Variables

Set secrets in GitHub/GitLab:

- `PYPI_API_TOKEN` - For PyPI uploads
- `CODECOV_TOKEN` - For coverage uploads
- `HMAC_SECRET` - For MBOM signing tests (if needed)

**GitHub:** Settings → Secrets and variables → Actions  
**GitLab:** Settings → CI/CD → Variables

## Troubleshooting

### Tests Pass Locally but Fail in CI

**Common causes:**
1. **Cache issues** - Clear CI cache
2. **Environment differences** - Check Python version, OS
3. **Missing dependencies** - Verify `requirements.txt`
4. **Timezone/locale** - Use explicit UTC timestamps

**Solution:**
```bash
# Test in clean venv locally
python -m venv clean_venv
source clean_venv/bin/activate
pip install -r requirements.txt
pytest -q
```

### Build Artifacts Too Large

**Problem:** Artifacts exceed size limits

**Solution:**
```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    name: dist
    path: dist/*.whl  # Only upload wheel, not sdist
```

### Slow CI Runs

**Optimizations:**
1. Cache pip packages
2. Use matrix for parallel jobs
3. Skip tests on docs-only PRs:
   ```yaml
   paths-ignore:
     - '**.md'
     - 'docs/**'
   ```

## Monitoring

### Status Badges

Add to README.md:

```markdown
![CI](https://github.com/varunsripad/sentineldf/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/varunsripad/sentineldf/branch/main/graph/badge.svg)
![PyPI](https://img.shields.io/pypi/v/sentineldf)
```

### Notifications

Configure notifications for:
- Failed CI runs
- Coverage drops
- Dependency updates (Dependabot)

---

**Note:** The CI configurations above are provided as templates. Adjust to your specific needs and repository setup.

**Version:** 0.1.0  
**Last Updated:** 2024-10-16
