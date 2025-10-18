# SentinelDF Iteration Plan

**Version:** 0.1.0  
**Last Updated:** 2024-10-16  
**Owner:** Engineering Team

---

## Purpose

This document defines our continuous improvement process for SentinelDF. It ensures we systematically incorporate pilot feedback, track detection quality, and maintain enterprise-grade reliability.

---

## Metrics Loop

### Daily Tracking

**What We Track:**
- Detection rate (% of known poison samples caught)
- False positive rate (% of clean samples flagged)
- Scan throughput (docs/sec)
- Cache hit rate (%)
- Error count and types

**Data Sources:**
- `reports/scan_*.json` - Scan results with risk scores
- `feedback/*.json` - User-reported issues (false positives/negatives)
- `.cache/` - Cache performance metrics

**Process:**
```bash
# Run daily (automated via cron/Task Scheduler)
make metrics >> logs/daily_metrics.log

# Review metrics every morning
tail -f logs/daily_metrics.log
```

**Thresholds:**
- ⚠️ Yellow alert: Detection rate <60% or FP rate >15%
- 🚨 Red alert: Detection rate <50% or FP rate >20%

### Weekly Analysis

**Every Monday 10am:**
1. Review 7-day metrics trend
2. Identify anomalies or degradation
3. Compare against [PRODUCT_METRICS.md](PRODUCT_METRICS.md) KPIs
4. Create tickets for investigation

**Tools:**
```bash
# Generate weekly report
python scripts/weekly_report.py --days 7 --output reports/weekly_$(date +%Y%m%d).md
```

### Monthly Retrospective

**Last Friday of each month:**
1. Full metrics review (30-day trend)
2. Pilot feedback synthesis
3. Model drift analysis
4. Roadmap adjustment

---

## User Feedback Intake

### Feedback Collection

**Streamlit "Feedback" Button:**
```python
# In frontend/streamlit_app.py (future enhancement)
if st.button("📝 Report Issue"):
    feedback = {
        "timestamp": datetime.utcnow().isoformat(),
        "document_id": selected_doc_id,
        "current_risk": current_risk_score,
        "user_assessment": st.radio("Should this be quarantined?", ["Yes", "No"]),
        "category": st.selectbox("Issue type", ["False Positive", "False Negative", "Other"]),
        "notes": st.text_area("Additional details (optional)"),
    }
    
    # Save locally (anonymized - no raw content)
    feedback_path = Path("feedback") / f"feedback_{timestamp}.json"
    feedback_path.write_text(json.dumps(feedback, indent=2))
    
    st.success("Feedback submitted! Thank you.")
```

**Anonymization Rules:**
- ✅ Store: doc_id, risk score, user assessment, category
- ❌ Never store: raw document content, user identity, timestamps with PII

### Feedback Processing

**Weekly Review:**
```bash
# Aggregate feedback
make feedback-summary

# Output: feedback/summary_YYYYMMDD.json
{
  "period": "2024-10-01 to 2024-10-07",
  "total_feedback": 23,
  "false_positives": 12,
  "false_negatives": 8,
  "other": 3,
  "top_patterns": [
    "ALL-CAPS in legitimate docs (5 cases)",
    "Medical jargon flagged as injection (4 cases)",
    "Code snippets mistaken for HTML injection (3 cases)"
  ]
}
```

**Action Items:**
1. **False Positives:** Add exclusion patterns or adjust thresholds
2. **False Negatives:** Investigate missed samples, enhance detectors
3. **Other:** Triage for bugs, UX improvements, or documentation gaps

---

## Model Improvement Process

### Safe Tuning Workflow

**Step 1: Collect Ground Truth**
```bash
# Annotate pilot data
python scripts/annotate_pilot_data.py \
  --input data/pilot_customer_A/ \
  --output data/ground_truth/customer_A_labels.csv
```

**Step 2: Evaluate Current Model**
```bash
# Baseline metrics
python scripts/evaluate_detector.py \
  --ground-truth data/ground_truth/customer_A_labels.csv \
  --config backend/utils/config.py \
  --output reports/baseline_metrics.json
```

**Step 3: Tune Parameters (Versioned)**
```yaml
# configs/heuristic_v0.1.1.yaml (example - not yet implemented)
version: 0.1.1
weights:
  heuristic: 0.45  # Increased from 0.40
  embedding: 0.55  # Decreased from 0.60
thresholds:
  quarantine: 65   # Lowered from 70 for higher recall
patterns:
  exclude:
    - "medical_jargon/*"  # Whitelist for healthcare pilot
```

**Step 4: Test on Holdout Set**
```bash
# Evaluate tuned config
python scripts/evaluate_detector.py \
  --ground-truth data/ground_truth/holdout.csv \
  --config configs/heuristic_v0.1.1.yaml \
  --output reports/tuned_metrics.json

# Compare
python scripts/compare_metrics.py \
  reports/baseline_metrics.json \
  reports/tuned_metrics.json
```

**Step 5: A/B Test (Pilot Customers)**
- Deploy tuned config to 50% of new scans
- Monitor for 2 weeks
- Compare metrics between control (v0.1.0) and treatment (v0.1.1)

**Step 6: Promote or Rollback**
```bash
# If metrics improve:
git tag -a v0.1.1 -m "Tuned heuristics for healthcare pilot"
git push origin v0.1.1

# If metrics degrade:
git revert <commit_hash>
```

### Retrain Isolation Forest

**When to Retrain:**
- Embedding distribution drift detected (weekly check)
- New attack patterns emerge (feedback-driven)
- Dataset domain shift (e.g., switching from web scrapes to medical notes)

**Process:**
```bash
# 1. Collect new seed corpus (benign samples)
python scripts/update_seed_corpus.py \
  --new-samples data/pilot_benign/ \
  --existing backend/detectors/seed_corpus.json \
  --output backend/detectors/seed_corpus_v2.json

# 2. Retrain Isolation Forest
python scripts/retrain_isolation_forest.py \
  --seed-corpus backend/detectors/seed_corpus_v2.json \
  --output backend/detectors/isolation_forest_v2.pkl

# 3. Evaluate on test set
python scripts/evaluate_detector.py \
  --detector embedding \
  --model backend/detectors/isolation_forest_v2.pkl \
  --ground-truth data/ground_truth/test.csv

# 4. Promote if metrics improve
mv backend/detectors/isolation_forest_v2.pkl backend/detectors/isolation_forest.pkl
```

**Versioning:**
- Store old models in `backend/detectors/archive/`
- Tag releases with model version in CHANGELOG

---

## Release Cadence

### Monthly Stable Tags

**Schedule:**
- **v0.1.x** (October 2024 - January 2025) - MVP iterations
- **v0.2.x** (February 2025 - April 2025) - Enterprise features
- **v0.3.x** (May 2025 - July 2025) - Multi-modal support

**Versioning Scheme:**
- **Major (v1.0):** Breaking API changes, major architecture overhaul
- **Minor (v0.2):** New features, non-breaking enhancements
- **Patch (v0.1.1):** Bug fixes, tuning, documentation updates

**Release Process:**

**Week 1: Development**
- Merge PRs, implement features
- Run CI on every commit

**Week 2: Stabilization**
- Feature freeze (bug fixes only)
- Regression testing on pilot data
- Performance benchmarking

**Week 3: Validation**
- Internal pilot testing (2 sign-offs required)
- Documentation updates
- CHANGELOG preparation

**Week 4: Release**
```bash
# Tag and push
git tag -a v0.1.1 -m "Release v0.1.1 - Healthcare pilot tuning"
git push origin v0.1.1

# Build distribution
make build

# Upload to PyPI (if public)
twine upload dist/sentineldf-0.1.1-*

# Notify pilot customers
python scripts/notify_release.py --version v0.1.1 --recipients pilot_emails.txt
```

---

## Quality Gates

### Pre-Release Checklist

**Automated Checks:**
- [ ] All tests passing (`pytest -q`) - 100% pass rate required
- [ ] Code coverage ≥95% (`pytest --cov`)
- [ ] No linter errors (`ruff check`, `mypy`)
- [ ] Performance benchmarks within ±10% of baseline
- [ ] Security scan clean (`bandit -r backend/`)

**Manual Checks:**
- [ ] 2 pilot sign-offs (minimum)
  - Customer A: ___________ (Signature + Date)
  - Customer B: ___________ (Signature + Date)
- [ ] Documentation updated (README, CHANGELOG, API docs)
- [ ] Release notes drafted
- [ ] Breaking changes communicated (if any)

**Pilot Sign-Off Template:**
```
I, [Name], [Title] at [Company], confirm that SentinelDF v0.1.1:
✓ Meets our detection quality requirements (≥70% catch rate)
✓ Has acceptable false positive rate (≤10%)
✓ Performs adequately on our infrastructure
✓ Is ready for our production pilot deployment

Signature: _______________  Date: _______________
```

### Coverage Requirements

**By Module:**
- `backend/detectors/` - 95% required (core logic)
- `backend/utils/` - 90% required (infrastructure)
- `cli/` - 85% required (user-facing)
- `frontend/` - 80% required (UI)

**Run Coverage Report:**
```bash
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Incident Response

### Severity Levels

**P0 - Critical (Respond within 1 hour)**
- Detection rate drops below 50%
- False positive rate exceeds 20%
- Data loss or corruption
- Security vulnerability disclosed

**P1 - High (Respond within 4 hours)**
- Detection rate drops below 60%
- False positive rate exceeds 15%
- Performance degradation >50%
- Pilot customer blocker

**P2 - Medium (Respond within 24 hours)**
- Detection rate drops below 70%
- False positive rate exceeds 10%
- Non-critical bugs affecting UX

**P3 - Low (Respond within 1 week)**
- Feature requests
- Documentation gaps
- Minor UX improvements

### False Negative Reported

**Example:** Pilot customer reports a known poison sample that scored 0.

**Process:**

**1. Acknowledge (Within 1 hour)**
```
Thank you for reporting this. We take detection quality seriously.

Ticket: FN-2024-10-16-001
Severity: P1 (High)
Assigned: [Engineer Name]
ETA: Root cause within 4 hours
```

**2. Investigate (Within 4 hours)**
```bash
# Reproduce issue
echo "SAMPLE_TEXT_HERE" > debug/fn_001.txt
python -m cli.sdf scan --path debug/fn_001.txt

# Extract debug info
python scripts/debug_detection.py \
  --file debug/fn_001.txt \
  --output debug/fn_001_analysis.json
```

**3. Root Cause (Within 24 hours)**
Possible causes:
- Pattern not in heuristic dictionary
- Embedding too similar to benign corpus
- Unicode normalization issue
- Cache serving stale result

**4. Fix (Within 48 hours)**
Options:
- **Quick fix:** Add pattern to HIGH_SEVERITY_PHRASES
- **Proper fix:** Enhance co-occurrence detection
- **Workaround:** Lower threshold for customer (custom config)

**5. Validate (Within 72 hours)**
```bash
# Test fix
pytest tests/test_heuristics.py -k "test_fn_001"

# Re-scan customer dataset
python -m cli.sdf scan --path customer_dataset/ --config configs/customer_A.yaml
```

**6. Deploy (Within 1 week)**
```bash
# Release patch
git tag -a v0.1.1 -m "Fix FN-001: Detect 'bypass safety' pattern"
make build
# Notify customer
```

**7. Post-Mortem (Within 2 weeks)**
- Document in `docs/postmortems/FN-001.md`
- Update test suite to prevent regression
- Review similar patterns for proactive fixes

### False Positive Reported

**Example:** Pilot customer reports legitimate medical jargon flagged as poison.

**Process:**

**1. Acknowledge (Within 4 hours)**
```
Thanks for the feedback. We'll review this false positive.

Ticket: FP-2024-10-16-001
Severity: P2 (Medium - not blocking)
Assigned: [Engineer Name]
```

**2. Validate (Within 24 hours)**
```bash
# Confirm it's a false positive
python scripts/manual_review.py --doc-id FP_001 --ground-truth CLEAN
```

**3. Fix (Within 1 week)**
Options:
- **Exclude pattern:** Add to whitelist (domain-specific)
- **Tune threshold:** Adjust risk fusion weights
- **Enhance context:** Improve co-occurrence logic to reduce noise

**4. A/B Test (2 weeks)**
- Deploy fix to 50% of scans
- Monitor FP rate decrease without FN rate increase

**5. Release (Next monthly tag)**
- Include in v0.1.2 or v0.2.0 depending on timing

---

## Continuous Improvement Principles

### Measure Everything
- Track metrics before and after every change
- Automated daily reports
- No blind tuning

### User Feedback First
- Pilot customers are our ground truth
- False negative > false positive (err on side of caution)
- Quick turnaround on P0/P1 issues

### Versioned Experiments
- All config changes in Git
- A/B test before full rollout
- Easy rollback path

### Document Decisions
- Update CHANGELOG with rationale
- Post-mortems for incidents
- Lessons learned in retrospectives

---

## Tooling Roadmap

### Q4 2024 (v0.1.x)
- [x] Basic metrics reporting (`make metrics`)
- [x] Feedback aggregation (`make feedback-summary`)
- [ ] Automated weekly reports
- [ ] Pilot customer dashboard (read-only metrics)

### Q1 2025 (v0.2.x)
- [ ] A/B testing framework
- [ ] Model drift detection (embedding distribution monitor)
- [ ] Automated retraining pipeline
- [ ] Slack/Teams integration for alerts

### Q2 2025 (v0.3.x)
- [ ] ML experiment tracking (MLflow/Weights & Biases)
- [ ] Canary deployments
- [ ] Automated rollback on metric regression
- [ ] Real-time monitoring dashboard

---

## Contact & Escalation

**Engineering Lead:** varunsripadkota@gmail.com  
**Slack Channel:** #sentineldf-engineering (internal)  
**On-Call Rotation:** [PagerDuty link placeholder]

**Escalation Path:**
1. Engineer → Engineering Lead (response within 4 hours)
2. Engineering Lead → CTO (response within 24 hours)
3. CTO → Customer (response within 48 hours)

---

**Last Reviewed:** 2024-10-16  
**Next Review:** 2024-11-16  
**Review Frequency:** Monthly

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*
