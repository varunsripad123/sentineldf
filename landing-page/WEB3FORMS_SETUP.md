# 📧 Web3Forms Setup (2 Minutes)

Web3Forms will send you instant email notifications for every beta signup!

## ✅ Step 1: Get Your Access Key

1. **Go to:** https://web3forms.com
2. **Enter your email:** `varunsripadkota@gmail.com`
3. **Click:** "Create Access Key"
4. **Copy the access key** (looks like: `abc123-def456-ghi789`)

---

## 🔧 Step 2: Add to Local Environment

Create a file called `.env.local` in your landing-page directory:

```bash
NEXT_PUBLIC_WEB3FORMS_KEY=YOUR_ACCESS_KEY_HERE
```

Replace `YOUR_ACCESS_KEY_HERE` with your actual key.

---

## 🚀 Step 3: Add to Netlify

1. **Go to:** Netlify Dashboard → Your site
2. **Click:** "Site configuration" (or "Site settings")
3. **Left sidebar** → Click "Environment variables"
4. **Click:** "Add a variable" → "Add a single variable"
5. **Key:** `NEXT_PUBLIC_WEB3FORMS_KEY`
6. **Value:** Paste your access key
7. **Click:** "Create variable"
8. **Redeploy your site** (Deploys → Trigger deploy → Deploy site)

---

## 📧 What You'll Receive

Every beta signup will email you:

```
To: varunsripadkota@gmail.com
Subject: New SentinelDF Beta Signup

From: SentinelDF Landing Page

email: user@company.com
company: Acme Corp
useCase: Scanning training data for chatbot
```

---

## 🧪 Test It

**After setup:**

1. Visit your live site
2. Fill out beta signup form
3. Submit
4. **Check your email** (arrives in ~10 seconds)
5. ✅ Done!

---

## 💰 Cost

**$0/month** - completely FREE!

- Unlimited form submissions
- Instant email delivery
- No credit card required
- No account needed (just email)

---

## 🔒 Security

- Your access key is in environment variables (not in code)
- Web3Forms has spam protection built-in
- You can revoke and regenerate keys anytime

---

## 📊 View All Submissions

Web3Forms doesn't store submissions (privacy-first), but:

- You get emails for every submission
- Set up email filters/labels in Gmail
- Or forward to a spreadsheet using Zapier (optional)

---

## ✅ Next Steps

1. Get your access key from Web3Forms
2. Add to `.env.local` for local testing
3. Add to Netlify environment variables
4. Push code and redeploy
5. Test the form!
