# 🚀 Complete Deployment Guide

## 📋 Deployment Overview

FlowSentinel uses a **split deployment** approach:
- **Frontend**: Netlify (Static hosting) ✅ **LIVE**
- **Backend**: Render.com (Python web service) ⏳ **Ready to deploy**
- **Database**: PostgreSQL on Render.com

---

## ✅ Frontend Deployment (Complete!)

### Status: **LIVE**
- **URL**: https://flowsentinel.netlify.app
- **Platform**: Netlify
- **Auto-deploys**: On every push to `main` branch
- **Build**: Vite production build

### Configuration
- Build command: `npm ci --legacy-peer-deps && npm run build`
- Publish directory: `dist`
- Node version: 20

No further action needed - frontend is fully deployed! 🎉

---

## 🔧 Backend Deployment (Next Step)

### Prerequisites
1. ✅ GitHub account with repo access
2. ✅ Render.com account (free tier works)
3. 🔑 IBM watsonx.ai API credentials
4. 🔑 Slack webhook URL (optional)

### Step-by-Step Guide

#### **1. Create Render Account**
```bash
# Go to: https://render.com
# Click "Get Started" or "Sign Up"
# Choose "Sign up with GitHub"
# Authorize Render to access your repositories
```

#### **2. Deploy from Dashboard (Automatic)**

**Option A: Using render.yaml (Recommended)**

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Select repository: `Nabilhassan12345/flowsentinel`
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**
6. Services will be created:
   - `flowsentinel-db` (PostgreSQL)
   - `flowsentinel-api` (Web Service)

**Option B: Manual Web Service Setup**

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect to repository: `Nabilhassan12345/flowsentinel`
4. Configure:
   ```
   Name: flowsentinel-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd src && uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

#### **3. Add Environment Variables** 🔐

**CRITICAL**: Add these in Render dashboard, NOT in your code!

Go to: **Your Service → Environment** tab

| Variable | Value | Required | Where to Get |
|----------|-------|----------|--------------|
| `WATSONX_API_KEY` | Your IBM API key | ✅ Yes | IBM Cloud Console |
| `WATSONX_PROJECT_ID` | Your project ID | ✅ Yes | IBM Cloud Console |
| `WATSONX_URL` | https://us-south.ml.cloud.ibm.com | ✅ Yes | Pre-set |
| `WATSONX_MODEL_ID` | ibm/granite-3-8b-instruct | ✅ Yes | Model name |
| `SLACK_WEBHOOK_URL` | Your webhook URL | ⚠️ Optional | Slack App Settings |
| `DATABASE_URL` | Auto-generated | ✅ Yes | From PostgreSQL service |
| `AGENT_ENABLED` | true | ✅ Yes | Enable autonomous agent |
| `AGENT_RUN_INTERVAL` | 300 | ✅ Yes | Run every 5 minutes |
| `ENVIRONMENT` | production | ✅ Yes | Production mode |
| `CORS_ORIGINS` | https://flowsentinel.netlify.app | ✅ Yes | Your frontend URL |

**How to get IBM watsonx.ai credentials:**

1. Go to https://cloud.ibm.com
2. Navigate to **watsonx.ai**
3. Create or select a project
4. Go to **Manage → Access (IAM)** → **API keys**
5. Create API key → Copy and save it
6. Get Project ID from your watsonx.ai project settings

**How to get Slack webhook (optional):**

1. Go to https://api.slack.com/apps
2. Create new app → "From scratch"
3. Enable **Incoming Webhooks**
4. Add webhook to workspace
5. Copy webhook URL

#### **4. Add PostgreSQL Database**

1. In Render Dashboard: **"New +"** → **"PostgreSQL"**
2. Configure:
   ```
   Name: flowsentinel-db
   Database: flowsentinel
   User: flowsentinel
   Region: Oregon (same as web service)
   Plan: Free
   ```
3. Click **"Create Database"**
4. **Copy the "Internal Database URL"**
5. Add to your web service:
   - Go to web service → **Environment** tab
   - Add `DATABASE_URL` with the internal URL

#### **5. Deploy!**

Render will automatically:
1. Clone your repository
2. Install dependencies (`pip install -r requirements.txt`)
3. Start the server (`uvicorn main:app`)
4. Give you a URL: `https://flowsentinel-backend.onrender.com`

**Initial deployment takes 2-5 minutes.**

---

## 🔗 Connect Frontend to Backend

Once backend is deployed, update the frontend to use it:

### **1. Create Production Environment File**

```bash
# In your local repo
cd /Users/nabilhassan/Desktop/flowsentinel/frontend

# Create production environment file
cat > .env.production << EOL
VITE_API_BASE_URL=https://flowsentinel-backend.onrender.com
EOL
```

### **2. Update Frontend API Client**

The frontend already has API configuration in `src/lib/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

This will automatically use the production URL when deployed.

### **3. Commit and Push**

```bash
git add frontend/.env.production
git commit -m "🔧 Configure production backend URL"
git push origin main
```

Netlify will automatically redeploy with the new backend URL.

---

## 🧪 Testing Deployment

### **Test Backend Health**

```bash
# Check if backend is running
curl https://flowsentinel-backend.onrender.com/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### **Test API Endpoints**

```bash
# Get agent status
curl https://flowsentinel-backend.onrender.com/agent/status

# View API documentation
# Open in browser:
https://flowsentinel-backend.onrender.com/docs
```

### **Test Frontend Connection**

1. Open https://flowsentinel.netlify.app
2. Check browser console for any API errors
3. Navigate to Dashboard - should load data from backend
4. Check Intelligence page - should show AI insights

---

## 🤖 Autonomous Agent Verification

The autonomous agent should:
- ✅ Start automatically when backend deploys
- ✅ Run every 5 minutes (300 seconds)
- ✅ Monitor events from last 24 hours
- ✅ Detect blockers/risks using IBM watsonx.ai
- ✅ Send Slack notifications (if configured)

**Check agent logs:**

1. Go to Render dashboard
2. Your service → **Logs** tab
3. Look for:
   ```
   INFO: Autonomous agent enabled, running every 300 seconds
   INFO: Agent analyzing events...
   INFO: Agent detected X blockers, status: GREEN/YELLOW/RED
   ```

---

## 📊 Post-Deployment Checklist

- [ ] Backend deployed and responding at `/health`
- [ ] Frontend deployed at https://flowsentinel.netlify.app
- [ ] Frontend can connect to backend API
- [ ] PostgreSQL database created and connected
- [ ] Environment variables set (API keys, webhooks)
- [ ] Autonomous agent running (check logs)
- [ ] API documentation accessible at `/docs`
- [ ] CORS configured correctly
- [ ] Slack notifications working (if enabled)

---

## 🔍 Monitoring & Debugging

### **View Logs**

**Backend logs (Render):**
```
Dashboard → Your Service → Logs
```

**Frontend logs (Netlify):**
```
Dashboard → Your Site → Deploys → Deploy Log
```

### **Common Issues**

**Backend won't start:**
- Check environment variables are set
- Verify `DATABASE_URL` is correct
- Check build logs for dependency errors

**Frontend can't connect to backend:**
- Verify `VITE_API_BASE_URL` is correct
- Check CORS configuration on backend
- Ensure backend is not sleeping (free tier)

**Agent not running:**
- Check `AGENT_ENABLED=true` is set
- Verify `AGENT_RUN_INTERVAL` is set
- Check backend logs for agent activity

**Database connection failed:**
- Verify `DATABASE_URL` environment variable
- Check database is running in Render
- Ensure database and web service are in same region

---

## 💰 Cost Overview

### **Current Setup (FREE)**

| Service | Plan | Cost | Limitations |
|---------|------|------|-------------|
| Netlify | Starter | $0 | 100GB bandwidth/month |
| Render Web | Free | $0 | Sleeps after 15min inactivity, 750hrs/month |
| Render PostgreSQL | Free | $0 | 1GB storage, 90 days retention |
| **Total** | | **$0/month** | |

### **Production Setup (Recommended)**

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| Netlify | Pro | $19/month | More bandwidth, analytics |
| Render Web | Starter | $7/month | No sleeping, 512MB RAM |
| Render PostgreSQL | Starter | $7/month | 10GB storage, continuous |
| **Total** | | **$33/month** | Always-on, production-ready |

---

## 🎯 Next Steps

1. **Deploy Backend Now**:
   - Follow steps above to deploy on Render
   - Should take 10-15 minutes total

2. **Add Demo Data**:
   ```bash
   # Once backend is deployed
   python add-demo-data.py --url https://flowsentinel-backend.onrender.com
   ```

3. **Test End-to-End**:
   - Visit https://flowsentinel.netlify.app
   - Check dashboard loads
   - Verify AI insights appear
   - Test autonomous agent status

4. **Monitor for 24 Hours**:
   - Watch Render logs
   - Check agent runs every 5 minutes
   - Verify Slack notifications (if configured)

5. **Submit to IBM Challenge**:
   - Update submission with live URLs
   - Include demo video
   - Document watsonx.ai integration

---

## 🆘 Support

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com

**Netlify Support:**
- Docs: https://docs.netlify.com
- Community: https://answers.netlify.com

**IBM watsonx.ai:**
- Docs: https://www.ibm.com/docs/en/watsonx-as-a-service
- Community: https://community.ibm.com/community/user/watsonai/home

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Full-stack application running 24/7
- ✅ Autonomous AI agent monitoring your workflow
- ✅ Professional URLs for demo/submission
- ✅ Production-ready architecture
- ✅ Automatic deployments on git push

**Live URLs:**
- Frontend: https://flowsentinel.netlify.app
- Backend: https://flowsentinel-backend.onrender.com
- API Docs: https://flowsentinel-backend.onrender.com/docs

Ready to change how teams build software! 🚀
