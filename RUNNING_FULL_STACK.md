# Running SentinelDF Full Stack (API + Landing Page)

This guide shows you how to run both the backend API and frontend landing page together for the complete experience.

---

## 🎯 What You'll Get

- ✅ **Landing Page** at http://localhost:3000
- ✅ **Backend API** at http://localhost:8000
- ✅ **Interactive Demo** that actually scans text
- ✅ **Beta Signup Form** (connected to your email)

---

## 📋 Prerequisites

Make sure you have:
- ✅ Python 3.10+ installed
- ✅ Node.js 18+ installed
- ✅ All backend dependencies (`pip install -r requirements.txt`)
- ✅ All frontend dependencies (run `npm install` in `landing-page/`)

---

## 🚀 Quick Start (2 Terminals)

### Terminal 1: Start Backend API

```powershell
# Navigate to project root
cd C:\Users\kvaru\Downloads\Syn\sentineldf

# Activate virtual environment
& c:/Users/kvaru/Downloads/Syn/venv/Scripts/Activate.ps1

# Start FastAPI server
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test it:**
```powershell
# In another terminal
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Terminal 2: Start Landing Page

```powershell
# Navigate to landing page folder
cd C:\Users\kvaru\Downloads\Syn\sentineldf\landing-page

# Copy environment variables
copy .env.example .env.local

# Start Next.js dev server
npm run dev
```

**Expected output:**
```
▲ Next.js 14.0.4
- Local:        http://localhost:3000
- Network:      http://192.168.1.x:3000

✓ Ready in 2.4s
```

---

## ✅ Test the Integration

### 1. **Visit Landing Page**
Open http://localhost:3000 in your browser

### 2. **Scroll to Interactive Demo**
Scroll down to the "Try It Live" section

### 3. **Test with Example**
Click one of the example buttons:
- "Prompt Injection" → Should get Risk: 80+
- "Clean Text" → Should get Risk: 0-30

### 4. **Check API Connection**
- If demo works → API is connected ✅
- If you see "Scan error" in browser console → API not running ❌

### 5. **Submit Beta Signup**
- Scroll to "Join Beta Testing" section
- Enter your email
- Click "Request Beta Access"
- Should see success message ✅

---

## 🔧 Configuration

### Backend API Configuration

Edit `config/config.yaml` if needed:
```yaml
detection:
  heuristic_weight: 0.4    # Adjust detection sensitivity
  embedding_weight: 0.6
  threshold: 70            # Risk threshold for quarantine

cache:
  enabled: true
  size_limit_mb: 1000
```

### Frontend Configuration

Create `landing-page/.env.local`:
```bash
# Point to your local API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Or point to deployed API
# NEXT_PUBLIC_API_URL=https://api.sentineldf.com
```

---

## 📊 What the Demo Actually Does

When you click "Scan Now" in the interactive demo:

1. **Frontend** creates a Blob from your text
2. **Sends POST request** to `http://localhost:8000/api/v1/scan`
3. **Backend** runs dual detection:
   - Heuristic detector (pattern matching)
   - Embedding detector (ML outliers)
4. **Calculates risk score** (0-100)
5. **Makes decision**: QUARANTINE (≥70) or ALLOW (<70)
6. **Returns result** to frontend
7. **Displays** risk score, decision, and reasons

**Flow diagram:**
```
User Input → Next.js Frontend → FastAPI Backend → Detectors
                                        ↓
                                  Risk Fusion
                                        ↓
                                   Decision
                                        ↓
Frontend Display ← JSON Response ← Backend
```

---

## 🐛 Troubleshooting

### Demo Shows "Scan error" in Console

**Problem:** Frontend can't reach backend API

**Solutions:**
1. Check if backend is running:
   ```powershell
   curl http://localhost:8000/health
   ```

2. Check CORS settings in `backend/app.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],  # ← Should include this
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Check browser console (F12) for error details

### Demo Uses Mock Data Instead of API

**Problem:** API call failed, fell back to mock

**This is expected behavior!** The demo has a fallback to mock data if API is unavailable. To force real API:

1. Make sure backend is running
2. Check `landing-page/.env.local` has correct API URL
3. Restart Next.js dev server (`npm run dev`)

### Port Already in Use

**Backend (port 8000):**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it
taskkill /PID <PID> /F

# Or use different port
uvicorn backend.app:app --port 8001
```

**Frontend (port 3000):**
```powershell
# Next.js auto-switches to 3001 if 3000 is busy
# Or manually specify:
npm run dev -- -p 3001
```

### Beta Signup Doesn't Send Email

**Expected:** Beta signup is currently **local-only** (no email sent yet)

To add email functionality:

**Option 1: Google Forms (Easiest)**
1. Create Google Form with email field
2. Get the form submission URL
3. Update `components/beta-signup.tsx`:
```typescript
const response = await fetch('https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse', {
  method: 'POST',
  body: new URLSearchParams({
    'entry.123456': email,  // Replace with your field ID
  }),
})
```

**Option 2: Mailchimp/ConvertKit**
1. Create account
2. Get API key
3. Add to `.env.local`:
```bash
MAILCHIMP_API_KEY=your_key
MAILCHIMP_LIST_ID=your_list
```
4. Create API route in `app/api/beta-signup/route.ts`

**Option 3: Email to Yourself**
1. Create API route: `app/api/beta-signup/route.ts`
2. Use Resend or SendGrid to email you
3. Example with Resend:
```typescript
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function POST(request: Request) {
  const { email } = await request.json()
  
  await resend.emails.send({
    from: 'signup@sentineldf.com',
    to: 'varunsripadkota@gmail.com',
    subject: 'New Beta Signup!',
    text: `Email: ${email}`,
  })
  
  return Response.json({ success: true })
}
```

---

## 🚀 Deployment

### Deploy Backend API

**Option 1: Fly.io (Free tier)**
```bash
# Install flyctl
# Windows: iwr https://fly.io/install.ps1 -useb | iex

cd sentineldf
fly launch
fly deploy
```

**Option 2: Railway (Free tier)**
1. Go to railway.app
2. Connect GitHub repo
3. Deploy from `sentineldf/` directory

**Option 3: AWS/GCP/Azure**
- See `docs/DEPLOYMENT.md` (if exists)
- Or use Docker: `docker build -t sentineldf-api .`

### Deploy Landing Page

**Vercel (Recommended - Free)**
```bash
# Install Vercel CLI
npm i -g vercel

cd landing-page
vercel

# Follow prompts:
# - Project name: sentineldf
# - Root directory: landing-page/
# - Build command: npm run build
# - Output directory: .next
```

**Update environment variable:**
```bash
# In Vercel dashboard, add:
NEXT_PUBLIC_API_URL=https://your-api.fly.dev
```

**Netlify (Alternative)**
```bash
# Install Netlify CLI
npm i -g netlify-cli

cd landing-page
netlify deploy --prod
```

---

## 📈 Next Steps

### Week 1: Beta Testing
- [ ] Get 5 people to fill out beta signup form
- [ ] Manually email them API keys
- [ ] Schedule 1-on-1 demo calls

### Week 2: Improve Demo
- [ ] Add file upload to demo (not just text)
- [ ] Show MBOM signature in results
- [ ] Add "Download Report" button

### Week 3: Add Analytics
- [ ] Install PostHog or Plausible
- [ ] Track: page views, demo usage, signups
- [ ] Set up conversion funnel

### Week 4: Content
- [ ] Write 1 blog post about LLM security
- [ ] Record 2-minute demo video
- [ ] Add video to landing page

---

## 🆘 Need Help?

**API Issues:**
- Check `backend/app.py` for errors
- Check `reports/` folder for scan logs
- Run tests: `pytest -v`

**Frontend Issues:**
- Check browser console (F12 → Console tab)
- Check `landing-page/.next/` for build errors
- Clear cache: delete `.next/` folder, run `npm run dev` again

**Integration Issues:**
- Test API directly with `curl` first
- Check CORS settings in backend
- Verify `.env.local` has correct API URL

**Questions?**
Email: varunsripadkota@gmail.com

---

## ✅ Checklist: You're Ready When...

- [ ] Backend API running at http://localhost:8000
- [ ] Landing page running at http://localhost:3000
- [ ] Interactive demo successfully scans text
- [ ] Demo shows real risk scores (not mock)
- [ ] Beta signup form works
- [ ] All CTAs link to #beta (not #pricing)
- [ ] No console errors in browser

**Then you're ready to deploy!** 🚀

---

*SentinelDF - From local dev to production in 1 day!*
