# 🚀 SentinelDF Cloud - Deployment Guide

Complete guide to deploying the enterprise architecture alongside your existing system.

---

## 📋 Prerequisites

- ✅ Existing `api_server.py` working on Render
- ✅ Render account with payment method
- ✅ AWS account for S3 (or Cloudflare R2)
- ✅ Stripe account for billing (optional initially)

---

## 🎯 Deployment Options

### Option 1: Gradual Migration (Recommended)

Deploy enterprise features alongside existing API, migrate users gradually.

### Option 2: Full Deployment

Deploy complete enterprise stack from day one.

### Option 3: Hybrid

Keep simple API for basic users, enterprise API for power users.

---

## 📦 Phase 1: Database & Cache Setup (Week 1)

### 1.1 Create Render Postgres Database

```bash
# Via Render Dashboard:
# 1. Go to Dashboard → New → PostgreSQL
# 2. Name: sentineldf-db
# 3. Plan: Standard (4GB RAM)
# 4. Region: Oregon (US West)
# 5. Click "Create Database"

# Get connection string from dashboard
# Format: postgresql://user:pass@host:5432/dbname
```

### 1.2 Create Redis Instances

```bash
# Cache Redis (for rate limits, API keys, embeddings)
# 1. Dashboard → New → Redis
# 2. Name: sentineldf-cache
# 3. Plan: Standard (1GB)
# 4. Max Memory Policy: allkeys-lru

# Queue Redis (for Celery job queue)
# 1. Dashboard → New → Redis
# 2. Name: sentineldf-queue
# 3. Plan: Standard (1GB)
# 4. Max Memory Policy: noeviction
```

### 1.3 Initialize Database

```bash
# Clone repo
cd sentineldf

# Install dependencies
pip install -r cloud/config/requirements_cloud.txt

# Set database URL
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Initialize tables
python -c "from cloud.config.database import init_db; init_db()"
```

---

## 🏗️ Phase 2: Deploy Control Plane (Week 2)

### 2.1 Deploy Enterprise API

```bash
# Via Render Dashboard:
# 1. New → Web Service
# 2. Connect your GitHub repo (sentineldf)
# 3. Name: sentineldf-cloud-api
# 4. Build Command: pip install -r cloud/config/requirements_cloud.txt
# 5. Start Command: uvicorn cloud.control_plane.api:app --host 0.0.0.0 --port $PORT --workers 4
# 6. Plan: Standard
# 7. Environment Variables:
```

**Required Environment Variables:**

```bash
DATABASE_URL=<from-postgres-dashboard>
REDIS_URL=<from-redis-dashboard>
ENVIRONMENT=production
LOG_LEVEL=INFO
S3_BUCKET=sentineldf-prod  # Create in AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

### 2.2 Configure Auto-Scaling

```yaml
# In Render dashboard → Service Settings → Scaling:
Min Instances: 2
Max Instances: 50
Target CPU: 70%
Target Memory: 70%
```

### 2.3 Test Control Plane

```bash
# Test health endpoint
curl https://sentineldf-cloud-api.onrender.com/health

# Test upload URL generation
curl -X POST https://sentineldf-cloud-api.onrender.com/v1/uploads \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"file_count": 5}'
```

---

## ⚙️ Phase 3: Deploy Data Plane Workers (Week 3)

### 3.1 Deploy Celery Workers

```bash
# Via Render Dashboard:
# 1. New → Background Worker
# 2. Name: sentineldf-workers
# 3. Build Command: pip install -r cloud/config/requirements_cloud.txt
# 4. Start Command: celery -A cloud.data_plane.worker worker --loglevel=info --concurrency=4
# 5. Plan: Standard
# 6. Environment Variables:
```

**Worker Environment Variables:**

```bash
REDIS_URL=<queue-redis-url>
S3_BUCKET=sentineldf-prod
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
ENVIRONMENT=production
```

### 3.2 Configure Worker Auto-Scaling

```yaml
# Render dashboard → Worker Settings → Scaling:
Min Instances: 5
Max Instances: 500
Scale on Queue Depth: 100 jobs
```

### 3.3 Test Workers

```bash
# Submit test job
curl -X POST https://sentineldf-cloud-api.onrender.com/v1/scan/async \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job_test123",
    "file_ids": ["file1", "file2"],
    "priority": "normal"
  }'

# Check job status
curl https://sentineldf-cloud-api.onrender.com/v1/scan/status/job_test123 \
  -H "Authorization: Bearer sk_live_..."
```

---

## 📊 Phase 4: Monitoring Setup (Week 4)

### 4.1 Enable Prometheus Metrics

```bash
# Metrics endpoint automatically available at:
https://sentineldf-cloud-api.onrender.com/metrics
```

### 4.2 Setup Grafana Dashboard

1. Create Grafana Cloud account (free tier)
2. Add Prometheus data source
3. Import dashboard from `cloud/monitoring/grafana_dashboard.json`

### 4.3 Setup Sentry (Error Tracking)

```bash
# 1. Create Sentry account at sentry.io
# 2. Create new project
# 3. Copy DSN
# 4. Add to Render environment variables:
SENTRY_DSN=https://xxx@sentry.io/yyy
```

---

## 🔄 Phase 5: Migration Strategy

### 5.1 Run Both APIs in Parallel

```
Old API: https://sentineldf.onrender.com (keep running)
New API: https://sentineldf-cloud-api.onrender.com (new users)
```

### 5.2 Gradual User Migration

```bash
# Week 1-2: 10% of users on new API
# Week 3-4: 50% of users on new API
# Week 5-6: 100% of users on new API
# Week 7+: Deprecate old API
```

### 5.3 Update SDK

```python
# Old SDK (still works):
from sentineldf import SentinelDF
client = SentinelDF(api_key="sk_live_...", base_url="https://sentineldf.onrender.com")

# New SDK (enterprise features):
from sentineldf import SentinelDF
client = SentinelDF(api_key="sk_live_...", base_url="https://sentineldf-cloud-api.onrender.com")
```

---

## 💰 Cost Estimates

### Startup Scale (< 1,000 users)

```
Control Plane API (2 instances):    $100/month
Workers (5 instances):               $250/month
Postgres Standard:                   $50/month
Redis (2x Standard):                 $100/month
S3 Storage + Transfer:               $50/month
-------------------------------------------------
Total:                               $550/month
```

### Growth Scale (10,000 users)

```
Control Plane API (5 instances):    $250/month
Workers (20 instances):              $1,000/month
Postgres Standard + Replicas:        $150/month
Redis (2x Standard):                 $100/month
S3 Storage + Transfer:               $200/month
-------------------------------------------------
Total:                               $1,700/month
```

### Enterprise Scale (100,000+ users)

```
Control Plane API (20 instances):   $1,000/month
Workers (100 instances):             $5,000/month
Postgres Pro + Replicas:             $500/month
Redis (2x Pro):                      $400/month
S3 Storage + Transfer:               $1,000/month
-------------------------------------------------
Total:                               $7,900/month
```

---

## 🔐 Security Checklist

- [ ] Enable 2FA on Render account
- [ ] Rotate AWS access keys every 90 days
- [ ] Enable S3 bucket encryption (KMS)
- [ ] Enable Postgres SSL connections
- [ ] Set up IP allowlisting for admin endpoints
- [ ] Enable rate limiting on all public endpoints
- [ ] Set up WAF rules via Cloudflare
- [ ] Regular security audits

---

## 🧪 Testing & Validation

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f cloud/tests/load_test.py \
  --host https://sentineldf-cloud-api.onrender.com \
  --users 1000 \
  --spawn-rate 100
```

### Integration Tests

```bash
# Run full test suite
pytest cloud/tests/ -v --cov=cloud
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue: Workers not processing jobs**
- Check Redis queue connection
- Verify S3 credentials
- Check worker logs in Render dashboard

**Issue: High API latency**
- Check database connection pool
- Verify Redis cache hit rate
- Scale up API instances

**Issue: High costs**
- Enable auto-scaling limits
- Optimize worker concurrency
- Review S3 lifecycle policies

### Getting Help

- 📖 Documentation: `/cloud/README.md`
- 🐛 Report Issues: GitHub Issues
- 💬 Community: Discord
- 📧 Enterprise Support: support@sentineldf.com

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Backup existing database
- [ ] Test in staging environment
- [ ] Review cost estimates
- [ ] Set up monitoring alerts
- [ ] Prepare rollback plan

### Deployment
- [ ] Deploy Postgres database
- [ ] Deploy Redis instances
- [ ] Initialize database schema
- [ ] Deploy Control Plane API
- [ ] Deploy Data Plane workers
- [ ] Configure auto-scaling
- [ ] Set up monitoring
- [ ] Run smoke tests

### Post-Deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify auto-scaling works
- [ ] Update documentation
- [ ] Announce to users
- [ ] Schedule follow-up review

---

## 🎯 Success Metrics

**Week 1:**
- ✅ All services deployed
- ✅ Health checks passing
- ✅ < 10% error rate

**Month 1:**
- ✅ 1,000+ users migrated
- ✅ P99 latency < 500ms
- ✅ 99.5% uptime

**Month 3:**
- ✅ All users migrated
- ✅ P99 latency < 250ms
- ✅ 99.9% uptime
- ✅ Cost per scan < $0.001

---

## 🚀 Next Steps

1. **Review this guide** with your team
2. **Set up staging environment** for testing
3. **Deploy Phase 1** (Database & Cache)
4. **Test thoroughly** before production
5. **Deploy gradually** with monitoring
6. **Iterate and optimize** based on metrics

**Good luck with your deployment!** 🎉
