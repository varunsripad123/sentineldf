# ✅ Netlify Environment Variables Checklist

Go to: https://app.netlify.com/ → Your Site → Site settings → Environment variables

## Required Variables:

### 1. Clerk Authentication Keys
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_a25vd24tYmFzcy00Ny5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_1A4XDszmgVvBTwXqmwqTgaEVTGWtZlB5CUqutcTyso
```

### 2. Clerk URLs (CRITICAL FOR REDIRECTS)
```
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## ⚠️ Important:
- All 6 variables must be added
- Use "Same value for all deploy contexts"
- After adding, click "Trigger deploy" → "Clear cache and deploy site"

## Test After Deploy:
1. Open incognito: https://sentineldf.netlify.app
2. Click "Sign Up"
3. Complete registration
4. Should automatically redirect to /dashboard ✅
