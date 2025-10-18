# 🏗️ SentinelDF Cloud - Enterprise Architecture

## System Overview

SentinelDF Cloud is designed to handle **1M+ users** and **billions of documents** with high throughput, low latency, and cost efficiency.

---

## 🎯 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                          │
│  Python SDK | REST API | Web Dashboard | Mobile Apps                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CDN / API GATEWAY                            │
│  Cloudflare | Rate Limiting | DDoS Protection | SSL/TLS             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      🟦 CONTROL PLANE (Render)                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │   FastAPI API Servers (Auto-scaled 2-50 instances)         │    │
│  │   • /v1/auth         - Authentication & API keys           │    │
│  │   • /v1/uploads      - Pre-signed URL generation           │    │
│  │   • /v1/scan/async   - Submit scan jobs                    │    │
│  │   • /v1/scan/status  - Check job status                    │    │
│  │   • /v1/usage        - Usage stats & billing               │    │
│  │   • /v1/mbom         - MBOM signing & verification         │    │
│  │   • /health          - Health checks                       │    │
│  └─────────┬──────────────────────────────────────────────────┘    │
│            │                                                         │
│  ┌─────────┴──────────┬──────────────┬──────────────────────┐      │
│  │                    │              │                      │      │
│  ▼                    ▼              ▼                      ▼      │
│  Redis Cluster     PostgreSQL    Stripe API         Redis Queue   │
│  • Rate limits     • Users       • Metered          • Job queue   │
│  • API keys cache  • API keys      billing         • Result queue │
│  • Session store   • Usage       • Subscriptions   • Dead letter  │
│  • Token bucket    • Scans       • Webhooks        • Priority     │
│  • Idempotency     • Orgs                                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🟨 DATA PLANE (Render Workers)                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │   Celery Workers (Auto-scaled 5-500 instances)             │    │
│  │   • Pull jobs from Redis queue                             │    │
│  │   • Download files from S3 (pre-signed URLs)               │    │
│  │   • Batch process (up to 256 docs/task)                    │    │
│  │   • Run ONNX INT8 quantized models                         │    │
│  │   • Cache embeddings by SHA256 hash                        │    │
│  │   • Upload results to S3                                   │    │
│  │   • Update status in Redis & Postgres                      │    │
│  └─────────┬──────────────────────────────────────────────────┘    │
│            │                                                         │
│  ┌─────────┴──────────┬──────────────────────────────────────┐     │
│  │                    │                                       │     │
│  ▼                    ▼                                       ▼     │
│  Redis Cache       S3/R2 Storage                    Prometheus     │
│  • Embedding       • Raw uploads                    • Metrics      │
│    cache           • Scan results                   • Worker load  │
│  • Feature cache   • MBOM artifacts                 • Queue depth  │
│  • SHA256 index    • Archived data                  • Latency      │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     🟩 OBSERVABILITY & MONITORING                    │
│  • Sentry (Error tracking & distributed tracing)                    │
│  • Grafana (Dashboards & alerting)                                  │
│  • OpenTelemetry (Trace collection)                                 │
│  • Structured JSON logs (centralized logging)                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Details

### Control Plane (Stateless API Layer)

**Purpose:** Handle user requests, authentication, billing, and job orchestration

**Components:**
- **FastAPI Servers** (Render Web Services)
  - Horizontally scalable (2-50 instances)
  - Stateless design (no local storage)
  - Rate limiting via Redis token bucket
  - Idempotency keys for duplicate prevention
  
- **PostgreSQL** (Render Managed Database)
  - User accounts & organizations
  - API key storage (bcrypt hashed)
  - Usage counters (partitioned by org + date)
  - Scan metadata & status
  - Billing records
  
- **Redis Cluster** (Render Redis or Upstash)
  - Rate limiting (token bucket algorithm)
  - API key cache (hot keys)
  - Session storage
  - Job queue (Celery broker)
  - Result queue
  - Idempotency tracking

**Scaling Strategy:**
- Auto-scale based on CPU (>70%) and request queue depth
- Multi-region deployment (US-East, US-West, EU, Asia)
- Read replicas for Postgres
- Redis sharding by key prefix

---

### Data Plane (Distributed Workers)

**Purpose:** Execute ML inference at scale with high throughput and low cost

**Components:**
- **Celery Workers** (Render Background Workers)
  - Pull jobs from Redis queue
  - Batch processing (up to 256 documents)
  - ONNX Runtime inference (quantized INT8 models)
  - SHA256-based caching (skip duplicate embeddings)
  - Result upload to S3
  
- **S3/R2 Storage** (AWS S3 or Cloudflare R2)
  - Raw file uploads (tenant-isolated prefixes)
  - Scan results (JSON artifacts)
  - MBOM signatures
  - Lifecycle policies (archive after 90 days)
  
- **Redis Cache** (Separate from control plane)
  - Embedding cache (SHA256 → vector)
  - Feature cache (heuristic results)
  - Deduplication index

**Scaling Strategy:**
- Auto-scale workers based on queue depth (>1000 jobs → +10 workers)
- Horizontal scaling (5-500 workers)
- Priority queues (premium users get faster processing)
- Region-specific workers (data locality)

---

## 📊 Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| **API P99 Latency** | < 250ms | Caching, CDN, connection pooling |
| **Worker Throughput** | 1000+ docs/min per 4-vCPU pod | ONNX INT8, batching, Rust tokenizers |
| **Daily Scan Capacity** | > 50M short docs/day | Horizontal scaling, multi-region |
| **Cold Start Time** | < 5s | Pre-warmed workers, model caching |
| **Cache Hit Rate** | > 80% | SHA256 deduplication |
| **Database Query Time** | < 50ms P99 | Indexes, partitioning, read replicas |

---

## 🔐 Security Architecture

### Data Encryption
- **At Rest:** AES-256 encryption for S3 (KMS managed)
- **In Transit:** TLS 1.3 for all API calls
- **API Keys:** Bcrypt hashed with salt (cost factor 12)

### Tenant Isolation
- **S3 Prefixes:** `s3://sentineldf-prod/{org_id}/{scan_id}/`
- **Database:** Row-level security (org_id filtering)
- **Redis:** Namespace isolation per org

### Access Control
- **Pre-signed URLs:** Time-limited (15 min) upload/download URLs
- **IAM Roles:** Least privilege for workers
- **API Key Scopes:** Granular permissions per key

---

## 💰 Cost Optimization

### Compute
- **Workers:** Spot instances for non-critical workloads (70% savings)
- **ONNX INT8:** 3-4× faster inference on CPU (no GPU needed)
- **Auto-scaling:** Scale down during low traffic (nights/weekends)

### Storage
- **Lifecycle Policies:** Archive to Glacier after 90 days
- **Compression:** gzip JSON artifacts (70% size reduction)
- **CDN Caching:** Reduce origin requests by 80%

### Database
- **Connection Pooling:** Reduce DB connections (max 100 per API server)
- **Partitioning:** Faster queries, easier archival
- **Read Replicas:** Offload analytics queries

**Estimated Costs (1M users, 10M scans/day):**
- Compute: $2,000/month (workers + API servers)
- Storage: $500/month (S3 + Redis + Postgres)
- Data Transfer: $300/month
- **Total: ~$2,800/month** (at scale)

---

## 🚀 Deployment Strategy

### Phase 1: Foundation (Week 1-2)
- ✅ Split control plane and data plane
- ✅ Migrate to managed Postgres + Redis
- ✅ Implement pre-signed S3 uploads
- ✅ Deploy Celery workers

### Phase 2: Optimization (Week 3-4)
- ✅ Convert models to ONNX INT8
- ✅ Add SHA256 caching layer
- ✅ Implement batch processing
- ✅ Add Rust tokenizers

### Phase 3: Scale & Monitor (Week 5-6)
- ✅ Multi-region deployment
- ✅ Prometheus + Grafana dashboards
- ✅ Sentry integration
- ✅ Auto-scaling configuration

### Phase 4: Production Hardening (Week 7-8)
- ✅ Stripe metered billing
- ✅ Rate limiting + quotas
- ✅ Security audit
- ✅ Load testing (simulate 1M users)

---

## 📈 Monitoring & Alerting

### Key Metrics (Prometheus)
- `sentineldf_api_requests_total` - Total API requests (by endpoint, status)
- `sentineldf_api_latency_seconds` - Request latency histogram
- `sentineldf_job_queue_depth` - Number of pending jobs
- `sentineldf_worker_active_tasks` - Active workers
- `sentineldf_cache_hit_rate` - Cache effectiveness
- `sentineldf_db_query_duration_seconds` - Database performance

### Alerts
- **Critical:** P99 latency > 1s, queue depth > 10,000
- **Warning:** Cache hit rate < 60%, worker utilization > 90%
- **Info:** New region deployed, auto-scale triggered

### Structured Logging
```json
{
  "timestamp": "2025-10-18T12:00:00Z",
  "level": "INFO",
  "trace_id": "abc123",
  "span_id": "xyz789",
  "service": "control-plane-api",
  "endpoint": "/v1/scan/async",
  "user_id": "user_123",
  "org_id": "org_456",
  "latency_ms": 45,
  "status_code": 200
}
```

---

## 🔄 Data Flow Example

### Async Scan Request Flow

1. **Client → API:** POST `/v1/scan/async` with file list
2. **API → S3:** Generate pre-signed upload URLs
3. **API → Client:** Return upload URLs + job_id
4. **Client → S3:** Upload files directly (bypasses API)
5. **Client → API:** POST `/v1/scan/async/confirm?job_id=xxx`
6. **API → Redis:** Enqueue scan job
7. **Worker → Redis:** Pull job from queue
8. **Worker → S3:** Download files (pre-signed URL)
9. **Worker → ML:** Run ONNX inference (batch)
10. **Worker → Redis Cache:** Store embeddings (SHA256 key)
11. **Worker → S3:** Upload results JSON
12. **Worker → Postgres:** Update scan status
13. **Client → API:** GET `/v1/scan/status?job_id=xxx`
14. **API → Client:** Return status + result URL
15. **Client → S3:** Download results (pre-signed URL)

---

## 🏁 Success Criteria

- ✅ Support 1M+ concurrent users
- ✅ Process 50M+ documents/day
- ✅ P99 API latency < 250ms
- ✅ 99.9% uptime SLA
- ✅ Auto-scale from 5 to 500 workers
- ✅ Cost < $0.0001 per document scanned
- ✅ SOC 2 Type II compliance ready
