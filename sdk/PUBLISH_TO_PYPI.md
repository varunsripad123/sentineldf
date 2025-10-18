# 📦 How to Publish SentinelDF SDK to PyPI

This guide explains how to publish your SDK so customers can run `pip install sentineldf`

---

## 🎯 What Happens When Someone Runs `pip install sentineldf`

```
Customer's laptop:
  $ pip install sentineldf
    ↓
pip contacts PyPI.org
    ↓
PyPI returns your package URL
    ↓
pip downloads: sentineldf-1.0.0.tar.gz
    ↓
pip extracts and installs to:
  /Users/customer/venv/lib/python3.11/site-packages/sentineldf/
    ↓
Customer can now use:
  from sentineldf import SentinelDF
```

---

## 🚀 Step-by-Step Publishing Guide

### Step 1: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create account with your email
3. Verify email
4. **Enable 2FA** (required for publishing)

### Step 2: Create API Token

1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Name: "SentinelDF Upload"
5. Scope: "Entire account"
6. Copy the token: `pypi-AgEIcHlwaS5vcmc...`
7. **Save it securely!** (You won't see it again)

### Step 3: Install Build Tools

```bash
cd C:\Users\kvaru\Downloads\Syn\sentineldf\sdk
pip install build twine
```

### Step 4: Update Package Metadata

Edit `setup.py` and make sure all info is correct:

```python
setup(
    name="sentineldf",
    version="1.0.0",
    author="Varun Sripad Kota",
    author_email="varunsripadkota@gmail.com",
    description="Official Python SDK for SentinelDF",
    # ... rest of setup.py
)
```

### Step 5: Build the Package

```bash
cd C:\Users\kvaru\Downloads\Syn\sentineldf\sdk
python -m build
```

This creates:
```
sdk/
├── dist/
│   ├── sentineldf-1.0.0.tar.gz     # Source distribution
│   └── sentineldf-1.0.0-py3-none-any.whl  # Wheel distribution
```

### Step 6: Test Locally First

Before publishing, test that it installs:

```bash
# Install from local file
pip install dist/sentineldf-1.0.0-py3-none-any.whl

# Test it works
python -c "from sentineldf import SentinelDF; print('✅ Works!')"

# Uninstall
pip uninstall sentineldf
```

### Step 7: Publish to Test PyPI (Recommended First Time)

Test PyPI is a separate instance for testing:

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: pypi-AgEIcHlwaS5vcmc... (your token)
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ sentineldf
```

### Step 8: Publish to Real PyPI

If test worked, publish to real PyPI:

```bash
python -m twine upload dist/*

# Username: __token__
# Password: pypi-AgEIcHlwaS5vcmc... (your token)
```

🎉 **Done!** Your package is now live!

### Step 9: Verify It Works

Anyone in the world can now install it:

```bash
pip install sentineldf
```

Check on PyPI: https://pypi.org/project/sentineldf/

---

## 📝 Updating Your Package

When you make changes:

### 1. Update Version Number

Edit `setup.py`:
```python
version="1.0.1",  # Increment version
```

Also update `sentineldf/__init__.py`:
```python
__version__ = "1.0.1"
```

### 2. Rebuild and Republish

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build new version
python -m build

# Upload new version
python -m twine upload dist/*
```

---

## 🏗️ Your Package Structure

```
sdk/
├── sentineldf/              # Package folder (what gets installed)
│   ├── __init__.py         # Package entry point
│   └── client.py           # Your SDK code
├── setup.py                 # Package metadata
├── README.md                # Shows on PyPI page
├── LICENSE                  # MIT license
├── MANIFEST.in              # What files to include
└── .gitignore              # Don't commit dist/, build/
```

---

## 🔐 Security Best Practices

### Use .pypirc for Token Storage

Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

Then you can just run:
```bash
twine upload dist/*  # No password prompt
```

### Never Commit Your Token

Add to `.gitignore`:
```
dist/
build/
*.egg-info/
.pypirc
```

---

## 📊 After Publishing

### Your PyPI Page

Visit: https://pypi.org/project/sentineldf/

Shows:
- Installation instructions
- Your README.md
- Download statistics
- Version history
- Links to GitHub, docs, etc.

### Monitor Downloads

Check stats at:
- https://pypistats.org/packages/sentineldf
- Shows daily/weekly/monthly downloads
- Geographic distribution
- Python version usage

---

## 🎯 Marketing Your SDK

### 1. Add PyPI Badge to README

```markdown
[![PyPI version](https://badge.fury.io/py/sentineldf.svg)](https://pypi.org/project/sentineldf/)
[![Downloads](https://pepy.tech/badge/sentineldf)](https://pepy.tech/project/sentineldf)
```

### 2. Tweet About It

```
🚀 Just published sentineldf to PyPI!

Secure your LLM training data with one command:

pip install sentineldf

Detects prompt injections, backdoors, and data poisoning in real-time.

#Python #LLM #AI #Security
```

### 3. Post on Reddit

- r/Python
- r/MachineLearning
- r/learnpython

### 4. Submit to Awesome Lists

- awesome-python
- awesome-machine-learning
- awesome-llm

---

## 🐛 Troubleshooting

### Error: "File already exists"

You already uploaded this version. Increment version number.

### Error: "Invalid authentication credentials"

Your API token is wrong. Generate a new one.

### Error: "Package name already taken"

Someone else has "sentineldf". Choose different name like:
- sentineldf-ai
- sentinel-df
- sentineldf-security

(Check availability at: https://pypi.org/project/YOUR-NAME/)

### Error: "README not rendering"

Make sure `long_description_content_type="text/markdown"` in setup.py

---

## 📈 Growth Tracking

Watch your package grow:

### Week 1: ~10 downloads
- Early adopters from your landing page

### Month 1: ~100 downloads
- Word of mouth, blog posts

### Month 3: ~1,000 downloads
- Integrations, tutorials

### Month 6: ~10,000 downloads
- Featured in awesome lists, conferences

### Year 1: ~100,000 downloads
- Industry standard for LLM security

---

## 🎓 Pro Tips

### 1. Pre-release Versions

Test with beta users before stable release:
```python
version="1.0.0b1"  # Beta 1
version="1.0.0rc1"  # Release candidate 1
```

### 2. Automate Releases with GitHub Actions

Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

### 3. Add Type Hints

Helps IDEs with autocomplete:
```python
def scan(self, texts: List[str]) -> ScanResponse:
    ...
```

### 4. Include Tests

Users trust packages with tests:
```
sdk/
├── sentineldf/
├── tests/
│   ├── test_client.py
│   └── test_auth.py
└── setup.py
```

---

## ✅ Checklist Before Publishing

- [ ] Package name is available on PyPI
- [ ] Version number is correct
- [ ] README.md is complete and formatted
- [ ] License file is included (MIT recommended)
- [ ] All imports work correctly
- [ ] Tested installation locally
- [ ] API key example uses placeholder (not real key!)
- [ ] GitHub repo is public and linked
- [ ] Email in setup.py is correct
- [ ] Tested on Test PyPI first

---

## 🎉 You're Ready!

Once published, anyone can install your SDK:

```bash
pip install sentineldf
```

And use it in their code:

```python
from sentineldf import SentinelDF

client = SentinelDF(api_key="sk_live_...")
results = client.scan(["text to scan"])
```

**Your SDK is now distributed globally via PyPI!** 🌍

---

## 📞 Need Help?

- PyPI Support: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Email: varunsripadkota@gmail.com
