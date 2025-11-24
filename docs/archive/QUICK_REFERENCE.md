# 🚀 FlowSentinel Quick Reference

## 📦 One-Line Setup Commands

### Install Docker (First Time Only)
```bash
# Download from: https://www.docker.com/products/docker-desktop
# Then run Docker Desktop application
```

### Setup PostgreSQL Database
```bash
# Automated setup (recommended)
./scripts/setup-postgres.sh

# OR Manual setup
docker-compose up -d postgres
docker exec -it flowsentinel-db psql -U flowsentinel -c "SELECT version();"
```

### Start FlowSentinel Backend
```bash
# Method 1: Direct
cd src && python main.py

# Method 2: With module
python -m src.main

# Method 3: With Docker Compose (includes database)
docker-compose up
```

### Run Tests
```bash
# Full system test
./scripts/test-all.sh

# Integration validation
python validate_integration.py

# Specific tests
pytest tests/test_analytics.py
pytest tests/test_webhooks.py
```

---

## 🔗 Important URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Swagger UI** | http://localhost:8000/docs | Interactive API documentation |
| **ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **Health Check** | http://localhost:8000/health | System health status |
| **Root Info** | http://localhost:8000/ | API version and features |

---

## 📊 API Endpoints Summary

### Core API (8 endpoints)
```bash
GET  /                    # API info and features
GET  /health              # Health check
POST /events/ingest       # Ingest single event
POST /events/ingest/batch # Ingest multiple events
GET  /state/latest        # Get latest project state
POST /simulation/run      # Run simulation
POST /agent/run           # Run analysis agent
GET  /actions/history     # Action history
```

### Analytics (6 endpoints)
```bash
GET /analytics/summary    # Overall statistics
GET /analytics/risk-score # Current risk assessment
GET /analytics/velocity   # Team velocity metrics
GET /analytics/trends     # Historical trends
GET /analytics/timeline   # Event timeline
GET /analytics/health     # System health score
```

### Teams (8 endpoints)
```bash
POST   /teams                      # Create team
GET    /teams                      # List teams
GET    /teams/{team_id}            # Get team
PATCH  /teams/{team_id}            # Update team
DELETE /teams/{team_id}            # Delete team
GET    /teams/{team_id}/events     # Team events
GET    /teams/{team_id}/state      # Team state
GET    /teams/{team_id}/analytics  # Team analytics
```

### Webhooks (7 endpoints)
```bash
POST   /webhooks                      # Register webhook
GET    /webhooks                      # List webhooks
GET    /webhooks/{webhook_id}         # Get webhook
PATCH  /webhooks/{webhook_id}         # Update webhook
DELETE /webhooks/{webhook_id}         # Delete webhook
POST   /webhooks/test                 # Test webhook
POST   /webhooks/{webhook_id}/trigger # Trigger webhook
```

### Intelligence (6 endpoints)
```bash
GET  /intelligence/predict-deadline-risk  # Deadline risk
GET  /intelligence/predict-bottlenecks    # Bottlenecks
POST /intelligence/recommendations        # AI suggestions
GET  /intelligence/team-health            # Team health
GET  /intelligence/insights               # Insights
GET  /intelligence/forecast               # 7-day forecast
```

**Total: 35+ endpoints** ✅

---

## 🐳 Docker Commands

```bash
# Start services
docker-compose up              # Start all (with logs)
docker-compose up -d           # Start all (background)
docker-compose up postgres -d  # Start only database

# Stop services
docker-compose stop            # Stop all
docker-compose stop postgres   # Stop database only
docker-compose down            # Stop and remove containers
docker-compose down -v         # Stop and delete volumes (⚠️ deletes data!)

# View logs
docker-compose logs            # All logs
docker-compose logs postgres   # Database logs only
docker-compose logs -f         # Follow logs (live)

# Restart services
docker-compose restart         # Restart all
docker-compose restart postgres # Restart database

# Check status
docker-compose ps              # List containers
docker ps                      # Running containers

# Database access
docker exec -it flowsentinel-db psql -U flowsentinel -d flowsentinel
```

---

## 🗄️ Database Commands

### Using Docker
```bash
# Connect to database
docker exec -it flowsentinel-db psql -U flowsentinel -d flowsentinel

# Run SQL query
docker exec -it flowsentinel-db psql -U flowsentinel -d flowsentinel -c "SELECT * FROM events LIMIT 5;"

# List tables
docker exec -it flowsentinel-db psql -U flowsentinel -d flowsentinel -c "\dt"

# Backup database
docker exec flowsentinel-db pg_dump -U flowsentinel flowsentinel > backup.sql

# Restore database
docker exec -i flowsentinel-db psql -U flowsentinel -d flowsentinel < backup.sql
```

### Using Python
```python
# Test connection
python -c "
import sys
sys.path.insert(0, 'src')
from database import test_connection
test_connection()
"

# Query database
python -c "
import sys
sys.path.insert(0, 'src')
from database import get_db
from models import EventDB
db = next(get_db())
events = db.query(EventDB).limit(5).all()
for e in events:
    print(f'{e.id}: {e.type} - {e.source}')
"
```

---

## ☁️ Deployment Commands

### Deploy to Render.com
```bash
# Commit changes
git add .
git commit -m "Ready for deployment"

# Push to GitHub
git push origin main

# Render automatically deploys from render.yaml
# Monitor at: https://dashboard.render.com
```

### Manual Deployment (if needed)
```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Deploy
render blueprint launch
```

---

## 🧪 Testing Commands

```bash
# Quick validation (17 tests)
python validate_integration.py

# All tests
pytest

# Specific test files
pytest tests/test_analytics.py
pytest tests/test_webhooks.py
pytest tests/test_teams.py
pytest tests/test_intelligence.py

# With coverage
pytest --cov=src tests/

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

---

## 🔧 Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip freeze > requirements.txt

# Format code (if black installed)
black src/ tests/

# Lint code (if flake8 installed)
flake8 src/ tests/

# Type check (if mypy installed)
mypy src/
```

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database connection
python -c "import sys; sys.path.insert(0, 'src'); from database import test_connection; test_connection()"
```

### Database connection failed
```bash
# Check if PostgreSQL is running
docker ps | grep flowsentinel-db

# Restart PostgreSQL
docker-compose restart postgres

# View PostgreSQL logs
docker-compose logs postgres

# Check .env file
cat .env | grep DATABASE_URL
```

### Docker issues
```bash
# Check Docker status
docker info

# Restart Docker Desktop (macOS/Windows)
# Or restart Docker service (Linux)
sudo systemctl restart docker

# Clean up Docker
docker system prune -a  # Remove unused containers/images
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8001 python -m src.main
```

---

## 📝 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | sqlite:///./flowsentinel.db | Database connection string |
| `PORT` | 8000 | Server port |
| `ENVIRONMENT` | development | Environment mode |
| `SLACK_WEBHOOK_URL` | - | Slack webhook for notifications |
| `WATSONX_API_KEY` | - | IBM watsonx.ai API key |
| `WATSONX_PROJECT_ID` | - | IBM watsonx.ai project ID |

---

## 🎯 Common Workflows

### Fresh Start
```bash
# 1. Install Docker Desktop
# 2. Clone repository
git clone <repo-url>
cd flowsentinel

# 3. Setup database
./scripts/setup-postgres.sh

# 4. Start backend
cd src && python main.py

# 5. Open browser
open http://localhost:8000/docs
```

### Local Development
```bash
# Terminal 1: Database
docker-compose up postgres

# Terminal 2: Backend
cd src && python main.py

# Terminal 3: Tests
pytest --watch
```

### Production Deployment
```bash
# 1. Ensure tests pass
python validate_integration.py

# 2. Commit changes
git add .
git commit -m "Feature: Add XYZ"

# 3. Push to GitHub
git push origin main

# 4. Render auto-deploys
# Monitor: https://dashboard.render.com
```

---

## 📚 Documentation

- **Main README**: `README.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Integration Checklist**: `INTEGRATION_CHECKLIST.md`
- **Integration Report**: `INTEGRATION_COMPLETE.md`
- **Intelligence Features**: `INTELLIGENCE.md`
- **API Documentation**: http://localhost:8000/docs

---

**Last Updated**: November 22, 2025  
**Version**: 2.0.0
