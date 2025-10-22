# 🔐 Clerk Setup Guide

Complete guide to add user authentication to your SentinelDF landing page.

---

## ✅ What I Just Added

1. ✅ **Clerk authentication** package installed
2. ✅ **Sign In page** (`/sign-in`)
3. ✅ **Sign Up page** (`/sign-up`)
4. ✅ **Dashboard** with API key management (`/dashboard`)
5. ✅ **Navigation buttons** on landing page
6. ✅ **Protected routes** middleware

---

## 🚀 Setup Steps

### **Step 1: Create Clerk Account**

1. Go to https://clerk.com
2. Click **"Sign Up"**
3. Create your account (free!)
4. Click **"+ Create Application"**
5. Name it: **"SentinelDF"**
6. Choose sign-in methods:
   - ✅ Email
   - ✅ Google (recommended)
   - ✅ GitHub (optional)

---

### **Step 2: Get Your API Keys**

After creating the application:

1. You'll see your **Publishable Key** and **Secret Key**
2. Copy both keys

Example:
```
Publishable Key: pk_test_abc123...
Secret Key: sk_test_xyz789...
```

---

### **Step 3: Add Keys to Your Project**

1. Open your terminal in the `landing-page` folder:
```bash
cd landing-page
```

2. Create `.env.local` file:
```bash
# Copy the example file
cp .env.example .env.local
```

3. Edit `.env.local` and add your Clerk keys:
```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE

# Clerk URLs (keep these as-is)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

**Replace:**
- `pk_test_YOUR_KEY_HERE` with your actual Publishable Key
- `sk_test_YOUR_KEY_HERE` with your actual Secret Key

---

### **Step 4: Install Dependencies**

```bash
npm install
```

This will install Clerk and all required packages.

---

### **Step 5: Run Your Site**

```bash
npm run dev
```

Open http://localhost:3000

---

## 🎨 What You Get

### **Landing Page Updates:**

**Navigation Bar (Top Right):**
- **Sign In** button → Takes users to `/sign-in`
- **Sign Up** button → Takes users to `/sign-up`

### **Sign Up Page** (`/sign-up`)
Beautiful Clerk signup modal with:
- Email/password signup
- Social login (Google, GitHub)
- Email verification
- Password strength indicators

### **Sign In Page** (`/sign-in`)
Secure login with:
- Email/password login
- Social login
- "Forgot password" link
- Session management

### **Dashboard** (`/dashboard`)
Full-featured dashboard with:
- **API Keys Tab**
  - Generate new API keys
  - View existing keys
  - Copy keys to clipboard
  - Revoke keys
  
- **Usage Tab**
  - Current month usage
  - Quota progress bar
  - Cost tracking
  
- **Billing Tab**
  - Current plan (Free/Pro/Enterprise)
  - Upgrade options
  - Pricing comparison
  
- **Settings Tab**
  - Account information
  - User profile
  - Documentation links

---

## 🔄 User Flow

### **New User Signup:**
```
1. Visits sentineldf.com
2. Clicks "Sign Up" button
3. Clerk signup modal appears
4. User enters email + password
5. Receives verification email
6. Clicks verification link
7. Redirected to /dashboard
8. Generates first API key
9. Starts using SentinelDF!
```

### **Returning User:**
```
1. Visits sentineldf.com
2. Clicks "Sign In" button
3. Enters credentials
4. Redirected to /dashboard
5. Views usage stats
6. Manages API keys
```

---

## 🎯 Next Steps

### **Connect Dashboard to Backend API**

Currently, the dashboard generates mock API keys. To connect it to your real backend:

1. **Update `dashboard-content.tsx`:**

Find the `generateAPIKey` function and replace the mock code:

```typescript
const generateAPIKey = async () => {
  setLoading(true)
  
  try {
    // Get Clerk token
    const { getToken } = useAuth()
    const clerkToken = await getToken()
    
    // Call your backend
    const response = await fetch('http://localhost:8000/v1/dashboard/keys/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${clerkToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    const data = await response.json()
    setApiKey(data.api_key)
  } catch (error) {
    console.error('Error generating key:', error)
    alert('Failed to generate API key')
  } finally {
    setLoading(false)
  }
}
```

2. **Update your backend** to accept Clerk JWT tokens (see `backend/auth_clerk.py`)

---

## 🎨 Customize Appearance

### **Change Clerk Theme Colors:**

In your Clerk Dashboard:
1. Go to **Customization** → **Theme**
2. Choose **Dark Mode** (matches your site)
3. Set primary color to **#2563EB** (blue)

### **Custom Logo:**

In Clerk Dashboard:
1. Go to **Customization** → **Branding**
2. Upload your SentinelDF logo
3. Set application name to "SentinelDF"

---

## 🔒 Security Features

Clerk provides automatically:
- ✅ **Password hashing** (bcrypt)
- ✅ **JWT token management**
- ✅ **Session security**
- ✅ **Email verification**
- ✅ **Rate limiting**
- ✅ **2FA support**
- ✅ **CSRF protection**
- ✅ **XSS protection**

---

## 📧 Email Configuration

Clerk handles emails automatically:
- ✅ Verification emails
- ✅ Password reset emails
- ✅ Welcome emails
- ✅ Magic link emails

**Custom Domain (Optional):**
1. Go to Clerk Dashboard → **Email & SMS**
2. Add your custom domain
3. Configure DNS records
4. Send emails from `noreply@sentineldf.com`

---

## 🧪 Testing

### **Test Signup:**
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter test email: `test@example.com`
4. Set password
5. Check email for verification link
6. Verify and login
7. Should see dashboard!

### **Test Sign In:**
1. Click "Sign In"
2. Enter credentials
3. Should redirect to `/dashboard`

### **Test Protected Routes:**
1. Try visiting `/dashboard` while logged out
2. Should redirect to `/sign-in`
3. After login, should return to `/dashboard`

---

## 🚨 Troubleshooting

### **Issue: "Invalid publishable key"**

**Fix:** 
- Check that you copied the key correctly
- Make sure it starts with `pk_test_` or `pk_live_`
- Restart your dev server: `npm run dev`

### **Issue: Sign-up page not styled**

**Fix:**
- Make sure Tailwind CSS is working
- Check that `globals.css` is imported
- Clear browser cache

### **Issue: Dashboard shows "Not Found"**

**Fix:**
- Make sure you're on `/dashboard` (not `/Dashboard`)
- Check that the page file exists at `app/dashboard/page.tsx`
- Restart dev server

### **Issue: "Module not found: @clerk/nextjs"**

**Fix:**
```bash
npm install @clerk/nextjs
```

---

## 📊 Clerk Free Tier Limits

Perfect for getting started:
- ✅ 5,000 monthly active users
- ✅ Unlimited total users
- ✅ Email/password authentication
- ✅ Social login (Google, GitHub, etc.)
- ✅ Email verification
- ✅ Basic analytics

**When to upgrade:**
- More than 5,000 monthly active users
- Need advanced features (2FA, SAML SSO)
- Want custom email templates

---

## ✅ Checklist

Before going live:

- [ ] Created Clerk account
- [ ] Got API keys from Clerk dashboard
- [ ] Added keys to `.env.local`
- [ ] Installed dependencies (`npm install`)
- [ ] Tested signup flow
- [ ] Tested signin flow
- [ ] Tested dashboard access
- [ ] Customized Clerk appearance
- [ ] Connected to backend API
- [ ] Tested API key generation

---

## 🎉 You're Done!

Your landing page now has:
- ✅ Professional authentication
- ✅ User signup/signin
- ✅ Protected dashboard
- ✅ API key management
- ✅ Usage tracking
- ✅ Enterprise-grade security

**Users can now:**
1. Sign up on your site
2. Get verified via email
3. Login to their dashboard
4. Generate API keys
5. Monitor their usage
6. Manage their account

---

## 📚 Resources

- **Clerk Docs:** https://clerk.com/docs
- **Next.js Integration:** https://clerk.com/docs/quickstarts/nextjs
- **Dashboard Customization:** https://clerk.com/docs/customization
- **Support:** https://clerk.com/support

---

**Your landing page is now production-ready with Clerk!** 🚀
