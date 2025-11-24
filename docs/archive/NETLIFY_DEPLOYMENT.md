# Netlify Deployment Guide for FlowSentinel

## 🚀 Deploy to flowsentinel.netlify.app

### Quick Deploy (Recommended)

#### Option 1: Deploy via Netlify CLI

```bash
# 1. Install Netlify CLI (if not installed)
npm install -g netlify-cli

# 2. Login to Netlify
netlify login

# 3. Initialize site (use existing site: flowsentinel)
cd /Users/nabilhassan/Desktop/flowsentinel
netlify init

# When prompted:
# - Choose: "Link this directory to an existing site"
# - Select: flowsentinel
# - Or create new site with name: flowsentinel

# 4. Deploy
netlify deploy --prod

# 5. Open the site
netlify open:site
```

#### Option 2: Deploy via Netlify Dashboard

1. **Go to:** https://app.netlify.com
2. **Login** with your account
3. **Sites** → Find "flowsentinel" or "New site from Git"
4. **Connect GitHub:**
   - Repository: `Nabilhassan12345/flowsentinel`
   - Branch: `main`
5. **Build settings:**
   - Base directory: (leave empty)
   - Build command: `npm run build`
   - Publish directory: `public`
6. **Environment variables** (Add these in Site settings → Environment variables):
   ```
   WATSONX_API_KEY=your_api_key_here
   WATSONX_PROJECT_ID=your_project_id
   SLACK_WEBHOOK_URL=your_webhook_url
   DATABASE_URL=your_postgres_url
   AGENT_ENABLED=true
   ENVIRONMENT=production
   ```
7. **Deploy site**

---

## 📋 Pre-Deployment Checklist

- [x] `netlify.toml` configuration created
- [x] `public/index.html` landing page created
- [x] `package.json` with build scripts
- [ ] GitHub repository is public or accessible to Netlify
- [ ] Environment variables configured in Netlify dashboard
- [ ] Custom domain `flowsentinel.netlify.app` claimed

---

## 🔧 Configuration Details

### netlify.toml
The `netlify.toml` file is already configured with:
- ✅ Build settings (publish: `public`)
- ✅ Redirects for API routes
- ✅ Functions directory setup
- ✅ Environment variables documentation

### Landing Page
The landing page at `public/index.html` includes:
- ✅ Professional design with dark theme
- ✅ Project information and features
- ✅ Statistics and metrics
- ✅ Tech stack showcase
- ✅ Links to GitHub and documentation
- ✅ Responsive design for mobile/tablet/desktop

---

## 🌐 Custom Domain Setup

If using `flowsentinel.netlify.app`:

1. **Go to:** Site settings → Domain management
2. **Site name:** Change to `flowsentinel`
3. **Custom domain:** Your site will be at `flowsentinel.netlify.app`

If using custom domain:

1. **Add custom domain** in Netlify dashboard
2. **Update DNS** with your provider:
   ```
   Type: A
   Name: @
   Value: 75.2.60.5
   
   Type: CNAME
   Name: www
   Value: flowsentinel.netlify.app
   ```
3. **Enable HTTPS** (automatic)

---

## 🚨 Important Notes

### Backend API Deployment

⚠️ **Note:** Netlify is primarily for static sites and serverless functions. For the full FastAPI backend, you have two options:

#### Option A: Keep Backend on Render.com (Recommended)

1. **Backend:** Deploy to Render.com (already configured with `render.yaml`)
   - URL: `https://flowsentinel.onrender.com`
   
2. **Frontend:** Deploy landing page to Netlify
   - URL: `https://flowsentinel.netlify.app`
   
3. **Update API links** in `public/index.html`:
   ```html
   <a href="https://flowsentinel.onrender.com/docs" class="btn btn-secondary">
       🔗 API Documentation
   </a>
   ```

#### Option B: Full Netlify Deployment (Advanced)

Convert FastAPI to Netlify Functions:

1. Create `netlify/functions/api.py`:
   ```python
   from mangum import Mangum
   from src.main import app
   
   handler = Mangum(app)
   ```

2. Install dependencies:
   ```bash
   pip install mangum
   ```

3. Update `requirements.txt`:
   ```
   mangum>=0.17.0
   ```

---

## 🔑 Environment Variables

Set these in Netlify Dashboard → Site settings → Environment variables:

### Required for Backend (if using Netlify Functions)
```bash
WATSONX_API_KEY=your_ibm_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

### Optional
```bash
SLACK_WEBHOOK_URL=your_slack_webhook
DATABASE_URL=postgresql://user:pass@host:5432/db
AGENT_ENABLED=true
ENVIRONMENT=production
```

---

## 📊 Deployment Status

After deployment, verify:

1. **Landing page loads:** `https://flowsentinel.netlify.app`
2. **GitHub link works**
3. **All sections display correctly**
4. **Mobile responsive**
5. **Animations work smoothly**

---

## 🐛 Troubleshooting

### Build Fails

**Issue:** "Build command failed"

**Fix:**
```bash
# Make sure package.json exists
npm init -y

# Update build script
npm pkg set scripts.build="echo 'Static site'"
```

### 404 on Subdirectories

**Issue:** Links to `/intelligence`, `/analytics` show 404

**Fix:** Already configured in `netlify.toml`:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Environment Variables Not Working

**Fix:**
1. Go to Site settings → Environment variables
2. Add each variable individually
3. Redeploy the site

---

## 🚀 Quick Commands

```bash
# Deploy to production
netlify deploy --prod

# Deploy preview (test before prod)
netlify deploy

# Check build logs
netlify watch

# Open site
netlify open:site

# Open admin dashboard
netlify open:admin

# Check status
netlify status

# Link to existing site
netlify link
```

---

## 📝 Post-Deployment Steps

1. **Verify deployment:**
   ```bash
   curl https://flowsentinel.netlify.app
   ```

2. **Update GitHub README** with live URL:
   ```markdown
   **Live Demo:** https://flowsentinel.netlify.app
   ```

3. **Test all links:**
   - GitHub repository link
   - API documentation link (if backend deployed)
   - Social media links (if any)

4. **Enable continuous deployment:**
   - Every push to `main` branch auto-deploys
   - Pull requests create preview deploys

---

## 🎯 What Your Friend Submitted

Since your friend already submitted the project but couldn't shoot the demo, this deployment will:

- ✅ Provide a **live, accessible URL** for judges
- ✅ Showcase the **professional landing page**
- ✅ Display **project features and stats**
- ✅ Link to **GitHub repository**
- ✅ Show **tech stack and architecture**
- ✅ Include **author credits** (Nabil Hassan & Abdulrahman)

The landing page is **demo-ready** and showcases everything without needing the backend running!

---

## 🏆 Success Criteria

After deployment, you should have:

- ✅ Live URL: `https://flowsentinel.netlify.app`
- ✅ Professional landing page
- ✅ All information about the project
- ✅ Links to GitHub repository
- ✅ Credits to authors
- ✅ Mobile-friendly design
- ✅ Fast loading (< 1 second)
- ✅ HTTPS enabled automatically

---

## 📞 Need Help?

If issues arise:

1. **Check build logs:** Netlify dashboard → Deploys → (latest deploy)
2. **Verify files exist:**
   - `netlify.toml`
   - `public/index.html`
   - `package.json`
3. **Contact:** Open issue on GitHub

---

**Ready to deploy!** 🚀

Run: `netlify deploy --prod` and your site will be live!
