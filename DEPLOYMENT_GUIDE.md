# 🚀 FlowSentinel PostgreSQL Setup & Cloud Deployment Guide

This guide walks you through setting up PostgreSQL locally and deploying to production.

---

## 📋 Prerequisites

- **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop))
- **Python 3.11+** installed
- **Git** installed
- **GitHub account** (for Render deployment)

---

## 🐘 PHASE 2: PostgreSQL Setup (1 hour)

### Step 2.1: Install Docker Desktop (15 min)

1. **Download Docker Desktop**:
   - Visit: https://www.docker.com/products/docker-desktop
   - Choose your OS (macOS, Windows, or Linux)
   - Install and launch Docker Desktop

2. **Verify Installation**:
   ```bash
   docker --version
   # Should show: Docker version 24.x.x or higher
   
   docker ps
   # Should show: Empty list (no errors)
   ```

### Step 2.2: Start PostgreSQL with Docker Compose (5 min)

Our project already has a `docker-compose.yml` configured! Just run:

```bash
# Start PostgreSQL database
docker-compose up postgres -d

# Verify it's running
docker ps | grep flowsentinel-db
# Should show: flowsentinel-db container running on port 5432

# Check logs
docker-compose logs postgres
# Should see: "database system is ready to accept connections"
```

**What this does**:
- ✅ Creates PostgreSQL 15 database
- ✅ Sets username: `flowsentinel`
- ✅ Sets password: `flowsentinel123`
- ✅ Creates database: `flowsentinel`
- ✅ Exposes on port: `5432`
- ✅ Persistent storage with Docker volumes

### Step 2.3: Update Environment Variables (Already Done! ✅)

The `.env` file has already been updated with:
```bash
DATABASE_URL=postgresql://flowsentinel:flowsentinel123@localhost:5432/flowsentinel
```

### Step 2.4: Verify Dependencies (Already Installed! ✅)

Check that PostgreSQL drivers are in `requirements.txt`:
```bash
cat requirements.txt | grep -E "sqlalchemy|psycopg2|alembic"
```

Should show:
- ✅ `sqlalchemy==2.0.23`
- ✅ `psycopg2-binary==2.9.9`
- ✅ `alembic==1.12.1`

### Step 2.5: Test Database Connection (5 min)

```bash
# Method 1: Using Docker exec
docker exec -it flowsentinel-db psql -U flowsentinel -d flowsentinel -c "SELECT version();"

# Method 2: Using Python
python -c "
import sys
sys.path.insert(0, 'src')
from database import test_connection
test_connection()
"
```

**Expected output**:
```
✅ Database connection successful
✅ PostgreSQL version: PostgreSQL 15.x
```

### Step 2.6: Initialize Database & Start Backend (10 min)

```bash
# Start the FlowSentinel backend
cd src && python main.py

# OR using the full path
python -m src.main
```

**Expected startup logs**:
```
🚀 FlowSentinel v2.0.0 Starting...
✅ Database initialized
✅ Database connection successful
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The database tables will be **automatically created** on first startup!

### Step 2.7: Test Data Persistence (10 min)

Open Swagger UI: http://localhost:8000/docs

**Test Sequence**:

1. **Create Simulation Data**:
   ```bash
   POST /simulation/run
   # Click "Execute"
   # Response: 200 OK with simulation results
   ```

2. **Run Agent Analysis**:
   ```bash
   POST /agent/run
   # Click "Execute"
   # Response: Project state with status (GREEN/YELLOW/RED)
   ```

3. **Check State**:
   ```bash
   GET /state/latest
   # Click "Execute"
   # Response: Shows current project state
   ```

4. **STOP the backend** (Ctrl+C in terminal)

5. **START the backend again**:
   ```bash
   python -m src.main
   ```

6. **Check State Again**:
   ```bash
   GET /state/latest
   # Should show THE SAME data! ✅ Persistence working!
   ```

### Step 2.8: Test All New Features (20 min)

In Swagger UI (http://localhost:8000/docs), test each module:

#### 📊 **Analytics Module** (6 endpoints):
```bash
GET /analytics/summary        # Overall statistics
GET /analytics/risk-score     # Current risk level
GET /analytics/velocity       # Team velocity metrics
GET /analytics/trends         # Historical trends
GET /analytics/timeline       # Event timeline
GET /analytics/health         # System health score
```

#### 👥 **Team Management** (8 endpoints):
```bash
POST /teams                   # Create: {"name": "Apollo Squad", "description": "Backend team"}
GET /teams                    # List all teams
GET /teams/{team_id}          # Get team details
PATCH /teams/{team_id}        # Update team
DELETE /teams/{team_id}       # Delete team
GET /teams/{team_id}/events   # Team events
GET /teams/{team_id}/state    # Team state
GET /teams/{team_id}/analytics # Team analytics
```

#### 🔔 **Webhooks** (7 endpoints):
```bash
POST /webhooks                # Register webhook
                              # Body: {
                              #   "url": "https://webhook.site/YOUR-ID",
                              #   "events": ["event.created"],
                              #   "active": true
                              # }
GET /webhooks                 # List webhooks
GET /webhooks/{webhook_id}    # Get webhook
PATCH /webhooks/{webhook_id}  # Update webhook
DELETE /webhooks/{webhook_id} # Delete webhook
POST /webhooks/test           # Test webhook delivery
POST /webhooks/{webhook_id}/trigger # Manual trigger
```

#### 🤖 **Intelligence/AI** (6 endpoints):
```bash
GET /intelligence/predict-deadline-risk  # Risk prediction
GET /intelligence/predict-bottlenecks    # Bottleneck analysis
POST /intelligence/recommendations       # AI recommendations
GET /intelligence/team-health            # Team health score
GET /intelligence/insights               # Project insights
GET /intelligence/forecast               # 7-day forecast
```

**All working?** ✅ **Database phase complete!**

---

## ☁️ PHASE 3: Cloud Deployment (1.5 hours)

Deploy to Render.com (Free tier available!)

### Step 3.1: Prepare Repository (10 min)

Already done! ✅ Your repo has:
- ✅ `render.yaml` - Deployment configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ Updated `main.py` - PORT environment variable support
- ✅ `docker-compose.yml` - Local development
- ✅ `.env.example` - Template for secrets

### Step 3.2: Push to GitHub (5 min)

```bash
# Add all files
git add .

# Commit changes
git commit -m "Add PostgreSQL support and deployment config"

# Push to GitHub
git push origin main
```

### Step 3.3: Deploy to Render (15 min)

1. **Sign up for Render**:
   - Visit: https://render.com/
   - Sign in with GitHub

2. **Connect Repository**:
   - Click "New +"
   - Select "Blueprint"
   - Connect your `flowsentinel` repository
   - Render will detect `render.yaml` automatically

3. **Review Services**:
   - ✅ `flowsentinel-db` (PostgreSQL)
   - ✅ `flowsentinel-api` (Web Service)
   - Click "Apply"

4. **Wait for Deployment** (~10 min):
   - Database provisions first
   - Backend builds and deploys
   - Watch logs in real-time

### Step 3.4: Configure Environment Variables (10 min)

In Render Dashboard → `flowsentinel-api` → Environment:

**Optional but recommended**:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
```

Click "Save Changes" → Triggers automatic redeployment

### Step 3.5: Test Production Deployment (20 min)

Your API is now live! URL format:
```
https://flowsentinel-api.onrender.com
```

**Test endpoints**:

1. **Health Check**:
   ```bash
   curl https://flowsentinel-api.onrender.com/health
   # Response: {"status": "healthy", ...}
   ```

2. **API Documentation**:
   ```
   https://flowsentinel-api.onrender.com/docs
   ```

3. **Create Data**:
   ```bash
   curl -X POST https://flowsentinel-api.onrender.com/simulation/run
   ```

4. **Check Persistence**:
   ```bash
   # Wait 16+ minutes (free tier sleeps)
   # API wakes up on request
   
   curl https://flowsentinel-api.onrender.com/state/latest
   # Data persists! ✅
   ```

### Step 3.6: Monitor & Maintain (10 min)

**Render Dashboard provides**:
- 📊 **Metrics**: CPU, Memory, Request count
- 📝 **Logs**: Real-time application logs
- 🔔 **Alerts**: Set up email notifications
- 📈 **Events**: Deployment history

**Free Tier Limits**:
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 750 hours/month runtime
- ⚠️ 512MB RAM
- ✅ PostgreSQL: 1GB storage, 90 days retention

**To prevent sleeping** (requires paid plan):
- Upgrade to Starter ($7/month)
- Add cron job to ping every 10 minutes

---

## 🔄 Local Development vs Production

### **Local Development**:
```bash
# Use Docker Compose
docker-compose up

# Access:
# - API: http://localhost:8000
# - Database: localhost:5432
# - Hot reload enabled
```

### **Production (Render)**:
```bash
# Automatic deployment on git push
git push origin main

# Access:
# - API: https://flowsentinel-api.onrender.com
# - Database: Managed by Render (internal)
# - Auto-scaling, SSL, monitoring included
```

---

## 🐛 Troubleshooting

### PostgreSQL Connection Issues:

```bash
# Check if container is running
docker ps | grep flowsentinel-db

# Check logs
docker-compose logs postgres

# Restart container
docker-compose restart postgres

# Reset database (⚠️ deletes all data!)
docker-compose down -v
docker-compose up postgres -d
```

### Backend Won't Start:

```bash
# Check Python path
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Check database URL in .env
cat .env | grep DATABASE_URL
```

### Render Deployment Failed:

1. Check build logs in Render dashboard
2. Verify `requirements.txt` has all dependencies
3. Ensure `render.yaml` is in repo root
4. Check environment variables are set

---

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] PostgreSQL container running (`docker ps`)
- [ ] Database connection successful (test script)
- [ ] Backend starts without errors
- [ ] Data persists after restart
- [ ] All 35+ endpoints working in Swagger
- [ ] Code pushed to GitHub
- [ ] Render.com account created
- [ ] Services deployed on Render
- [ ] Production API responding
- [ ] Production database persisting data

**All checked?** 🎉 **You're done! FlowSentinel is production-ready!**

---

## 📚 Next Steps

1. **Add Custom Domain** (Optional):
   - Render Settings → Custom Domain
   - Point your domain's CNAME to Render

2. **Set Up Monitoring** (Recommended):
   - Render Dashboard → Alerts
   - Configure email notifications

3. **Enable Real Integrations**:
   - Add Slack webhook URL
   - Configure watsonx.ai credentials
   - Connect GitHub/Jira APIs

4. **Scale Up** (When needed):
   - Upgrade to paid plan
   - Increase RAM/CPU
   - Add Redis for caching

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **Docker Docs**: https://docs.docker.com

---

**Created**: November 2025  
**Last Updated**: November 22, 2025  
**Version**: 2.0.0
