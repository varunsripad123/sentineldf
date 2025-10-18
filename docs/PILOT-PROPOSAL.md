# SentinelDF Pilot Program — 30-Day Proof of Concept

**Version:** 0.1.0  
**Last Updated:** 2024-10-16

---

## Objective

Validate SentinelDF's ability to detect and quarantine poisoned or prompt-injection samples in your LLM training datasets while maintaining zero external dependencies and full data sovereignty.

**Pilot Goals:**
- Demonstrate detection of known attack patterns (prompt injection, backdoor triggers, HTML/JS payloads)
- Measure false positive rate on clean production data
- Generate cryptographically signed audit trails (MBOMs) for compliance
- Validate performance on your infrastructure (CPU-only, no GPU required)

---

## Scope & Deliverables

### What We'll Scan

**Dataset Size:** Up to 100,000 records  
**Formats Supported:** Plain text, JSON, CSV (with text columns)  
**Processing:** 100% local on your infrastructure - no cloud uploads

### Deliverables

**1. Comprehensive Risk Report**
- Per-document risk scores (0-100 scale)
- Quarantine vs. allow decision matrix
- Detection reasons with interpretable explanations
- Distribution analysis (risk histogram, percentiles)

**2. Signed MBOMs (Material Bill of Materials)**
- HMAC-SHA256 signed audit trails
- Batch-level summaries with statistics
- Per-document risk details
- Verifiable integrity proofs

**3. Interactive Dashboard Access**
- Streamlit UI for visual exploration
- Risk distribution charts
- UMAP embedding visualization (≤1000 docs)
- Document-level drill-down

**4. Optional: Live Demo Session** (30-60 minutes)
- Screen-share walkthrough of results
- Q&A on detection logic
- Threshold tuning recommendations
- Integration planning discussion

---

## Success Metrics

### Detection Quality

**Primary Metric:**
- **≥70% detection rate** on known poisoned samples at default threshold (70)
- **<10% false positive rate** on verified clean samples

**Secondary Metrics:**
- **Precision:** Percentage of quarantined docs that are true positives
- **Recall:** Percentage of poisoned docs successfully caught
- **F1 Score:** Harmonic mean of precision and recall

### Performance

**Target Benchmarks:**
- **End-to-end scan time:** ≤15 minutes for 100K records (8-core CPU)
- **Throughput:** ~100-200 docs/sec on warm runs (with caching)
- **Memory footprint:** <4GB RAM for batch processing

### Operational

- **Zero external API calls** - all processing local
- **Reproducibility** - same data yields same scores (deterministic)
- **Audit readiness** - MBOM signatures validate correctly

---

## Timeline: 30 Days

### Week 1: Kickoff & Data Prep
**Days 1-2:** Kickoff call, NDA execution (if required), credentials exchange  
**Days 3-5:** Data subset extraction, format validation, test scan (1000 docs)  
**Days 6-7:** Review test results, adjust thresholds if needed

### Week 2: Full Scan & Analysis
**Days 8-10:** Full dataset scan (up to 100K records)  
**Days 11-12:** Generate reports, MBOMs, and visualizations  
**Days 13-14:** Internal review of quarantine decisions

### Week 3: Review & Iteration
**Days 15-17:** Live demo session, Q&A, threshold tuning  
**Days 18-20:** Re-scan with adjusted parameters (if needed)  
**Day 21:** Final report delivery

### Week 4: Decision & Next Steps
**Days 22-25:** Customer evaluation, stakeholder review  
**Days 26-28:** Integration planning (if proceeding)  
**Days 29-30:** Pilot debrief, feedback collection, contract discussion

---

## Customer Inputs Needed

### Required

1. **Sample Dataset** (up to 100K records)
   - Preferred format: Plain text files, JSONL, or CSV
   - Must include representative clean and (if known) suspicious samples
   - Can be anonymized/redacted as needed

2. **Infrastructure Access**
   - Linux/Windows server or VM with Python 3.10+
   - 8+ CPU cores, 8GB+ RAM recommended
   - No internet access required (air-gapped OK)

3. **Technical Contact**
   - Name, email, Slack/Teams for coordination
   - Availability for 2-3 sync calls over 30 days

### Optional

4. **Ground Truth Labels** (if available)
   - Known poison samples for validation
   - Previously flagged suspicious content
   - Helps measure detection accuracy

5. **NDA** (Non-Disclosure Agreement)
   - We can sign your standard NDA
   - Or use our mutual NDA template

6. **Custom Thresholds**
   - Preferred false positive tolerance
   - Compliance requirements (e.g., SOC 2, GDPR)

---

## Security & Compliance

### Data Protection

✅ **Local-only processing** - No data transmitted to external servers  
✅ **No cloud dependencies** - Runs entirely on your infrastructure  
✅ **No telemetry** - Zero phone-home behavior  
✅ **Air-gap compatible** - Works without internet access

### Cryptographic Assurance

- **HMAC-SHA256 signatures** on all audit trails
- **SHA-256 content hashing** for deduplication
- **Constant-time signature comparison** to prevent timing attacks

### Compliance Readiness

- **SOC 2 Type II aligned** - Audit trail, integrity verification, access controls
- **GDPR compliant** - Local processing, no cross-border data transfer
- **HIPAA friendly** - PHI stays on your premises
- **FedRAMP compatible** - Government air-gap deployments supported

### What We DON'T Collect

- ❌ Raw document content
- ❌ Personally identifiable information (PII)
- ❌ API keys or credentials
- ❌ Usage telemetry or analytics

**We only see:**
- Aggregate statistics (counts, averages)
- Detection reasons (high-level patterns)
- Risk score distributions

---

## Pricing & Licensing

### Pilot Program

**Cost:** Free 30-day trial  
**License:** Evaluation license (non-production use)  
**Support:** Email + Slack channel access

### Post-Pilot Options

**Tier 1: Startup/Research** (<100K docs/month)  
- $500/month
- Email support
- Quarterly feature updates

**Tier 2: Growth** (<1M docs/month)  
- $2,500/month
- Slack support, 48h SLA
- Monthly feature updates
- Custom threshold tuning

**Tier 3: Enterprise** (Unlimited)  
- Custom pricing
- Dedicated support, 24h SLA
- On-premise deployment
- SSO, RBAC, audit logging
- Custom detector development

**Annual Discounts:** 20% off with annual commitment

---

## Contacts & Next Steps

### Pilot Lead

**Varun Sripad Kota**  
Email: varunsripadkota@gmail.com  
LinkedIn: [linkedin.com/in/varunsripad](https://linkedin.com/in/varunsripad)

### Schedule a Kickoff Call

📅 **Book 30 minutes:** [calendar placeholder - use Calendly/Cal.com]

### Request Pilot Access

📧 **Email us:** varunsripadkota@gmail.com  
**Subject:** "SentinelDF Pilot Request - [Your Company]"

**Include:**
- Company name and size
- Use case description (LLM training, RAG, fine-tuning, etc.)
- Estimated dataset size
- Target start date
- Primary contact info

### Resources

- **GitHub:** [github.com/varunsripad/sentineldf](https://github.com/varunsripad/sentineldf)
- **Documentation:** [README.md](../README.md)
- **5-Minute Demo:** [docs/DEMO.md](DEMO.md)
- **Security Details:** [docs/SECURITY-BRIEF.md](SECURITY-BRIEF.md)

---

## Frequently Asked Questions

### Q: Can we test on a smaller dataset first?

**A:** Absolutely. We recommend starting with 1,000-10,000 records to validate the approach before scaling to 100K.

### Q: What if we don't have labeled poison samples?

**A:** No problem. We'll analyze your data distribution and flag statistical outliers. You can manually review high-risk samples to build ground truth.

### Q: Does it require GPU acceleration?

**A:** No. SentinelDF runs entirely on CPU (sentence transformers use CPU inference). GPU support is optional and provides ~2-3x speedup.

### Q: Can we run it air-gapped?

**A:** Yes. Download dependencies once, transfer to air-gapped environment. No internet required after initial setup.

### Q: How do we validate MBOM signatures?

**A:** Use the built-in CLI: `sdf validate <mbom_file>`. Returns ✅ if signature matches, ❌ if tampered.

### Q: What happens after the pilot?

**A:** You decide:
1. **Proceed to paid tier** - Sign contract, deploy to production
2. **Extend pilot** - Continue evaluation with more data
3. **Pass** - No obligation, we part ways

### Q: Do you offer managed hosting?

**A:** Not currently. SentinelDF is self-hosted on your infrastructure. Managed cloud option coming in Q2 2025.

---

## Terms & Conditions

### Pilot Agreement

By participating in the pilot, you agree to:
1. Use SentinelDF for evaluation purposes only (not production)
2. Provide feedback on detection quality and usability
3. Respect the evaluation license (no redistribution)
4. Not reverse-engineer or benchmark against competitors

### Data Ownership

- **Your data remains yours** - We do not access, copy, or store it
- **MBOMs are yours** - You own all generated audit trails
- **Feedback is mutual** - We may use aggregated insights (no raw data) for product improvement

### Termination

Either party may terminate the pilot at any time with 48-hour notice. Upon termination:
- You delete SentinelDF software
- We delete any shared credentials
- All data remains on your systems

---

**Ready to protect your LLM training data?**

👉 **[Schedule Kickoff Call]** | 📧 **varunsripadkota@gmail.com**

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*
