# SentinelDF Outreach Email Templates

**Version:** 0.1.0  
**Last Updated:** 2024-10-16

---

## Template A: Data Security Lead

**Subject:** Protect Your LLM Data Pipeline — 30-Day Pilot Invite

**Body:**

```
Hi [First Name],

I'm Varun, creator of SentinelDF — a data firewall for LLM training pipelines.

Your training data is under attack. Adversaries inject prompt injections, backdoor triggers, and malicious payloads into datasets to hijack model behavior. Traditional data quality tools miss these threats because they focus on syntax, not semantics.

SentinelDF detects poisoned samples using dual-layer analysis:
• Heuristic patterns (30+ attack signatures)
• Embedding outliers (SBERT + Isolation Forest)

Key features for security teams:
✓ 100% local processing (no cloud dependencies)
✓ HMAC-signed audit trails for compliance
✓ Air-gap compatible (no internet required)
✓ 56% baseline detection, 0% false positives

We're offering a free 30-day pilot:
• Scan up to 100K records
• Risk report + signed MBOMs
• Live demo session
• No commitment required

Interested in protecting your LLM data?

[Schedule 30-minute kickoff call]
Or reply with "Tell me more" and I'll send details.

Best,
Varun Sripad Kota
Creator, SentinelDF
varunsripadkota@gmail.com
github.com/varunsripad/sentineldf
```

---

## Template B: Head of AI Engineering

**Subject:** Offline LLM Data Scanner — No GPU Needed (30-Day Trial)

**Body:**

```
Hi [First Name],

Quick question: How confident are you that your LLM training data is free from prompt injections and backdoor triggers?

I built SentinelDF to solve this exact problem for AI teams like yours.

Technical highlights:
• Dual detection: Heuristics + embedding outliers (SBERT)
• Performance: 100-200 docs/sec on CPU (no GPU needed)
• Caching: 5-10x speedup on warm runs (SQLite persistent cache)
• Deterministic: Same data = same scores (reproducible for audits)
• Offline: Zero network calls, air-gap compatible

Detection quality (v0.1.0):
• 56% poison detection @ threshold 70
• 0% false positives on clean data
• Configurable weights (default: 0.4 heuristic, 0.6 embedding)

Example use cases:
→ Pre-filter scraped web data (remove HTML/JS injections)
→ Audit fine-tuning datasets (catch backdoor triggers)
→ Validate RAG corpuses (detect prompt hijacking attempts)

MBOM signatures:
• HMAC-SHA256 signed audit trails
• Batch summaries + per-doc risk scores
• CLI validation: `sdf validate <mbom.json>`

Free 30-day pilot:
• Scan up to 100K records on your infrastructure
• Risk report + MBOMs + Streamlit dashboard access
• Live technical walkthrough

Want to see it in action?

[Schedule 30-minute demo]
Or reply and I'll send a Docker setup guide + sample data.

Cheers,
Varun Sripad Kota
varunsripadkota@gmail.com
GitHub: github.com/varunsripad/sentineldf
```

---

## Template C: Startup Founder / CTO

**Subject:** Your Investors Will Ask About This (LLM Data Security)

**Body:**

```
Hi [First Name],

Congrats on [recent funding/launch/milestone]! I saw your team is building [LLM product/service].

Quick heads up: Investors and customers are starting to ask tough questions about LLM training data security. Examples:

❓ "How do you ensure your datasets aren't poisoned?"
❓ "What's your process for detecting adversarial examples?"
❓ "Can you prove data quality for compliance audits?"

Most teams don't have good answers yet.

SentinelDF gives you those answers:

For investors:
✓ Cryptographically signed audit trails (MBOM receipts)
✓ Reproducible results (deterministic detection)
✓ Compliance-ready (SOC 2, GDPR, HIPAA aligned)

For customers:
✓ Demonstrable data quality process
✓ Proactive threat detection (not reactive cleanup)
✓ Offline processing (data sovereignty)

For your team:
✓ Fast CPU-only scanning (no GPU tax)
✓ Easy integration (Python lib, CLI, REST API)
✓ Open source (Apache 2.0 license)

Cost-effective:
• Free 30-day pilot (up to 100K records)
• Startup pricing: $500/month after trial
• Self-hosted (no recurring cloud costs)

The "trust" angle is becoming a major differentiator in AI. Companies that can prove data quality will win enterprise deals.

Want to get ahead of this?

[Schedule 30-minute call]
Or reply with "Send pilot details" and I'll share the full proposal.

Best,
Varun
varunsripadkota@gmail.com
github.com/varunsripad/sentineldf

P.S. — We're adding SSO and RBAC in Q1 2025 for enterprise customers. Early adopters get beta access.
```

---

## Template D: Compliance Lead / Legal

**Subject:** LLM Data Auditing Solution (SOC 2 / GDPR Ready)

**Body:**

```
Hi [First Name],

I'm reaching out because [Company] is using LLMs, and you likely need audit trails for training data quality.

The challenge:
• New regulations (EU AI Act, Executive Orders) require data provenance
• Auditors want proof of data quality checks
• Traditional logging doesn't cover semantic threats (prompt injections, etc.)

SentinelDF solves this:

Compliance features:
✓ HMAC-signed MBOMs (tamper-proof audit trails)
✓ SHA-256 content hashing (integrity verification)
✓ Deterministic results (reproducible audits months later)
✓ Local-only processing (no data transfer, GDPR compliant)

Alignment matrix:
• SOC 2 Type II: Audit logging, integrity controls
• GDPR: Data minimization, local processing, right to erasure
• HIPAA: PHI stays on premises, access controls via OS
• FedRAMP: Air-gap compatible, no cloud dependencies

Output format:
• JSON MBOMs with batch summaries
• Per-document risk scores + detection reasons
• CLI validation command for future audits

Example audit scenario:
1. Scan dataset → Generate signed MBOM
2. Store MBOM + dataset hash
3. Months later: Re-scan same data
4. Compare MBOMs: Should match exactly (proves no tampering)

Free 30-day pilot:
• Test on your datasets (up to 100K records)
• Get sample MBOMs for auditor review
• Live walkthrough of compliance features

Interested in seeing how this fits your audit requirements?

[Schedule 30-minute call]
Or reply and I'll send the security brief + MBOM sample.

Best,
Varun Sripad Kota
varunsripadkota@gmail.com
Docs: github.com/varunsripad/sentineldf
```

---

## Template E: Follow-Up (No Response)

**Subject:** Re: [Original Subject] — Quick Question

**Body:**

```
Hi [First Name],

I sent a note last week about SentinelDF (LLM data scanning for poisoned samples).

Totally understand if now's not the right time.

Quick question: Is this something you're actively looking at, or should I check back in [Q1/Q2/Q3]?

If timing works, happy to:
• Send a 2-minute demo video
• Share our security brief
• Connect you with a pilot customer in [industry]

Just let me know.

Thanks,
Varun
varunsripadkota@gmail.com
```

---

## Template F: Thank You (Post-Call)

**Subject:** Thanks for the call — SentinelDF Next Steps

**Body:**

```
Hi [First Name],

Great chatting today! Here's what we discussed:

Your use case:
• [Dataset size / type]
• [Detection goals]
• [Timeline / constraints]

Agreed next steps:
1. [Action item 1 — owner: You/Varun]
2. [Action item 2 — owner: You/Varun]
3. [Action item 3 — owner: You/Varun]

Resources I mentioned:
• GitHub: github.com/varunsripad/sentineldf
• Pilot proposal: [link to PILOT-PROPOSAL.md]
• Security brief: [link to SECURITY-BRIEF.md]

Quick timeline:
• Week 1: [Kickoff, data prep]
• Week 2: [Initial scan]
• Week 3: [Review, tuning]
• Week 4: [Final report]

Questions? Just reply or Slack me at [your_slack].

Looking forward to working together!

Best,
Varun
varunsripadkota@gmail.com
```

---

## Template G: Pilot Approval (Kickoff)

**Subject:** SentinelDF Pilot — Let's Get Started!

**Body:**

```
Hi [First Name],

Excited to kick off the SentinelDF pilot with [Company]!

Here's what I need from you to get started:

1. Sample dataset (up to 100K records)
   • Preferred format: Plain text, JSONL, or CSV
   • Upload link: [Dropbox/Google Drive/S3 bucket]
   • Or: SSH access to your server (we'll run it there)

2. Infrastructure details
   • OS: Linux / Windows / macOS
   • CPU cores: [8+ recommended]
   • RAM: [8GB+ recommended]
   • Internet access: Yes / No (air-gapped OK)

3. Technical contact
   • Name + email for Slack/Teams coordination
   • Availability for kickoff call next week

4. NDA (if required)
   • We can sign your standard NDA
   • Or use our mutual NDA template

Timeline:
• Week 1 (Nov 1-7): Kickoff + data prep + test scan
• Week 2 (Nov 8-14): Full scan + report generation
• Week 3 (Nov 15-21): Review + demo session
• Week 4 (Nov 22-28): Final report + decision

Please reply with items 1-4 above, and let's schedule a 30-minute kickoff call.

[Calendar link]

Thanks!
Varun
varunsripadkota@gmail.com
```

---

## Best Practices

### Email Timing
- **Ideal send time:** Tuesday-Thursday, 10am-2pm local time
- **Follow-up cadence:** Day 3, Day 7, Day 14
- **Max follow-ups:** 3 attempts, then archive

### Subject Line Tips
- Keep it under 50 characters
- Include urgency only if genuine ("30-day pilot")
- Avoid spam triggers ("FREE", "ACT NOW", etc.)
- Personalize with company name or pain point

### Body Copy Guidelines
- **Opening:** Hook with pain point (1-2 sentences)
- **Value prop:** What you solve (3-4 bullet points)
- **Proof:** Metrics, testimonials, or case studies
- **CTA:** Single clear action ("Schedule call" OR "Reply with X")
- **Length:** 150-250 words (under 2 minutes to read)

### Personalization Tokens
Replace these placeholders before sending:
- `[First Name]` — Use their actual first name
- `[Company]` — Their company name
- `[recent funding/launch/milestone]` — Recent news about them
- `[LLM product/service]` — Specific product they're building
- `[industry]` — Their industry vertical

### Conversion Tracking
Track these metrics per template:
- Open rate (aim for >30%)
- Reply rate (aim for >5%)
- Meeting booked rate (aim for >2%)
- Pilot conversion rate (aim for >50% of meetings)

---

## Legal Disclaimer

By using these templates, you agree to:
- Comply with CAN-SPAM Act (US) and GDPR (EU)
- Include unsubscribe links in automated campaigns
- Honor opt-out requests within 10 business days
- Not purchase email lists from third parties

---

**Questions?** Contact varunsripadkota@gmail.com

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*
