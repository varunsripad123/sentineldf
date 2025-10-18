# SentinelDF 2.0.0 - Quick Start Guide

## 📦 Installation

```bash
pip install sentineldf-ai
```

After installation, you'll see a welcome message with quick start instructions! 🎉

---

## 🔑 Get Your API Key

1. Visit https://sentineldf.com/dashboard
2. Sign up or log in
3. Copy your API key from the dashboard

**Pro Tip:** Set it as an environment variable:
```bash
# Windows (PowerShell)
$env:SENTINELDF_API_KEY="your-key-here"

# Linux/Mac
export SENTINELDF_API_KEY="your-key-here"
```

---

## 🚀 CLI Usage

### 1. Basic Commands

```bash
# Show help
sentineldf --help

# Check version
sentineldf --version

# Show banner
sentineldf
```

### 2. Scan Text

```bash
# Scan a suspicious string
sentineldf scan-text "DROP TABLE users;" --api-key YOUR_KEY

# With detailed analysis
sentineldf scan-text "Your text here" --api-key YOUR_KEY --detailed
```

### 3. Scan a Single File

```bash
# Basic scan
sentineldf scan-file data.txt --api-key YOUR_KEY

# With detailed threat report
sentineldf scan-file data.txt --api-key YOUR_KEY --detailed

# Save report as HTML
sentineldf scan-file data.txt --api-key YOUR_KEY --output report.html

# Save report as JSON
sentineldf scan-file data.txt --api-key YOUR_KEY --output report.json
```

### 4. Scan a Folder (Batch Processing)

```bash
# Scan all files in a folder (recursive)
sentineldf scan-folder ./datasets --api-key YOUR_KEY -r

# With HTML report
sentineldf scan-folder ./data --api-key YOUR_KEY --output security_report.html

# Show all quarantined files
sentineldf scan-folder ./data --api-key YOUR_KEY --show-threats

# Quiet mode (no progress output)
sentineldf scan-folder ./data --api-key YOUR_KEY -q

# Custom batch size
sentineldf scan-folder ./data --api-key YOUR_KEY --batch-size 50
```

### 5. Using Environment Variable

```bash
# Set API key once
export SENTINELDF_API_KEY="your-key-here"

# Then run commands without --api-key flag
sentineldf scan-file data.txt
sentineldf scan-folder ./datasets -r --output report.html
```

---

## 🐍 Python SDK Usage

### Basic Scanning

```python
from sentineldf import SentinelDF

# Initialize client
client = SentinelDF(api_key="YOUR_KEY")

# Scan a single text
response = client.scan(["Your text to scan"])
result = response.results[0]

print(f"Risk Score: {result.risk}")
print(f"Quarantined: {result.quarantine}")
print(f"Reasons: {result.reasons}")
```

### Batch Scanning

```python
from sentineldf import SentinelDF

client = SentinelDF(api_key="YOUR_KEY")

# Scan multiple texts at once
texts = [
    "Normal text content",
    "DROP TABLE users;",
    "Click here: http://phishing-site.com"
]

response = client.scan(texts)

for i, result in enumerate(response.results):
    print(f"Text {i+1}: Risk={result.risk:.2f}, Quarantine={result.quarantine}")
```

### Scan Files

```python
from sentineldf import SentinelDF, FileScanner

client = SentinelDF(api_key="YOUR_KEY")

# Read and scan a file
content = FileScanner.read_file("data.txt")
response = client.scan([content], doc_ids=["data.txt"])

result = response.results[0]
print(f"File: data.txt")
print(f"Risk: {result.risk}")
print(f"Status: {'QUARANTINED' if result.quarantine else 'SAFE'}")
```

### Scan Folders

```python
from sentineldf import SentinelDF, scan_and_analyze

client = SentinelDF(api_key="YOUR_KEY")

# Scan entire folder
results = scan_and_analyze(
    client,
    folder_path="./datasets",
    recursive=True,
    batch_size=100,
    progress_callback=lambda p, t: print(f"Progress: {p}/{t}")
)

# Check summary
summary = results['summary']
print(f"Total Files: {summary['total_files']}")
print(f"Quarantined: {summary['quarantined_files']}")
print(f"Average Risk: {summary['avg_risk']:.2f}")

# Get individual results
for result in results['results']:
    if result.quarantine:
        print(f"⚠️ {result.doc_id}: Risk={result.risk:.2f}")
```

### Generate Detailed Reports

```python
from sentineldf import SentinelDF, ThreatReport, save_report_to_html

client = SentinelDF(api_key="YOUR_KEY")

# Scan text
content = "Your suspicious text here"
response = client.scan([content])
result = response.results[0]

# Create detailed report
report = ThreatReport(result, content)

# Print to console
report.print_report()

# Get as dictionary
detailed_report = report.get_detailed_report()
print(detailed_report)

# Save as HTML
save_report_to_html(detailed_report, "threat_report.html")

# Save as JSON
import json
with open("threat_report.json", "w") as f:
    json.dump(detailed_report, f, indent=2)
```

### Batch Reports

```python
from sentineldf import SentinelDF, generate_batch_report, save_report_to_html

client = SentinelDF(api_key="YOUR_KEY")

# Scan multiple documents
texts = ["doc1 content", "doc2 content", "doc3 content"]
response = client.scan(texts, doc_ids=["doc1", "doc2", "doc3"])

# Generate batch report
batch_report = generate_batch_report(
    response.results,
    files=[{"path": f"doc{i+1}"} for i in range(3)]
)

# Save as HTML
save_report_to_html(batch_report, "batch_security_report.html")

print(f"Batch Report Stats:")
print(f"  Total: {batch_report['summary']['total_documents']}")
print(f"  Quarantined: {batch_report['summary']['quarantined']}")
print(f"  High Risk: {batch_report['summary']['high_risk_count']}")
```

---

## 📊 Real-World Examples

### Example 1: Scan Training Dataset

```python
from sentineldf import SentinelDF, scan_and_analyze, save_report_to_html

client = SentinelDF(api_key="YOUR_KEY")

# Scan your LLM training data
results = scan_and_analyze(
    client,
    folder_path="./training_data",
    recursive=True
)

# Generate security report
from sentineldf import generate_batch_report
report = generate_batch_report(results['results'])
save_report_to_html(report, "training_data_security_audit.html")

print(f"✅ Scanned {results['summary']['total_files']} files")
print(f"🚨 Found {results['summary']['quarantined_files']} threats")
print(f"📄 Report saved to training_data_security_audit.html")
```

### Example 2: Monitor User-Generated Content

```python
from sentineldf import SentinelDF

client = SentinelDF(api_key="YOUR_KEY")

def moderate_content(user_input):
    """Check if user content is safe before adding to training data."""
    response = client.scan([user_input])
    result = response.results[0]
    
    if result.quarantine:
        print(f"⚠️ Content blocked: {', '.join(result.reasons)}")
        return False
    else:
        print(f"✅ Content approved (Risk: {result.risk:.2f})")
        return True

# Example usage
user_text = "This is some user-generated content"
if moderate_content(user_text):
    # Add to training data
    pass
```

### Example 3: Automated Security Pipeline

```bash
#!/bin/bash
# security_pipeline.sh

# Scan new data before training
sentineldf scan-folder ./new_data \
    --api-key $SENTINELDF_API_KEY \
    --recursive \
    --output security_report_$(date +%Y%m%d).html \
    --show-threats

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Security scan passed"
    # Proceed with training
    python train_model.py
else
    echo "❌ Security issues found"
    exit 1
fi
```

---

## 🔧 Advanced Features

### Custom File Extensions

```python
from sentineldf import FileScanner

# Scan only specific file types
files = FileScanner.scan_folder(
    "./data",
    extensions=['.txt', '.md', '.py'],
    max_files=100,
    max_file_size_mb=5
)

print(f"Found {len(files)} files")
```

### Progress Tracking

```python
from sentineldf import SentinelDF, scan_and_analyze

def progress_handler(processed, total):
    percent = (processed / total) * 100
    print(f"Scanning: {processed}/{total} ({percent:.1f}%)", end='\r')

client = SentinelDF(api_key="YOUR_KEY")
results = scan_and_analyze(
    client,
    "./data",
    progress_callback=progress_handler
)
```

### Error Handling

```python
from sentineldf import (
    SentinelDF,
    SentinelDFError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError
)

client = SentinelDF(api_key="YOUR_KEY")

try:
    response = client.scan(["text to scan"])
except AuthenticationError:
    print("❌ Invalid API key")
except QuotaExceededError:
    print("❌ Monthly quota exceeded")
except RateLimitError:
    print("❌ Rate limit exceeded, try again later")
except SentinelDFError as e:
    print(f"❌ Error: {e}")
```

---

## 📚 Additional Resources

- **Documentation:** https://docs.sentineldf.com
- **Dashboard:** https://sentineldf.com/dashboard
- **GitHub:** https://github.com/varunsripad123/sentineldf
- **Support:** support@sentineldf.com

---

## 💡 Tips & Best Practices

1. **Set API key as environment variable** to avoid hardcoding
2. **Use batch processing** for large datasets (faster and more efficient)
3. **Generate HTML reports** for easy sharing with team
4. **Monitor quarantine rates** to track data quality over time
5. **Integrate into CI/CD** for automated security checks

---

## 🐛 Troubleshooting

**Command not found: sentineldf**
```bash
pip install --upgrade sentineldf-ai
```

**Authentication error**
- Check your API key at https://sentineldf.com/dashboard
- Ensure no extra spaces in the key

**File not found**
- Use absolute paths or check current directory
- On Windows, use forward slashes: `./data/file.txt`

**Import error**
```bash
pip uninstall sentineldf-ai -y
pip install --no-cache-dir sentineldf-ai
```

---

**🎉 Happy Scanning! Protect your AI before it's too late!**
