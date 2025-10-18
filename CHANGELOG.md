# Changelog

All notable changes to SentinelDF will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-16

### Added

**Core Detection**
- Heuristic detector with 30+ high-severity phrase patterns
- Embedding outlier detection using SBERT + Isolation Forest
- Risk fusion with configurable weights (default: 0.4 heuristic, 0.6 embedding)
- Deterministic detection with fixed random seeds

**Advanced Heuristic Features**
- Unicode normalization (NFKD) for obfuscated text detection
- Co-occurrence detection for 7 term pairs (e.g., "ignore" + "instructions")
- ALL-CAPS imperative burst detection
- Imperative-at-start analysis (first 5 tokens)
- Extreme repetition detection (70%+ duplicate words)
- Nonlinear scoring with diminishing returns to prevent overshoot

**Performance & Caching**
- SQLite-based persistent cache (`./.cache/sentineldf.db`)
- SHA-256 content-addressable storage
- Schema versioning for cache invalidation
- 70-90% cache hit rates on warm runs
- 5-10x performance improvement with caching (16 → 133 docs/sec)

**MBOM (Material Bill of Materials)**
- Cryptographically signed audit trails using HMAC-SHA256
- Batch summaries with quarantine statistics
- Per-document risk scores and reasons
- MBOM validation CLI command

**User Interfaces**
- FastAPI backend with `/scan` and `/mbom` endpoints
- Streamlit interactive dashboard (637 lines)
  - File/folder input with upload support
  - Adjustable thresholds and weights
  - Risk distribution histogram
  - UMAP embedding visualization (cached, ≤1000 docs)
  - MBOM generation and download
- CLI tool (`sdf`) with three commands:
  - `sdf scan` - Analyze documents
  - `sdf mbom` - Create signed MBOMs
  - `sdf validate` - Verify MBOM signatures

**Testing & Quality**
- 172 comprehensive tests covering all components
- Value proof tests ensuring ≥50% poison detection rate
- Current detection: 56.2% (9/16 samples @ threshold 70)
- 0% false positive rate on clean samples
- Test execution: ~7-10 seconds

**Documentation**
- Comprehensive README (714 lines)
- Architecture diagrams (ASCII art)
- Detector explanations and rationale
- Performance benchmarks
- Troubleshooting guide (Windows/Unix)
- MBOM format specification

### Technical Details

**Dependencies**
- Python 3.10+ required
- FastAPI 0.104.1 for API backend
- Sentence Transformers 2.2.2 for embeddings
- Streamlit 1.28.1 for dashboard
- Click 8.1.7 for CLI
- No external API calls - fully local processing

**Compatibility**
- Cross-platform: Windows, macOS, Linux
- CPU-only (no GPU required)
- SQLite for caching (no external database)

### Known Limitations

**Detection**
- Unicode obfuscation: Some fancy unicode patterns not detected
- Null byte injection: Null byte patterns score 0
- Context-dependent attacks: Subtle attacks without explicit keywords may slip through
- Current detection rate: 56% (room for improvement to 80%+ target)

**Performance**
- CPU-bound: Embeddings are slow on CPU (~16 docs/sec cold run)
- No GPU support: PyTorch CPU-only implementation
- Single-process: Heuristics not parallelized yet

**Infrastructure**
- Local-only: No distributed caching
- SQLite limitations: May not scale to millions of documents without sharding

### Security

- **Local processing**: No data leaves your machine
- **Deterministic**: Reproducible results for compliance
- **HMAC signing**: Tamper-proof audit trails
- **Secret management**: HMAC_SECRET via environment variables

### Configuration

Default thresholds (tunable via environment variables):
- `HEURISTIC_WEIGHT=0.4`
- `EMBEDDING_WEIGHT=0.6`
- `RISK_QUARANTINE_THRESHOLD=70`
- `HMAC_SECRET=dev-secret-key-change-in-production`

### Contributors

- Varun Sripad Kota (varunsripadkota@gmail.com)

---

## [Unreleased]

### Planned Features

- Multi-processing for heuristics
- GPU support for embeddings (PyTorch CUDA)
- YAML policy engine for custom rules
- Incremental MBOM (append-only ledger)
- Shared bad-hash signature database
- Multi-modal support (images, audio)
- Pluggable vector backends

---

**Legend**:
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes
