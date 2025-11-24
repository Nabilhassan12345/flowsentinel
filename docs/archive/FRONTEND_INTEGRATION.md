# Frontend Integration Guide

## 🚀 Quick Integration Steps

### Step 1: Get Frontend Code from Lovable

1. Copy the entire `FRONTEND_PROMPT.md` content
2. Go to https://lovable.dev
3. Create new project: "FlowSentinel Dashboard"
4. Paste the prompt
5. Let it generate the code
6. Download/Export the generated code

### Step 2: Add Frontend to Repo

```bash
# In your flowsentinel directory
cd /Users/nabilhassan/Desktop/flowsentinel

# Create frontend directory
mkdir -p frontend

# Extract the Lovable code into frontend/
# (Lovable will give you a zip file or git repo)
```

### Step 3: Update Frontend API URL

The frontend will need to connect to your backend. Make sure it uses:

```typescript
// In frontend/src/api/client.ts or similar
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
```

Create `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
```

### Step 4: Enable CORS in Backend

Your backend (`src/main.py`) should already have CORS enabled, but verify:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 5: Run Both Backend & Frontend

**Terminal 1 - Backend:**
```bash
cd /Users/nabilhassan/Desktop/flowsentinel/src
python main.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd /Users/nabilhassan/Desktop/flowsentinel/frontend
npm install  # or yarn install
npm run dev  # or yarn dev
# Frontend runs on http://localhost:5173 (or 3000)
```

### Step 6: Test Integration

1. Open frontend URL (e.g., http://localhost:5173)
2. Dashboard should load and fetch data from backend
3. Click "Load Demo Data" button
4. Dashboard should update with demo events
5. Click "Run Analysis" to trigger IBM watsonx.ai
6. Test Q&A by asking a question

### Step 7: Update Docker Setup

Once frontend is working, update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: flowsentinel
      POSTGRES_PASSWORD: flowsentinel
      POSTGRES_DB: flowsentinel
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Create `frontend/Dockerfile`:
```dockerfile
# Build stage
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Step 8: Deploy Together

**For Render.com:**

Update `render.yaml`:
```yaml
services:
  # Backend (already exists)
  - type: web
    name: flowsentinel-backend
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: WATSONX_API_KEY
        sync: false
      - key: SLACK_WEBHOOK_URL
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: flowsentinel-db
          property: connectionString

  # Frontend (new)
  - type: web
    name: flowsentinel-frontend
    env: docker
    dockerfilePath: ./frontend/Dockerfile
    envVars:
      - key: VITE_API_URL
        value: https://flowsentinel-backend.onrender.com

databases:
  - name: flowsentinel-db
    databaseName: flowsentinel
    user: flowsentinel
```

---

## 🔧 Common Issues & Fixes

### Issue 1: CORS Errors

**Symptom:** "Access-Control-Allow-Origin" error in browser console

**Fix:** Make sure backend has CORS middleware enabled (see Step 4)

### Issue 2: API Connection Refused

**Symptom:** "ERR_CONNECTION_REFUSED" or "Network Error"

**Fix:** 
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check frontend API URL is correct
3. Make sure no firewall blocking port 8000

### Issue 3: Environment Variables Not Loading

**Symptom:** API calls go to wrong URL

**Fix:**
1. Create `frontend/.env` file
2. Restart frontend dev server
3. In Vite, use `import.meta.env.VITE_API_URL`

### Issue 4: Build Errors

**Symptom:** npm/yarn errors during build

**Fix:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 Checklist Before Submitting

- [ ] Backend runs on http://localhost:8000
- [ ] Frontend runs on http://localhost:5173 (or 3000)
- [ ] Dashboard loads successfully
- [ ] "Load Demo Data" button works
- [ ] "Run Analysis" triggers AI and updates state
- [ ] Q&A system works
- [ ] Analytics charts display data
- [ ] Events table shows data
- [ ] Agent status widget shows correct info
- [ ] No CORS errors in browser console
- [ ] No API errors in browser console
- [ ] Mobile responsive design works
- [ ] Dark theme looks good
- [ ] All buttons have working functionality

---

## 🎯 What I'll Do When You Share Frontend Code

1. Review the generated code structure
2. Fix any API integration issues
3. Add missing endpoints connections
4. Optimize API calls with React Query
5. Add error handling and loading states
6. Test all features end-to-end
7. Update Docker configuration
8. Create deployment scripts
9. Write frontend README
10. Commit everything to repo

---

## 💡 Tips for Lovable

When chatting with Lovable:

**Start with:**
"Build the dashboard page first with layout, sidebar, and main dashboard view"

**Then ask:**
"Now add the Intelligence page with Q&A interface"

**Then:**
"Add Analytics page with charts using Recharts"

**Be specific:**
"Use Tailwind CSS for styling"
"Use shadcn/ui for components"
"Make it dark theme by default"
"Use IBM blue (#0066CC) as primary color"

**If something doesn't work:**
"The API call to /state/latest is failing. Can you add error handling and show a loading spinner?"

**For styling tweaks:**
"Make the status indicator larger and add a pulsing animation"

---

## 🚀 Ready to Go!

1. Copy `FRONTEND_PROMPT.md` content
2. Go to Lovable
3. Generate the frontend
4. Come back and I'll help integrate it
5. We'll have a full-stack app in no time!

Good luck! 🎉
