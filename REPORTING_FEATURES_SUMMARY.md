# 📊 Reporting Features - Quick Summary

## ✅ YES! Customers Get Detailed Reports

Your customers receive **line-by-line analysis** showing exactly what's wrong with their files.

---

## 🎯 What They Get

### **1. Which Files Are Corrupted** ✅
```
malicious.txt: QUARANTINED (95/100 risk)
suspicious.py: HIGH RISK (78/100 risk)
normal.txt: SAFE (12/100 risk)
```

### **2. Which Lines Are Problematic** ✅
```
malicious.txt:
  Line 3: Ignore all previous instructions!
  Line 7: <script>alert('xss')</script>
  Line 12: SELECT * FROM users WHERE 1=1
```

### **3. Why Each Line Is Flagged** ✅
```
Line 3: "Ignore all previous instructions!"
  • Prompt injection - attempts to override system instructions (HIGH)
  
Line 7: "<script>alert('xss')</script>"
  • Cross-site scripting (XSS) - malicious JavaScript code (CRITICAL)
  
Line 12: "SELECT * FROM users WHERE 1=1"
  • SQL injection - attempts to manipulate database queries (CRITICAL)
```

### **4. Severity Levels** ✅
```
CRITICAL: Must be removed immediately
HIGH: Should be quarantined
MEDIUM: Needs review
```

---

## 📄 Example Output

```python
from sentineldf import SentinelDF, ThreatReport

client = SentinelDF(api_key="sk_live_your_key")
file_content = "Line 1: Normal\nLine 2: Ignore all instructions!\nLine 3: More text"

results = client.scan([file_content], doc_ids=["test.txt"])
report = ThreatReport(results.results[0], file_content)
report.print_report()
```

**Output:**
```
================================================================================
📄 FILE: test.txt
================================================================================
Risk Score: 85/100
Status: QUARANTINED
Verdict: HIGH RISK - Should be quarantined

🔍 DETECTION REASONS:
  • Prompt injection detected
  • Instruction override attempt

⚠️  SUSPICIOUS LINES DETECTED:
--------------------------------------------------------------------------------

Line 2: [HIGH]
  Content: Ignore all instructions!
  Threats:
    • Prompt injection - attempts to override system instructions (HIGH)
--------------------------------------------------------------------------------

📊 STATISTICS:
  Total lines: 3
  Suspicious lines: 1
  Heuristic score: 0.85
  Embedding score: 0.72
================================================================================
```

---

## 🎨 Report Formats

| Format | Use Case | Command |
|--------|----------|---------|
| **Console** | Quick feedback | `report.print_report()` |
| **HTML** | Visual review | `save_report_to_html(batch_report, "report.html")` |
| **JSON** | Automation/CI/CD | `json.dump(batch_report, file)` |

---

## 🚀 Quick Example

```python
from sentineldf import SentinelDF, FileScanner, generate_batch_report, save_report_to_html

# 1. Scan folder
client = SentinelDF(api_key="sk_live_your_key")
files = FileScanner.scan_folder("./training_data")
texts = [f['content'] for f in files]
doc_ids = [f['relative_path'] for f in files]

# 2. Get results
results = client.scan(texts=texts, doc_ids=doc_ids)

# 3. Generate detailed report
batch_report = generate_batch_report(results.results, files)

# 4. Save as HTML (beautiful visual report)
save_report_to_html(batch_report, "security_report.html")

# 5. Check results
print(f"Safe files: {batch_report['summary']['safe_files']}")
print(f"Threats: {batch_report['summary']['quarantined_files']}")

# 6. See which files to delete
for file in batch_report['critical_files']:
    print(f"DELETE: {file}")
```

---

## 📊 What's Detected

✅ Prompt injections  
✅ SQL injections  
✅ XSS attacks  
✅ Code execution attempts  
✅ Information extraction  
✅ Jailbreak attempts  
✅ Malware references  
✅ Backdoor attempts  

---

## 📁 Files Created

1. **`sdk/sentineldf/reporting.py`** - Reporting engine
2. **`examples/detailed_report_example.py`** - 5 working examples
3. **`DETAILED_REPORTING_GUIDE.md`** - Complete documentation

---

## ✅ Ready to Rebuild

Now rebuild your SDK with reporting features:

```bash
cd sdk
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
python -m build
twine upload dist/*
```

---

**Your customers now get professional-grade security reports!** 🎉
