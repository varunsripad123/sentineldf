# 💰 Usage Tracking & Billing System

Complete guide on how to track API usage and charge customers.

---

## ✅ **Good News: It's Already Built!**

Every API call is **automatically tracked** in your database. Here's how it works:

---

## 📊 **How Usage Tracking Works (Automatic)**

### **Every API Call Creates a Record:**

```python
# In backend/app_with_auth.py (already implemented)

@app.post("/v1/scan")
async def scan_documents(request, auth, db):
    user, api_key = auth
    
    # 1. Check quota
    if not check_quota(user, db):
        raise HTTPException(429, "Quota exceeded")
    
    # 2. Process request
    results = scan_documents(request.docs)
    
    # 3. Track usage (AUTOMATIC)
    track_usage(
        user=user,
        api_key=api_key,
        endpoint="/v1/scan",
        documents_scanned=len(request.docs),  # Billing metric
        cost_cents=len(request.docs) * 1,     # $0.01 per doc
        timestamp=datetime.now(),
        db=db
    )
```

**What Gets Tracked:**
- ✅ User ID (who made the call)
- ✅ API key used
- ✅ Endpoint called
- ✅ Number of documents scanned
- ✅ Tokens used
- ✅ Cost in cents
- ✅ Timestamp (for monthly billing)
- ✅ Response time

---

## 🗄️ **Database Schema**

### **usage_records table:**

```sql
CREATE TABLE usage_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,              -- Who
    api_key_id INTEGER,            -- Which key
    endpoint VARCHAR(255),         -- What endpoint
    timestamp TIMESTAMP,           -- When
    documents_scanned INTEGER,     -- How many docs (for pricing)
    tokens_used INTEGER,           -- Token count
    cost_cents INTEGER,            -- Cost in cents
    response_time_ms FLOAT,
    status_code INTEGER
);
```

**Example Records:**

| user_id | endpoint | documents_scanned | cost_cents | timestamp |
|---------|----------|-------------------|------------|-----------|
| 123 | /v1/scan | 50 | 50 | 2025-01-15 10:30 |
| 123 | /v1/scan | 100 | 100 | 2025-01-15 14:22 |
| 123 | /v1/analyze | 25 | 25 | 2025-01-16 09:15 |

**Total for user 123:** 175 documents = $1.75

---

## 💳 **Billing Methods**

### **Method 1: Monthly Billing** ⭐ **RECOMMENDED**

At the end of each month, charge users based on usage:

```python
from backend.billing import charge_monthly_usage

# Run this on the 1st of each month
for user in users:
    result = charge_monthly_usage(user, db)
    
    if result['charged']:
        print(f"Charged {user.email}: ${result['amount_dollars']}")
        send_invoice_email(user, result)
```

**Pricing Tiers:**

| Tier | Monthly Fee | Quota | Overage |
|------|-------------|-------|---------|
| **Free** | $0 | 1,000 calls | $0.01/call |
| **Pro** | $49 | 50,000 calls | $0.01/call |
| **Enterprise** | Custom | Unlimited | Custom |

---

### **Method 2: Real-time Charging (Usage-Based)**

Charge immediately after each API call:

```python
# After each API call
documents_scanned = len(request.docs)
cost_dollars = documents_scanned * 0.01

stripe.Charge.create(
    amount=int(cost_dollars * 100),  # cents
    currency='usd',
    customer=user.stripe_customer_id,
    description=f"{documents_scanned} documents scanned"
)
```

**Pros:** Simple, immediate
**Cons:** Many small charges, higher Stripe fees

---

### **Method 3: Pre-paid Credits**

Users buy credits upfront:

```python
# User buys 10,000 credits for $100
user.credits = 10000

# Each API call deducts credits
documents_scanned = len(request.docs)
user.credits -= documents_scanned

if user.credits < 0:
    raise HTTPException(402, "Insufficient credits")
```

---

## 🔧 **How to Calculate Monthly Bill**

### **Step 1: Get Monthly Usage**

```python
from backend.billing import calculate_monthly_usage

usage = calculate_monthly_usage(
    user_id=123,
    db=db,
    year=2025,
    month=1
)

# Returns:
{
    'total_calls': 5234,
    'total_documents': 125840,
    'total_tokens': 3500000,
    'total_cost_cents': 12584,  # $125.84
    'total_cost_dollars': 125.84
}
```

### **Step 2: Apply Pricing Tier**

```python
# Free tier ($0/month, 1000 quota)
if user.subscription_tier == 'free':
    if usage['total_calls'] <= 1000:
        charge = 0  # Within quota
    else:
        overage = usage['total_calls'] - 1000
        charge = overage * 0.01  # $0.01 per call

# Pro tier ($49/month, 50000 quota)
elif user.subscription_tier == 'pro':
    base_fee = 49.00
    if usage['total_calls'] <= 50000:
        charge = base_fee
    else:
        overage = usage['total_calls'] - 50000
        charge = base_fee + (overage * 0.01)
```

### **Step 3: Charge via Stripe**

```python
import stripe

charge = stripe.Charge.create(
    amount=int(charge_amount * 100),  # Convert to cents
    currency='usd',
    customer=user.stripe_customer_id,
    description=f"SentinelDF - January 2025 ({usage['total_calls']} calls)"
)
```

---

## 📅 **Automated Monthly Billing Script**

Create a cron job that runs on the 1st of each month:

```python
# scripts/monthly_billing.py

from backend.database import SessionLocal, User
from backend.billing import charge_monthly_usage
from datetime import datetime

def run_monthly_billing():
    """Charge all users for last month's usage."""
    db = SessionLocal()
    
    # Get all active users
    users = db.query(User).filter(User.is_active == True).all()
    
    results = {
        'total_users': len(users),
        'charged': 0,
        'total_revenue_cents': 0,
        'errors': []
    }
    
    for user in users:
        try:
            result = charge_monthly_usage(user, db)
            
            if result['charged']:
                results['charged'] += 1
                results['total_revenue_cents'] += result['amount_cents']
                
                # Send invoice email
                send_invoice_email(user, result)
                
                print(f"✅ Charged {user.email}: ${result['amount_dollars']:.2f}")
            else:
                print(f"⏭️  Skipped {user.email}: {result.get('reason', 'No charge')}")
                
        except Exception as e:
            results['errors'].append({
                'user': user.email,
                'error': str(e)
            })
            print(f"❌ Error charging {user.email}: {e}")
    
    print(f"\n📊 Monthly Billing Complete:")
    print(f"   Users charged: {results['charged']}/{results['total_users']}")
    print(f"   Total revenue: ${results['total_revenue_cents']/100:.2f}")
    
    if results['errors']:
        print(f"   Errors: {len(results['errors'])}")
    
    return results

if __name__ == "__main__":
    run_monthly_billing()
```

**Run with cron:**
```bash
# Run on 1st of each month at 1 AM
0 1 1 * * python scripts/monthly_billing.py
```

---

## 📧 **Invoice Email Template**

```python
def send_invoice_email(user, billing_result):
    """Send monthly invoice to user."""
    
    usage = billing_result['usage']
    
    email_body = f"""
    Hi {user.name},
    
    Your SentinelDF invoice for {usage['month']}/{usage['year']}:
    
    📊 Usage Summary:
    - API Calls: {usage['total_calls']:,}
    - Documents Scanned: {usage['total_documents']:,}
    - Tokens Used: {usage['total_tokens']:,}
    
    💰 Charges:
    - Subscription: ${get_base_fee(user.subscription_tier):.2f}
    - Usage Charges: ${billing_result['amount_dollars']:.2f}
    - Total: ${billing_result['amount_dollars']:.2f}
    
    View detailed invoice: https://sentineldf.com/invoices/{usage['year']}/{usage['month']}
    
    Questions? Reply to this email or visit our support page.
    
    Thanks for using SentinelDF!
    """
    
    send_email(
        to=user.email,
        subject=f"SentinelDF Invoice - {usage['month']}/{usage['year']}",
        body=email_body
    )
```

---

## 🎯 **Customer-Facing Usage Dashboard**

Users can check their usage anytime:

```python
# GET /v1/billing/usage
{
  "current_usage": {
    "total_calls": 847,
    "total_documents": 23450,
    "total_cost_dollars": 234.50
  },
  "quota": {
    "total": 1000,
    "used": 847,
    "remaining": 153,
    "percent_used": 84.7
  },
  "projected": {
    "calls": 1200,
    "cost_dollars": 20.00
  },
  "subscription_tier": "free"
}
```

**Example Dashboard:**

```
📊 Your Usage (January 2025)

API Calls: 847 / 1,000 (84.7%)
[=================>    ]

Documents Scanned: 23,450
Tokens Used: 650,000
Current Cost: $8.47

💡 Projected end-of-month: $12.00

⚠️ You're approaching your quota limit!
Upgrade to Pro for 50,000 calls/month: $49
[Upgrade Now]
```

---

## 🔄 **Complete Billing Flow**

```
User makes API call
    ↓
Verify API key
    ↓
Check quota (reject if exceeded)
    ↓
Process request
    ↓
Track usage in database ✅
    ↓
Return results

--- End of Month ---

Cron job runs
    ↓
Calculate each user's usage
    ↓
Apply pricing tier logic
    ↓
Charge via Stripe
    ↓
Send invoice email
    ↓
Update user records
```

---

## 📊 **Usage Analytics**

### **View Usage Trends:**

```python
# GET /v1/billing/usage/history?months=6

{
  "history": [
    {"month": 1, "year": 2025, "total_calls": 847, "cost_dollars": 8.47},
    {"month": 12, "year": 2024, "total_calls": 1234, "cost_dollars": 23.40},
    {"month": 11, "year": 2024, "total_calls": 890, "cost_dollars": 0.00},
    ...
  ]
}
```

### **Top Users by Usage:**

```sql
SELECT 
    u.email,
    COUNT(ur.id) as total_calls,
    SUM(ur.documents_scanned) as total_docs,
    SUM(ur.cost_cents)/100.0 as total_cost_dollars
FROM users u
JOIN usage_records ur ON u.id = ur.user_id
WHERE EXTRACT(MONTH FROM ur.timestamp) = 1
  AND EXTRACT(YEAR FROM ur.timestamp) = 2025
GROUP BY u.id
ORDER BY total_cost_dollars DESC
LIMIT 10;
```

---

## ⚙️ **Setup Instructions**

### **1. Install Stripe:**

```bash
pip install stripe
```

### **2. Set Stripe API Key:**

```bash
export STRIPE_SECRET_KEY="sk_live_your_key_here"
```

### **3. Create Stripe Products:**

```bash
# Create Pro Plan product
stripe products create --name="SentinelDF Pro" --description="50,000 scans/month"

# Create price for Pro Plan ($49/month)
stripe prices create \
  --product=prod_xxx \
  --unit-amount=4900 \
  --currency=usd \
  --recurring[interval]=month
```

### **4. Update billing.py:**

```python
PRICING_TIERS = {
    'pro': {
        'stripe_price_id': 'price_YOUR_PRICE_ID_HERE'  # From step 3
    }
}
```

### **5. Add Billing Routes to API:**

```python
# In backend/app_with_auth.py

from backend.billing_routes import router as billing_router

app.include_router(billing_router)
```

### **6. Set Up Monthly Billing Cron:**

```bash
# Add to crontab
crontab -e

# Run on 1st of month at 1 AM
0 1 1 * * cd /path/to/sentineldf && python scripts/monthly_billing.py
```

---

## 🧪 **Testing Billing**

```python
# Test monthly calculation
from backend.billing import calculate_monthly_usage
from backend.database import SessionLocal

db = SessionLocal()
usage = calculate_monthly_usage(user_id=1, db=db)
print(f"User 1 usage: {usage}")

# Test charging (use Stripe test mode)
from backend.billing import charge_monthly_usage
from backend.database import User

user = db.query(User).first()
result = charge_monthly_usage(user, db)
print(f"Charge result: {result}")
```

---

## ✅ **Summary**

**Usage Tracking:**
- ✅ Automatic on every API call
- ✅ Stored in `usage_records` table
- ✅ Tracks: calls, documents, tokens, cost

**Billing:**
- ✅ Monthly billing script
- ✅ Stripe integration
- ✅ Tiered pricing (Free, Pro, Enterprise)
- ✅ Overage charges
- ✅ Invoice emails

**Customer Tools:**
- ✅ Real-time usage dashboard
- ✅ Usage history API
- ✅ Quota warnings
- ✅ Upgrade options

**You're ready to charge customers!** 💰

---

## 📁 **Files Created:**

1. `backend/billing.py` - Billing logic
2. `backend/billing_routes.py` - API endpoints
3. `scripts/monthly_billing.py` - Automated billing (create this)
4. `USAGE_TRACKING_AND_BILLING.md` - This guide
