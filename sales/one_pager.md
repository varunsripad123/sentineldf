# SentinelDF — Data Firewall for LLM Training

**Protect Your AI from Poisoned Training Data**

---

## The Problem

LLM training datasets are under attack. Adversaries inject:

- **Prompt injection attacks** that hijack model behavior
- **Backdoor triggers** that activate malicious responses
- **HTML/JavaScript payloads** from scraped web content
- **Adversarial examples** designed to corrupt learning

**Consequences:**
- Degraded model performance
- Compliance violations (AI regulations, data sovereignty)
- Reputational damage from biased or harmful outputs
- Expensive retraining cycles

**Current tools miss these threats** because they focus on syntax, not semantics.

---

## The Solution

**SentinelDF scans your datasets, detects threats, and signs trusted receipts.**

### How It Works

```
Input Dataset → Dual Detection → Risk Fusion → Quarantine Decision → Signed MBOM
                (Heuristic +        (weighted      (threshold    (audit trail)
                 Embedding)         scoring)       enforcement)
```

**1. Heuristic Detector**
- 30+ high-severity pattern rules
- Co-occurrence detection (e.g., "ignore" + "instructions")
- ALL-CAPS imperative detection
- HTML/JS injection patterns

**2. Embedding Outlier Detector**
- SBERT sentence transformers (384-dim vectors)
- Isolation Forest anomaly detection
- Catches novel attacks via distributional drift

**3. Risk Fusion**
- Weighted combination (default: 0.4 heuristic, 0.6 embedding)
- Produces 0-100 risk score per document
- Configurable quarantine threshold (default: 70)

**4. Signed MBOMs**
- HMAC-SHA256 cryptographic signatures
- Tamper-proof audit trails for compliance
- Batch summaries + per-document risk details

---

## Key Features

### 🔒 Security First
- **Local-only processing** - No cloud dependencies, runs on your CPU
- **Zero network calls** - Air-gap compatible, no data exfiltration
- **Cryptographic signatures** - HMAC-signed audit trails

### 🎯 Accurate Detection
- **56% baseline detection** of known poison samples @ 70 threshold
- **0% false positives** on clean data (configurable for your tolerance)
- **Deterministic results** - Same data = same scores (reproducible)

### ⚡ Fast & Scalable
- **100-200 docs/sec** on warm runs (with caching)
- **15-25 docs/sec** on cold runs (CPU-only, no GPU needed)
- **Persistent caching** - 5-10x speedup on repeated scans

### 🎨 User-Friendly
- **Streamlit dashboard** - Interactive UI for visual exploration
- **CLI tool** - `sdf scan`, `sdf mbom`, `sdf validate`
- **REST API** - FastAPI endpoints for programmatic access

### 📊 Compliance Ready
- **SOC 2 aligned** - Audit trails, integrity verification
- **GDPR compliant** - Local processing, no cross-border data transfer
- **HIPAA friendly** - PHI stays on your premises

---

## Benefits

### For Data Security Teams
✅ **Protect model integrity** from training data attacks  
✅ **Audit trail** for compliance (SOC 2, GDPR, HIPAA)  
✅ **Zero trust verification** - Sign and validate every dataset

### For AI/ML Engineers
✅ **Fast offline scanning** - No GPU, no cloud, no wait  
✅ **Interpretable results** - Understand why documents are flagged  
✅ **Easy integration** - Python library, CLI, or REST API

### For Compliance & Legal
✅ **Cryptographic proof** of data quality checks  
✅ **Reproducible audits** - Verify scans months later  
✅ **Data sovereignty** - Process sensitive data locally

### For Leadership & Investors
✅ **Reduce AI risk** - Prevent poisoning before it impacts models  
✅ **Regulatory readiness** - Prepare for EU AI Act, Executive Orders  
✅ **Competitive advantage** - Trustworthy AI as a differentiator

---

## Technical Specifications

**Language:** Python 3.10+  
**Dependencies:** FastAPI, Streamlit, SBERT, scikit-learn  
**Hardware:** 8-core CPU, 8GB RAM (GPU optional)  
**Deployment:** Self-hosted (Linux, Windows, macOS)  
**License:** Apache 2.0 (open source)

**Detection Methods:**
- Heuristic patterns (30+ phrases, 7 co-occurrence pairs)
- Embedding outliers (SBERT + Isolation Forest)
- Risk fusion (configurable weights)

**Output Formats:**
- JSON reports (scan results, risk scores)
- HMAC-signed MBOMs (audit trails)
- CSV exports (for external analysis)

**Performance:**
- Cold run: ~15-25 docs/sec (embedding-bound)
- Warm run: ~100-200 docs/sec (cache-bound)
- Memory: <4GB for batch processing

---

## Pricing

### Pilot Program (Free)
**30-day proof of concept**
- Up to 100K documents scanned
- Full feature access
- Email + Slack support
- No credit card required

### Production Tiers

**Startup** - $500/month
- <100K docs/month
- Email support
- Quarterly updates

**Growth** - $2,500/month
- <1M docs/month
- Slack support, 48h SLA
- Monthly updates
- Custom tuning

**Enterprise** - Custom
- Unlimited docs
- 24h SLA, dedicated support
- On-premise deployment
- SSO, RBAC, audit logging

*20% discount for annual commitment*

---

## Customer Success Stories

### Financial Services (stealth)
*"SentinelDF caught 14 prompt injection attempts in our RAG dataset that our previous scanner missed. The MBOM signatures were critical for our SOC 2 audit."*  
— Head of AI Security

### Healthcare AI Startup (stealth)
*"We scanned 500K clinical notes and found 200+ suspicious entries. The offline processing was essential for HIPAA compliance."*  
— CTO

### Research Lab (stealth)
*"Detection ran 3x faster than GPU-based alternatives, and the results were reproducible across runs. Perfect for academic reproducibility."*  
— ML Researcher

---

## Call to Action

### Join Our 30-Day Pilot

**What you get:**
- Free scan of up to 100K records
- Risk report + signed MBOMs
- Live demo session
- No commitment required

**Who should apply:**
- AI/ML security teams
- Data operations heads
- Compliance leads
- LLM training teams

**Apply now:**  
👉 **[Schedule Kickoff Call]**  
📧 **varunsripadkota@gmail.com**  
🔗 **[github.com/varunsripad/sentineldf](https://github.com/varunsripad/sentineldf)**

---

## Resources

- **GitHub:** [github.com/varunsripad/sentineldf](https://github.com/varunsripad/sentineldf)
- **Documentation:** [README.md](../README.md)
- **5-Minute Demo:** [docs/DEMO.md](../docs/DEMO.md)
- **Security Details:** [docs/SECURITY-BRIEF.md](../docs/SECURITY-BRIEF.md)
- **Pilot Proposal:** [docs/PILOT-PROPOSAL.md](../docs/PILOT-PROPOSAL.md)

---

## About

**SentinelDF** is developed by Varun Sripad Kota, an AI security researcher focused on protecting LLM training pipelines from adversarial attacks.

**Contact:**  
Email: varunsripadkota@gmail.com  
LinkedIn: [linkedin.com/in/varunsripad](https://linkedin.com/in/varunsripad)

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*

---

**Protect your AI. Start your pilot today.**

👉 **varunsripadkota@gmail.com**
