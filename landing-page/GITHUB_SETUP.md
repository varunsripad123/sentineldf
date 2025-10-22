# 📦 Push Landing Page to GitHub

## Commands to Run

```powershell
# Navigate to landing page directory
cd C:\Users\kvaru\Downloads\Syn\sentineldf\landing-page

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: SentinelDF landing page with Netlify Forms"

# Add your GitHub repository as remote
# REPLACE "YOUR_USERNAME" with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/sentineldf-landing.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

## ⚠️ Important Notes

1. **Replace `YOUR_USERNAME`** with your actual GitHub username in the `git remote add origin` command

2. **If you get authentication errors:**
   - GitHub requires a Personal Access Token (PAT) instead of password
   - Create one at: https://github.com/settings/tokens/new
   - Select scope: `repo` (full control of private repositories)
   - Copy the token and use it as your password when prompted

3. **If git is not installed:**
   ```powershell
   winget install Git.Git
   ```
   Then restart PowerShell

## ✅ Verify Success

After pushing, visit your repository:
```
https://github.com/YOUR_USERNAME/sentineldf-landing
```

You should see all your files!

## 🚀 Next Step: Deploy to Netlify

Once code is pushed to GitHub:
1. Go to https://app.netlify.com/signup
2. Sign up with GitHub (free)
3. Click "Add new site" → "Import an existing project"
4. Select your repository
5. Click "Deploy site"
6. Done! 🎉
