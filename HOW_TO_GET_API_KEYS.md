# 🔑 How Customers Get API Keys

## 🎯 Three Ways to Get an API Key

### **Method 1: Sign Up on Landing Page** ⭐ **EASIEST & RECOMMENDED**

```
User visits: https://sentineldf.com
    ↓
Scrolls to "Get Early Access" section
    ↓
Fills out form:
  - Work Email: customer@company.com
  - Company: Acme Corp
  - Use Case: (optional)
    ↓
Clicks "Request Beta Access"
    ↓
✅ API key generated INSTANTLY!
    ↓
Shown on screen + Sent to email
    ↓
Ready to use immediately!
```

**What Happens:**
1. Form submits to your API: `POST /v1/keys/users`
2. API creates user account
3. API generates unique API key: `sk_live_abc123...`
4. Key shown on success page
5. Key emailed to user
6. User can start using API right away!

---

### **Method 2: Direct API Call**

For developers who want to automate or integrate:

```bash
curl -X POST https://api.sentineldf.com/v1/keys/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@company.com",
    "name": "John Doe",
    "company": "Acme Corp"
  }'
```

**Response:**
```json
{
  "user_id": 123,
  "email": "customer@company.com",
  "api_key": "sk_live_abc123def456ghi789...",
  "message": "API key created successfully. Save it now - you won't see it again!"
}
```

⚠️ **Important:** The API key is only shown once! Save it immediately.

---

### **Method 3: Developer Dashboard** (Future Feature)

Build a self-service dashboard where users can:
- Log in with email
- View all their API keys
- Create new keys
- Revoke old keys
- See usage statistics

---

## 📧 What the Email Looks Like

When someone signs up, they receive this email:

```
To: customer@company.com
From: SentinelDF <noreply@sentineldf.com>
Subject: Your SentinelDF API Key

Welcome to SentinelDF!

Your API key is: sk_live_abc123def456ghi789...

⚠️ IMPORTANT: Save this key securely. You won't be able to see it again!

Quick Start:
1. Install the SDK:
   pip install sentineldf-ai

2. Use your API key:
   from sentineldf import SentinelDF
   client = SentinelDF(api_key="sk_live_abc123...")
   results = client.scan(["your text to scan"])

Documentation: https://docs.sentineldf.com
Support: support@sentineldf.com

Happy scanning!
- The SentinelDF Team
```

---

## 🎨 Landing Page Flow (Updated)

Your landing page now automatically generates API keys!

### **User Experience:**

1. **User fills form:**
   ```
   Email: customer@company.com
   Company: Acme Corp
   ```

2. **User clicks "Request Beta Access"**

3. **Success screen appears:**
   ```
   🎉 You're In!
   
   Your API key: sk_live_abc123def456...  [Copy]
   
   Quick Start:
   pip install sentineldf-ai
   from sentineldf import SentinelDF
   client = SentinelDF(api_key="sk_live_abc123...")
   
   ⚠️ This key has also been emailed to you
   ```

4. **User copies key and starts using API immediately!**

---

## 🔄 Complete Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LANDING PAGE (sentineldf.com)                             │
│                                                             │
│  User fills form → Clicks submit                           │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /v1/keys/users
                     │ {email, name, company}
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  YOUR API BACKEND (api.sentineldf.com)                     │
│                                                             │
│  1. Create user in database                                │
│  2. Generate API key: sk_live_abc123...                    │
│  3. Hash key and store in database                         │
│  4. Return key to frontend                                 │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Returns: {api_key: "sk_live_..."}
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  LANDING PAGE                                               │
│                                                             │
│  1. Shows API key on screen                                │
│  2. Sends email with API key                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  CUSTOMER'S EMAIL                                           │
│                                                             │
│  📧 "Your SentinelDF API Key: sk_live_..."                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Setup Instructions (For You)

### **Step 1: Make Sure API is Running**

```bash
cd sentineldf/backend
python app_with_auth.py

# Should see:
# 🚀 Starting SentinelDF API with authentication...
# 📖 API Docs: http://localhost:8000/docs
```

### **Step 2: Update Landing Page Environment Variables**

Create `.env.local` in `landing-page/` folder:

```bash
# API endpoint (change to production URL when deploying)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Web3Forms key (for sending emails)
NEXT_PUBLIC_WEB3FORMS_KEY=a39080a5-6227-43df-8ba0-6f3812a8c6a8
```

### **Step 3: Test the Flow**

```bash
cd landing-page
npm run dev

# Visit: http://localhost:3000
# Fill out beta signup form
# Check that API key appears!
```

---

## 🔐 Security Notes

### **How API Keys Are Stored:**

```python
# When key is generated:
full_key = "sk_live_abc123def456..."  # Shown to user ONCE

# In database:
key_hash = sha256(full_key)  # Only hash is stored!

# When user uses API:
received_key = "sk_live_abc123..."
if sha256(received_key) == stored_hash:
    # ✅ Valid key
else:
    # ❌ Invalid key
```

**Why this is secure:**
- Original key is never stored
- If database is leaked, attackers can't use keys
- Only the user who received it knows the actual key

---

## 📊 Database Schema

### **Users Table:**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  company VARCHAR(255),
  monthly_quota INTEGER DEFAULT 1000,
  subscription_tier VARCHAR(50) DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW()
);
```

### **API Keys Table:**
```sql
CREATE TABLE api_keys (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  key_hash VARCHAR(64),  -- SHA-256 hash
  key_prefix VARCHAR(20), -- First few chars for display
  name VARCHAR(255) DEFAULT 'Default Key',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP
);
```

---

## 🎯 Customer Journey

### **Day 1: Sign Up**
```
1. Visit sentineldf.com
2. Fill beta signup form
3. Get API key instantly
4. Receive email with key
```

### **Day 1: First Use**
```
5. Install SDK: pip install sentineldf-ai
6. Write code:
   from sentineldf import SentinelDF
   client = SentinelDF(api_key="sk_live_...")
   results = client.scan(["text"])
7. See results immediately!
```

### **Week 1: Regular Usage**
```
8. Scan training datasets
9. Integrate into pipelines
10. Monitor usage dashboard (future)
```

### **Month 1: Upgrade**
```
11. Hit free tier limit (1,000 scans)
12. Upgrade to Pro ($49/month)
13. Get 50,000 scans/month
```

---

## ✅ Checklist for You

Before launching:

- [ ] API backend is deployed (Railway/Render)
- [ ] Database is set up (PostgreSQL)
- [ ] Landing page is deployed (Netlify/Vercel)
- [ ] Environment variables are configured
- [ ] Web3Forms is configured for emails
- [ ] Test the signup flow end-to-end
- [ ] Verify emails are being sent
- [ ] Verify API keys work

---

## 🆘 Troubleshooting

### **Issue: "Failed to create user"**

**Check:**
1. Is API backend running?
2. Is database initialized?
3. Check API logs for errors

**Solution:**
```bash
# Restart API
python backend/app_with_auth.py

# Check logs
tail -f logs/api.log
```

### **Issue: "Email not received"**

**Check:**
1. Is Web3Forms key correct?
2. Check spam folder
3. Verify email address is correct

**Solution:**
```bash
# Test Web3Forms directly
curl -X POST https://api.web3forms.com/submit \
  -d access_key=YOUR_KEY \
  -d email=test@test.com \
  -d message="Test"
```

### **Issue: "API key doesn't work"**

**Check:**
1. Is key copied correctly (no spaces)?
2. Is it the full key starting with `sk_live_`?
3. Check if key is active in database

**Solution:**
```python
# Check in database
from backend.database import SessionLocal, APIKey
db = SessionLocal()
key = db.query(APIKey).filter(APIKey.key_prefix.contains("abc123")).first()
print(f"Active: {key.is_active}")
```

---

## 📚 Files Created

1. **`landing-page/lib/api-client.ts`** - API integration functions
2. **`landing-page/components/beta-signup.tsx`** - Updated with API key generation
3. **`HOW_TO_GET_API_KEYS.md`** - This guide

---

## 🎉 Summary

**Customers get API keys by:**

✅ **Landing Page** - Sign up → Instant API key (easiest!)  
✅ **Direct API Call** - POST to `/v1/keys/users`  
✅ **Developer Dashboard** - Future feature for self-service  

**They receive:**
- API key shown on screen
- API key emailed to them
- Quick start instructions
- Ready to use immediately!

**Your landing page now handles everything automatically!** 🚀
