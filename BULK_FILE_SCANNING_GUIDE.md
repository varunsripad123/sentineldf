# 📂 Bulk File & Folder Scanning Guide

Complete guide for scanning multiple files and folders with SentinelDF.

---

## 🎯 Use Cases

- **Scan entire training datasets** before fine-tuning
- **Audit code repositories** for malicious code
- **Filter downloaded datasets** from the internet
- **Validate user-uploaded content** in bulk
- **Monitor data pipelines** continuously

---

## 🚀 Quick Start

### Example 1: Scan a Single Folder

```python
from sentineldf import SentinelDF, scan_and_analyze

# Initialize client
client = SentinelDF(api_key="sk_live_your_key")

# Scan all files in a folder
results = scan_and_analyze(
    client=client,
    folder_path="/path/to/training_data",
    recursive=True,  # Include subfolders
    batch_size=100   # Process 100 files at a time
)

# View summary
print(f"Total files: {results['summary']['total_files']}")
print(f"Safe files: {results['summary']['safe_files']}")
print(f"Quarantined: {results['summary']['quarantined_files']}")

# Get only safe files
safe_files = [r for r in results['results'] if not r.quarantine]
```

---

### Example 2: Scan with Progress Bar

```python
from sentineldf import SentinelDF, scan_and_analyze

client = SentinelDF(api_key="sk_live_your_key")

def progress_callback(processed, total):
    percent = (processed / total) * 100
    print(f"Progress: {processed}/{total} files ({percent:.1f}%)")

results = scan_and_analyze(
    client=client,
    folder_path="/path/to/data",
    progress_callback=progress_callback
)

print("\n✅ Scanning complete!")
```

**Output:**
```
Progress: 100/500 files (20.0%)
Progress: 200/500 files (40.0%)
Progress: 300/500 files (60.0%)
Progress: 400/500 files (80.0%)
Progress: 500/500 files (100.0%)

✅ Scanning complete!
```

---

### Example 3: Scan Specific File Types

```python
from sentineldf import SentinelDF, FileScanner

client = SentinelDF(api_key="sk_live_your_key")

# Scan only Python files
files = FileScanner.scan_folder(
    folder_path="/path/to/code",
    recursive=True,
    extensions=['.py', '.ipynb']  # Only Python files
)

# Scan them
texts = [f['content'] for f in files]
doc_ids = [f['relative_path'] for f in files]

results = client.scan(texts=texts, doc_ids=doc_ids)

print(f"Scanned {len(files)} Python files")
print(f"Threats found: {results.summary.quarantined_count}")
```

---

### Example 4: Scan and Save Results to JSON

```python
from sentineldf import SentinelDF, scan_and_analyze
import json

client = SentinelDF(api_key="sk_live_your_key")

# Scan folder
results = scan_and_analyze(
    client=client,
    folder_path="/path/to/data"
)

# Save results
report = {
    'summary': results['summary'],
    'quarantined_files': [
        {
            'file': r.doc_id,
            'risk': r.risk,
            'reasons': r.reasons
        }
        for r in results['results'] if r.quarantine
    ],
    'safe_files': [
        r.doc_id for r in results['results'] if not r.quarantine
    ]
}

with open('scan_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("✅ Report saved to scan_report.json")
```

---

### Example 5: Copy Only Safe Files to New Folder

```python
from sentineldf import SentinelDF, scan_and_analyze
import shutil
from pathlib import Path

client = SentinelDF(api_key="sk_live_your_key")

# Scan folder
results = scan_and_analyze(
    client=client,
    folder_path="/path/to/raw_data",
    recursive=True
)

# Create clean data folder
clean_folder = Path("/path/to/clean_data")
clean_folder.mkdir(exist_ok=True)

# Copy only safe files
for result in results['results']:
    if not result.quarantine:
        # Get original file path from doc_id
        src = Path("/path/to/raw_data") / result.doc_id
        dst = clean_folder / result.doc_id
        
        # Create parent directories
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(src, dst)
        print(f"✅ Copied: {result.doc_id}")
    else:
        print(f"⚠️ Skipped (threat): {result.doc_id}")

print(f"\n✅ Clean dataset created with {results['summary']['safe_files']} files")
```

---

## 🎨 Advanced Examples

### Example 6: Real-time Monitoring of Folder

```python
from sentineldf import SentinelDF, FileScanner
import time
from pathlib import Path

client = SentinelDF(api_key="sk_live_your_key")
watched_folder = Path("/path/to/incoming_data")
processed_files = set()

print("👀 Monitoring folder for new files...")

while True:
    # Get all files
    files = FileScanner.scan_folder(str(watched_folder))
    
    # Find new files
    current_files = {f['path'] for f in files}
    new_files = current_files - processed_files
    
    if new_files:
        print(f"\n📁 Found {len(new_files)} new files")
        
        # Scan new files
        new_file_objs = [f for f in files if f['path'] in new_files]
        texts = [f['content'] for f in new_file_objs]
        doc_ids = [f['name'] for f in new_file_objs]
        
        results = client.scan(texts=texts, doc_ids=doc_ids)
        
        # Handle results
        for result in results.results:
            if result.quarantine:
                print(f"⚠️ THREAT: {result.doc_id} - {result.reasons}")
            else:
                print(f"✅ Safe: {result.doc_id}")
        
        processed_files.update(new_files)
    
    time.sleep(10)  # Check every 10 seconds
```

---

### Example 7: Parallel Processing for Large Datasets

```python
from sentineldf import SentinelDF, FileScanner
from concurrent.futures import ThreadPoolExecutor
import numpy as np

client = SentinelDF(api_key="sk_live_your_key")

# Scan folder
files = FileScanner.scan_folder(
    folder_path="/path/to/huge_dataset",
    max_files=10000  # Limit for demo
)

print(f"Found {len(files)} files")

# Split into chunks
chunk_size = 100
chunks = np.array_split(files, len(files) // chunk_size + 1)

def scan_chunk(chunk):
    """Scan a chunk of files."""
    texts = [f['content'] for f in chunk]
    doc_ids = [f['name'] for f in chunk]
    return client.scan(texts=texts, doc_ids=doc_ids)

# Process chunks in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(scan_chunk, chunks))

# Combine results
all_results = []
for r in results:
    all_results.extend(r.results)

quarantined = sum(1 for r in all_results if r.quarantine)
print(f"\n✅ Scanned {len(all_results)} files")
print(f"⚠️ Quarantined: {quarantined}")
```

---

### Example 8: Scan Git Repository

```python
from sentineldf import SentinelDF, FileScanner
from pathlib import Path

client = SentinelDF(api_key="sk_live_your_key")

# Scan code repository
repo_path = "/path/to/your_repo"

# Scan only code files, excluding certain folders
files = FileScanner.scan_folder(
    folder_path=repo_path,
    recursive=True,
    extensions=['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp']
)

# Filter out files in node_modules, venv, etc.
filtered_files = [
    f for f in files
    if not any(x in f['path'] for x in ['node_modules', 'venv', '.git', '__pycache__'])
]

print(f"Scanning {len(filtered_files)} code files...")

# Scan
texts = [f['content'] for f in filtered_files]
doc_ids = [f['relative_path'] for f in filtered_files]

results = client.scan(texts=texts, doc_ids=doc_ids)

# Report threats
print(f"\n📊 Results:")
print(f"Total files: {len(filtered_files)}")
print(f"Safe: {results.summary.allowed_count}")
print(f"Threats: {results.summary.quarantined_count}")

if results.summary.quarantined_count > 0:
    print("\n⚠️ Threats found in:")
    for r in results.results:
        if r.quarantine:
            print(f"  - {r.doc_id}: {', '.join(r.reasons)}")
```

---

### Example 9: Filter Training Dataset from HuggingFace

```python
from sentineldf import SentinelDF
from datasets import load_dataset

client = SentinelDF(api_key="sk_live_your_key")

# Load dataset
print("📥 Loading dataset...")
dataset = load_dataset("your-dataset", split="train")

# Scan in batches
batch_size = 100
clean_samples = []

for i in range(0, len(dataset), batch_size):
    batch = dataset[i:i+batch_size]
    texts = batch['text']  # Assuming 'text' column
    
    print(f"Scanning batch {i//batch_size + 1}...")
    results = client.scan(texts=texts)
    
    # Keep only safe samples
    for j, result in enumerate(results.results):
        if not result.quarantine:
            clean_samples.append(batch[j])
    
    print(f"Progress: {len(clean_samples)} clean samples")

print(f"\n✅ Filtered dataset:")
print(f"Original: {len(dataset)} samples")
print(f"Clean: {len(clean_samples)} samples")
print(f"Removed: {len(dataset) - len(clean_samples)} threats")

# Save clean dataset
# clean_dataset = Dataset.from_list(clean_samples)
# clean_dataset.save_to_disk("./clean_dataset")
```

---

## 📊 File Format Support

SentinelDF automatically handles these text formats:

### Source Code
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`
- Java: `.java`
- C/C++: `.c`, `.cpp`, `.h`
- Go: `.go`
- Rust: `.rs`
- Ruby: `.rb`
- PHP: `.php`

### Data Files
- Text: `.txt`, `.md`
- JSON: `.json`
- YAML: `.yaml`, `.yml`
- CSV: `.csv`
- XML: `.xml`
- HTML: `.html`

### Configuration
- Shell scripts: `.sh`, `.bash`
- SQL: `.sql`
- Log files: `.log`

---

## ⚙️ Configuration Options

### FileScanner Options

```python
from sentineldf import FileScanner

files = FileScanner.scan_folder(
    folder_path="/path/to/data",
    recursive=True,              # Scan subfolders (default: True)
    extensions=['.txt', '.py'],  # File types (default: all text files)
    max_files=1000,              # Limit number of files (default: None)
    max_file_size_mb=10          # Skip large files (default: 10MB)
)
```

### scan_and_analyze Options

```python
from sentineldf import scan_and_analyze

results = scan_and_analyze(
    client=client,
    folder_path="/path/to/data",
    batch_size=100,              # Files per API call (max 1000)
    recursive=True,              # Include subfolders
    progress_callback=my_func    # Progress updates
)
```

---

## 💰 Cost Optimization

### Tip 1: Use Batch Processing
```python
# ❌ Bad: Individual requests (expensive, slow)
for file in files:
    client.scan([file['content']])  # 1000 API calls!

# ✅ Good: Batch processing (cheap, fast)
texts = [f['content'] for f in files]
client.scan(texts)  # 1 API call!
```

### Tip 2: Filter by Extension
```python
# Only scan relevant files
files = FileScanner.scan_folder(
    folder_path="/data",
    extensions=['.txt', '.json']  # Skip images, binaries, etc.
)
```

### Tip 3: Set Size Limits
```python
# Skip large files
files = FileScanner.scan_folder(
    folder_path="/data",
    max_file_size_mb=5  # Skip files > 5MB
)
```

---

## 📈 Performance Tips

### Large Datasets (> 10,000 files)

```python
from sentineldf import SentinelDF, FileScanner
from tqdm import tqdm  # Progress bar

client = SentinelDF(api_key="sk_live_your_key")

# Scan files
files = FileScanner.scan_folder("/path/to/huge_dataset")

# Process in batches with progress bar
batch_size = 100
all_results = []

for i in tqdm(range(0, len(files), batch_size)):
    batch = files[i:i+batch_size]
    texts = [f['content'] for f in batch]
    results = client.scan(texts=texts)
    all_results.extend(results.results)

# Analyze
quarantined = sum(1 for r in all_results if r.quarantine)
print(f"Quarantined: {quarantined}/{len(all_results)}")
```

---

## 🎯 Common Workflows

### Workflow 1: Pre-training Validation

```python
# 1. Download dataset
# 2. Scan all files
results = scan_and_analyze(client, "/data/raw")

# 3. Copy clean files
for r in results['results']:
    if not r.quarantine:
        copy_to_training_folder(r.doc_id)

# 4. Start training with clean data
```

### Workflow 2: CI/CD Integration

```python
# In your CI pipeline:
results = scan_and_analyze(client, "./src")

if results['summary']['quarantined_files'] > 0:
    print("❌ Security threats detected!")
    exit(1)  # Fail the build
else:
    print("✅ No threats found")
    exit(0)  # Pass the build
```

### Workflow 3: Data Pipeline Monitoring

```python
# Run as cron job every hour
results = scan_and_analyze(client, "/data/incoming")

# Send alerts if threats found
if results['summary']['quarantined_files'] > 0:
    send_slack_alert(f"⚠️ {results['summary']['quarantined_files']} threats detected!")
```

---

## 🆘 Troubleshooting

### Issue: "Out of quota"

**Solution:** Upgrade your plan or wait for quota reset.

```python
usage = client.get_usage()
if usage.quota_remaining < 100:
    print(f"⚠️ Low quota: {usage.quota_remaining} remaining")
```

### Issue: "Files not found"

**Solution:** Check folder path and permissions.

```python
import os
if not os.path.exists(folder_path):
    print(f"❌ Folder doesn't exist: {folder_path}")
```

### Issue: "Scan taking too long"

**Solution:** Reduce batch size or filter file types.

```python
# Scan only small, relevant files
files = FileScanner.scan_folder(
    folder_path="/data",
    extensions=['.txt'],  # Specific type
    max_file_size_mb=1    # Small files only
)
```

---

## 📚 See Also

- **API Integration Guide**: Complete API reference
- **SDK Documentation**: Full Python SDK docs
- **Best Practices**: Security and performance tips

---

## ✅ Summary

With SentinelDF, you can:

✅ **Scan entire folders** recursively  
✅ **Process thousands of files** in batches  
✅ **Filter by file type** (code, data, logs)  
✅ **Track progress** with callbacks  
✅ **Save results** to JSON  
✅ **Copy clean files** automatically  
✅ **Monitor in real-time** with continuous scanning  

**Start scanning your datasets today!** 🚀
