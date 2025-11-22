# 🗄️ FlowSentinel Database Guide

Complete guide for setting up and managing the FlowSentinel database.

---

## 📋 Table of Contents

1. [Database Models](#database-models)
2. [Supported Databases](#supported-databases)
3. [Setup Instructions](#setup-instructions)
4. [Migrations](#migrations)
5. [Common Operations](#common-operations)

---

## 🏗️ Database Models

### **EventDB**
Stores all ingested events from external sources.

| Column | Type | Description |
|--------|------|-------------|
| id | String(36) | UUID primary key |
| source | String(50) | Event source (slack, jira, github, calendar) |
| type | String(100) | Event type |
| timestamp | DateTime | When the event occurred |
| data | JSON | Full event payload |
| processed | Boolean | Processing status |
| team_id | String(36) | Team identifier (multi-tenant) |
| created_at | DateTime | Record creation time |

**Indexes:**
- `idx_events_timestamp_team` - Fast time-based queries per team
- `idx_events_source_type` - Filter by source and type
- `idx_events_processed_team` - Find unprocessed events

### **ProjectStateDB**
Tracks project health status over time.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment primary key |
| status | String(20) | GREEN, YELLOW, or RED |
| blockers | JSON | Array of blocker objects |
| risks | JSON | Array of risk objects |
| completed_today | JSON | Array of completed work |
| next_deadline | String(100) | Next upcoming deadline |
| last_updated | DateTime | Last analysis time |
| team_id | String(36) | Team identifier |
| created_at | DateTime | Record creation time |

### **ActionDB**
Records all automated actions.

| Column | Type | Description |
|--------|------|-------------|
| id | String(36) | UUID primary key |
| type | String(50) | notify_user, create_task, generate_report |
| status | String(20) | sent, created, completed, failed |
| payload | JSON | Action-specific data |
| timestamp | DateTime | When action was taken |
| team_id | String(36) | Team identifier |
| created_at | DateTime | Record creation time |

### **QAHistoryDB**
Stores Q&A conversation history.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment primary key |
| question | Text | User's question |
| answer | Text | AI-generated answer |
| reasoning | JSON | Array of reasoning steps |
| timestamp | DateTime | When question was asked |
| team_id | String(36) | Team identifier |
| created_at | DateTime | Record creation time |

### **TeamDB**
Multi-tenant team management.

| Column | Type | Description |
|--------|------|-------------|
| id | String(36) | UUID primary key |
| name | String(200) | Team name (unique) |
| description | Text | Team description |
| members | JSON | Array of member IDs/emails |
| settings | JSON | Team configuration |
| created_at | DateTime | Team creation time |
| updated_at | DateTime | Last update time |

### **WebhookDB**
Webhook configurations.

| Column | Type | Description |
|--------|------|-------------|
| id | String(36) | UUID primary key |
| url | String(500) | Webhook URL |
| events | JSON | Event types to trigger on |
| active | Boolean | Webhook enabled/disabled |
| team_id | String(36) | Team identifier |
| created_at | DateTime | Record creation time |

### **AnalyticsDB**
Metrics and analytics data.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment primary key |
| metric_name | String(100) | Metric identifier |
| metric_value | Float | Metric value |
| metadata | JSON | Additional context |
| timestamp | DateTime | When metric was recorded |
| team_id | String(36) | Team identifier |
| created_at | DateTime | Record creation time |

---

## 🗄️ Supported Databases

### **PostgreSQL** (Recommended for Production)
- Best performance for large datasets
- Full JSON support
- ACID compliant
- Excellent for multi-tenant applications

### **MySQL/MariaDB**
- Good performance
- Wide hosting support
- JSON support in modern versions

### **SQLite**
- Perfect for development
- No setup required
- File-based database
- Not recommended for production

---

## 🚀 Setup Instructions

### **Option 1: SQLite (Development)**

No setup required! Just set environment variable:

```bash
# .env
DATABASE_URL=sqlite:///./flowsentinel.db
```

Run migrations:
```bash
python -c "from src.database import init_db; init_db()"
```

### **Option 2: PostgreSQL (Production)**

**1. Install PostgreSQL:**
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

**2. Create Database:**
```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE flowsentinel;
CREATE USER flowsentinel_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE flowsentinel TO flowsentinel_user;
\q
```

**3. Update `.env`:**
```bash
DATABASE_URL=postgresql://flowsentinel_user:your_secure_password@localhost:5432/flowsentinel
```

**4. Run Migrations:**
```bash
python -c "from src.database import init_db; init_db()"
```

### **Option 3: Docker PostgreSQL**

```bash
# Start PostgreSQL in Docker
docker run --name flowsentinel-db \
  -e POSTGRES_DB=flowsentinel \
  -e POSTGRES_USER=flowsentinel_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -d postgres:15-alpine

# Update .env
DATABASE_URL=postgresql://flowsentinel_user:your_secure_password@localhost:5432/flowsentinel

# Run migrations
python -c "from src.database import init_db; init_db()"
```

---

## 🔄 Migrations

### **Initialize Alembic:**
```bash
alembic init alembic
```

### **Create Migration:**
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to events table"
```

### **Apply Migrations:**
```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current
```

---

## 📊 Common Operations

### **Check Database Connection:**
```python
from src.database import check_db_connection

if check_db_connection():
    print("✅ Database connected")
else:
    print("❌ Database connection failed")
```

### **Create Sample Data:**
```python
from src.database import get_db_context
from src.models import EventDB, TeamDB
from datetime import datetime

with get_db_context() as db:
    # Create team
    team = TeamDB(
        name="Engineering Team",
        description="Main engineering team",
        members=["alice@example.com", "bob@example.com"]
    )
    db.add(team)
    db.commit()
    
    # Create event
    event = EventDB(
        source="slack",
        type="message",
        timestamp=datetime.utcnow(),
        data={"channel": "#engineering", "message": "Backend is blocked"},
        team_id=team.id
    )
    db.add(event)
    db.commit()
```

### **Query Data:**
```python
from src.database import get_db_context
from src.models import EventDB
from datetime import datetime, timedelta

with get_db_context() as db:
    # Get unprocessed events
    unprocessed = db.query(EventDB).filter_by(processed=False).all()
    
    # Get recent events (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent = db.query(EventDB).filter(EventDB.timestamp >= yesterday).all()
    
    # Get events by source
    slack_events = db.query(EventDB).filter_by(source="slack").all()
```

### **Update Records:**
```python
from src.database import get_db_context
from src.models import EventDB

with get_db_context() as db:
    # Mark event as processed
    event = db.query(EventDB).filter_by(id="event_id_here").first()
    if event:
        event.processed = True
        db.commit()
```

### **Delete Records:**
```python
from src.database import get_db_context
from src.models import EventDB
from datetime import datetime, timedelta

with get_db_context() as db:
    # Delete old events (older than 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    db.query(EventDB).filter(EventDB.timestamp < cutoff).delete()
    db.commit()
```

---

## 🔧 Troubleshooting

### **Connection Refused**
```bash
# Check if PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Restart PostgreSQL
brew services restart postgresql@15  # macOS
sudo systemctl restart postgresql  # Linux
```

### **Authentication Failed**
```bash
# Check PostgreSQL password
psql -U flowsentinel_user -d flowsentinel -h localhost

# Reset password if needed
psql postgres
ALTER USER flowsentinel_user WITH PASSWORD 'new_password';
```

### **Database Not Found**
```bash
# List databases
psql postgres -c "\l"

# Create database
psql postgres -c "CREATE DATABASE flowsentinel;"
```

---

## 📈 Performance Tips

1. **Indexes** - Already created on frequently queried columns
2. **Connection Pooling** - Configured in `database.py`
3. **Batch Operations** - Use bulk insert for multiple records
4. **Pagination** - Use `.limit()` and `.offset()` for large queries
5. **Query Optimization** - Use `.select_related()` to avoid N+1 queries

---

## 🔐 Security

1. **Never commit `.env` file** - Contains database credentials
2. **Use strong passwords** - 16+ characters, mixed case, numbers, symbols
3. **Limit database user permissions** - Only grant necessary privileges
4. **Enable SSL** - For production PostgreSQL connections
5. **Regular backups** - Automate database backups

---

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Need help?** Check the [main README](../README.md) or open an issue!
