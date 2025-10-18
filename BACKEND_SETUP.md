# 🔧 Backend API Setup for Landing Page

## Required Environment Variable

Add this to your **Netlify environment variables**:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

Replace `https://your-backend-api.com` with your actual FastAPI backend URL.

---

## Where to Add

1. Go to Netlify Dashboard
2. Select your site (**sentineldf.netlify.app**)
3. Go to **Site settings** → **Environment variables**
4. Click **"Add a variable"**
5. Add:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://your-backend-url.com`
   - **Scopes:** All deploy contexts

---

## Backend Endpoints Required

Your FastAPI backend must have these endpoints:

### 1. Generate API Key
```
POST /v1/keys/create?name=Dashboard%20Key
Authorization: Bearer {clerk_token}
```

### 2. Get User's API Keys
```
GET /v1/keys/me
Authorization: Bearer {clerk_token}
```

### 3. Get Usage Stats
```
GET /v1/keys/usage
Authorization: Bearer {clerk_token}
```

---

## Testing Locally

Create `.env.local` in the landing-page directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

Then run:
```bash
npm run dev
```

---

## Production Deployment

After adding the environment variable to Netlify:

1. Trigger a new deploy (or push a commit)
2. Test the dashboard API key generation
3. Verify usage statistics are loading

---

## Troubleshooting

### API Key Generation Fails

- Check backend logs for errors
- Verify Clerk token is being sent correctly
- Check CORS settings on backend
- Ensure backend endpoint is accessible

### Usage Stats Not Loading

- Verify `/v1/keys/usage` endpoint exists
- Check backend authentication
- Look for errors in browser console (F12)
