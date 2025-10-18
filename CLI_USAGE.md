# SentinelDF CLI Usage Guide

The SentinelDF CLI provides command-line tools for scanning documents, creating signed MBOMs, and validating integrity.

## Installation

```bash
# Install Click if not already installed
pip install click==8.1.7

# Or install the package in development mode
pip install -e .
```

## Commands

### 1. `sdf scan` - Scan Documents

Analyze documents for threats and generate a JSON report.

**Usage:**
```bash
sdf scan --path data/samples
sdf scan --path data/samples --output custom_report.json
```

**Options:**
- `--path` (required): Path to directory containing .txt files or single file
- `--output` (optional): Custom output path (default: `reports/scan_{timestamp}.json`)

**Exit Codes:**
- `0`: All documents passed (no quarantine)
- `1`: One or more documents flagged for quarantine

**Example Output:**
```
🔧 Loading configuration... ✓
📂 Loading files from data/samples... ✓ Found 3 document(s)
🔍 Analyzing documents...
Processing  [####################################]  100%

✅ Scan complete! Report saved to: reports/scan_20250116_120000.json

📊 Summary:
   Total documents: 3
   Allowed: 2
   Quarantined: 1
   Average risk: 45.33
   Max risk: 85
   Batch ID: batch_abc123def456

⚠️  1 document(s) flagged for quarantine
```

**Report Format:**
```json
{
  "scan_metadata": {
    "timestamp": "2025-01-16T12:00:00Z",
    "source_path": "data/samples",
    "tool_version": "1.0.0"
  },
  "summary": {
    "total_docs": 3,
    "quarantined_count": 1,
    "allowed_count": 2,
    "avg_risk": 45.33,
    "max_risk": 85,
    "batch_id": "batch_abc123def456"
  },
  "results": [...]
}
```

---

### 2. `sdf mbom` - Create Signed MBOM

Generate a cryptographically signed Machine-readable Bill of Materials from scan results.

**Usage:**
```bash
sdf mbom --results reports/scan_*.json --approver you@company.com
sdf mbom --results reports/scan_20250116_120000.json --approver admin@org.com --output custom_mbom.json
```

**Options:**
- `--results` (required): Path to scan results JSON (supports wildcards)
- `--approver` (required): Email or identifier of the approver
- `--output` (optional): Custom output path (default: `reports/mbom_{timestamp}.json`)

**Exit Codes:**
- `0`: MBOM created successfully
- `1`: Creation failed

**Example Output:**
```
📄 Loading scan results from: reports/scan_20250116_120000.json
✓ Loaded 3 document result(s)
🔐 Generating signed MBOM... ✓

✅ MBOM created and signed! Saved to: reports/mbom_20250116_120100.json

📋 MBOM Details:
   MBOM ID: mbom_a1b2c3d4e5f6
   Batch ID: batch_abc123def456
   Approved by: you@company.com
   Timestamp: 2025-01-16T12:01:00Z
   Signature: 8f7a6b5c4d3e2f1a...1a2b3c4d5e6f7a8b
   Documents: 3
   Quarantined: 1
```

**MBOM Format:**
```json
{
  "mbom_id": "mbom_a1b2c3d4e5f6",
  "batch_id": "batch_abc123def456",
  "approved_by": "you@company.com",
  "timestamp": "2025-01-16T12:01:00Z",
  "signature": "8f7a6b5c4d3e2f1a...",
  "summary": {
    "total_docs": 3,
    "quarantined": 1,
    "allowed": 2,
    "avg_risk": 45.33
  },
  "results": [...],
  "metadata": {
    "source_file": "reports/scan_20250116_120000.json",
    "tool_version": "1.0.0"
  }
}
```

---

### 3. `sdf validate` - Validate MBOM Signature

Verify the cryptographic signature and integrity of MBOM documents.

**Usage:**
```bash
sdf validate --mbom reports/mbom_*.json
sdf validate --mbom reports/mbom_20250116_120100.json
```

**Options:**
- `--mbom` (required): Path to MBOM file (supports wildcards)

**Exit Codes:**
- `0`: All MBOMs valid
- `1`: One or more MBOMs invalid or tampered

**Example Output (Valid):**
```
🔍 Validating: reports/mbom_20250116_120100.json
   ✅ Signature valid
      MBOM ID: mbom_a1b2c3d4e5f6
      Approved by: you@company.com
      Timestamp: 2025-01-16T12:01:00Z
      Documents: 3

✅ All MBOMs validated successfully
```

**Example Output (Invalid):**
```
🔍 Validating: reports/mbom_tampered.json
   ❌ Signature mismatch - MBOM may be tampered!
      Expected: 8f7a6b5c4d3e2f1a...
      Got:      1a2b3c4d5e6f7a8b...

❌ Some MBOMs failed validation
```

---

## Complete Workflow Example

```bash
# Step 1: Scan documents
sdf scan --path data/samples
# Output: reports/scan_20250116_120000.json
# Exit code: 1 (quarantine detected)

# Step 2: Review and approve, then create MBOM
sdf mbom --results reports/scan_*.json --approver security@company.com
# Output: reports/mbom_20250116_120100.json
# Exit code: 0

# Step 3: Validate MBOM integrity
sdf validate --mbom reports/mbom_*.json
# Exit code: 0 (valid signature)
```

---

## Integration with Backend

The CLI reuses the same detection logic as the FastAPI endpoints:
- `_analyze_document()` - Document analysis
- `_sign_mbom()` - HMAC-SHA256 signing
- `_generate_batch_id()` - Batch ID generation

This ensures consistency between CLI and API results.

---

## Configuration

The CLI uses the same configuration as the backend:
- `APP_HEURISTIC_WEIGHT` - Heuristic detector weight (default: 0.4)
- `APP_EMBEDDING_WEIGHT` - Embedding detector weight (default: 0.6)
- `APP_QUARANTINE_THRESHOLD` - Risk threshold for quarantine (default: 70)

Set via environment variables or `.env` file.

---

## Testing

Run CLI tests:
```bash
pytest tests/test_cli.py -v
```

All tests use Click's `CliRunner` for isolated testing without side effects.

---

## Troubleshooting

**Issue:** "Backend modules not available"
- **Solution:** Ensure you're running from the `sentineldf` directory with backend module in PYTHONPATH

**Issue:** "No documents found to scan"
- **Solution:** Ensure the path contains `.txt` files or is a valid text file

**Issue:** "No files matching pattern"
- **Solution:** Check the glob pattern and ensure files exist in the reports directory

**Issue:** "Signature mismatch"
- **Solution:** The MBOM file may have been modified. Regenerate the MBOM from original scan results.
