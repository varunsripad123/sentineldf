# 🚀 Quick Publish Commands for SentinelDF 2.0.0

## One-Command Publishing (Copy-Paste Ready)

```powershell
# Navigate to SDK directory
cd c:\Users\kvaru\Downloads\Syn\sentineldf\sdk

# Clean, build, and prepare for upload
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue; python -m build

# Upload to PyPI (you'll be prompted for credentials)
python -m twine upload dist/*
```

---

## Step-by-Step Commands

### 1. Prepare Environment
```powershell
# Install/upgrade build tools
pip install --upgrade pip build twine
```

### 2. Navigate to SDK
```powershell
cd c:\Users\kvaru\Downloads\Syn\sentineldf\sdk
```

### 3. Clean Previous Builds
```powershell
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

### 4. Build Package
```powershell
python -m build
```

**Expected Output:**
```
Successfully built sentineldf-ai-2.0.0.tar.gz and sentineldf_ai-2.0.0-py3-none-any.whl
```

### 5. Test Locally (Optional)
```powershell
# Install from local build
pip install dist/sentineldf_ai-2.0.0-py3-none-any.whl

# Test CLI
sentineldf --help
sentineldf --version

# Test import
python -c "from sentineldf import SentinelDF; print('✅ Import works!')"

# Uninstall
pip uninstall sentineldf-ai -y
```

### 6. Upload to PyPI
```powershell
python -m twine upload dist/*
```

**When prompted:**
- Username: `__token__`
- Password: `pypi-AgE...` (your PyPI API token)

---

## ✅ Verification Commands

### Check on PyPI
```powershell
# Open in browser
start https://pypi.org/project/sentineldf-ai/
```

### Test Installation from PyPI
```powershell
# Create test environment
python -m venv test_install
test_install\Scripts\activate

# Install from PyPI
pip install sentineldf-ai

# Verify CLI
sentineldf --help

# Verify import
python -c "from sentineldf import SentinelDF, scan_and_analyze; print('✅ Success!')"

# Cleanup
deactivate
Remove-Item -Recurse -Force test_install
```

---

## 🔄 Update Version (For Future Releases)

### Version 2.0.1 (Bug Fix)
```powershell
# 1. Update version in both files
# - sdk/setup.py: version="2.0.1"
# - sdk/sentineldf/__init__.py: __version__ = "2.0.1"

# 2. Clean and rebuild
cd c:\Users\kvaru\Downloads\Syn\sentineldf\sdk
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
python -m build

# 3. Upload
python -m twine upload dist/*
```

### Version 2.1.0 (Minor Feature)
```powershell
# Same as above, but use version 2.1.0
```

### Version 3.0.0 (Major Release)
```powershell
# Same as above, but use version 3.0.0
```

---

## 🐛 Troubleshooting

### Error: "File already exists"
```powershell
# You can't re-upload the same version
# Increment version and rebuild
```

### Error: "Invalid credentials"
```powershell
# For API token:
Username: __token__
Password: pypi-AgE... (full token)

# Make sure there are NO spaces
```

### Error: "Twine not found"
```powershell
pip install --upgrade twine
```

### Error: "Build failed"
```powershell
# Install dependencies
pip install --upgrade setuptools wheel build

# Try again
python -m build
```

---

## 📊 What Gets Published

### Package Contents
- ✅ Python SDK (`sentineldf/` module)
- ✅ CLI tool (`sentineldf` command)
- ✅ File utilities (batch scanning)
- ✅ Reporting tools (HTML/JSON)
- ✅ Post-install welcome message

### Available Commands After Install
```bash
sentineldf                    # Show banner
sentineldf --help            # Show help
sentineldf --version         # Show version
sentineldf scan-text         # Scan text
sentineldf scan-file         # Scan file
sentineldf scan-folder       # Scan folder
python -m sentineldf         # Alternative entry point
```

### Python Imports
```python
from sentineldf import (
    SentinelDF,              # Main client
    ScanResult,              # Result class
    FileScanner,             # File utilities
    scan_and_analyze,        # Batch scanning
    ThreatReport,            # Detailed reports
    generate_batch_report,   # Batch reports
    save_report_to_html,     # HTML export
)
```

---

## 🎯 Post-Publish Checklist

After successful publish:

- [ ] Verify package appears on https://pypi.org/project/sentineldf-ai/
- [ ] Test fresh install: `pip install sentineldf-ai`
- [ ] Test CLI: `sentineldf --help`
- [ ] Test Python import: `from sentineldf import SentinelDF`
- [ ] Check welcome message displays
- [ ] Update documentation website
- [ ] Announce on social media
- [ ] Update GitHub README
- [ ] Create GitHub release/tag

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Build | `python -m build` |
| Upload | `python -m twine upload dist/*` |
| Clean | `Remove-Item -Recurse -Force dist, build, *.egg-info` |
| Test Install | `pip install dist/*.whl` |
| Uninstall | `pip uninstall sentineldf-ai -y` |

---

**🚀 Ready to publish? Copy the commands above and go!**
