# 🛡️ SentinelDF - Data Firewall for LLM Training

**SentinelDF** is a data quality and security system designed to detect poisoned or malicious samples in LLM training datasets. It combines heuristic analysis, embedding-based outlier detection, and cryptographic provenance tracking (MBOM - Material Bill of Materials) to ensure dataset integrity.

## Why SentinelDF?

LLM training datasets are vulnerable to:
- **Prompt injection attacks** embedded in training data
- **Backdoor triggers** that activate malicious behavior
- **HTML/JavaScript payloads** in scraped web content
- **Adversarial examples** designed to corrupt model behavior
- **Data poisoning** at scale via automated crawlers

SentinelDF provides:
✅ **Local-only processing** - No external API calls, runs on CPU  
✅ **Deterministic detection** - Reproducible results for compliance  
✅ **Cryptographic audit trails** - HMAC-signed MBOMs for provenance  
✅ **Fast scanning** - Persistent caching for warm runs  
✅ **Interactive dashboard** - Streamlit UI for review and triage  

---

## 🚀 Quickstart

### Prerequisites

- Python 3.10 or higher
- pip and virtualenv

### Installation

1. **Clone the repository:**

```bash
git clone <repository-url>
cd sentineldf
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run Tests

Verify the installation by running the test suite:

```bash
pytest tests/ -v
```

Or use the Makefile:

```bash
make test
```

### Run the Application

**Start the FastAPI backend:**

```bash
uvicorn backend.app:app --reload
# Or: make run-api
```

Access the API at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

**Start the Streamlit Dashboard:**

```bash
streamlit run frontend/streamlit_app.py
# Or: make run-ui
# Or: make ui
```

Access the dashboard at: `http://localhost:8501`

---

## 📊 Run the Dashboard

The Streamlit dashboard provides an interactive interface for scanning documents, analyzing risk patterns, and generating signed audit trails.

### Features

- **📁 File/Folder Input:** Load documents from local paths or upload files directly
- **🎚️ Threshold Controls:** Adjust quarantine threshold and detector weights with live validation
- **🔍 Batch Scanning:** Analyze multiple documents with progress tracking
- **📊 Summary Cards:** View total documents, quarantine counts, average/P95 risk
- **📋 Results Table:** Interactive table with risk bars, reason chips, and quarantine toggles
- **👁️ Document Viewer:** Click to view full content, signals, and reasons for each document
- **📈 Visualizations:**
  - Risk distribution histogram with quarantine threshold line
  - UMAP embedding scatter plot (for ≤1000 documents, cached for performance)
- **🔐 MBOM Generation:** Download cryptographically signed audit trails as JSON
- **💾 Cache Management:** View cache statistics and clear caches

### Usage

1. **Start the dashboard:**
```bash
make ui
```

2. **Configure detection:**
   - Choose input method (local path or upload)
   - Adjust quarantine threshold (0-100)
   - Set detector weights (must sum to 1.0)

3. **Scan documents:**
   - Click "🔍 Scan" button
   - View progress bar and timing info
   - Results appear automatically

4. **Interact with results:**
   - Toggle quarantine status per document
   - Click "👁️" to view document details
   - Explore risk distribution histogram
   - View UMAP embeddings (if ≤1000 docs)

5. **Generate MBOM:**
   - Enter approver email
   - Click "🔐 Generate MBOM"
   - Download signed JSON file
   - Validate with: `sdf validate --mbom <file>`

### Performance Notes

- **UMAP Visualization:** Automatically skipped for >1000 documents or if computation exceeds 30s time budget
- **Caching:** Results are cached in session state; embeddings are cached with 1-hour TTL
- **Batch Processing:** Uses existing backend caches for heuristic and embedding scores

### Example Workflow

```bash
# Scan sample corpus
1. Set path to "data/samples"
2. Keep default thresholds (70, weights 0.4/0.6)
3. Click "Scan"
4. Review 20 documents with risk scores
5. See 1 quarantined document
6. Toggle quarantine if needed
7. Generate MBOM with your email
8. Download and validate MBOM
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SentinelDF Pipeline                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Input Documents │
                    │  (text/JSON)     │
                    └──────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────────┐
         │          Detection Layer                │
         ├─────────────────────────────────────────┤
         │                                         │
         │  ┌──────────────┐   ┌───────────────┐  │
         │  │  Heuristic   │   │  Embedding    │  │
         │  │  Detector    │   │  Outlier      │  │
         │  │              │   │  Detector     │  │
         │  │  • Patterns  │   │  • SBERT      │  │
         │  │  • Keywords  │   │  • Isolation  │  │
         │  │  • Entropy   │   │    Forest     │  │
         │  └──────────────┘   └───────────────┘  │
         │         │                    │          │
         │         └────────┬───────────┘          │
         │                  ▼                      │
         │          ┌──────────────┐               │
         │          │  Risk Fusion │               │
         │          │  (weighted)  │               │
         │          └──────────────┘               │
         └─────────────────┬───────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Risk Score (0-100)   │
              │   Quarantine Decision  │
              └────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │         MBOM Generation             │
         │  • Batch summary                    │
         │  • Per-doc risk scores              │
         │  • HMAC signature                   │
         │  • Timestamp & approver             │
         └─────────────────────────────────────┘
```

### Module Map

- **`backend/detectors/`** - Core detection algorithms
  - `heuristic_detector.py` - Pattern matching, entropy, co-occurrence
  - `embedding_outlier.py` - SBERT + Isolation Forest
  - `fusion.py` - Risk score combination strategies

- **`backend/mbom/`** - Provenance tracking (planned expansion)
  - Signing, validation, ledger (current: in `backend/app.py`)

- **`backend/utils/`** - Infrastructure
  - `config.py` - Environment-based configuration
  - `cache.py` - Redis integration (optional)
  - `persistent_cache.py` - Local SQLite cache
  - `io_manager.py` - File operations

- **`frontend/`** - Streamlit dashboard
- **`cli/`** - Command-line interface (`sdf` tool)
- **`tests/`** - 172 tests covering all components

## 🔍 Detectors Overview

### Heuristic Detector

**Purpose:** Fast, interpretable detection of known attack patterns

**Features:**
- **High-severity phrase matching** (23 patterns)
  - "ignore all previous instructions"
  - "override safety", "disable guardrails"
  - "backdoor trigger", "jailbreak", "dan mode"
- **Co-occurrence detection** (7 term pairs)
  - (ignore, instructions), (override, safety), (bypass, policy)
- **ALL-CAPS imperatives** with safety keywords
- **HTML/JS injection** patterns (`<script>`, `onerror=`, etc.)
- **Extreme repetition** detection (70%+ duplicate tokens)
- **Entropy analysis** (high/low entropy signals)

**Scoring:** Nonlinear with diminishing returns to prevent overshoot  
**Weight:** Default 0.4 (configurable via `HEURISTIC_WEIGHT`)

### Embedding Outlier Detector

**Purpose:** Catch novel attacks via distributional anomalies

**Model:** `sentence-transformers/all-MiniLM-L6-v2`  
**Method:** Isolation Forest on 384-dim embeddings  
**Seed Corpus:** 20 benign examples for baseline distribution

**Features:**
- **Contrastive detection** - Compares against seed corpus
- **Deterministic** - Fixed random seed for reproducibility
- **Cached embeddings** - SQLite persistent cache with SHA-256 keys

**Scoring:** Raw anomaly score normalized to [0,1]  
**Weight:** Default 0.6 (configurable via `EMBEDDING_WEIGHT`)

### Risk Fusion

**Formula:**
```python
risk = (heuristic_score * heuristic_weight + 
        embedding_score * embedding_weight) * 100
```

**Thresholds:**
- **Quarantine:** Default 70 (configurable via `RISK_QUARANTINE_THRESHOLD`)
- **Elevated:** 50-69 (warning zone)
- **Clean:** 0-49

**Rationale:**  
Weighted fusion allows tuning for precision vs recall. Default weights (0.4/0.6) favor embeddings for generalization while keeping heuristics for interpretability.

**Tuning:**
```bash
# Increase heuristic weight for stricter known-pattern enforcement
export HEURISTIC_WEIGHT=0.55
export EMBEDDING_WEIGHT=0.45

# Lower threshold for MVP/high-recall scenarios
export RISK_QUARANTINE_THRESHOLD=60
```

## ⚡ Performance & Caching

### Cache Architecture

**Location:** `./.cache/sentineldf.db` (SQLite)  
**Versioning:** Schema version 1 (auto-invalidates on schema bump)  
**Keys:** SHA-256 hash of normalized content (lowercase, stripped)

**Cached Data:**
- **Embeddings:** 384-dim vectors + model name/version
- **Heuristics:** Score, reasons, features + detector version

**Hit Rates:** Typically 70-90% on second run of same corpus

### Performance Metrics

**Cold Run (no cache):**
- ~15-25 docs/sec on CPU (varies by doc length)
- Embedding computation dominates (SBERT inference)

**Warm Run (cache hit):**
- ~100-200 docs/sec on CPU
- Cache lookup is O(1) with SQLite indexing

**Batch Optimization:**
- Embeddings computed in batches of 128 (configurable)
- Heuristics parallelizable (future: multiprocessing)

### Cache Management

**View cache stats:**
```bash
sdf scan --path data/samples  # Shows cache hit/miss in output
```

**Clear cache:**
```bash
rm -rf .cache/
# Or via Python:
python -c "from backend.utils.persistent_cache import get_persistent_cache; get_persistent_cache().clear()"
```

**Cache location:**
- Default: `./.cache/sentineldf.db`
- Override: Set `CACHE_DIR` environment variable

### Time Budgeting

**CLI:**
```bash
sdf scan --path data/ --time-budget 30  # Skip UMAP if >30s
```

**Behavior:**
- Skips non-critical operations (UMAP visualization)
- Always returns per-document results
- Sets `"budget_exhausted": true` in batch summary

## 🔐 MBOM (Material Bill of Materials)

### What's Included

**Batch Summary:**
- `mbom_id` - Unique identifier
- `batch_id` - Scan batch identifier
- `timestamp` - ISO 8601 timestamp
- `approved_by` - Approver email
- `summary` - Aggregated stats (total, quarantined, allowed, avg_risk)
- `results_hash` - SHA-256 of full results array
- `signature` - HMAC-SHA256 signature

**Per-Document Results:**
- `doc_id` - Document identifier
- `risk` - Final risk score (0-100)
- `quarantine` - Boolean decision
- `heuristic` - Heuristic detector output
- `embedding` - Embedding detector output
- `timestamp` - Detection timestamp

**Example:**
```json
{
  "mbom_id": "mbom_20241016_123456",
  "batch_id": "batch_abc123",
  "timestamp": "2024-10-16T12:34:56Z",
  "approved_by": "analyst@example.com",
  "signature": "a1b2c3d4e5f6...",
  "summary": {
    "total_docs": 20,
    "quarantined": 2,
    "allowed": 18,
    "avg_risk": 12.5
  },
  "results_hash": "sha256:7f8e9d...",
  "results": [...]  
}
```

### HMAC Signing

**Algorithm:** HMAC-SHA256  
**Secret:** `HMAC_SECRET` environment variable  
**Signed Payload:** `{mbom_id, batch_id, approved_by, timestamp, summary, results_hash}`

**Validation:**
```bash
sdf validate --mbom path/to/mbom.json
# Output: ✅ MBOM signature valid
```

**Secret Rotation:**
1. Generate new secret: `openssl rand -hex 32`
2. Update environment: `export HMAC_SECRET=<new_secret>`
3. Re-sign historical MBOMs if needed (custom script)

### Use Cases

- **Compliance Audit:** Prove which samples were quarantined and when
- **Dataset Provenance:** Track data lineage across processing stages
- **Reproducibility:** Verify detection results match original scan
- **Access Control:** Signature prevents tampering with decisions

## 📁 Project Structure

```
sentineldf/
├── backend/                    # Core detection and MBOM logic
│   ├── app.py                 # FastAPI application entry point
│   ├── detectors/             # Detection algorithms
│   │   ├── heuristic_detector.py   # Rule-based detection
│   │   ├── embedding_detector.py   # Embedding outlier detection
│   │   └── fusion.py              # Ensemble fusion strategies
│   ├── mbom/                  # Material Bill of Materials system
│   │   ├── signer.py          # Cryptographic signing
│   │   └── ledger.py          # Provenance ledger
│   └── utils/                 # Shared utilities
│       ├── io_manager.py      # Dataset I/O operations
│       ├── hashing.py         # Cryptographic hashing
│       └── config.py          # Configuration management
├── frontend/                   # Streamlit web interface
│   └── streamlit_app.py       # Interactive UI for detection
├── cli/                        # Command-line interface
│   └── sdf.py                 # CLI for batch processing
├── tests/                      # Test suite
│   ├── test_heuristics.py     # Heuristic detector tests
│   ├── test_embedding_outliers.py  # Embedding detector tests
│   └── test_mbom.py           # MBOM system tests
├── data/                       # Sample datasets
│   └── samples/               # 20 sample texts (6 marked poison-like)
├── reports/                    # Generated detection reports
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata
├── Makefile                   # Development tasks
├── .pre-commit-config.yaml    # Pre-commit hooks
└── README.md                  # This file
```

---

## 🗺️ Development Roadmap

### **Phase 1: Core Detection (Current - Scaffolding Complete)**

- ✅ Project scaffold and structure
- ⏳ Implement heuristic detector:
  - Text entropy analysis
  - Repetition and pattern detection
  - Length and complexity statistics
- ⏳ Implement embedding detector:
  - Sentence transformer integration
  - Isolation Forest for outlier detection
  - DBSCAN clustering support
- ⏳ Build detector fusion:
  - Weighted averaging
  - Voting ensembles
  - Confidence thresholding

### **Phase 2: MBOM & Provenance Tracking**

- ⏳ Cryptographic signing:
  - Ed25519 keypair generation
  - Record signing and verification
  - Timestamped attestations
- ⏳ Ledger implementation:
  - JSON-based ledger storage
  - Entry hashing and chaining
  - Lineage queries and reports
- ⏳ Integration with detection pipeline:
  - Automatic ledger entries on detection
  - Dataset hash tracking
  - Audit trail generation

### **Phase 3: Production Features**

- ⏳ Enhanced UI/UX:
  - Interactive result visualization
  - Bulk dataset upload and processing
  - Real-time detection progress
- ⏳ CLI improvements:
  - Batch processing pipelines
  - Report export (HTML, JSON, CSV)
  - Configuration file support
- ⏳ Performance optimization:
  - Parallel processing for large datasets
  - Caching for embeddings
  - Incremental detection
- ⏳ Documentation & deployment:
  - API documentation
  - User guide and tutorials
  - Docker containerization

---

## 🧪 Testing

**Expected Status:** 172 tests passing

Run the full test suite:

```bash
pytest -q
# Output: 172 passed in ~7-10s
```

Run specific test modules:

```bash
pytest tests/test_heuristics.py -v
pytest tests/test_embedding_outliers.py -v  
pytest tests/test_mbom.py -v
pytest tests/test_value_proof.py -v  # Detection effectiveness tests
```

**Key Test Suites:**
- **`test_heuristics.py`** - Pattern matching, entropy, co-occurrence
- **`test_embedding_outliers.py`** - SBERT integration, outlier detection
- **`test_fusion.py`** - Risk score combination logic
- **`test_value_proof.py`** - End-to-end detection quality (≥50% poison detection)
- **`test_mbom.py`** - HMAC signing and validation
- **`test_api.py`** - FastAPI endpoint integration
- **`test_cli.py`** - CLI command interface

**Running with Coverage:**
```bash
pytest --cov=backend --cov-report=term-missing
```

---

## 🛠️ Development

### Code Quality Tools

Format code:

```bash
make format
# Or manually:
black backend/ frontend/ cli/ tests/
isort backend/ frontend/ cli/ tests/
```

Run linters:

```bash
make lint
# Or manually:
ruff check backend/ frontend/ cli/ tests/
mypy backend/ --ignore-missing-imports
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

Run hooks manually:

```bash
pre-commit run --all-files
```

---

## 📊 Sample Data

The `data/samples/` directory contains 20 sample text files for testing:

- **10 clean samples**: Normal training data (sample_*.txt)
- **10 poison samples**: Attack patterns (poison_*.txt, sample_*.txt with POISON-LIKE marker)

**Poison Patterns Include:**
- Prompt injection ("ignore previous instructions")
- Jailbreak attempts ("DAN mode", "developer mode")
- Backdoor triggers ("backdoor activate")
- HTML/JS injection (`<script>`, `onerror=`)
- Unicode obfuscation (mathematical alphanumerics)
- Extreme repetition patterns

These samples serve as ground truth for the value proof tests.

## 🔧 Troubleshooting

### Windows Path Issues

**Problem:** Backslashes in paths cause errors  
**Solution:** Use forward slashes or raw strings
```python
path = "data/samples"  # ✅ Works
path = r"data\samples"  # ✅ Works
path = "data\\samples"  # ✅ Works
```

### Virtual Environment Not Activating

**Windows:**
```bash
# If execution policy blocks scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**Unix/macOS:**
```bash
# Ensure activate script is executable:
chmod +x venv/bin/activate
source venv/bin/activate
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'backend'`  
**Solution:** Ensure you're in the project root and virtual environment is active
```bash
pwd  # Should show .../sentineldf
python -c "import sys; print(sys.prefix)"  # Should show venv path
```

### Tests Failing After Code Changes

**Problem:** Cached results from old detector version  
**Solution:** Clear persistent cache
```bash
rm -rf .cache/
pytest -q
```

### Slow Embedding Computation

**Problem:** First run takes long time  
**Expected:** Embeddings are cached after first run. Subsequent runs ~5-10x faster.

**Optimization:**
```python
# In backend/detectors/embedding_outlier.py:
# Increase batch_size for GPU if available (default 128 for CPU)
detector = EmbeddingOutlierDetector(batch_size=256)  
```

### HMAC Validation Fails

**Problem:** `sdf validate` reports invalid signature  
**Cause:** `HMAC_SECRET` mismatch or MBOM file modified

**Solution:**
1. Verify secret matches: `echo $HMAC_SECRET`
2. Re-generate MBOM with correct secret
3. Check MBOM file not corrupted (valid JSON)

### Streamlit Port Already in Use

**Problem:** `Address already in use` error  
**Solution:** Kill existing process or use different port
```bash
# Find process:
lsof -i :8501  # Unix/macOS
netstat -ano | findstr :8501  # Windows

# Use different port:
streamlit run frontend/streamlit_app.py --server.port 8502
```

---

## 🔄 Continuous Improvement

SentinelDF uses a systematic approach to incorporate feedback and maintain enterprise-grade quality:

### Metrics & Monitoring
```bash
# Generate metrics report from recent scans
make metrics

# Aggregate user feedback
make feedback-summary
```

### Iteration Process
- **[Iteration Plan](docs/iteration/ITERATION_PLAN.md)** - Development workflow, feedback intake, model improvement
- **[Product Metrics](docs/iteration/PRODUCT_METRICS.md)** - KPIs and targets (detection rate, FP rate, speed)
- **[Risk Register](docs/iteration/RISK_REGISTER.md)** - Operational and technical risks with mitigations
- **[Review Cadence](docs/iteration/REVIEW_CADENCE.md)** - Weekly triage, pilot syncs, retrospectives

### Quality Gates
- Detection rate ≥70% (target: 80%)
- False positive rate ≤10%
- All tests passing (172/172)
- 2 pilot sign-offs before release

---

## 📖 Documentation

- **[5-Minute Demo](docs/DEMO.md)** - Live demo script with expected outputs
- **[Security](docs/SECURITY.md)** - Data handling, HMAC, threat model
- **[Security Brief](docs/SECURITY-BRIEF.md)** - Compliance details (SOC 2, GDPR, HIPAA)
- **[Roadmap](docs/ROADMAP.md)** - Near-term and future plans
- **[Contributing](CONTRIBUTING.md)** - Developer guide and PR checklist
- **[Pilot Proposal](docs/PILOT-PROPOSAL.md)** - 30-day POC program details

## 📝 License

Apache License 2.0 - See [LICENSE](LICENSE) file for details

Copyright © 2024 Varun Sripad Kota

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- PR process

## 📧 Contact

**Varun Sripad Kota**  
Email: varunsripadkota@gmail.com

---

**Status:** Phase 11 Complete - Production Ready ✅**
