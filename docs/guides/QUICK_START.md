# 🎯 FlowSentinel - Quick Reference

## ✅ Current Status: FULLY INTEGRATED & RUNNING!

### Running Services
- ✅ **Backend**: http://localhost:8000 (FastAPI)
- ✅ **Frontend**: http://localhost:8080 (React + Vite)
- ✅ **API Docs**: http://localhost:8000/docs
- ✅ **Demo Data**: Loaded (10 events, project state)

---

## 🚀 Quick Commands

### Start Both Servers

**Terminal 1 - Backend:**
```bash
cd /Users/nabilhassan/Desktop/flowsentinel
python src/main.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/nabilhassan/Desktop/flowsentinel/frontend
npm run dev
```

### Add Demo Data
```bash
cd /Users/nabilhassan/Desktop/flowsentinel
python3 add-demo-data.py
```

### Stop Servers
- Press `Ctrl+C` in each terminal

### Kill Stuck Processes
```bash
# Kill backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Kill frontend (port 8080)
lsof -ti:8080 | xargs kill -9
```

---

## 📊 What You Can Do Now

### 1. View Dashboard
- Go to: http://localhost:8080
- See real-time project status
- View recent events
- Check analytics metrics

### 2. Test Intelligence Features
- Navigate to: http://localhost:8080/intelligence
- Ask AI questions
- View risk predictions
- Check bottleneck detection

### 3. Use API Directly
- Go to: http://localhost:8000/docs
- Try any of the 37 endpoints
- Add events, update state, query analytics

### 4. Watch Real-Time Updates
1. Keep Dashboard open in browser
2. Add events via API docs or demo script
3. Watch them appear in real-time (or refresh page)

---

## 🔌 How Frontend Connects to Backend

### Development Setup (Current)
- Frontend runs on port **8080**
- Backend runs on port **8000**
- Vite proxy configured: `/api/*` → `http://localhost:8000/*`
- CORS enabled on backend

### API Calls
All frontend requests go through:
```typescript
// frontend/src/lib/api.ts
const API_BASE_URL = "/api"  // Proxied to backend
```

Example:
- Frontend calls: `GET /api/state/latest`
- Vite proxies to: `http://localhost:8000/state/latest`
- Backend responds with JSON data

---

## 📁 Key Files

### Backend
- `src/main.py` - Main FastAPI app (1,830 lines, 37 endpoints)
- `src/database.py` - Database connection
- `src/models.py` - 7 database models
- `.env` - Backend config (API keys, database URL)

### Frontend
- `frontend/src/App.tsx` - Main React app
- `frontend/src/lib/api.ts` - API client (Axios)
- `frontend/src/pages/Dashboard.tsx` - Main dashboard
- `frontend/src/pages/Intelligence.tsx` - AI features
- `frontend/.env` - Frontend config (`VITE_API_BASE_URL=/api`)
- `frontend/vite.config.ts` - Vite proxy config

### Integration
- `netlify.toml` - Deployment config
- `FULLSTACK_INTEGRATION.md` - Integration guide
- `SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `add-demo-data.py` - Demo data generator

---

## 🧪 Testing the Integration

### Test 1: Backend Health
```bash
curl http://localhost:8000/
```
Expected: `{"message":"FlowSentinel API","version":"2.0.0"}`

### Test 2: Add Event via API
```bash
curl -X POST http://localhost:8000/events/add \
  -H "Content-Type: application/json" \
  -d '{
    "source": "slack",
    "type": "message",
    "data": {"user": "test", "message": "Hello!"}
  }'
```

### Test 3: Check Frontend API Calls
1. Open http://localhost:8080
2. Open DevTools (F12)
3. Go to Network tab
4. Refresh page
5. See API calls to `/api/state/latest`, `/api/events/list`, etc.

---

## 🎨 Available Pages

### Frontend Routes
- `/` - Dashboard (main page)
- `/intelligence` - AI features
- `/analytics` - Analytics & charts (if implemented)
- `/teams` - Team management (if implemented)

### Backend Endpoints (37 total)

**Project State:**
- `GET /state/latest` - Get latest project state
- `POST /state/update` - Update project state
- `GET /state/history` - State history

**Events:**
- `GET /events/list` - List events
- `POST /events/add` - Add event
- `GET /events/{event_id}` - Get specific event
- `GET /events/by-source/{source}` - Filter by source

**Intelligence:**
- `POST /qa/ask` - Ask AI questions
- `GET /intelligence/predict-deadline-risk` - Risk prediction
- `GET /intelligence/predict-bottlenecks` - Bottleneck detection
- `GET /intelligence/team-health` - Team health analysis
- `GET /intelligence/forecast` - 7-day forecast

**Analytics:**
- `GET /analytics/summary` - Analytics summary
- `GET /analytics/trends` - Event trends
- `GET /analytics/velocity` - Team velocity
- `GET /analytics/response-times` - Response times

**Teams:**
- `GET /teams/list` - List all teams
- `POST /teams/create` - Create team
- `GET /teams/{team_id}` - Get team details
- `POST /teams/{team_id}/members` - Add member

**Agent:**
- `POST /agent/start` - Start autonomous agent
- `POST /agent/stop` - Stop agent
- `GET /agent/status` - Agent status

**And more...**

---

## 📈 Project Stats

- **Backend**: 1,830 lines, 37 endpoints, 88% test coverage
- **Frontend**: React + TypeScript, 50+ components
- **Database**: 7 models (SQLite/PostgreSQL)
- **AI**: IBM watsonx.ai Granite 3 8B Instruct
- **Features**: Real-time monitoring, predictive analytics, autonomous agent

---

## 🔧 Configuration

### Backend Environment (.env)
```env
WATSONX_API_KEY=your_key
WATSONX_PROJECT_ID=your_project_id
SLACK_WEBHOOK_URL=your_webhook
DATABASE_URL=sqlite:///./flowsentinel.db
```

### Frontend Environment (frontend/.env)
```env
VITE_API_BASE_URL=/api
```

---

## 🐛 Troubleshooting

### Frontend shows "Failed to fetch"
1. Check backend is running: `curl http://localhost:8000/`
2. Check frontend proxy in `vite.config.ts`
3. Check browser console for errors

### "Address already in use" error
```bash
# Kill process on port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:8080 | xargs kill -9  # Frontend
```

### API calls return 404
- Check endpoint exists: http://localhost:8000/docs
- Verify URL in frontend code
- Check proxy configuration

### Changes not showing
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Clear browser cache
- Check browser console for errors

---

## 📦 Deployment

### Frontend (Netlify)
1. Push to GitHub
2. Netlify auto-deploys from `main` branch
3. Build command: `cd frontend && npm install && npm run build`
4. Publish directory: `frontend/dist`

### Backend (Separate Hosting)
Deploy to Render, Railway, Fly.io, or any cloud provider

Update frontend `.env.production`:
```env
VITE_API_BASE_URL=https://your-backend-url.com
```

---

## 🎉 Next Steps

1. ✅ ~~Merge frontend into backend repo~~ - DONE
2. ✅ ~~Configure API integration~~ - DONE
3. ✅ ~~Add demo data~~ - DONE
4. ⏳ Test all features thoroughly
5. ⏳ Deploy to production
6. ⏳ Submit to IBM watsonx Challenge

---

## 🔗 Important Links

- **GitHub Repo**: https://github.com/Nabilhassan12345/flowsentinel
- **Frontend (Local)**: http://localhost:8080
- **Backend (Local)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Netlify** (when deployed): flowsentinel.netlify.app

---

## 💡 Pro Tips

1. Keep both terminal windows visible to monitor logs
2. Use API docs to test endpoints before frontend implementation
3. Watch browser DevTools Network tab for API debugging
4. Backend auto-reloads on file changes
5. Frontend hot-reloads instantly
6. Add more demo data to see real-time updates

---

**Status**: ✅ **FULLY OPERATIONAL**  
**Integration**: ✅ **WORKING**  
**Demo Data**: ✅ **LOADED**  
**Ready**: ✅ **YES!**
