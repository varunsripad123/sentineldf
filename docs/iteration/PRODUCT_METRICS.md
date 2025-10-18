# SentinelDF Product Metrics

**Version:** 0.1.0  
**Last Updated:** 2024-10-16  
**Owner:** Product & Engineering

---

## Overview

This document defines Key Performance Indicators (KPIs) for SentinelDF. These metrics guide our development priorities and validate that the product meets enterprise-grade quality standards.

---

## Core KPIs

### 1. Detection Rate

**Definition:** Percentage of known poison samples correctly identified and quarantined.

**Formula:**
```
Detection Rate = (True Positives / (True Positives + False Negatives)) × 100
```

**Target:** ≥70%  
**Stretch Goal:** ≥80%  
**Minimum Acceptable:** 50%

**Measurement:**
```bash
# Run on labeled test set
python scripts/evaluate_detector.py \
  --ground-truth data/ground_truth/test_labels.csv \
  --threshold 70 \
  --output reports/detection_metrics.json

# Output:
{
  "detection_rate": 72.5,
  "true_positives": 29,
  "false_negatives": 11,
  "total_poison": 40
}
```

**Tracking:**
- **Daily:** Automated run on pilot feedback data
- **Weekly:** Aggregate across all pilot customers
- **Monthly:** Trend analysis and regression check

**Red Flags:**
- ⚠️ Drops below 65% (investigate within 24h)
- 🚨 Drops below 50% (emergency response, halt new deploys)

---

### 2. False Positive Rate

**Definition:** Percentage of clean samples incorrectly flagged as poison.

**Formula:**
```
FP Rate = (False Positives / (False Positives + True Negatives)) × 100
```

**Target:** ≤10%  
**Stretch Goal:** ≤5%  
**Maximum Acceptable:** 20%

**Measurement:**
```bash
# Same evaluation script
python scripts/evaluate_detector.py \
  --ground-truth data/ground_truth/test_labels.csv \
  --threshold 70 \
  --output reports/detection_metrics.json

# Output:
{
  "false_positive_rate": 8.3,
  "false_positives": 5,
  "true_negatives": 55,
  "total_clean": 60
}
```

**Tracking:**
- **Daily:** Monitor pilot feedback for FP reports
- **Weekly:** Aggregate FP rate across datasets
- **Monthly:** Per-industry vertical analysis (medical, legal, financial)

**Red Flags:**
- ⚠️ Exceeds 15% (review threshold tuning)
- 🚨 Exceeds 20% (consider lowering quarantine threshold)

**Tradeoff:**
- Lowering threshold → higher detection, higher FP rate
- Raising threshold → lower detection, lower FP rate
- **Sweet spot:** 70 threshold balances both (~70% detection, ~10% FP)

---

### 3. Scan Speed

**Definition:** Average number of documents processed per minute on standard CPU hardware.

**Formula:**
```
Scan Speed = Total Documents / Scan Time (minutes)
```

**Target:** ≥500 docs/min (≈8.3 docs/sec)  
**Stretch Goal:** ≥1000 docs/min (≈16.7 docs/sec)  
**Minimum Acceptable:** 300 docs/min (≈5 docs/sec)

**Measurement:**
```bash
# Time a scan
time python -m cli.sdf scan --path data/samples/

# Parse logs
grep "Scanning documents" logs/sentineldf.log | tail -1
# Example: "Scanned 1000 docs in 120.5 seconds (8.3 docs/sec)"
```

**Tracking:**
- **Per scan:** Log in scan reports
- **Daily:** Aggregate median and P95
- **Weekly:** Trend analysis (cache performance)

**Factors:**
- **Cold run:** ~15-25 docs/sec (embedding-bound)
- **Warm run:** ~100-200 docs/sec (cache-bound)
- **Cache hit rate:** Directly impacts speed

**Optimization Levers:**
1. Increase cache hit rate (longer TTL)
2. Batch size tuning (default 128)
3. Parallel processing (future: multiprocessing)

---

### 4. MBOM Validation Pass Rate

**Definition:** Percentage of generated MBOMs that pass signature validation.

**Formula:**
```
MBOM Validation Rate = (Valid MBOMs / Total MBOMs) × 100
```

**Target:** 100%  
**Acceptable:** ≥99.9%  
**Unacceptable:** <99%

**Measurement:**
```bash
# Validate all MBOMs
for mbom in reports/mbom_*.json; do
  sdf validate "$mbom" || echo "FAILED: $mbom"
done

# Count successes
total=$(ls reports/mbom_*.json | wc -l)
valid=$(sdf validate reports/mbom_*.json 2>&1 | grep -c "Signature valid")
rate=$(echo "scale=2; $valid / $total * 100" | bc)
echo "MBOM Validation Rate: $rate%"
```

**Tracking:**
- **Per generation:** Immediate validation
- **Weekly:** Batch validation of all historical MBOMs
- **Monthly:** Cross-environment validation (test HMAC rotation)

**Red Flags:**
- ⚠️ Single validation failure (investigate immediately)
- 🚨 Multiple failures (HMAC secret mismatch or corruption)

**Root Causes:**
- Incorrect HMAC_SECRET environment variable
- File corruption during storage/transfer
- Bug in signing logic (rare, would fail tests)

---

### 5. User Satisfaction Score

**Definition:** Average rating from pilot customers on 1-5 scale.

**Formula:**
```
Satisfaction = Sum(Ratings) / Count(Ratings)
```

**Target:** ≥4.0 / 5.0  
**Stretch Goal:** ≥4.5 / 5.0  
**Minimum Acceptable:** 3.5 / 5.0

**Survey Questions:**
1. **Detection Quality:** "How accurate is SentinelDF at identifying threats?" (1-5)
2. **Performance:** "How satisfied are you with scan speed?" (1-5)
3. **Ease of Use:** "How easy is SentinelDF to integrate and use?" (1-5)
4. **Documentation:** "How helpful is the documentation?" (1-5)
5. **Support:** "How responsive is the SentinelDF team?" (1-5)
6. **Overall:** "Would you recommend SentinelDF to a colleague?" (1-5)

**Measurement:**
```bash
# Send monthly survey via email
python scripts/send_survey.py --recipients pilot_emails.txt

# Aggregate results
python scripts/aggregate_surveys.py --output reports/satisfaction_YYYYMM.json

# Output:
{
  "month": "2024-10",
  "responses": 12,
  "avg_detection_quality": 4.2,
  "avg_performance": 4.5,
  "avg_ease_of_use": 3.8,
  "avg_documentation": 4.0,
  "avg_support": 4.7,
  "avg_overall": 4.3
}
```

**Tracking:**
- **Monthly:** Survey sent last week of month
- **Quarterly:** NPS (Net Promoter Score) calculation
- **Annually:** In-depth satisfaction interviews

**Action Thresholds:**
- Score <4.0 on any dimension → Create improvement plan
- Score <3.5 on any dimension → Emergency sprint to fix
- Overall <4.0 → Delay next release until addressed

---

## Secondary Metrics

### 6. Cache Hit Rate

**Definition:** Percentage of documents served from cache vs computed fresh.

**Target:** ≥70%  
**Stretch Goal:** ≥85%

**Measurement:**
```python
# In backend/utils/persistent_cache.py
cache_stats = get_persistent_cache().get_stats()
hit_rate = cache_stats['hit_rate']
# Logged per scan
```

**Impact:**
- Directly affects scan speed (5-10x improvement when cached)
- Reduces CPU load and energy consumption
- Critical for re-scanning same datasets

### 7. Test Coverage

**Definition:** Percentage of code covered by automated tests.

**Target:** ≥95%  
**Minimum:** 90%

**Measurement:**
```bash
pytest --cov=backend --cov-report=term-missing
# Coverage: 94% (target: 95%)
```

**Tracking:**
- **Per PR:** Coverage report in CI
- **Weekly:** Coverage trend graph
- **Monthly:** Identify untested modules

### 8. Time to Detection (TTD)

**Definition:** Elapsed time from dataset upload to quarantine decision.

**Target:** ≤15 minutes for 100K records

**Measurement:**
```bash
# End-to-end timing
start=$(date +%s)
python -m cli.sdf scan --path large_dataset/
end=$(date +%s)
echo "TTD: $((end - start)) seconds"
```

### 9. Memory Footprint

**Definition:** Peak RAM usage during scan.

**Target:** ≤4GB for batches up to 10K docs  
**Maximum:** 8GB

**Measurement:**
```bash
# Using memory_profiler
python -m memory_profiler cli/sdf.py scan --path data/samples/
# Peak usage: 3.2 GB
```

### 10. Error Rate

**Definition:** Percentage of scans that encounter errors.

**Target:** <1%  
**Acceptable:** <5%

**Measurement:**
```bash
# Count errors in logs
total_scans=$(grep "Scan complete" logs/*.log | wc -l)
errors=$(grep "ERROR" logs/*.log | wc -l)
error_rate=$(echo "scale=2; $errors / $total_scans * 100" | bc)
```

---

## Metric Dependencies

### Detection Rate ↔ False Positive Rate

**Tradeoff:**
- Lowering threshold → ↑ Detection Rate, ↑ FP Rate
- Raising threshold → ↓ Detection Rate, ↓ FP Rate

**Optimal Balance:**
- Threshold = 70 (current default)
- Detection ≈ 70%, FP ≈ 10%

**Tuning Process:**
```bash
# Test thresholds: 60, 65, 70, 75, 80
for thresh in 60 65 70 75 80; do
  python scripts/evaluate_detector.py \
    --threshold $thresh \
    --output reports/threshold_$thresh.json
done

# Plot ROC curve
python scripts/plot_roc.py --input reports/threshold_*.json
```

### Scan Speed ↔ Cache Hit Rate

**Relationship:**
- Higher cache hit rate → Faster scans
- Cache miss → 5-10x slower (embedding computation)

**Optimization:**
- Warm cache before pilot demos
- Pre-compute embeddings for common datasets
- Increase cache TTL (default: 900s)

---

## Dashboards

### Real-Time Metrics (Future: Grafana/Prometheus)

**Panels:**
1. Detection Rate (7-day rolling average)
2. False Positive Rate (7-day rolling average)
3. Scan Throughput (docs/min, live)
4. Cache Hit Rate (live)
5. Error Count (last 24h)

### Weekly Report (Automated Email)

**Recipients:** Engineering team, pilot customers (opt-in)

**Content:**
```
SentinelDF Weekly Metrics (2024-10-14 to 2024-10-20)

Detection Quality:
  Detection Rate: 72.3% (↑1.2% vs last week)
  False Positive Rate: 9.1% (↓0.4% vs last week)

Performance:
  Avg Scan Speed: 8.7 docs/sec (↑0.3 vs last week)
  Cache Hit Rate: 78% (↑5% vs last week)

Reliability:
  MBOM Validation: 100% (42/42 valid)
  Error Rate: 0.5% (2 errors in 400 scans)

User Feedback:
  False Positive Reports: 3 (down from 5)
  False Negative Reports: 1 (same as last week)

Action Items:
  - Investigate FN-2024-10-18-001 (medical jargon)
  - Review FP pattern: code snippets flagged as HTML injection
```

---

## Benchmarking Against Competitors

### Comparison Matrix (Placeholder)

| Metric | SentinelDF | Competitor A | Competitor B |
|--------|-----------|--------------|--------------|
| Detection Rate | 72% | 65% | 80% |
| False Positive | 10% | 15% | 5% |
| Scan Speed | 8 docs/sec | 12 docs/sec | 6 docs/sec |
| Local Processing | ✅ Yes | ❌ Cloud only | ✅ Yes |
| MBOM Signatures | ✅ Yes | ❌ No | ⚠️ Optional |
| Open Source | ✅ Apache 2.0 | ❌ Proprietary | ❌ Proprietary |

**Competitive Advantages:**
1. Local-only processing (data sovereignty)
2. Cryptographic audit trails (MBOMs)
3. Open source (transparency, extensibility)

**Areas to Improve:**
1. Detection rate (target: match Competitor B at 80%)
2. Scan speed (explore GPU acceleration)

---

## Reporting Frequency

| Metric | Daily | Weekly | Monthly | Quarterly |
|--------|-------|--------|---------|-----------|
| Detection Rate | ✅ | ✅ | ✅ | ✅ |
| False Positive Rate | ✅ | ✅ | ✅ | ✅ |
| Scan Speed | ✅ | ✅ | ✅ | - |
| MBOM Validation | - | ✅ | ✅ | - |
| User Satisfaction | - | - | ✅ | ✅ |
| Cache Hit Rate | ✅ | ✅ | - | - |
| Test Coverage | - | ✅ | ✅ | - |

---

## Metric Ownership

| Metric | Owner | Escalation Path |
|--------|-------|----------------|
| Detection Rate | ML Engineer | Engineering Lead → CTO |
| False Positive Rate | ML Engineer | Engineering Lead → CTO |
| Scan Speed | Backend Engineer | Engineering Lead |
| MBOM Validation | Security Engineer | Engineering Lead → CISO |
| User Satisfaction | Product Manager | VP Product → CEO |

---

## SLAs (Service Level Agreements)

### Pilot Customers

**Detection Quality SLA:**
- Detection Rate ≥70% on customer's labeled dataset
- False Positive Rate ≤10% on customer's clean dataset
- Measured monthly, averaged over rolling 30 days

**Performance SLA:**
- Scan Speed ≥500 docs/min on customer's infrastructure (8-core CPU)
- Uptime N/A (self-hosted, customer responsibility)

**Support SLA:**
- P0 incidents: Response within 1 hour
- P1 incidents: Response within 4 hours
- P2 incidents: Response within 24 hours

**Penalties:**
- SLA breach → 10% monthly fee credit (if paid tier)
- 3 consecutive breaches → Customer may exit contract

---

## Continuous Improvement

### Metric Evolution

**v0.1.0 (Current):**
- Focus: Detection quality, basic performance
- KPIs: 5 core metrics

**v0.2.0 (Q1 2025):**
- Add: Precision/Recall curves, F1 score
- Add: Per-attack-type detection rates
- Add: Drift detection (embedding distribution)

**v0.3.0 (Q2 2025):**
- Add: Real-time monitoring (Grafana dashboard)
- Add: Predictive alerts (ML-based anomaly detection)
- Add: Customer-specific SLAs (configurable thresholds)

---

**Last Reviewed:** 2024-10-16  
**Next Review:** 2024-11-16  
**Review Frequency:** Monthly

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*
