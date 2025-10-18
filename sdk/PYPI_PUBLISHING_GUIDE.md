# Publishing SentinelDF 2.0.0 to PyPI

Complete guide to publish your updated package with CLI support.

## 🎯 What's New in 2.0.0

✅ **Command-Line Interface (CLI)**
- `sentineldf` command available globally after install
- Scan files, folders, and text from terminal
- Beautiful ASCII art banner
- Progress tracking for batch operations

✅ **Enhanced Features**
- Batch folder scanning with recursive support
- Detailed HTML and JSON reports
- Line-by-line threat analysis
- Advanced file filtering

✅ **Post-Install Welcome Message**
- Shows quick start guide after installation
- Displays available commands
- Links to documentation

---

## 📋 Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify your email

2. **API Token** (Recommended)
   - Go to https://pypi.org/manage/account/
   - Scroll to "API tokens"
   - Create token with scope: "Entire account (all projects)"
   - **Save the token** (you'll only see it once!)

3. **Install Build Tools**
   ```bash
   pip install --upgrade pip build twine
   ```

---

## 🚀 Step-by-Step Publishing

### Step 1: Navigate to SDK Directory

```bash
cd c:\Users\kvaru\Downloads\Syn\sentineldf\sdk
```

### Step 2: Clean Previous Builds

```bash
# Remove old build artifacts
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

### Step 3: Build the Package

```bash
python -m build
```

**Expected Output:**
```
Successfully built sentineldf-ai-2.0.0.tar.gz and sentineldf_ai-2.0.0-py3-none-any.whl
```

### Step 4: Test Local Installation (Optional)

```bash
# Install locally to test
pip install dist/sentineldf_ai-2.0.0-py3-none-any.whl

# Test the CLI
sentineldf --help

# Uninstall after testing
pip uninstall sentineldf-ai -y
```

### Step 5: Upload to PyPI

**Using API Token (Recommended):**

```bash
python -m twine upload dist/*
```

When prompted:
- **Username:** `__token__`
- **Password:** Paste your PyPI API token (starts with `pypi-...`)

**Using Username/Password (Alternative):**

```bash
python -m twine upload dist/* -u YOUR_PYPI_USERNAME -p YOUR_PASSWORD
```

### Step 6: Verify Upload

1. Go to https://pypi.org/project/sentineldf-ai/
2. Check that version 2.0.0 is live
3. Verify the README displays correctly

---

## 🧪 Testing After Publish

### Test Fresh Installation

```bash
# Create a test virtual environment
python -m venv test_env
test_env\Scripts\activate

# Install from PyPI
pip install sentineldf-ai

# You should see the welcome message! 🎉

# Test CLI
sentineldf --help
sentineldf --version

# Test in Python
python -c "from sentineldf import SentinelDF; print('Success!')"

# Cleanup
deactivate
Remove-Item -Recurse -Force test_env
```

---

## 📝 Usage Examples

### CLI Usage

```bash
# Scan a text string
sentineldf scan-text "DELETE * FROM users" --api-key YOUR_KEY

# Scan a single file
sentineldf scan-file data.txt --api-key YOUR_KEY --detailed

# Scan a folder (recursive)
sentineldf scan-folder ./datasets --api-key YOUR_KEY -r --output report.html

# Scan with progress
sentineldf scan-folder ./data --api-key YOUR_KEY --show-threats
```

### Python SDK Usage

```python
from sentineldf import SentinelDF, FileScanner, ThreatReport

# Initialize client
client = SentinelDF(api_key="YOUR_KEY")

# Scan text
response = client.scan(["Your text here"])
print(f"Risk: {response.results[0].risk}")

# Scan a folder
from sentineldf import scan_and_analyze

results = scan_and_analyze(
    client,
    folder_path="./data",
    recursive=True
)

print(f"Scanned: {results['summary']['total_files']} files")
print(f"Quarantined: {results['summary']['quarantined_files']}")

# Generate detailed report
from sentineldf import generate_batch_report, save_report_to_html

report = generate_batch_report(results['results'])
save_report_to_html(report, "security_report.html")
```

---

## 🔧 Troubleshooting

### Build Errors

**Error: `No module named 'setuptools'`**
```bash
pip install --upgrade setuptools wheel
```

**Error: `README.md not found`**
```bash
# Make sure you're in the sdk/ directory
cd c:\Users\kvaru\Downloads\Syn\sentineldf\sdk
```

### Upload Errors

**Error: `403 Forbidden`**
- Check your API token is correct
- Ensure username is `__token__` (with double underscores)
- Token must have "upload" permission

**Error: `File already exists`**
- You can't re-upload the same version
- Bump version in `setup.py` and `__init__.py`
- Rebuild and upload again

**Error: `Invalid distribution file`**
```bash
# Rebuild from scratch
Remove-Item -Recurse -Force dist, build, *.egg-info
python -m build
```

### Installation Errors

**Error: `Command 'sentineldf' not found`**
```bash
# Reinstall the package
pip uninstall sentineldf-ai -y
pip install --no-cache-dir sentineldf-ai
```

---

## 📊 Version History

| Version | Features |
|---------|----------|
| 2.0.0   | ✅ CLI tool, batch scanning, detailed reports, welcome message |
| 1.0.0   | Initial release with basic scanning |

---

## 🔄 Future Updates

To publish updates:

1. **Update version** in `setup.py` and `__init__.py`
2. **Clean build artifacts:**
   ```bash
   Remove-Item -Recurse -Force dist, build, *.egg-info
   ```
3. **Build:**
   ```bash
   python -m build
   ```
4. **Upload:**
   ```bash
   python -m twine upload dist/*
   ```

---

## 📚 Resources

- **PyPI Dashboard:** https://pypi.org/manage/projects/
- **Twine Docs:** https://twine.readthedocs.io/
- **Packaging Guide:** https://packaging.python.org/
- **SentinelDF Dashboard:** https://sentineldf.com/dashboard

---

## ✅ Post-Publish Checklist

- [ ] Package appears on PyPI
- [ ] README displays correctly
- [ ] Fresh install works: `pip install sentineldf-ai`
- [ ] CLI works: `sentineldf --help`
- [ ] Welcome message displays
- [ ] Python import works: `from sentineldf import SentinelDF`
- [ ] Update website/docs with new CLI features
- [ ] Announce on social media/blog

---

**🎉 Congratulations! Your package is live on PyPI!**

Users can now install it with:
```bash
pip install sentineldf-ai
```
