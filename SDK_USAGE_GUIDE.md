# 📚 SentinelDF SDK - Complete Usage Guide

## 🚀 Quick Start

### Installation

```bash
pip install sentineldf
```

### Basic Usage

```python
from sentineldf import SentinelDF

# Initialize client
client = SentinelDF(api_key="your_api_key_here")

# Scan a single text
result = client.scan("Your text to scan here")
print(f"Is safe: {result['is_safe']}")
print(f"Threats detected: {result['threats']}")
```

---

## 📖 Complete Examples

### 1. Scan Single Text

```python
from sentineldf import SentinelDF

client = SentinelDF(api_key="sk_live_...")

# Scan text
text = "Hello, this is a sample text to scan"
result = client.scan(text)

# Check results
if result['is_safe']:
    print("✅ Text is safe!")
else:
    print("⚠️ Threats detected:")
    for threat in result['threats']:
        print(f"  - {threat['type']}: {threat['description']}")
        print(f"    Confidence: {threat['confidence']:.2%}")
```

### 2. Scan Multiple Texts (Batch)

```python
from sentineldf import SentinelDF

client = SentinelDF(api_key="sk_live_...")

# List of texts to scan
texts = [
    "First document content",
    "Second document content",
    "Third document content"
]

# Batch scan
results = client.scan(texts)

# Process results
for i, result in enumerate(results):
    print(f"\n📄 Document {i+1}:")
    print(f"  Safe: {result['is_safe']}")
    print(f"  Threats: {len(result['threats'])}")
```

### 3. Scan Files

```python
from sentineldf import SentinelDF

client = SentinelDF(api_key="sk_live_...")

# Scan a file
result = client.scan_file("data/training_data.txt")

if not result['is_safe']:
    print("⚠️ File contains threats!")
    for threat in result['threats']:
        print(f"  Line {threat.get('line_number', 'unknown')}: {threat['type']}")
```

### 4. Scan Dataset (CSV/JSON)

```python
from sentineldf import SentinelDF
import pandas as pd

client = SentinelDF(api_key="sk_live_...")

# Load dataset
df = pd.read_csv("training_dataset.csv")

# Scan text column
results = []
for text in df['text_column']:
    result = client.scan(text)
    results.append(result)

# Add results to dataframe
df['is_safe'] = [r['is_safe'] for r in results]
df['threat_count'] = [len(r['threats']) for r in results]

# Filter out unsafe samples
safe_df = df[df['is_safe']]
print(f"✅ Safe samples: {len(safe_df)}/{len(df)}")

# Save clean dataset
safe_df.to_csv("clean_training_data.csv", index=False)
```

### 5. Real-time Monitoring

```python
from sentineldf import SentinelDF
import time

client = SentinelDF(api_key="sk_live_...")

def monitor_incoming_data(data_stream):
    """Monitor and scan incoming data in real-time"""
    for item in data_stream:
        result = client.scan(item['text'])
        
        if not result['is_safe']:
            # Alert on threat detection
            print(f"🚨 ALERT: Threat detected in {item['source']}")
            print(f"   Threats: {[t['type'] for t in result['threats']]}")
            # Send to review queue or reject
            quarantine_item(item, result)
        else:
            # Safe to process
            process_item(item)
```

### 6. CLI Usage

#### Scan Single File
```bash
sentineldf scan-file data.txt --api-key YOUR_KEY
```

#### Scan Directory
```bash
sentineldf scan-directory ./training_data/ --api-key YOUR_KEY
```

#### Launch GUI
```bash
sentineldf gui --api-key YOUR_KEY
```

#### Generate Report
```bash
sentineldf scan-file data.txt --api-key YOUR_KEY --output report.json
```

---

## 🎯 Use Cases

### A. Pre-Training Dataset Validation

```python
from sentineldf import SentinelDF

def validate_training_dataset(dataset_path):
    """Validate entire training dataset before fine-tuning"""
    client = SentinelDF(api_key="sk_live_...")
    
    # Load dataset
    with open(dataset_path, 'r') as f:
        lines = f.readlines()
    
    # Scan all samples
    print(f"📊 Scanning {len(lines)} samples...")
    results = client.scan(lines)
    
    # Analyze results
    total = len(results)
    safe = sum(1 for r in results if r['is_safe'])
    unsafe = total - safe
    
    print(f"\n✅ Safe samples: {safe}/{total} ({safe/total*100:.1f}%)")
    print(f"⚠️ Unsafe samples: {unsafe}/{total} ({unsafe/total*100:.1f}%)")
    
    # Generate detailed report
    threat_types = {}
    for result in results:
        for threat in result['threats']:
            threat_type = threat['type']
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
    
    if threat_types:
        print(f"\n📋 Threat Breakdown:")
        for threat_type, count in sorted(threat_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {threat_type}: {count}")
    
    return results

# Usage
results = validate_training_dataset("my_training_data.jsonl")
```

### B. Production API Integration

```python
from flask import Flask, request, jsonify
from sentineldf import SentinelDF

app = Flask(__name__)
sentinel = SentinelDF(api_key="sk_live_...")

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Endpoint that scans user feedback before saving"""
    data = request.json
    feedback_text = data.get('text')
    
    # Scan before processing
    scan_result = sentinel.scan(feedback_text)
    
    if not scan_result['is_safe']:
        # Log threat
        print(f"⚠️ Blocked malicious feedback: {scan_result['threats']}")
        return jsonify({
            'error': 'Content rejected due to security concerns',
            'blocked': True
        }), 400
    
    # Safe to process
    save_feedback(feedback_text)
    return jsonify({'success': True, 'message': 'Feedback received'})
```

### C. Automated CI/CD Pipeline

```yaml
# .github/workflows/scan-training-data.yml
name: Scan Training Data

on:
  push:
    paths:
      - 'data/**'
      - 'training/**'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install SentinelDF
        run: pip install sentineldf
      
      - name: Scan Training Data
        env:
          SENTINELDF_API_KEY: ${{ secrets.SENTINELDF_API_KEY }}
        run: |
          sentineldf scan-directory ./data/ --api-key $SENTINELDF_API_KEY --fail-on-threat
      
      - name: Upload Report
        if: failure()
        uses: actions/upload-artifact@v2
        with:
          name: scan-report
          path: scan_report.json
```

### D. Jupyter Notebook Analysis

```python
# In Jupyter Notebook
from sentineldf import SentinelDF
import pandas as pd
import matplotlib.pyplot as plt

# Initialize
client = SentinelDF(api_key="sk_live_...")

# Load and scan data
df = pd.read_csv("user_generated_content.csv")
scan_results = [client.scan(text) for text in df['content']]

# Add results
df['is_safe'] = [r['is_safe'] for r in scan_results]
df['num_threats'] = [len(r['threats']) for r in scan_results]

# Visualize
df['is_safe'].value_counts().plot(kind='bar', title='Safety Distribution')
plt.ylabel('Count')
plt.xlabel('Is Safe')
plt.show()

# Show unsafe samples
unsafe_df = df[~df['is_safe']]
print(f"Found {len(unsafe_df)} unsafe samples:")
display(unsafe_df.head())
```

---

## 🔧 Advanced Configuration

### Custom Timeouts

```python
client = SentinelDF(
    api_key="sk_live_...",
    timeout=30  # 30 seconds timeout
)
```

### Async Usage

```python
import asyncio
from sentineldf import SentinelDF

client = SentinelDF(api_key="sk_live_...")

async def scan_async(texts):
    """Scan multiple texts concurrently"""
    tasks = [client.scan_async(text) for text in texts]
    results = await asyncio.gather(*tasks)
    return results

# Usage
texts = ["text1", "text2", "text3"]
results = asyncio.run(scan_async(texts))
```

### Error Handling

```python
from sentineldf import SentinelDF, SentinelDFError

client = SentinelDF(api_key="sk_live_...")

try:
    result = client.scan("Your text here")
except SentinelDFError as e:
    print(f"Error: {e}")
    # Handle error (retry, log, alert, etc.)
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 📊 Response Format

### Successful Scan

```json
{
  "is_safe": false,
  "confidence": 0.95,
  "threats": [
    {
      "type": "prompt_injection",
      "description": "Detected attempt to manipulate model behavior",
      "confidence": 0.95,
      "severity": "high",
      "line_number": 5,
      "matched_pattern": "Ignore previous instructions..."
    }
  ],
  "scan_id": "scan_abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Threat Types Detected

- `prompt_injection` - Attempts to manipulate model instructions
- `data_poisoning` - Malicious training data
- `backdoor` - Hidden triggers for model behavior
- `jailbreak` - Attempts to bypass safety filters
- `pii_leakage` - Personal identifiable information exposure
- `code_injection` - Embedded executable code
- `sql_injection` - Database manipulation attempts
- `xss` - Cross-site scripting patterns
- `malicious_url` - Harmful links
- `phishing` - Social engineering attempts
- `hate_speech` - Offensive content
- `violence` - Violent content
- `self_harm` - Self-harm related content
- `illegal_activity` - Illegal content references

---

## 💡 Best Practices

### 1. Scan Before Training
Always scan datasets before fine-tuning to prevent model poisoning.

### 2. Batch Processing
Use batch scanning for better performance with large datasets.

### 3. Continuous Monitoring
Implement real-time scanning for user-generated content.

### 4. Secure Key Storage
Store API keys in environment variables, never hardcode.

```python
import os
api_key = os.environ.get('SENTINELDF_API_KEY')
client = SentinelDF(api_key=api_key)
```

### 5. Rate Limiting
Implement rate limiting for high-volume applications.

---

## 🆘 Support

- **Documentation**: https://docs.sentineldf.com
- **API Reference**: https://api.sentineldf.com/docs
- **Email**: support@sentineldf.com
- **Discord**: https://discord.gg/sentineldf
- **GitHub**: https://github.com/sentineldf/sdk

---

## 📝 License

MIT License - See LICENSE file for details
