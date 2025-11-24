# ✅ FlowSentinel - Production Deployment Checklist

Use this checklist to ensure a smooth deployment to production.

## 📋 Pre-Deployment Checklist

### 🔐 Security

- [ ] All API keys stored in environment variables (not hardcoded)
- [ ] `.env` file added to `.gitignore`
- [ ] No sensitive data committed to repository
- [ ] CORS origins restricted in production
- [ ] Database credentials secured
- [ ] IBM watsonx.ai credentials tested and working

### 🧪 Testing

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Test coverage at or above 88%
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Manual testing of critical features completed
- [ ] Demo data script tested
- [ ] API documentation accessible and accurate

### 📚 Documentation

- [ ] README.md updated with current features
- [ ] API documentation current
- [ ] Environment variables documented in `.env.example`
- [ ] Deployment guides reviewed
- [ ] Project structure documented

### 🏗️ Code Quality

- [ ] No `console.log` statements in production frontend code
- [ ] No debug print statements in production backend code
- [ ] Code formatted and linted
- [ ] Type hints added to Python functions
- [ ] TypeScript strict mode enabled
- [ ] No unused imports or variables

### 📦 Dependencies

- [ ] `requirements.txt` up to date
- [ ] `package.json` dependencies reviewed
- [ ] No security vulnerabilities (`npm audit`, `pip check`)
- [ ] Lock files committed (`package-lock.json`, `bun.lockb`)

---

## 🚀 Backend Deployment

### Option 1: Render.com

1. **Create Account**
   - [ ] Sign up at [render.com](https://render.com)
   - [ ] Connect GitHub account

2. **Create Web Service**
   - [ ] New → Web Service
   - [ ] Connect `flowsentinel` repository
   - [ ] Configure settings:
     ```
     Name: flowsentinel-backend
     Environment: Python
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Environment Variables**
   - [ ] Add `WATSONX_API_KEY`
   - [ ] Add `WATSONX_PROJECT_ID`
   - [ ] Add `DATABASE_URL` (if using PostgreSQL)
   - [ ] Add `SLACK_WEBHOOK_URL` (optional)

4. **Database (if using PostgreSQL)**
   - [ ] Create PostgreSQL database on Render
   - [ ] Copy connection string to `DATABASE_URL`

5. **Deploy**
   - [ ] Click "Create Web Service"
   - [ ] Wait for deployment to complete
   - [ ] Test API at: `https://your-app.onrender.com/docs`
   - [ ] Note backend URL for frontend configuration

### Option 2: Railway.app

1. **Setup**
   - [ ] Sign up at [railway.app](https://railway.app)
   - [ ] New Project → Deploy from GitHub

2. **Configuration**
   - [ ] Select `flowsentinel` repository
   - [ ] Railway auto-detects Python
   - [ ] Add environment variables in dashboard

3. **Deploy**
   - [ ] Railway automatically deploys
   - [ ] Get public URL from dashboard
   - [ ] Test deployment

### Option 3: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**
   ```bash
   cd /path/to/flowsentinel
   fly launch
   fly secrets set WATSONX_API_KEY=your_key
   fly secrets set WATSONX_PROJECT_ID=your_project
   fly deploy
   ```

3. **Verify**
   - [ ] Check logs: `fly logs`
   - [ ] Test API: `https://your-app.fly.dev/docs`

---

## 🎨 Frontend Deployment

### Netlify (Recommended)

1. **Connect Repository**
   - [ ] Sign in to [netlify.com](https://netlify.com)
   - [ ] New site from Git
   - [ ] Connect GitHub
   - [ ] Select `flowsentinel` repository

2. **Build Settings**
   - [ ] Verify Netlify detects `netlify.toml`
   - [ ] Build command: `cd frontend && npm install && npm run build`
   - [ ] Publish directory: `frontend/dist`
   - [ ] Node version: 18 or higher

3. **Environment Variables**
   - [ ] Go to Site settings → Environment variables
   - [ ] Add `VITE_API_BASE_URL` = `https://your-backend-url.com`
   - [ ] Example: `https://flowsentinel-backend.onrender.com`

4. **Deploy**
   - [ ] Click "Deploy site"
   - [ ] Wait for build to complete
   - [ ] Visit your site: `https://your-site.netlify.app`

5. **Custom Domain (Optional)**
   - [ ] Go to Domain settings
   - [ ] Add custom domain
   - [ ] Update DNS records

6. **Continuous Deployment**
   - [ ] Push to `main` branch triggers auto-deploy
   - [ ] Monitor deployments in Netlify dashboard

---

## 🧪 Post-Deployment Testing

### Backend Verification

- [ ] API root responds: `GET https://your-backend/`
- [ ] API docs accessible: `https://your-backend/docs`
- [ ] Health check passes
- [ ] Database connection successful
- [ ] Environment variables loaded correctly
- [ ] IBM watsonx.ai integration working

### Frontend Verification

- [ ] Homepage loads correctly
- [ ] Dashboard displays without errors
- [ ] API calls to backend successful (check DevTools Network tab)
- [ ] No console errors in browser
- [ ] All routes accessible
- [ ] Mobile responsive design works
- [ ] Intelligence page AI features working

### Integration Testing

- [ ] Add test event via API docs
- [ ] Verify event appears in frontend dashboard
- [ ] Test autonomous agent trigger
- [ ] Verify analytics calculations
- [ ] Test team creation and management
- [ ] Test webhook delivery

### Performance Testing

- [ ] API response time < 200ms
- [ ] Frontend page load < 3s
- [ ] No memory leaks
- [ ] Database queries optimized
- [ ] API handles concurrent requests

---

## 📊 Monitoring & Maintenance

### Set Up Monitoring

- [ ] Backend logs accessible
- [ ] Frontend error tracking (e.g., Sentry)
- [ ] Uptime monitoring (e.g., UptimeRobot)
- [ ] Performance monitoring
- [ ] Database backup configured

### Regular Maintenance

- [ ] Update dependencies monthly
- [ ] Review and fix security vulnerabilities
- [ ] Monitor database size and performance
- [ ] Review error logs weekly
- [ ] Test backups

---

## 🐛 Common Issues & Solutions

### Backend Won't Start

**Issue**: Port already in use
```bash
# Solution
lsof -ti:8000 | xargs kill -9
```

**Issue**: Database connection fails
- Check `DATABASE_URL` format
- Verify database is accessible
- Check firewall rules

### Frontend Build Fails

**Issue**: npm install fails
```bash
# Solution
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**Issue**: Environment variable not found
- Verify `VITE_API_BASE_URL` is set in Netlify
- Rebuild deployment after adding env vars

### API Calls Fail

**Issue**: CORS errors
- Update `allow_origins` in `src/main.py`
- Add frontend URL to allowed origins

**Issue**: 404 on API calls
- Check backend URL in frontend `.env.production`
- Verify API endpoints exist in backend

---

## 📝 Final Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] Database working
- [ ] All features tested
- [ ] No errors in logs
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team notified of URLs
- [ ] Backup plan in place

---

## 🎉 Deployment Complete!

After completing this checklist:

1. **Share URLs**:
   - Frontend: `https://your-site.netlify.app`
   - Backend: `https://your-backend.onrender.com`
   - API Docs: `https://your-backend.onrender.com/docs`

2. **Update README**:
   - Add live demo links
   - Update deployment status badge

3. **Celebrate**! 🎊
   - Your project is live!
   - Monitor for issues
   - Gather feedback

---

## 📞 Support

If you encounter issues:

1. Check logs (backend and frontend)
2. Review [docs/guides/](guides/)
3. Open GitHub issue
4. Check troubleshooting sections in README

---

**Last Updated**: November 24, 2025
**Status**: Ready for Production ✅
