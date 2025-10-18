# 📂 How Customers Upload & Analyze Multiple Files/Folders

## 🎯 The Simple Answer

Customers have **3 easy options** to scan multiple files/folders:

### **Option 1: Use Python SDK (Easiest)** ⭐

```python
from sentineldf import SentinelDF, scan_and_analyze

client = SentinelDF(api_key="sk_live_your_key")

# Scan entire folder in one line
results = scan_and_analyze(
    client=client,
    folder_path="/path/to/training_data"
)

print(f"Safe files: {results['summary']['safe_files']}")
print(f"Threats: {results['summary']['quarantined_files']}")
```

**Done!** The SDK handles everything:
- Reads all files from folder
- Batches them automatically
- Sends to your API
- Returns results

---

### **Option 2: Manual File Upload via API**

For customers not using Python:

```bash
# They zip their files
zip -r mydata.zip ./training_data/

# Upload to your API (you need to add this endpoint)
curl -X POST https://api.sentineldf.com/v1/upload \
  -H "Authorization: Bearer sk_live_your_key" \
  -F "file=@mydata.zip"

# Get results
{
  "scan_id": "scan_abc123",
  "status": "processing",
  "results_url": "/v1/scans/scan_abc123"
}
```

---

### **Option 3: Web Dashboard** (Future)

Build a web interface where customers can:
1. Drag & drop folders
2. Click "Scan"
3. View results in browser
4. Download clean dataset

---

## 🏗️ How It Works End-to-End

```
┌─────────────────────────────────────────────────────────────┐
│  CUSTOMER'S COMPUTER                                        │
│                                                             │
│  /training_data/                                            │
│  ├── file1.txt    ← "Normal text about cats"              │
│  ├── file2.txt    ← "Ignore previous instructions!"       │
│  └── file3.txt    ← "More training data..."               │
│                                                             │
│  Customer runs:                                             │
│  python scan_folder.py                                      │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ SDK reads files locally
                     │ Creates batches of 100 files
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  YOUR API (sentineldf.com)                                  │
│                                                             │
│  POST /v1/scan                                              │
│  Authorization: Bearer sk_live_abc123                       │
│  {                                                          │
│    "docs": [                                                │
│      {"id": "file1.txt", "content": "Normal text..."},     │
│      {"id": "file2.txt", "content": "Ignore previous..."},  │
│      {"id": "file3.txt", "content": "More training..."}     │
│    ]                                                        │
│  }                                                          │
│                                                             │
│  1. Validates API key ✅                                   │
│  2. Checks quota ✅                                        │
│  3. Scans each document                                     │
│  4. Returns results                                         │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Returns JSON response
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  CUSTOMER RECEIVES RESULTS                                  │
│                                                             │
│  {                                                          │
│    "results": [                                             │
│      {"doc_id": "file1.txt", "quarantine": false},         │
│      {"doc_id": "file2.txt", "quarantine": true,           │
│       "reasons": ["Prompt injection detected"]},           │
│      {"doc_id": "file3.txt", "quarantine": false}          │
│    ],                                                       │
│    "summary": {                                             │
│      "total_files": 3,                                      │
│      "safe_files": 2,                                       │
│      "quarantined_files": 1                                 │
│    }                                                        │
│  }                                                          │
│                                                             │
│  Customer can now:                                          │
│  - Delete file2.txt (threat)                                │
│  - Use file1.txt and file3.txt for training ✅             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Real Customer Workflow

### **Scenario: AI Company Training an LLM**

**Step 1:** Download dataset from internet (10,000 files)
```bash
wget https://example.com/training_data.zip
unzip training_data.zip
# Now they have /training_data/ folder
```

**Step 2:** Install SentinelDF SDK
```bash
pip install sentineldf
```

**Step 3:** Run scan script
```python
# scan.py
from sentineldf import SentinelDF, scan_and_analyze

client = SentinelDF(api_key="sk_live_abc123...")

results = scan_and_analyze(
    client=client,
    folder_path="./training_data",
    batch_size=100
)

print(f"Original: 10,000 files")
print(f"Clean: {results['summary']['safe_files']} files")
print(f"Removed: {results['summary']['quarantined_files']} threats")
```

**Step 4:** Copy only safe files to training folder
```python
import shutil
from pathlib import Path

clean_folder = Path("./clean_training_data")
clean_folder.mkdir(exist_ok=True)

for result in results['results']:
    if not result.quarantine:
        src = Path("./training_data") / result.doc_id
        dst = clean_folder / result.doc_id
        shutil.copy2(src, dst)

print("✅ Clean dataset ready for training!")
```

**Step 5:** Train their model on clean data
```bash
# Only clean files, no poisoned data!
python train_llm.py --data ./clean_training_data
```

---

## 🎨 File Processing Options

### **Option A: SDK Handles Everything** (Recommended)

```python
# Customer doesn't send files to you
# SDK reads files locally and sends content via API
results = scan_and_analyze(client, folder_path="/data")
```

**Pros:**
- ✅ No file upload infrastructure needed
- ✅ Customer files stay on their computer (privacy)
- ✅ Automatic batching
- ✅ Works for any file size

**Cons:**
- ❌ Requires Python

---

### **Option B: File Upload Endpoint** (For non-Python users)

Create endpoint where customers upload files:

```python
# backend/app_with_auth.py

@app.post("/v1/upload")
async def upload_files(
    files: List[UploadFile],
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Upload and scan multiple files."""
    user, api_key = auth
    
    results = []
    for file in files:
        content = await file.read()
        text = content.decode('utf-8')
        
        # Scan content
        scan_result = scan_document(text)
        results.append(scan_result)
    
    return {"results": results}
```

Customers use:
```bash
curl -X POST https://api.sentineldf.com/v1/upload \
  -H "Authorization: Bearer sk_live_your_key" \
  -F "files=@file1.txt" \
  -F "files=@file2.txt" \
  -F "files=@file3.txt"
```

**Pros:**
- ✅ Works from any language/tool
- ✅ Can use from web browser

**Cons:**
- ❌ You need file storage
- ❌ Upload limits
- ❌ Privacy concerns (files leave customer's computer)

---

### **Option C: Web Dashboard** (Best UX)

Build a React/Next.js dashboard:

```typescript
// components/FileUploader.tsx
function FileUploader() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState(null);
  
  const handleUpload = async () => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`
      },
      body: formData
    });
    
    const data = await response.json();
    setResults(data);
  };
  
  return (
    <div>
      <input type="file" multiple onChange={e => setFiles([...e.target.files])} />
      <button onClick={handleUpload}>Scan Files</button>
      
      {results && (
        <div>
          <p>Safe: {results.safe_files}</p>
          <p>Threats: {results.quarantined_files}</p>
        </div>
      )}
    </div>
  );
}
```

**Pros:**
- ✅ Best user experience
- ✅ Visual interface
- ✅ No coding required

**Cons:**
- ❌ More work to build
- ❌ File upload infrastructure

---

## 💰 Pricing for Bulk Scans

### **Example: Customer scans 10,000 files**

**Free tier:** 1,000 files/month
- First 1,000 files: **$0**
- Remaining 9,000 files: 9,000 × $0.01 = **$90**
- **Total: $90**

**Pro tier:** $49/month for 50,000 files
- All 10,000 files included
- **Total: $49/month**

**Enterprise tier:** Custom pricing for unlimited

---

## 🚀 Quick Start for Customers

### **For Python Users:**

```bash
# 1. Install SDK
pip install sentineldf

# 2. Set API key
export SENTINELDF_API_KEY="sk_live_your_key"

# 3. Scan folder
python -c "
from sentineldf import SentinelDF, scan_and_analyze
client = SentinelDF(api_key='sk_live_your_key')
results = scan_and_analyze(client, './data')
print(f'Quarantined: {results[\"summary\"][\"quarantined_files\"]}')
"
```

### **For Other Languages:**

Use the REST API directly:

```bash
# Read files locally
FILES=$(find ./data -type f -name "*.txt")

# Send to API in batches
for FILE in $FILES; do
  CONTENT=$(cat "$FILE")
  curl -X POST https://api.sentineldf.com/v1/scan \
    -H "Authorization: Bearer sk_live_your_key" \
    -d "{\"docs\":[{\"id\":\"$FILE\",\"content\":\"$CONTENT\"}]}"
done
```

---

## ✅ Summary

**How customers scan multiple files/folders:**

1. **Option 1 (Easiest):** Use Python SDK
   - One line: `scan_and_analyze(client, folder_path)`
   - SDK handles file reading and batching

2. **Option 2:** Upload files to your API
   - You need to build upload endpoint
   - Works from any language

3. **Option 3:** Use web dashboard
   - Drag & drop interface
   - Best UX but more work to build

**Recommended approach:** Start with **Python SDK** (Option 1)
- Easiest to implement
- No file upload infrastructure needed
- Works immediately

---

**Files created for you:**
- ✅ `sdk/sentineldf/file_utils.py` - File scanning utilities
- ✅ `examples/scan_folder_example.py` - Working example
- ✅ `BULK_FILE_SCANNING_GUIDE.md` - Complete guide

**Customers can start scanning folders right now!** 🎉
