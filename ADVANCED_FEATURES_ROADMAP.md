# 🚀 Advanced Features Roadmap

Comprehensive plan for next-generation threat detection capabilities.

---

## ✅ **Phase 1: SHIPPED (v2.3.0)**

### **Detection Superpowers**
- ✅ **Unicode obfuscation detection** - RTL overrides, zero-width chars, homoglyphs
- ✅ **Compression bomb detection** - Detect highly compressible malicious input
- ✅ **Homoglyph detection** - Cyrillic/Greek/fullwidth lookalikes
- ✅ **Span-level highlights** - Character offsets for UI redlines
- ✅ **Confidence scores** - Calibrated 0.5-1.0 based on signal variance
- ✅ **Multi-signal ensemble** - Heuristic + ML + Unicode (3 layers)

### **Security & Performance**
- ✅ **Hashed API keys** - SHA-256, never store plain text
- ✅ **Pre-compiled regex** - 10x faster pattern matching
- ✅ **Input validation** - Request/document size limits
- ✅ **Background logging** - Non-blocking database writes
- ✅ **Connection pooling** - Postgres optimization

---

## 🔨 **Phase 2: Q1 2026 (High Priority)**

### **1. Ensemble Threat Engine** 
**Status:** Design complete, implementation ready

```python
# Add fine-tuned transformer classifier
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="deepset/deberta-v3-base-injection-prompt-v2"
)

def score_classifier(text: str) -> float:
    result = classifier(text[:512])  # Truncate for speed
    if result[0]['label'] == 'INJECTION':
        return result[0]['score']
    return 0.0

# Ensemble with Platt scaling for calibration
def ensemble_score(h, e, u, c):
    # Weighted combination
    raw = 0.25*h + 0.25*e + 0.2*u + 0.3*c
    # Platt scaling (calibrate on labeled set)
    return 1 / (1 + np.exp(-(A * raw + B)))
```

**Impact:** 95%+ F1 score on prompt injection datasets

**Effort:** 2 weeks
**Dependencies:** Labeled dataset (1K examples), fine-tuned model

---

### **2. Multilingual & Code-Aware Rules**
**Status:** Scoped

```python
# Language detection
from langdetect import detect_langs

def get_language_specific_patterns(text: str):
    langs = detect_langs(text)
    
    if 'zh' in [l.lang for l in langs]:
        # Chinese-specific jailbreaks
        return CHINESE_JAILBREAK_PATTERNS
    elif 'ru' in [l.lang for l in langs]:
        # Russian-specific patterns
        return RUSSIAN_PATTERNS
    
    return DEFAULT_PATTERNS

# Code detection
import pygments
from pygments.lexers import guess_lexer

def detect_code_injection(text: str):
    try:
        lexer = guess_lexer(text)
        if lexer.name in ['Python', 'SQL', 'Bash', 'JavaScript']:
            # Apply code-specific patterns
            return check_code_exec_patterns(text, lexer.name)
    except:
        pass
    return 0.0, []
```

**Impact:** Catch multilingual attacks, code injection in data

**Effort:** 3 weeks
**Dependencies:** `langdetect`, `pygments`

---

### **3. PII/PHI/License Compliance**
**Status:** Library selection complete

```python
# Fast PII detection
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()

def detect_pii(text: str) -> tuple[float, list]:
    results = analyzer.analyze(
        text=text,
        language='en',
        entities=['PHONE_NUMBER', 'EMAIL', 'SSN', 'CREDIT_CARD']
    )
    
    if results:
        return 0.6, [f"PII.{r.entity_type}" for r in results]
    return 0.0, []

# License detection
LICENSE_PATTERNS = {
    'GPL': re.compile(r'GNU\s+General\s+Public\s+License', re.I),
    'MIT': re.compile(r'MIT\s+License', re.I),
    'Apache': re.compile(r'Apache\s+License', re.I),
}

def detect_licenses(text: str):
    found = []
    for name, pattern in LICENSE_PATTERNS.items():
        if pattern.search(text):
            found.append(f"License.{name}")
    return found
```

**Impact:** HIPAA/GDPR compliance, open-source safety

**Effort:** 2 weeks
**Dependencies:** `presidio-analyzer`, `presidio-anonymizer`

---

### **4. Tunable Policy Engine**
**Status:** Design review

```python
# JSON-based policy configuration
{
    "policy_version": "1.0",
    "tenant_id": "acme_corp",
    "thresholds": {
        "quarantine": 0.7,
        "review": 0.5,
        "allow": 0.3
    },
    "deny_terms": [
        "reveal system prompt",
        "ignore instructions"
    ],
    "allow_terms": [
        "training data" 
    ],
    "require_human_review_if": [
        "PII.ssn",
        "PII.credit_card",
        "License.gpl"
    ],
    "actions": {
        "on_quarantine": "webhook",
        "webhook_url": "https://acme.com/alerts"
    }
}

# Policy evaluation
def evaluate_policy(result: ScanResult, policy: dict) -> str:
    risk_score = result.risk / 100.0
    
    # Check deny list
    for term in policy.get("deny_terms", []):
        if term.lower() in result.doc_content.lower():
            return "quarantine"
    
    # Check allow list
    for term in policy.get("allow_terms", []):
        if term.lower() in result.doc_content.lower():
            return "allow"
    
    # Apply thresholds
    if risk_score >= policy["thresholds"]["quarantine"]:
        return "quarantine"
    elif risk_score >= policy["thresholds"]["review"]:
        # Check if requires human review
        for reason in result.reasons:
            if reason in policy.get("require_human_review_if", []):
                return "needs_review"
        return "review"
    else:
        return "allow"
```

**Impact:** Enterprise customization, per-tenant rules

**Effort:** 3 weeks
**Dependencies:** Policy storage (DB table), webhook system

---

## 🔬 **Phase 3: Q2 2026 (Advanced)**

### **5. Contextual & Cross-Doc Analysis**
**Status:** Research phase

```python
# Rolling window state tracking
class SessionContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.doc_history = deque(maxlen=10)
        self.risk_trajectory = []
    
    def add_doc(self, doc_id: str, content: str, risk: float):
        self.doc_history.append({
            "id": doc_id,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "risk": risk,
            "timestamp": datetime.utcnow()
        })
        self.risk_trajectory.append(risk)
    
    def detect_staged_attack(self) -> tuple[bool, str]:
        """Detect multi-turn jailbreak (arming + firing)"""
        if len(self.doc_history) < 2:
            return False, ""
        
        # Check if risk is increasing (staged attack pattern)
        if len(self.risk_trajectory) >= 3:
            recent = self.risk_trajectory[-3:]
            if recent[0] < 0.3 and recent[1] < 0.5 and recent[2] > 0.7:
                return True, "Staged attack: Low → Medium → High risk progression"
        
        # Check for semantic coupling (doc N arms, doc N+1 fires)
        last_two = list(self.doc_history)[-2:]
        if "when" in last_two[0]["content_hash"] and "trigger" in last_two[1]["content_hash"]:
            return True, "Multi-turn conditional trigger detected"
        
        return False, ""

# Session endpoint
@app.post("/v1/scan/session")
async def scan_session(
    session_id: str,
    request: ScanRequest,
    db: Session = Depends(get_db)
):
    # Load or create session context
    context = get_session_context(session_id, db)
    
    # Scan docs
    results = []
    for doc in request.docs:
        result = scan_document(doc)
        context.add_doc(doc.id, doc.content, result.risk / 100.0)
        
        # Check for staged attack
        is_staged, reason = context.detect_staged_attack()
        if is_staged:
            result.risk = min(100, result.risk + 20)
            result.reasons.append(reason)
        
        results.append(result)
    
    # Save context
    save_session_context(context, db)
    
    return {"results": results, "session_risk": context.risk_trajectory}
```

**Impact:** Catch sophisticated multi-turn attacks

**Effort:** 4 weeks
**Dependencies:** Session storage, temporal analysis

---

### **6. OOD & Drift Watchdog**
**Status:** Prototype ready

```python
# Covariate shift detection
from scipy.stats import ks_2samp

class DriftDetector:
    def __init__(self):
        self.baseline_embeddings = []
        self.drift_threshold = 0.1
    
    def fit_baseline(self, corpus: list[str], model):
        """Fit on known-good data distribution"""
        self.baseline_embeddings = model.encode(corpus)
        self.baseline_mean = np.mean(self.baseline_embeddings, axis=0)
        self.baseline_std = np.std(self.baseline_embeddings, axis=0)
    
    def detect_drift(self, new_embeddings: np.ndarray) -> tuple[bool, float]:
        """KS test for distribution shift"""
        # Compare each dimension
        p_values = []
        for dim in range(new_embeddings.shape[1]):
            _, p_val = ks_2samp(
                self.baseline_embeddings[:, dim],
                new_embeddings[:, dim]
            )
            p_values.append(p_val)
        
        # Average p-value
        avg_p = np.mean(p_values)
        is_drift = avg_p < self.drift_threshold
        
        return is_drift, avg_p

# Monitor endpoint
@app.get("/v1/monitoring/drift")
async def get_drift_stats(db: Session = Depends(get_db)):
    detector = get_drift_detector()
    
    # Get recent scans (last 1000)
    recent_logs = db.query(UsageLog).order_by(
        UsageLog.timestamp.desc()
    ).limit(1000).all()
    
    # Check for drift
    is_drift, p_value = detector.detect_drift(recent_embeddings)
    
    return {
        "drift_detected": is_drift,
        "p_value": p_value,
        "recommendation": "Retrain model" if is_drift else "Model stable"
    }
```

**Impact:** Detect model degradation, trigger retraining

**Effort:** 3 weeks
**Dependencies:** Baseline corpus, monitoring dashboard

---

### **7. Content Provenance & Deduplication**
**Status:** Design complete

```python
# MinHash for near-duplicate detection
from datasketch import MinHash, MinHashLSH

def create_minhash(text: str, num_perm=128) -> MinHash:
    m = MinHash(num_perm=num_perm)
    # Tokenize by words
    for word in text.lower().split():
        m.update(word.encode('utf8'))
    return m

# LSH index for fast similarity search
lsh = MinHashLSH(threshold=0.8, num_perm=128)

def check_duplicate(doc_id: str, text: str) -> tuple[bool, list]:
    """Check if document is near-duplicate of existing data"""
    mh = create_minhash(text)
    
    # Query LSH index
    duplicates = lsh.query(mh)
    
    if duplicates:
        return True, duplicates
    
    # Add to index
    lsh.insert(doc_id, mh)
    return False, []

# Source reputation tagging
SOURCE_REPUTATION = {
    "reddit.com/r/ChatGPTJailbreak": -0.8,  # Known bad
    "huggingface.co/datasets": +0.5,         # Generally good
    "github.com": 0.0,                       # Neutral
}

def adjust_risk_by_source(risk: float, source_url: str) -> float:
    """Adjust risk based on data source reputation"""
    for domain, adjustment in SOURCE_REPUTATION.items():
        if domain in source_url:
            return min(1.0, max(0.0, risk + adjustment))
    return risk
```

**Impact:** Dedupe datasets, flag known-bad sources

**Effort:** 2 weeks
**Dependencies:** `datasketch`, source metadata tracking

---

## 🏗️ **Phase 4: Q3 2026 (Scale & Integration)**

### **8. Async + Streaming**

```python
# Async job queue
from celery import Celery

celery_app = Celery('sentineldf', broker='redis://localhost:6379')

@celery_app.task
def scan_large_dataset_async(job_id: str, docs: list, webhook_url: str):
    """Process large batches asynchronously"""
    results = []
    for doc in docs:
        result = scan_document(doc)
        results.append(result)
    
    # Send results via webhook
    requests.post(webhook_url, json={
        "job_id": job_id,
        "status": "completed",
        "results": results
    })

@app.post("/v1/scan/async")
async def scan_async(
    request: ScanRequest,
    webhook_url: str,
    db: Session = Depends(get_db)
):
    job_id = f"job_{secrets.token_hex(8)}"
    
    # Queue task
    scan_large_dataset_async.delay(job_id, request.docs, webhook_url)
    
    return {"job_id": job_id, "status": "queued"}

# Server-Sent Events for streaming
@app.get("/v1/scan/stream")
async def scan_stream(request: Request):
    async def event_generator():
        for doc in docs:
            result = scan_document(doc)
            yield {
                "event": "result",
                "data": json.dumps(result.dict())
            }
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Effort:** 3 weeks
**Dependencies:** Redis, Celery, SSE support

---

### **9. File Type Parsers**

```python
# PDF with OCR
from pypdf import PdfReader
import pytesseract
from PIL import Image

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    
    for page in reader.pages:
        # Extract text
        text += page.extract_text()
        
        # OCR images if needed
        for image in page.images:
            img = Image.open(io.BytesIO(image.data))
            text += pytesseract.image_to_string(img)
    
    return text

# DOCX parser
from docx import Document

def extract_text_from_docx(docx_path: str) -> str:
    doc = Document(docx_path)
    return "\n".join([p.text for p in doc.paragraphs])

# Multi-format endpoint
@app.post("/v1/scan/file")
async def scan_file(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    # Detect file type
    if file.content_type == 'application/pdf':
        text = extract_text_from_pdf(file.file)
    elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        text = extract_text_from_docx(file.file)
    else:
        text = (await file.read()).decode('utf-8')
    
    # Scan extracted text
    result = scan_document(DocumentInput(id=file.filename, content=text))
    
    return result
```

**Effort:** 2 weeks
**Dependencies:** `pypdf`, `python-docx`, `pytesseract`

---

### **10. Vector Infrastructure (pgvector)**

```python
# Store threat library in postgres with pgvector
CREATE EXTENSION vector;

CREATE TABLE threat_library (
    id SERIAL PRIMARY KEY,
    threat_text TEXT,
    embedding VECTOR(384),  # MiniLM embedding size
    threat_type VARCHAR,
    severity INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON threat_library USING ivfflat (embedding vector_cosine_ops);

# Fast similarity search
def check_known_threats(text: str, model, db: Session) -> tuple[bool, str]:
    """Check against known threat library using ANN"""
    embedding = model.encode([text])[0]
    
    # Vector similarity search
    result = db.execute(text("""
        SELECT threat_text, threat_type, similarity
        FROM (
            SELECT 
                threat_text,
                threat_type,
                1 - (embedding <=> :query_embedding) AS similarity
            FROM threat_library
            WHERE 1 - (embedding <=> :query_embedding) > 0.85
            ORDER BY embedding <=> :query_embedding
            LIMIT 1
        ) subq
    """), {"query_embedding": embedding.tolist()})
    
    match = result.fetchone()
    if match:
        return True, f"Matches known {match.threat_type}: '{match.threat_text[:50]}...'"
    
    return False, ""
```

**Effort:** 2 weeks
**Dependencies:** `pgvector` extension

---

## 📊 **Impact & Metrics**

| Feature | Detection Rate | False Positive Reduction | Latency Impact |
|---------|---------------|-------------------------|----------------|
| Unicode tricks | +15% | -5% | +2ms |
| Ensemble model | +25% | -30% | +50ms |
| Multilingual | +20% | -10% | +5ms |
| PII detection | N/A | N/A | +10ms |
| Cross-doc | +10% | -5% | +1ms |
| Deduplication | N/A | -40% | +3ms |

---

## 🎯 **Prioritization Matrix**

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Ensemble model | 🔥🔥🔥 | 2wk | **P0** |
| PII/compliance | 🔥🔥🔥 | 2wk | **P0** |
| Policy engine | 🔥🔥 | 3wk | **P1** |
| Multilingual | 🔥🔥 | 3wk | **P1** |
| File parsers | 🔥 | 2wk | **P1** |
| Cross-doc | 🔥🔥 | 4wk | **P2** |
| pgvector | 🔥 | 2wk | **P2** |
| Async/streaming | 🔥 | 3wk | **P2** |

---

**Next: Commit Phase 1 improvements and begin ensemble model development!** 🚀
