# 💎 SentinelDF Upgrade Guide - $7/month Plan

## 💰 Your New Setup

```
API Server (Starter):       $7/month
PostgreSQL (Starter):       $7/month  (optional but recommended)
────────────────────────────────────
Total:                      $7-14/month
```

---

## ✅ What You Get

### API Server Upgrade ($7/month)
- ✨ **No cold starts** - Always responsive (< 1s)
- 🚀 **512MB RAM** - Better performance
- ⚡ **0.1 CPU** - Faster processing
- 🔄 **Persistent connections** - More reliable
- 📈 **Better for production** - Suitable for real users

### Database Upgrade ($7/month - Optional)
- 💾 **256MB PostgreSQL** - Persistent storage
- 🔐 **API keys don't reset** - Survive redeploys
- 📊 **Usage tracking** - Store scan history
- 🔄 **Auto backups** - Data safety
- 📈 **Scalable** - Grow to 10K+ users

---

## 🚀 Deployment Options

### Option 1: Quick Upgrade (API Only - $7/month)

**Just upgrade your existing service:**

1. **Via Render Dashboard:**
   - Go to your service → Settings
   - Change Plan: Free → **Starter**
   - Save Changes
   - Done! ✅

**What happens:**
- Service restarts in ~30 seconds
- No more cold starts
- Still uses in-memory storage (resets on redeploy)

---

### Option 2: Full Upgrade (API + Database - $14/month) ⭐ RECOMMENDED

**Get persistence + always-on:**

1. **Push code changes:**
```powershell
cd c:\Users\kvaru\Downloads\Syn\sentineldf

git add api_server_with_db.py render.yaml
git commit -m "Upgrade to Starter plan with PostgreSQL"
git push origin main
```

2. **In Render Dashboard:**
   - Go to Dashboard → **New → PostgreSQL**
   - Name: `sentineldf-db`
   - Plan: **Starter** ($7/month)
   - Click **Create Database**

3. **Update your web service:**
   - Go to your API service → Settings
   - Change Plan: Free → **Starter**
   - Go to Environment tab
   - Add: `DATABASE_URL` (connect to `sentineldf-db`)
   - Save all changes

4. **Trigger redeploy:**
```powershell
Invoke-WebRequest -Uri "https://api.render.com/deploy/srv-d3pi4eali9vc73bjffig?key=DyNc3M2sPvo" -Method POST
```

**What you get:**
- ✅ No cold starts
- ✅ Persistent API keys
- ✅ Better performance
- ✅ Production-ready

---

## 📊 Comparison

| Feature | Free | Starter ($7) | Starter + DB ($14) |
|---------|------|--------------|-------------------|
| Cold Starts | ✅ Yes (30s) | ❌ No | ❌ No |
| RAM | 512MB | 512MB | 512MB |
| API Keys Persist | ❌ No | ❌ No | ✅ Yes |
| Database | None | None | ✅ 256MB Postgres |
| Good For | Testing | Beta users | Production |
| Max Users | ~100 | ~1,000 | ~10,000 |

---

## 🧪 Test Your Upgrade

After deployment, test:

```powershell
# Test API health
curl https://sentineldf.onrender.com/health

# Should show:
{
  "status": "healthy",
  "plan": "starter",
  "database": "postgresql"  # If you added DB
}

# Generate API key
curl -X POST https://sentineldf.onrender.com/v1/keys/create?name=Test

# Test scan
sentineldf --api-key sk_live_... scan-text "jailbreak test"

# Redeploy and check keys still exist (if using DB)
```

---

## 💡 Pro Tips

### 1. Monitor Usage
```powershell
# Check your Render dashboard for:
# - Request count
# - Response times
# - Memory usage
# - Database size
```

### 2. Set Up Alerts
- Render Dashboard → Service → Alerts
- Get notified if:
  - Service goes down
  - High memory usage
  - Database gets full

### 3. Database Backups
- Render automatically backs up Postgres daily
- Keep last 7 days
- Can restore from dashboard

---

## 🔄 Rollback Plan

If you need to go back to free tier:

```powershell
# 1. Change plan back to Free in dashboard
# 2. Delete database (optional)
# 3. Revert to old api_server.py:

git checkout main -- api_server.py render.yaml
git commit -m "Rollback to free tier"
git push origin main
```

---

## 📈 Next Upgrade Path

When you outgrow Starter:

### Standard Plan ($25/month)
- 2GB RAM
- 0.5 CPU
- Handle 10K+ concurrent users
- Better for production apps

### Pro Plan ($85/month)
- 4GB RAM
- 1.0 CPU
- Enterprise features
- Priority support

---

## ✅ Recommended: Start with Option 2

**$14/month gets you:**
- Production-ready API
- No cold starts
- Persistent storage
- Can handle thousands of users
- Professional setup

**Cost per user:** ~$0.001/user/month at 1000 users

---

## 🚀 Deploy Now!

**Quick command:**
```powershell
cd c:\Users\kvaru\Downloads\Syn\sentineldf

# Commit changes
git add .
git commit -m "Upgrade to Starter plan with database"
git push origin main

# Create database in Render dashboard
# Then trigger deploy
Invoke-WebRequest -Uri "https://api.render.com/deploy/srv-d3pi4eali9vc73bjffig?key=DyNc3M2sPvo" -Method POST
```

**Your SentinelDF will be production-ready in 5 minutes!** 🎉
