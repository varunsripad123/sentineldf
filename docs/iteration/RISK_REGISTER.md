# SentinelDF Risk Register

**Version:** 0.1.0  
**Last Updated:** 2024-10-16  
**Owner:** Engineering & Product

---

## Overview

This document tracks operational and technical risks that could impact SentinelDF's quality, performance, or reputation. Each risk includes mitigation strategies and assigned ownership.

**Risk Severity:**
- **Critical:** Could halt operations or cause major customer issues
- **High:** Significant impact on quality or user experience
- **Medium:** Moderate impact, manageable workarounds available
- **Low:** Minor impact, unlikely to occur

---

## Active Risks

| ID | Category | Risk | Impact | Likelihood | Severity | Mitigation | Owner | Status |
|----|----------|------|--------|------------|----------|------------|-------|--------|
| R1 | Data | PII/PHI in input data | High - Compliance violation | Medium | **High** | Recommend pre-scrubbing, add PII detection warnings | Security Lead | Open |
| R2 | Model | Embedding drift over time | Medium - Detection degradation | High | **Medium** | Weekly drift checks, monthly retraining | ML Engineer | Open |
| R3 | Ops | Cache corruption | Low - Performance hit | Low | **Low** | SHA-256 checksums, auto-repair on mismatch | Backend Engineer | Open |
| R4 | Security | HMAC secret leak | Critical - MBOM forgery | Low | **Critical** | Rotate secrets quarterly, audit access logs | Security Lead | Open |
| R5 | Model | Adversarial evasion | High - False negatives | Medium | **High** | Red team testing, feedback loop for new attacks | ML Engineer | Open |
| R6 | Ops | Disk space exhaustion | Medium - Cache/logs fill disk | Medium | **Medium** | Log rotation (14 days), cache size limits (10GB) | Backend Engineer | Open |
| R7 | Data | Unicode edge cases | Medium - Missed detections | Medium | **Medium** | Enhanced NFKD normalization, test suite expansion | ML Engineer | Open |
| R8 | Performance | Slow cold scans | Low - User frustration | High | **Low** | Pre-warm cache, optimize embedding batch size | Backend Engineer | Open |
| R9 | Compliance | GDPR data retention | Medium - Regulatory risk | Low | **Medium** | Default 14-day log retention, config documentation | Legal/Compliance | Open |
| R10 | Security | Dependency vulnerabilities | Medium - Supply chain attack | Medium | **Medium** | Monthly `pip audit`, pin versions, SBOM generation | Security Lead | Open |
| R11 | UX | False positive fatigue | High - Users ignore alerts | Medium | **High** | Lower FP rate (<10%), tuning per vertical | Product Manager | Open |
| R12 | Ops | Multi-platform bugs | Medium - Windows/Linux inconsistencies | Low | **Medium** | CI on multiple OS, cross-platform testing | Backend Engineer | Open |

---

## Risk Details

### R1: PII/PHI in Input Data

**Description:**  
Customers may scan datasets containing Personally Identifiable Information (PII) or Protected Health Information (PHI) without pre-scrubbing. This creates compliance risk (GDPR, HIPAA) if data is logged or cached insecurely.

**Impact:**
- GDPR violations (fines up to €20M or 4% revenue)
- HIPAA violations (fines up to $50K per violation)
- Customer trust damage
- Legal liability

**Mitigation:**
1. **Documentation:** Warn users to redact PII before scanning
2. **Detection:** Add optional PII detection patterns (names, SSNs, emails)
3. **Logging:** Never log raw document content (only counts, hashes)
4. **Cache:** Encrypt cache database at rest (recommend FDE)

**Owner:** Security Lead  
**Status:** Open (documentation in place, detection TBD for v0.2)

---

### R2: Embedding Drift Over Time

**Description:**  
The Isolation Forest model is trained on a seed corpus of benign samples. As language evolves or attack patterns change, the embedding distribution may drift, causing false negatives.

**Impact:**
- Detection rate degrades gradually
- False negatives increase
- Customer dissatisfaction

**Mitigation:**
1. **Monitor:** Weekly KL divergence check between new embeddings and seed corpus
2. **Alert:** Trigger warning if drift exceeds 0.1 (threshold TBD)
3. **Retrain:** Monthly retrain on latest benign samples from pilots
4. **A/B Test:** Compare old vs new model before deploying

**Owner:** ML Engineer  
**Status:** Open (manual monitoring, automation planned for v0.2)

---

### R3: Cache Corruption

**Description:**  
SQLite cache database could corrupt due to disk failure, power loss, or bug. This would cause performance degradation (cache miss) or incorrect results.

**Impact:**
- 5-10x scan slowdown
- Potential false positives/negatives if stale results served

**Mitigation:**
1. **Integrity checks:** SHA-256 hash stored with each cache entry
2. **Auto-repair:** Detect mismatch, invalidate entry, recompute
3. **Backup:** Daily cache backup (optional for customers)
4. **TTL:** 15-minute cache expiry prevents long-term staleness

**Owner:** Backend Engineer  
**Status:** Open (basic integrity checks in place, auto-repair TBD)

---

### R4: HMAC Secret Leak

**Description:**  
If `HMAC_SECRET` environment variable is leaked (e.g., Git commit, logs, screenshot), attackers could forge MBOMs.

**Impact:**
- Loss of MBOM trust
- Compliance failures (forged audit trails)
- Customer reputation damage

**Mitigation:**
1. **Secret management:** Use environment variables, never hardcode
2. **Rotation:** Rotate secrets every 90 days
3. **Access control:** Limit who can view production secrets
4. **Audit:** Log all MBOM validations, detect anomalies
5. **Git hooks:** Pre-commit hook to block secrets in code

**Owner:** Security Lead  
**Status:** Open (documented, rotation procedure in place)

---

### R5: Adversarial Evasion

**Description:**  
Attackers may craft payloads specifically to evade SentinelDF's detection (e.g., unicode obfuscation, synonym substitution, context-dependent triggers).

**Impact:**
- False negatives increase
- Detection rate drops below SLA (70%)
- Customer loses trust

**Mitigation:**
1. **Red team:** Quarterly adversarial testing by security team
2. **Feedback loop:** Incorporate reported false negatives into test suite
3. **Research:** Monitor academic papers for new evasion techniques
4. **Updates:** Rapid patching (target: 48h from discovery to fix)

**Owner:** ML Engineer  
**Status:** Open (feedback loop in place, red team TBD)

---

### R6: Disk Space Exhaustion

**Description:**  
Cache and logs could grow unbounded, filling disk and causing crashes.

**Impact:**
- Application crashes
- Data loss (if disk full during write)
- Downtime until disk cleaned

**Mitigation:**
1. **Log rotation:** 14-day retention, 100MB per file, auto-rotate
2. **Cache limits:** 10GB cap, LRU eviction when exceeded
3. **Monitoring:** Alert if disk usage >80%
4. **Documentation:** Recommend monitoring disk space

**Owner:** Backend Engineer  
**Status:** Open (log rotation implemented, cache limits TBD)

---

### R7: Unicode Edge Cases

**Description:**  
Some unicode obfuscation techniques (zero-width chars, RTL overrides, mathematical alphanumerics) bypass normalization.

**Impact:**
- False negatives on obfuscated attacks
- Detection rate drops

**Mitigation:**
1. **Enhanced normalization:** Strip zero-width chars, RTL marks
2. **Test suite:** Add unicode edge case tests
3. **Research:** Monitor attacker TTPs (Tactics, Techniques, Procedures)

**Owner:** ML Engineer  
**Status:** Open (partial normalization in place, enhancement planned)

---

### R8: Slow Cold Scans

**Description:**  
First-time scans are 5-10x slower than cached scans, causing user frustration.

**Impact:**
- Poor first impression
- Pilot customers perceive system as "slow"

**Mitigation:**
1. **Pre-warming:** Offer to pre-scan customer datasets before demo
2. **Optimization:** Batch embeddings (default: 128), tune for CPU
3. **Expectations:** Document cold vs warm performance in README
4. **Progress bars:** Show real-time progress to manage expectations

**Owner:** Backend Engineer  
**Status:** Open (documented, optimization ongoing)

---

### R9: GDPR Data Retention

**Description:**  
Default 14-day log retention may violate GDPR's "right to erasure" if logs contain PII.

**Impact:**
- GDPR non-compliance
- Fines up to €20M

**Mitigation:**
1. **No PII logging:** Never log raw content, only aggregates
2. **Configurable retention:** Allow customers to set shorter (e.g., 7 days)
3. **Documentation:** Clearly state what's logged and for how long
4. **Manual deletion:** Provide script to purge logs on demand

**Owner:** Legal/Compliance  
**Status:** Open (documentation in place, configurable retention TBD)

---

### R10: Dependency Vulnerabilities

**Description:**  
Third-party packages (PyTorch, FastAPI, etc.) may have security vulnerabilities.

**Impact:**
- Remote code execution (RCE)
- Data exfiltration
- Supply chain attack

**Mitigation:**
1. **Monthly audits:** `pip audit` or `safety check`
2. **Pin versions:** Use exact versions in `requirements.txt`
3. **SBOM:** Generate Software Bill of Materials for transparency
4. **Rapid patching:** Update vulnerable deps within 7 days of CVE

**Owner:** Security Lead  
**Status:** Open (versions pinned, audit automation TBD)

---

### R11: False Positive Fatigue

**Description:**  
If FP rate is too high (>10%), users may ignore alerts ("alert fatigue"), causing them to miss true positives.

**Impact:**
- Real threats missed
- Detection system becomes ineffective
- Customer abandons product

**Mitigation:**
1. **Tuning:** Per-vertical threshold tuning (medical, legal, financial)
2. **Feedback:** Prioritize FP reduction based on user reports
3. **Whitelist:** Allow customers to exclude known-safe patterns
4. **Target:** Keep FP rate <10% as primary KPI

**Owner:** Product Manager  
**Status:** Open (tuning ongoing, whitelist feature planned)

---

### R12: Multi-Platform Bugs

**Description:**  
Code may behave differently on Windows vs Linux (path separators, file permissions, etc.).

**Impact:**
- Broken functionality for Windows users
- Poor user experience
- Support burden

**Mitigation:**
1. **CI/CD:** Test on Windows, Linux, macOS in GitHub Actions
2. **Path handling:** Use `pathlib.Path` (cross-platform)
3. **Testing:** Run full test suite on all platforms before release

**Owner:** Backend Engineer  
**Status:** Open (CI planned, pathlib used in most places)

---

## Closed/Mitigated Risks

| ID | Risk | Resolution | Closed Date |
|----|------|------------|-------------|
| R0 | Example: Test coverage too low | Increased to 95%, enforced in CI | 2024-10-01 |

---

## Risk Review Process

### Weekly Triage
- Review new risks from pilot feedback
- Update likelihood/severity based on data
- Assign owners for unowned risks

### Monthly Risk Review
- Re-evaluate all open risks
- Close mitigated risks
- Escalate critical risks to leadership

### Quarterly Deep Dive
- Conduct threat modeling workshop
- Invite external security consultant
- Update risk register based on findings

---

## Escalation Criteria

**Escalate to Engineering Lead if:**
- New critical risk identified
- Existing risk severity increases
- Mitigation plan not working

**Escalate to CTO/CEO if:**
- Multiple critical risks active
- Risk could cause customer exodus
- Legal/regulatory implications

---

## Risk Appetite

**Acceptable:**
- Low severity risks with mitigation plans
- Medium severity risks with active monitoring
- High severity risks with near-term resolution (<30 days)

**Unacceptable:**
- Critical risks without mitigation
- High severity risks persisting >90 days
- Any risk that violates compliance (GDPR, HIPAA)

---

**Last Reviewed:** 2024-10-16  
**Next Review:** 2024-10-23 (Weekly)  
**Review Frequency:** Weekly (triage), Monthly (full review)

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*
