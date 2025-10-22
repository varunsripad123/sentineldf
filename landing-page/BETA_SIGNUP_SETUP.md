# Beta Signup Setup Instructions

## Current Status
Beta signup form is ready but needs a form service to send submissions to **varunsripadkota@gmail.com**

## Option 1: Formspree (Recommended - 2 minutes setup)

### Steps:
1. Go to https://formspree.io
2. Sign up with `varunsripadkota@gmail.com`
3. Click "New Form"
4. Name: "SentinelDF Beta Signups"
5. Copy your Form ID (e.g., `abc123xyz`)
6. Replace in `landing-page/components/beta-signup.tsx` line 23:
   ```typescript
   fetch('https://formspree.io/f/YOUR_FORM_ID', {
   ```
   Change `YOUR_FORM_ID` to your actual form ID

### What You'll Get:
Every beta signup will email you:
- **Subject:** "SentinelDF Beta Signup: [user@email.com]"
- **Email:** User's work email
- **Company:** Company name (or "Not provided")
- **Use Case:** What they'll use it for
- **Reply-To:** Automatically set to user's email

### Free Tier:
- ✅ 50 submissions/month (upgradable)
- ✅ Email notifications
- ✅ Spam protection
- ✅ CSV export

---

## Option 2: Google Forms

### Steps:
1. Create Google Form at https://forms.google.com
2. Add fields:
   - Email (required)
   - Company Name (optional)
   - Use Case (paragraph text)
3. Go to "Responses" → Click "..." → "Select response destination" → Choose email notifications
4. Get form submission endpoint
5. Update `beta-signup.tsx` to use Google Forms endpoint

---

## Option 3: Custom Backend API (Advanced)

Create API route at `landing-page/app/api/beta-signup/route.ts`:

```typescript
import { NextResponse } from 'next/server'
import nodemailer from 'nodemailer'

export async function POST(request: Request) {
  const { email, company, useCase } = await request.json()
  
  // Configure email transporter
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.GMAIL_USER,
      pass: process.env.GMAIL_APP_PASSWORD, // Use App Password, not regular password
    },
  })
  
  // Send email
  await transporter.sendMail({
    from: process.env.GMAIL_USER,
    to: 'varunsripadkota@gmail.com',
    subject: `SentinelDF Beta Signup: ${email}`,
    text: `New beta signup:\n\nEmail: ${email}\nCompany: ${company || 'Not provided'}\nUse Case: ${useCase || 'Not provided'}`,
    replyTo: email,
  })
  
  return NextResponse.json({ success: true })
}
```

Then update form URL:
```typescript
fetch('/api/beta-signup', {
```

---

## Recommendation

**Use Formspree (Option 1)** for:
- ✅ Fastest setup (2 minutes)
- ✅ No backend coding needed
- ✅ Automatic spam protection
- ✅ Works immediately on Vercel/Netlify
- ✅ No environment variables needed

Choose Option 3 only if you need custom logic or already have email infrastructure.

---

## Testing

After setup, test with:
1. Visit landing page
2. Scroll to "Join Beta Testing"
3. Fill in form with your email
4. Submit
5. Check your inbox for notification

You should receive an email within seconds!
