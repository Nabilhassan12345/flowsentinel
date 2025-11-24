# 🚀 FlowSentinel Setup & Run Instructions

## Quick Start (Both Frontend + Backend)

### 1. Start Backend Server

```bash
# Terminal 1 - Backend
cd /Users/nabilhassan/Desktop/flowsentinel

# Activate virtual environment (create if needed)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file for backend
cat > .env << EOF
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
SLACK_WEBHOOK_URL=your_slack_webhook_url
DATABASE_URL=sqlite:///./flowsentinel.db
EOF

# Start backend
python src/main.py
```

Backend will run at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

### 2. Start Frontend Server

```bash
# Terminal 2 - Frontend (in a NEW terminal)
cd /Users/nabilhassan/Desktop/flowsentinel/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will run at: **http://localhost:8080**

### 3. Access the Application

Open your browser and go to: **http://localhost:8080**

The frontend will automatically proxy all API calls to the backend at `http://localhost:8000`

---

## ✅ What's Connected

### Frontend → Backend Communication

The frontend is configured to communicate with the backend through:

1. **Development Mode** (npm run dev):
   - Frontend: `http://localhost:8080`
   - Backend: `http://localhost:8000`
   - All `/api/*` requests from frontend are proxied to backend
   - Example: `GET /api/state/latest` → `http://localhost:8000/state/latest`

2. **API Client** (`frontend/src/lib/api.ts`):
   - Uses Axios with base URL from `VITE_API_BASE_URL`
   - Automatically handles JSON requests/responses
   - Error interceptor for debugging

3. **CORS Enabled**:
   - Backend has CORS middleware allowing all origins
   - No cross-origin issues during development

---

## 📋 Testing the Integration

### Test 1: Check Backend Health
```bash
curl http://localhost:8000/
```
Should return: `{"message":"FlowSentinel API","version":"2.0.0"}`

### Test 2: Check API Documentation
Open: http://localhost:8000/docs

You should see all 37 API endpoints

### Test 3: Test Frontend Connection

With both servers running:
1. Open http://localhost:8080
2. Open browser DevTools (F12) → Console tab
3. Navigate to Dashboard page
4. You should see API calls being made successfully
5. Check Network tab for `/api/state/latest`, `/api/events/list`, etc.

### Test 4: Test a Specific Endpoint

From frontend, the Dashboard page calls:
- `GET /api/state/latest` - Project state
- `GET /api/events/list?limit=10` - Recent events
- `GET /api/agent/status` - Agent status
- `GET /api/analytics/summary` - Analytics

All should return data from the backend.

---

## 🔧 Configuration Files

### Backend Configuration
- `.env` - Backend environment variables (API keys, database URL)
- `src/main.py` - Main FastAPI application
- Port: 8000

### Frontend Configuration
- `frontend/.env` - Development environment (`VITE_API_BASE_URL=/api`)
- `frontend/.env.production` - Production environment
- `frontend/vite.config.ts` - Vite proxy configuration
- Port: 8080

---

## 🎯 Common Issues & Solutions

### Issue: "Failed to fetch" errors in frontend

**Solution:**
1. Make sure backend is running: `curl http://localhost:8000/`
2. Check backend logs for errors
3. Verify CORS is enabled in `src/main.py`

### Issue: Port already in use

**Backend (8000):**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

**Frontend (8080):**
```bash
# Find and kill process
lsof -ti:8080 | xargs kill -9
```

### Issue: npm install fails

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Backend database errors

**Solution:**
```bash
# Delete old database and recreate
rm flowsentinel.db
python src/main.py
# Database will be automatically created
```

---

## 📊 Monitoring in Real-Time

### Backend Logs
Watch the terminal running `python src/main.py` for:
- API request logs
- Database queries
- Error messages
- Agent activity

### Frontend Logs
1. Open http://localhost:8080
2. Press F12 → Console tab
3. Watch for:
   - API calls
   - Component renders
   - Errors/warnings

### Database Inspection
```bash
# If using SQLite
sqlite3 flowsentinel.db
sqlite> .tables
sqlite> SELECT * FROM events LIMIT 5;
sqlite> .exit
```

---

## 🚀 Available Pages

Once both servers are running, you can access:

- **Dashboard**: http://localhost:8080/
  - Real-time project status
  - Event feed
  - Analytics metrics
  - Agent status

- **Intelligence**: http://localhost:8080/intelligence
  - AI Q&A interface
  - Deadline risk predictions
  - Bottleneck detection
  - Team health monitoring

- **API Docs**: http://localhost:8000/docs
  - Interactive API documentation
  - Test endpoints directly
  - View schemas

---

## 💾 Adding Test Data

### Option 1: Use the API Documentation UI
1. Go to http://localhost:8000/docs
2. Find "POST /events/add"
3. Click "Try it out"
4. Add test event:
```json
{
  "source": "slack",
  "type": "message",
  "data": {
    "user": "john",
    "channel": "dev-team",
    "message": "Bug fixed in authentication module"
  }
}
```
5. Click "Execute"

### Option 2: Use curl
```bash
curl -X POST http://localhost:8000/events/add \
  -H "Content-Type: application/json" \
  -d '{
    "source": "github",
    "type": "pull_request",
    "data": {
      "repo": "flowsentinel",
      "action": "opened",
      "pr_number": 123
    }
  }'
```

### Option 3: Run Demo Script
```bash
python tests/demo.py
```

Then refresh the Dashboard to see the new events!

---

## 🎨 Development Workflow

### Making Backend Changes
1. Edit files in `src/`
2. FastAPI auto-reloads on file changes
3. Refresh browser to see changes
4. Check terminal for errors

### Making Frontend Changes
1. Edit files in `frontend/src/`
2. Vite hot-reloads automatically
3. Changes appear instantly in browser
4. Check browser console for errors

### Adding New API Endpoints
1. Add endpoint in `src/main.py` or endpoint modules
2. Update TypeScript types in `frontend/src/lib/api.ts`
3. Use the endpoint in React components
4. Test in API docs first: http://localhost:8000/docs

---

## 📦 Production Deployment

### Frontend (Netlify)
```bash
# Build frontend
cd frontend
npm run build

# Deploy to Netlify (automatic via GitHub)
git add .
git commit -m "Deploy frontend"
git push origin main
```

### Backend (Render/Railway/Fly.io)
The backend needs to be deployed separately. Options:
1. **Render**: Connect GitHub repo, auto-deploy
2. **Railway**: One-click deployment
3. **Fly.io**: `fly launch` command

Update `frontend/.env.production` with backend URL:
```
VITE_API_BASE_URL=https://your-backend-url.com
```

---

## ✨ Features to Try

1. **Real-time Updates**: Leave Dashboard open, add events via API docs, watch them appear
2. **AI Intelligence**: Go to Intelligence page, ask questions about your project
3. **Analytics**: View event trends, velocity, and risk scores
4. **Multi-team**: Create teams and see isolated event streams
5. **Autonomous Agent**: Start the agent to auto-analyze events every 5 minutes

---

## 🆘 Need Help?

Check:
1. Both terminals for error messages
2. Browser DevTools Console (F12)
3. API Documentation: http://localhost:8000/docs
4. Backend logs in terminal
5. Network tab in DevTools

Common commands:
```bash
# Restart backend
cd /Users/nabilhassan/Desktop/flowsentinel
python src/main.py

# Restart frontend
cd /Users/nabilhassan/Desktop/flowsentinel/frontend
npm run dev

# Check what's running on ports
lsof -ti:8000  # Backend
lsof -ti:8080  # Frontend
```

---

**Status**: ✅ Frontend and Backend are fully integrated and ready to run!
