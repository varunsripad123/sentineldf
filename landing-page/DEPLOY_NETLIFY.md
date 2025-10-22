# 🚀 Deploy Landing Page to Netlify (FREE)

Your beta signup form is now configured to work with **Netlify Forms** - much better than Google Forms!

## ✅ Why Netlify?

- **100% FREE** forever
- **Unlimited form submissions**
- **Email notifications** to varunsripadkota@gmail.com
- **No CORS issues** (unlike Google Forms)
- **No field IDs needed**
- **Built-in spam protection**
- **Easy deployment** from GitHub

---

## 📋 Step-by-Step Deployment

### 1. Push Code to GitHub

```powershell
cd C:\Users\kvaru\Downloads\Syn\sentineldf\landing-page

# Initialize git (if not already done)
git init
git add .
git commit -m "Add landing page with Netlify Forms"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/sentineldf-landing.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Netlify

1. **Go to:** https://app.netlify.com/signup
2. **Sign up** with GitHub (free account)
3. **Click:** "Add new site" → "Import an existing project"
4. **Connect to GitHub** and select your repository
5. **Build settings:**
   - Build command: `npm run build`
   - Publish directory: `.next`
   - Base directory: (leave empty)
6. **Click:** "Deploy site"

### 3. Enable Form Notifications

1. **After deployment**, go to: **Site settings** → **Forms**
2. **Form notifications** → Click "Add notification"
3. **Select:** "Email notification"
4. **Email to notify:** `varunsripadkota@gmail.com`
5. **Event to notify:** "New form submission"
6. **Select form:** `beta-signup`
7. **Save!**

---

## 📧 What You'll Receive

Every beta signup will email you:

```
Subject: New Netlify Form Submission

Form: beta-signup

Email: user@company.com
Company: Acme Corp
Use Case: Scanning training data for chatbot
```

---

## 🧪 Testing

### Local Testing (Development)
```powershell
npm run dev
```
- Forms will show "success" but won't actually submit
- This is normal - forms only work when deployed to Netlify

### Production Testing (After Deployment)
1. Visit your Netlify URL (e.g., `https://your-site.netlify.app`)
2. Fill out the beta signup form
3. Submit
4. Check:
   - ✅ Success message appears
   - ✅ Email arrives at varunsripadkota@gmail.com
   - ✅ Submission appears in Netlify dashboard under "Forms"

---

## 🎯 Custom Domain (Optional)

Want `sentineldf.com` instead of `.netlify.app`?

1. **Buy domain** (e.g., Namecheap, Google Domains)
2. **In Netlify:** Site settings → Domain management → Add custom domain
3. **Follow instructions** to update DNS records
4. **Free SSL** included automatically!

---

## 🔒 Spam Protection (Built-in)

Netlify Forms includes:
- ✅ Honeypot spam filtering
- ✅ reCAPTCHA (can enable if needed)
- ✅ Rate limiting

---

## 📊 View All Submissions

Anytime:
1. **Login to Netlify**
2. **Your site** → **Forms** tab
3. **See all submissions** in a table
4. **Export to CSV** if needed

---

## 💰 Cost

**$0/month** - completely FREE!

- Unlimited form submissions
- Unlimited email notifications
- 100 GB bandwidth/month
- Automatic HTTPS
- Continuous deployment

---

## 🚀 Quick Deploy Now

```powershell
# 1. Install Netlify CLI (optional, for easier deployment)
npm install -g netlify-cli

# 2. Login
netlify login

# 3. Deploy
cd C:\Users\kvaru\Downloads\Syn\sentineldf\landing-page
netlify deploy --prod
```

---

## ✅ Done!

After deployment, your beta signup form will:
1. ✅ Accept submissions (no 400 errors!)
2. ✅ Email you instantly
3. ✅ Store submissions in Netlify dashboard
4. ✅ Work perfectly with no CORS issues

**Ready to deploy?** Just push to GitHub and connect to Netlify! 🎉
