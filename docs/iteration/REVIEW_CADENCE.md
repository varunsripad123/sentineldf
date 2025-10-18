# SentinelDF Review Cadence

**Version:** 0.1.0  
**Last Updated:** 2024-10-16  
**Owner:** Engineering & Product

---

## Overview

This document defines our internal rituals and meeting cadence to ensure continuous improvement, effective communication, and systematic decision-making.

---

## Weekly Triage

**Frequency:** Every Monday, 10:00am - 10:30am (30 minutes)  
**Attendees:** Engineering team, Product Manager  
**Owner:** Engineering Lead

### Agenda

**1. Metrics Review (10 minutes)**
- Review weekly metrics report (auto-generated)
- Detection rate, FP rate, scan speed, cache hit rate
- Compare to previous week and KPI targets
- Flag any regressions or anomalies

**2. Issue Triage (10 minutes)**
- Review new GitHub issues from past week
- Prioritize bugs (P0/P1/P2/P3)
- Assign owners
- Estimate effort (S/M/L/XL)

**3. Feedback Review (5 minutes)**
- Review pilot customer feedback from `feedback/` folder
- Count false positives, false negatives, feature requests
- Identify patterns (e.g., "medical jargon" flagged repeatedly)

**4. Action Items (5 minutes)**
- Assign 2-3 action items for the week
- Example: "Investigate FN-2024-10-18-001 (P1)"
- Example: "Add 'medical_terms' to whitelist (P2)"

### Output

- Updated GitHub project board
- Action items in Slack #sentineldf-engineering
- Metrics dashboard updated

### Meeting Notes Template

```markdown
# Weekly Triage - 2024-10-21

## Metrics
- Detection Rate: 72.3% (↑1.2% vs last week) ✅
- False Positive Rate: 9.1% (↓0.4% vs last week) ✅
- Scan Speed: 8.7 docs/sec (↑0.3 vs last week) ✅
- Cache Hit Rate: 78% (↑5% vs last week) ✅

## Issues Triaged
- #42: FP on medical jargon (P2, assigned: @ml-engineer, 2-3 days)
- #43: Slow scan on Windows (P3, assigned: @backend-engineer, 1 day)
- #44: Docs: Add troubleshooting for cache corruption (P3, assigned: @doc-writer, 1 day)

## Feedback Summary
- 3 false positive reports (medical, legal, code snippets)
- 1 false negative report (unicode obfuscation)
- 2 feature requests (GPU acceleration, custom thresholds)

## Action Items
- [ ] @ml-engineer: Investigate FN-2024-10-18-001 (unicode) by Wed
- [ ] @backend-engineer: Profile Windows scan performance by Fri
- [ ] @product-manager: Schedule call with Customer A to discuss FP reports by Fri
```

---

## Bi-Weekly Pilot Sync

**Frequency:** Every other Wednesday, 2:00pm - 3:00pm (60 minutes)  
**Attendees:** Engineering Lead, Product Manager, 1-2 Pilot Customers (rotating)  
**Owner:** Product Manager

### Agenda

**1. Introductions & Updates (5 minutes)**
- Welcome pilot customer
- Quick recap of last sync

**2. Metrics Review (10 minutes)**
- Share customer-specific metrics (detection rate, FP rate)
- Compare to baseline and targets
- Discuss any trends or concerns

**3. Customer Feedback (20 minutes)**
- What's working well?
- What's frustrating or confusing?
- Any false positives/negatives to discuss?
- Feature requests or improvements?

**4. Demo (15 minutes)**
- Show new features from past 2 weeks
- Walk through recent bug fixes
- Preview upcoming features (next sprint)

**5. Technical Deep Dive (5 minutes, optional)**
- If customer has technical questions
- Explain detection logic, threshold tuning, etc.

**6. Action Items & Next Steps (5 minutes)**
- Summarize action items (both sides)
- Confirm next sync date
- Share contact info for urgent issues

### Call Preparation Checklist

**48 hours before:**
- [ ] Generate customer-specific metrics report
- [ ] Review recent feedback from this customer
- [ ] Prepare demo slides (if new features)
- [ ] Send calendar invite with Zoom link

**24 hours before:**
- [ ] Send agenda to customer
- [ ] Test demo environment
- [ ] Prepare answers to known questions

**After call:**
- [ ] Send thank-you email with action items
- [ ] Update internal notes in CRM/Notion
- [ ] Create GitHub issues for requested features

### Call Notes Template

```markdown
# Pilot Sync - Customer A - 2024-10-23

## Attendees
- Customer: Jane Doe (Head of AI Security)
- SentinelDF: [Engineering Lead], [Product Manager]

## Metrics (2024-10-01 to 2024-10-20)
- Detection Rate: 74% (target: 70%) ✅
- False Positive Rate: 12% (target: 10%) ⚠️
- Scans Performed: 15 (total: 150K documents)
- Avg Scan Speed: 7.2 docs/sec

## Feedback
✅ **What's working:**
- "Detection catches most obvious attacks"
- "MBOM signatures are great for audit trail"
- "Offline processing is critical for us"

⚠️ **What's frustrating:**
- "Too many false positives on medical terminology"
- "Scan speed could be faster (currently 20min for 100K docs)"
- "Docs need more examples for healthcare vertical"

💡 **Feature requests:**
- Custom whitelist for domain-specific terms
- GPU acceleration option
- Email alerts for high-risk samples

## Demo
- Showed new cache performance improvements (5-10x speedup)
- Demoed upcoming whitelist feature (v0.2)

## Action Items
- [ ] @ml-engineer: Create medical terminology whitelist by Nov 1
- [ ] @doc-writer: Add healthcare examples to docs by Nov 5
- [ ] @product-manager: Explore GPU acceleration feasibility by Nov 10
- [ ] @customer: Provide 100 false positive examples by Oct 30

## Next Sync
- Date: 2024-11-06, 2:00pm
- Topic: Review whitelist feature, discuss v0.2 roadmap
```

---

## Monthly Retrospective

**Frequency:** Last Friday of each month, 3:00pm - 4:30pm (90 minutes)  
**Attendees:** Full engineering team, Product Manager  
**Owner:** Engineering Lead

### Agenda

**1. Metrics Deep Dive (20 minutes)**
- 30-day metrics review (detection, FP, speed, satisfaction)
- Compare to previous month and KPI targets
- Identify trends (improving, stable, degrading)
- Chart visualization (line graphs, histograms)

**2. Wins & Celebrations (10 minutes)**
- What went well this month?
- Customer success stories
- Technical achievements
- Team milestones

**3. Challenges & Learnings (15 minutes)**
- What didn't go well?
- Incidents or outages
- Missed deadlines
- Surprises or unexpected issues

**4. Feedback Synthesis (15 minutes)**
- Aggregate pilot feedback (false positives, false negatives)
- Identify patterns across customers
- Prioritize top 3 pain points

**5. Process Improvements (15 minutes)**
- What can we improve in our workflow?
- Tools or automation needs
- Communication gaps
- Meeting cadence adjustments

**6. Roadmap Review (10 minutes)**
- Review Q4 roadmap progress
- Adjust priorities based on feedback
- Add/remove features as needed

**7. Action Items (5 minutes)**
- Assign owners for top 3 improvements
- Set deadlines for next month

### Retrospective Format (Plus-Delta)

**Plus (What went well):**
- ✅ Example: "Improved detection rate by 5%"
- ✅ Example: "Onboarded 3 new pilot customers"
- ✅ Example: "Resolved all P0 issues within SLA"

**Delta (What to change):**
- 🔄 Example: "False positive rate still too high (12%)"
- 🔄 Example: "Slow turnaround on customer feedback (avg 7 days)"
- 🔄 Example: "Need better documentation for troubleshooting"

### Output

- Retrospective notes shared in Confluence/Notion
- Action items added to sprint backlog
- Metrics charts included in monthly report

---

## Quarterly Roadmap Revision

**Frequency:** First week of each quarter (Jan, Apr, Jul, Oct)  
**Duration:** Half-day workshop (9:00am - 1:00pm)  
**Attendees:** Engineering team, Product Manager, CEO/CTO (optional)  
**Owner:** Product Manager

### Agenda

**1. Q-1 Review (60 minutes)**
- What did we ship? (features, bug fixes, improvements)
- What did we learn? (customer feedback, metrics, incidents)
- What surprised us? (unexpected challenges or opportunities)

**2. Market & Competitive Analysis (30 minutes)**
- What are competitors doing?
- What are customers asking for?
- What are industry trends (AI regulations, attack patterns)?

**3. Q+1 Planning (90 minutes)**
- Define top 3-5 themes (e.g., "Improve detection quality", "Enterprise features")
- Draft high-level feature list
- Estimate effort and dependencies
- Prioritize using RICE framework (Reach, Impact, Confidence, Effort)

**4. Resource Allocation (30 minutes)**
- Engineering capacity (person-weeks available)
- Budget for tools, infrastructure, contractors
- Hiring needs (if any)

**5. OKRs (Objectives & Key Results) (30 minutes)**
- Define 3-5 OKRs for the quarter
- Example: "Improve detection quality (70% → 80% detection rate)"
- Example: "Onboard 10 new pilot customers"

**6. Communication Plan (10 minutes)**
- How to share roadmap with customers?
- Internal all-hands presentation
- External blog post or changelog

### Roadmap Format

```markdown
# SentinelDF Roadmap - Q1 2025

## Theme 1: Detection Quality
**Goal:** Increase detection rate from 72% to 80%

- ✅ P0: Add 50 new high-severity patterns (2 weeks)
- ✅ P1: Enhanced unicode normalization (1 week)
- ✅ P1: Domain-specific tuning (healthcare, finance, legal) (3 weeks)
- 🔄 P2: Red team testing (ongoing)

## Theme 2: Enterprise Features
**Goal:** Make SentinelDF production-ready for large enterprises

- ✅ P0: SSO integration (Okta, Azure AD) (3 weeks)
- ✅ P1: RBAC (role-based access control) (2 weeks)
- 🔄 P2: Audit logging (all actions, immutable) (2 weeks)
- 🔄 P3: Multi-tenancy (separate data per customer) (4 weeks)

## Theme 3: Performance
**Goal:** Reduce scan time from 15min to 5min for 100K docs

- ✅ P0: GPU acceleration (optional, 3x speedup) (3 weeks)
- ✅ P1: Batch size tuning (1 week)
- 🔄 P2: Parallel heuristic processing (2 weeks)

## Theme 4: Developer Experience
**Goal:** Make SentinelDF easier to integrate and extend

- ✅ P1: Python SDK (clean API, typed) (2 weeks)
- ✅ P2: Custom detector plugin system (3 weeks)
- 🔄 P3: Docker deployment guide (1 week)

## Theme 5: Compliance
**Goal:** Achieve SOC 2 Type II certification

- ✅ P0: Security audit (external consultant) (4 weeks)
- ✅ P0: Penetration testing (2 weeks)
- 🔄 P1: Documentation (security controls, policies) (2 weeks)
- 🔄 P1: SOC 2 audit (6 months)

## OKRs (Q1 2025)
1. **Detection Quality:** 80% detection rate, <8% FP rate
2. **Customer Adoption:** 10 new pilot customers, 5 convert to paid
3. **Enterprise Readiness:** SSO + RBAC shipped, 2 enterprise pilots
4. **Performance:** <5min scan time for 100K docs (80% of scans)
5. **Compliance:** SOC 2 audit initiated, all controls implemented
```

---

## Daily Standup (Optional)

**Frequency:** Every weekday, 9:30am - 9:45am (15 minutes)  
**Attendees:** Engineering team  
**Owner:** Engineering Lead  
**Format:** Async (Slack) or Sync (Zoom)

### Template (Async in Slack)

```
🌅 Daily Standup - 2024-10-21

@engineer1:
✅ Yesterday: Fixed bug #42 (FP on medical terms)
🚧 Today: Working on unicode normalization enhancement
🚫 Blockers: None

@engineer2:
✅ Yesterday: Implemented cache size limits (10GB cap)
🚧 Today: Testing on Windows, investigating slow scan
🚫 Blockers: Waiting for Windows VM setup

@product-manager:
✅ Yesterday: Pilot sync with Customer A
🚧 Today: Writing up action items, updating roadmap
🚫 Blockers: Need customer to provide FP examples
```

---

## Ad-Hoc Rituals

### Post-Incident Review (PIR)

**When:** Within 48 hours of P0/P1 incident resolution  
**Duration:** 60 minutes  
**Attendees:** Incident participants, Engineering Lead

**Agenda:**
1. Timeline of incident (what happened, when)
2. Root cause analysis (why it happened)
3. Impact assessment (customers affected, downtime)
4. Mitigation steps taken (immediate fixes)
5. Lessons learned (what went well, what didn't)
6. Action items (prevent recurrence)

**Template:** See `docs/postmortems/TEMPLATE.md`

### Design Reviews

**When:** Before starting major feature work  
**Duration:** 60 minutes  
**Attendees:** Feature owner, Engineering team, Product Manager

**Agenda:**
1. Problem statement (what are we solving?)
2. Proposed solution (high-level design)
3. Alternatives considered (why did we choose this?)
4. Implementation plan (phases, milestones)
5. Risks & mitigations
6. Q&A and feedback

---

## Communication Channels

### Real-Time

**Slack Channels:**
- `#sentineldf-engineering` - Engineering team, day-to-day
- `#sentineldf-incidents` - P0/P1 incidents only (PagerDuty integration)
- `#sentineldf-releases` - Release announcements (automated)

### Async

**Email Lists:**
- `engineering@sentineldf.com` - Engineering team
- `pilots@sentineldf.com` - Pilot customers (opt-in)

**Documents:**
- Confluence/Notion - Internal docs, meeting notes
- GitHub - Issues, PRs, project boards
- Google Drive - Metrics reports, presentations

---

## Meeting Best Practices

### Before Meeting
- [ ] Send agenda 24 hours in advance
- [ ] Prepare any materials (slides, reports, demos)
- [ ] Test screen sharing / video if demoing

### During Meeting
- [ ] Start on time (within 2 minutes)
- [ ] Designate note-taker (rotate weekly)
- [ ] Stay on topic (parking lot for tangents)
- [ ] End on time (or early!)

### After Meeting
- [ ] Share notes within 2 hours
- [ ] Create action items in tracking system (GitHub/Jira)
- [ ] Follow up on commitments

---

## Continuous Improvement

### Quarterly Review of Cadence

**Ask:**
- Are these meetings effective?
- Are we spending too much/too little time in meetings?
- Should we add/remove/adjust any rituals?

**Adjust:**
- Change frequency (e.g., weekly → bi-weekly)
- Change duration (e.g., 60min → 30min)
- Change format (e.g., sync → async)

---

**Last Reviewed:** 2024-10-16  
**Next Review:** 2025-01-16 (Quarterly)  
**Review Frequency:** Quarterly

---

*SentinelDF v0.1.0 - Data Firewall for LLM Training*  
*Copyright © 2024 Varun Sripad Kota. Apache-2.0 License.*
