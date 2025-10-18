# 🔐 Clerk Integration Guide

Complete guide to using Clerk for user authentication with SentinelDF.

---

## 🎯 **Why Use Clerk?**

**Clerk provides:**
- ✅ User signup/login
- ✅ Email verification
- ✅ Password management
- ✅ Social login (Google, GitHub, etc.)
- ✅ 2FA / Multi-factor authentication
- ✅ User sessions & JWT tokens
- ✅ User profiles & metadata
- ✅ Admin dashboard

**vs. Building it yourself:**
- ❌ Weeks of development
- ❌ Security vulnerabilities
- ❌ Maintenance burden
- ❌ Compliance issues

**Clerk = Professional authentication in 30 minutes!**

---

## 🏗️ **Architecture**

### **Old Flow (Direct API Key):**
```
Landing Page → Fill form → Get API key
```

### **New Flow (With Clerk):**
```
Landing Page → Clerk Signup → Dashboard → Generate API keys → Use API
```

---

## 🚀 **Setup Instructions**

### **Step 1: Create Clerk Account**

1. Go to https://clerk.com
2. Sign up for free account
3. Create new application: "SentinelDF"
4. Copy API keys

### **Step 2: Install Clerk in Dashboard**

```bash
cd sentineldf/dashboard  # Create new Next.js app for dashboard

# Create Next.js dashboard
npx create-next-app@latest dashboard --typescript --tailwind --app

cd dashboard

# Install Clerk
npm install @clerk/nextjs
```

### **Step 3: Configure Clerk**

Create `.env.local`:

```bash
# Clerk keys (from Clerk dashboard)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Your API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Step 4: Add Clerk Provider**

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
```

### **Step 5: Create Sign In/Up Pages**

```typescript
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <SignIn />
    </div>
  );
}
```

```typescript
// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <SignUp />
    </div>
  );
}
```

### **Step 6: Create Protected Dashboard**

```typescript
// app/dashboard/page.tsx
import { auth, currentUser } from "@clerk/nextjs";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const { userId } = auth();
  
  // Redirect to sign-in if not authenticated
  if (!userId) {
    redirect('/sign-in');
  }
  
  const user = await currentUser();
  
  return (
    <div className="p-8">
      <h1>Welcome, {user?.firstName}!</h1>
      
      {/* API Keys Section */}
      <APIKeysManager userId={userId} />
      
      {/* Usage Stats */}
      <UsageStats userId={userId} />
      
      {/* Billing */}
      <BillingInfo userId={userId} />
    </div>
  );
}
```

---

## 🔑 **API Key Management in Dashboard**

### **Component: API Keys Manager**

```typescript
// components/APIKeysManager.tsx
'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@clerk/nextjs'

export default function APIKeysManager() {
  const { getToken } = useAuth()
  const [apiKeys, setApiKeys] = useState([])
  const [newKey, setNewKey] = useState(null)

  const generateAPIKey = async () => {
    // Get Clerk JWT token
    const token = await getToken()
    
    // Call your backend to create API key
    const response = await fetch('http://localhost:8000/v1/keys/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,  // Clerk JWT
        'Content-Type': 'application/json'
      }
    })
    
    const data = await response.json()
    setNewKey(data.api_key)
    loadAPIKeys()
  }

  const loadAPIKeys = async () => {
    const token = await getToken()
    
    const response = await fetch('http://localhost:8000/v1/keys/list', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    const data = await response.json()
    setApiKeys(data.keys)
  }

  useEffect(() => {
    loadAPIKeys()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">API Keys</h2>
        <button 
          onClick={generateAPIKey}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
        >
          Generate New Key
        </button>
      </div>

      {/* Show new key if just generated */}
      {newKey && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <p className="text-sm text-green-800 mb-2">
            ✅ New API key generated! Save it now:
          </p>
          <code className="block bg-white p-3 rounded text-sm font-mono">
            {newKey}
          </code>
          <p className="text-xs text-green-600 mt-2">
            ⚠️ You won't be able to see this again!
          </p>
        </div>
      )}

      {/* List of existing keys */}
      <div className="space-y-3">
        {apiKeys.map(key => (
          <div key={key.id} className="border rounded-lg p-4 flex justify-between items-center">
            <div>
              <p className="font-mono text-sm">{key.key_prefix}</p>
              <p className="text-xs text-gray-500">
                Created: {new Date(key.created_at).toLocaleDateString()}
              </p>
              <p className="text-xs text-gray-500">
                Last used: {key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never'}
              </p>
            </div>
            <button 
              onClick={() => revokeKey(key.id)}
              className="text-red-600 hover:text-red-800"
            >
              Revoke
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 🔐 **Backend: Verify Clerk JWT**

Update your backend to accept Clerk JWT tokens:

```python
# backend/auth_clerk.py

from fastapi import Header, HTTPException
from jose import jwt, JWTError
import requests
import os

CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

async def verify_clerk_token(
    authorization: str = Header(...)
) -> dict:
    """
    Verify Clerk JWT token from dashboard.
    
    This is different from API key authentication!
    - Clerk JWT: For dashboard access (manage keys, view usage)
    - API Key: For actual API usage (scan documents)
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify with Clerk
        # Get Clerk's public key
        jwks_url = f"https://api.clerk.dev/v1/jwks"
        jwks_response = requests.get(jwks_url)
        jwks = jwks_response.json()
        
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_signature": True}
        )
        
        return {
            "clerk_user_id": payload["sub"],
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified")
        }
        
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

### **New Dashboard Endpoints:**

```python
# backend/dashboard_routes.py

from fastapi import APIRouter, Depends
from backend.auth_clerk import verify_clerk_token
from backend.database import get_db, User, generate_api_key, APIKey

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])

@router.post("/keys/generate")
async def generate_new_api_key(
    clerk_user: dict = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
):
    """
    Generate new API key for logged-in user.
    
    Called from dashboard (authenticated via Clerk JWT).
    """
    # Get or create user based on Clerk ID
    user = db.query(User).filter(
        User.clerk_id == clerk_user["clerk_user_id"]
    ).first()
    
    if not user:
        # Create user from Clerk data
        user = User(
            clerk_id=clerk_user["clerk_user_id"],
            email=clerk_user["email"],
            name=clerk_user["email"].split('@')[0]
        )
        db.add(user)
        db.flush()
    
    # Generate API key
    full_key, key_hash, key_prefix = generate_api_key()
    
    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix
    )
    db.add(api_key)
    db.commit()
    
    return {
        "api_key": full_key,  # Show once!
        "key_prefix": key_prefix
    }

@router.get("/keys/list")
async def list_my_api_keys(
    clerk_user: dict = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
):
    """List all API keys for logged-in user."""
    user = db.query(User).filter(
        User.clerk_id == clerk_user["clerk_user_id"]
    ).first()
    
    if not user:
        return {"keys": []}
    
    keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    
    return {
        "keys": [
            {
                "id": k.id,
                "key_prefix": k.key_prefix,
                "created_at": k.created_at,
                "last_used_at": k.last_used_at,
                "is_active": k.is_active
            }
            for k in keys
        ]
    }
```

---

## 🎨 **Updated Landing Page**

Change signup button to redirect to Clerk:

```typescript
// landing-page/components/hero.tsx

export default function Hero() {
  return (
    <div>
      <h1>Protect Your LLM Training Data</h1>
      <p>Enterprise-grade data firewall for AI systems</p>
      
      {/* OLD: Form that creates user */}
      {/* NEW: Button that redirects to Clerk */}
      <a 
        href="https://dashboard.sentineldf.com/sign-up"
        className="px-8 py-4 bg-blue-600 text-white rounded-lg"
      >
        Get Started Free
      </a>
    </div>
  )
}
```

---

## 📊 **User Flow Comparison**

### **OLD (Direct API Key):**
```
Landing page form
  ↓
Email + company
  ↓
Get API key via email
  ↓
Use API
  ↓
Can't see usage later ❌
Can't manage keys ❌
```

### **NEW (With Clerk):**
```
Landing page
  ↓
Click "Get Started"
  ↓
Clerk signup (email + password)
  ↓
Email verification
  ↓
Login to dashboard
  ↓
Generate API keys
  ↓
View usage stats ✅
Manage multiple keys ✅
Update billing ✅
Professional experience ✅
```

---

## ✅ **Benefits of Clerk**

| Feature | Without Clerk | With Clerk |
|---------|--------------|------------|
| User signup | Basic email form | Professional signup flow |
| Authentication | None | Secure JWT tokens |
| Password | No password | Encrypted passwords |
| Email verification | Manual | Automatic |
| Social login | Not possible | Google, GitHub, etc. |
| 2FA | Not possible | Built-in |
| User dashboard | Need to build | Easy to build |
| Session management | Manual | Automatic |
| Security | DIY (risky) | Enterprise-grade |
| Development time | Weeks | Hours |
| Cost | Your time | $25/month (free tier: 5000 users) |

---

## 💰 **Clerk Pricing**

- **Free**: Up to 5,000 monthly active users
- **Pro**: $25/month for 10,000 MAU
- **Enterprise**: Custom pricing

**For SentinelDF:** Start with free tier, upgrade as you grow!

---

## 🚀 **Migration Path**

### **Phase 1: Keep Both (Transition)**
- Old users: Continue using direct API keys
- New users: Sign up via Clerk
- Gradually migrate old users

### **Phase 2: Clerk Only**
- All new signups via Clerk
- Email old users to create Clerk accounts
- Link existing API keys to Clerk accounts

---

## ✅ **Summary**

**Use Clerk for:**
- ✅ User signup/login
- ✅ Email verification  
- ✅ Password management
- ✅ User sessions
- ✅ Dashboard authentication

**Keep your system for:**
- ✅ API key generation (after Clerk login)
- ✅ Usage tracking
- ✅ Billing
- ✅ API authentication (API keys, not Clerk JWT)

**Best of both worlds!** 🎉

---

## 📁 **Next Steps**

1. Create Clerk account
2. Build dashboard (Next.js)
3. Integrate Clerk auth
4. Add API key management UI
5. Update landing page to redirect to Clerk
6. Deploy dashboard
7. Test end-to-end flow

**Clerk makes everything professional and secure!** 🔐
