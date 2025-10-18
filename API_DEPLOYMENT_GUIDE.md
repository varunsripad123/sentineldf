# 🚀 SentinelDF API Deployment Guide

Complete guide to deploying your API-as-a-Service platform like Firecrawl.

---

## 📋 Overview

**What You're Building:**
- ✅ API with key-based authentication
- ✅ Usage tracking & billing
- ✅ Rate limiting per user
- ✅ Developer dashboard
- ✅ Code snippets for customers
- ✅ Stripe integration for payments

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Customer  │────▶│  API Gateway │────▶│  SentinelDF │
│ (API Key)   │     │  (FastAPI)   │     │   Service   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │  (API Keys,  │
                    │   Usage)     │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Stripe    │
                    │  (Billing)   │
                    └──────────────┘
```

---

## ⚙️ Step 1: Install Dependencies

```bash
cd sentineldf
pip install -r requirements_api.txt
```

---

## 🗄️ Step 2: Set Up Database

### Option A: SQLite (Development)

Already configured! Just run:

```bash
python -c "from backend.database import init_db; init_db()"
```

### Option B: PostgreSQL (Production)

1. **Create database:**
```sql
CREATE DATABASE sentineldf_api;
CREATE USER sentineldf WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sentineldf_api TO sentineldf;
```

2. **Update database.py:**
```python
# In backend/database.py, change:
DATABASE_URL = "postgresql://sentineldf:password@localhost/sentineldf_api"
```

3. **Initialize:**
```bash
python -c "from backend.database import init_db; init_db()"
```

---

## 🔑 Step 3: Test API Key System

### Create a Test User

```bash
curl -X POST http://localhost:8000/v1/keys/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "company": "Test Co"
  }'
```

Response:
```json
{
  "user_id": 1,
  "email": "test@example.com",
  "api_key": "sk_live_abc123...",
  "message": "API key created. Save it now!"
}
```

### Test Authenticated Endpoint

```bash
API_KEY="sk_live_abc123..."

curl -X POST http://localhost:8000/v1/scan \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      {"id": "doc_1", "content": "This is a test"}
    ]
  }'
```

### Check Usage

```bash
curl -X GET http://localhost:8000/v1/keys/usage \
  -H "Authorization: Bearer $API_KEY"
```

---

## 💳 Step 4: Integrate Stripe (Billing)

### 1. Create Stripe Account

Sign up at: https://stripe.com

### 2. Get API Keys

Dashboard → Developers → API Keys

### 3. Add Stripe Integration

Create `backend/billing.py`:

```python
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_customer(email: str, name: str) -> str:
    """Create Stripe customer and return customer_id."""
    customer = stripe.Customer.create(
        email=email,
        name=name,
        metadata={'source': 'sentineldf_api'}
    )
    return customer.id

def create_subscription(customer_id: str, price_id: str) -> dict:
    """Create subscription for customer."""
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{'price': price_id}],
    )
    return {
        'subscription_id': subscription.id,
        'status': subscription.status,
        'current_period_end': subscription.current_period_end
    }

def charge_usage(customer_id: str, amount_cents: int, description: str):
    """Charge customer for usage."""
    charge = stripe.Charge.create(
        amount=amount_cents,
        currency="usd",
        customer=customer_id,
        description=description
    )
    return charge
```

### 4. Create Stripe Products

```bash
# Create Pro Plan
stripe products create \
  --name="SentinelDF Pro" \
  --description="50,000 scans/month"

# Create price for Pro Plan ($49/month)
stripe prices create \
  --product=prod_xxx \
  --unit-amount=4900 \
  --currency=usd \
  --recurring[interval]=month
```

### 5. Environment Variables

```bash
# .env
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRO_PRICE_ID=price_xxx
```

---

## 🌐 Step 5: Deploy to Production

### Option A: Deploy on Railway

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login:**
```bash
railway login
```

3. **Create project:**
```bash
railway init
```

4. **Add PostgreSQL:**
```bash
railway add postgres
```

5. **Set environment variables:**
```bash
railway variables set STRIPE_SECRET_KEY=sk_live_xxx
railway variables set DATABASE_URL=postgresql://...
```

6. **Deploy:**
```bash
railway up
```

### Option B: Deploy on Render

1. Create `render.yaml`:

```yaml
services:
  - type: web
    name: sentineldf-api
    env: python
    buildCommand: pip install -r requirements_api.txt
    startCommand: uvicorn backend.app_with_auth:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: sentineldf-db
          property: connectionString
      - key: STRIPE_SECRET_KEY
        sync: false

databases:
  - name: sentineldf-db
    databaseName: sentineldf_api
    user: sentineldf
```

2. **Deploy:**
- Connect your GitHub repo
- Render auto-deploys on push

### Option C: Deploy on AWS (Advanced)

Use AWS ECS + RDS + Load Balancer:

```bash
# Use our Terraform scripts
cd deploy/terraform
terraform init
terraform apply
```

---

## 📊 Step 6: Set Up Monitoring

### Sentry (Error Tracking)

```python
# backend/app_with_auth.py
import sentry_sdk

sentry_sdk.init(
    dsn="your_sentry_dsn",
    traces_sample_rate=1.0,
)
```

### Prometheus (Metrics)

```python
from prometheus_client import Counter, Histogram

api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint', 'status'])
api_latency = Histogram('api_latency_seconds', 'API latency')
```

---

## 🎨 Step 7: Build Developer Dashboard

Create a Next.js dashboard at `/dashboard`:

```typescript
// pages/dashboard.tsx
export default function Dashboard() {
  const [usage, setUsage] = useState(null);
  const apiKey = localStorage.getItem('api_key');

  useEffect(() => {
    fetch('https://api.sentineldf.com/v1/keys/usage', {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    })
    .then(res => res.json())
    .then(setUsage);
  }, []);

  return (
    <div>
      <h1>API Usage</h1>
      <p>Calls this month: {usage?.total_calls}</p>
      <p>Quota remaining: {usage?.quota_remaining}</p>
      <p>Cost: ${usage?.cost_dollars}</p>
    </div>
  );
}
```

---

## 🚀 Step 8: Launch Checklist

### Before Launch:

- [ ] Switch to PostgreSQL (not SQLite)
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure custom domain
- [ ] Set up Stripe webhook endpoints
- [ ] Enable rate limiting
- [ ] Set up monitoring & alerts
- [ ] Create API documentation (use FastAPI /docs)
- [ ] Write Terms of Service & Privacy Policy
- [ ] Set up customer support email
- [ ] Test error handling & edge cases

### After Launch:

- [ ] Monitor error rates
- [ ] Track API usage patterns
- [ ] Gather customer feedback
- [ ] Iterate on pricing
- [ ] Add more endpoints as needed

---

## 💰 Pricing Strategy

### Suggested Tiers:

| Tier | Price | Quota | Target |
|------|-------|-------|--------|
| **Free** | $0 | 1,000 scans/month | Hobbyists, testing |
| **Starter** | $19/mo | 10,000 scans/month | Small teams |
| **Pro** | $99/mo | 100,000 scans/month | Growing companies |
| **Enterprise** | Custom | Unlimited | Large orgs |

**Overage:** $0.001 per scan (after quota)

---

## 📈 Marketing Your API

### 1. Developer-First Landing Page
- Show code snippets immediately
- Interactive API playground
- Clear pricing
- Fast signup (email → API key in 10 seconds)

### 2. Content Marketing
- Write blog posts about LLM security
- Create tutorials on YouTube
- Contribute to open source
- Speak at conferences

### 3. Distribution Channels
- Product Hunt launch
- Hacker News "Show HN"
- Dev.to articles
- Twitter/X for developers
- Reddit (/r/MachineLearning, /r/programming)

### 4. Integrations
- LangChain integration
- LlamaIndex integration
- Hugging Face Datasets integration
- OpenAI plugin

---

## 🔒 Security Best Practices

### 1. API Key Security
- Hash keys in database (never store plaintext)
- Support key rotation
- Allow users to revoke keys instantly
- Audit log for all key usage

### 2. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/scan")
@limiter.limit("60/minute")
async def scan(request: Request, ...):
    pass
```

### 3. Input Validation
- Limit document size (max 1MB per document)
- Limit batch size (max 1000 documents)
- Validate all input fields
- Sanitize error messages (don't leak internal details)

---

## 📞 Support

Questions? Email: varunsripadkota@gmail.com

---

## ✅ Summary

You now have:
1. ✅ API key authentication system
2. ✅ Usage tracking & billing
3. ✅ Rate limiting
4. ✅ Stripe integration ready
5. ✅ Deployment scripts
6. ✅ Code snippets for customers
7. ✅ Monitoring setup

**Next:** Deploy to production and start getting customers! 🚀
