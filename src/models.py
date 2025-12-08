"""
FlowSentinel Database Models

SQLAlchemy ORM models for persistent storage.
Supports PostgreSQL, MySQL, and SQLite.

Models:
- EventDB: Stores all ingested events from various sources
- ProjectStateDB: Tracks project health status over time
- ActionDB: Records all automated actions taken by the system
- QAHistoryDB: Stores Q&A conversation history
- TeamDB: Multi-tenant team management
- WebhookDB: Webhook configurations for external integrations
- AnalyticsDB: Metrics and analytics data
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base class for all models
Base = declarative_base()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def generate_uuid() -> str:
    """Generate a UUID string for primary keys"""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()


# ============================================================================
# DATABASE MODELS
# ============================================================================


class EventDB(Base):
    """
    Stores all events ingested from external sources.
    
    Sources: Slack, Jira, GitHub, Calendar
    Indexed for fast time-based and team-based queries.
    """

    __tablename__ = "events"

    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Event metadata
    source = Column(
        String(50), nullable=False, index=True
    )  # slack, jira, github, calendar
    type = Column(String(100), nullable=False, index=True)  # Event type
    timestamp = Column(DateTime, nullable=False, index=True)  # Event occurred time
    data = Column(JSON, nullable=False)  # Full event payload

    # Processing status
    processed = Column(Boolean, default=False, index=True)

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index("idx_events_timestamp_team", "timestamp", "team_id"),
        Index("idx_events_source_type", "source", "type"),
        Index("idx_events_processed_team", "processed", "team_id"),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, source={self.source}, type={self.type}, timestamp={self.timestamp})>"


class ProjectStateDB(Base):
    """
    Tracks project health status over time.
    
    Status: GREEN (healthy), YELLOW (attention needed), RED (critical)
    Stores blockers, risks, and completed work.
    """

    __tablename__ = "project_states"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Project status
    status = Column(
        String(20), nullable=False, index=True
    )  # GREEN, YELLOW, RED

    # Analysis results (stored as JSON arrays)
    blockers = Column(JSON, nullable=False, default=list)
    risks = Column(JSON, nullable=False, default=list)
    completed_today = Column(JSON, nullable=False, default=list)

    # Next deadline
    next_deadline = Column(String(100), nullable=True)

    # Timestamps
    last_updated = Column(DateTime, nullable=False, default=utc_now)

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index("idx_states_status_team", "status", "team_id"),
        Index("idx_states_updated_team", "last_updated", "team_id"),
    )

    def __repr__(self):
        return f"<ProjectState(id={self.id}, status={self.status}, blockers={len(self.blockers)}, risks={len(self.risks)})>"


class ActionDB(Base):
    """
    Records all automated actions taken by the system.
    
    Types: notify_user, create_task, generate_report
    Status: sent, created, completed, failed
    """

    __tablename__ = "actions"

    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Action metadata
    type = Column(
        String(50), nullable=False, index=True
    )  # notify_user, create_task, generate_report
    status = Column(
        String(20), nullable=False, index=True
    )  # sent, created, completed, failed
    payload = Column(JSON, nullable=False)  # Action-specific data

    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=utc_now, index=True)

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index("idx_actions_type_status", "type", "status"),
        Index("idx_actions_timestamp_team", "timestamp", "team_id"),
    )

    def __repr__(self):
        return f"<Action(id={self.id}, type={self.type}, status={self.status}, timestamp={self.timestamp})>"


class QAHistoryDB(Base):
    """
    Stores question-answer conversation history.
    
    Used for Q&A interface and conversation context.
    """

    __tablename__ = "qa_history"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Q&A data
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    reasoning = Column(JSON, nullable=False, default=list)  # Array of reasoning steps

    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=utc_now, index=True)

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Indexes for performance
    __table_args__ = (Index("idx_qa_timestamp_team", "timestamp", "team_id"),)

    def __repr__(self):
        return f"<QAHistory(id={self.id}, question={self.question[:50]}..., timestamp={self.timestamp})>"


class TeamDB(Base):
    """
    Multi-tenant team management.
    
    Each team has isolated data and settings.
    """

    __tablename__ = "teams"

    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Team metadata
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Team members (stored as JSON array of user IDs/emails)
    members = Column(JSON, nullable=False, default=list)

    # Team settings (stored as JSON object)
    settings = Column(
        JSON,
        nullable=False,
        default=dict,
    )  # notification preferences, integrations, etc.

    # Timestamps
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, members={len(self.members)})>"


class WebhookDB(Base):
    """
    Webhook configurations for external integrations.
    
    Allows external systems to receive notifications on specific events.
    """

    __tablename__ = "webhooks"

    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Webhook configuration
    url = Column(String(500), nullable=False)
    events = Column(
        JSON, nullable=False, default=list
    )  # Event types to trigger on
    active = Column(Boolean, default=True, index=True)
    description = Column(String(500), nullable=True)  # Optional webhook description

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Webhook stats
    trigger_count = Column(Integer, default=0, nullable=False)  # How many times triggered
    last_triggered = Column(DateTime, nullable=True)  # When last triggered
    last_status = Column(String(20), nullable=True)  # Last trigger status (success/failed/error)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Indexes for performance
    __table_args__ = (Index("idx_webhooks_active_team", "active", "team_id"),)

    def __repr__(self):
        return f"<Webhook(id={self.id}, url={self.url}, active={self.active})>"


class AnalyticsDB(Base):
    """
    Metrics and analytics data.
    
    Tracks system performance, usage patterns, and business metrics.
    """

    __tablename__ = "analytics"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Metric data
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_metadata = Column(JSON, nullable=True, default=dict)  # Additional context

    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=utc_now, index=True)

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index("idx_analytics_metric_timestamp", "metric_name", "timestamp"),
        Index("idx_analytics_team_timestamp", "team_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Analytics(id={self.id}, metric={self.metric_name}, value={self.metric_value}, timestamp={self.timestamp})>"


class EmbeddingDB(Base):
    """
    Tracks embedding status for events.
    
    Used to know which events have been indexed in the vector store
    and when they were last updated.
    """

    __tablename__ = "embeddings"

    # Primary key (matches event_id)
    event_id = Column(String(36), primary_key=True)

    # Embedding metadata
    embedded_at = Column(DateTime, default=utc_now, nullable=False)
    model_name = Column(String(100), nullable=True)  # Model used for embedding
    vector_id = Column(String(100), nullable=True)  # ID in vector store
    
    # Content hash to detect if re-embedding is needed
    content_hash = Column(String(64), nullable=True)

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

    # Indexes for performance
    __table_args__ = (
        Index("idx_embeddings_team", "team_id"),
        Index("idx_embeddings_model", "model_name"),
    )

    def __repr__(self):
        return f"<Embedding(event_id={self.event_id}, model={self.model_name}, embedded_at={self.embedded_at})>"


# ============================================================================
# PHASE 7-10 MODELS: Memory, Security, Scalability, Reliability
# ============================================================================


class ConversationDB(Base):
    """
    Stores AI conversation sessions for memory persistence.
    Phase 7: Conversation Memory
    """
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    summary = Column(Text, nullable=True)
    extra_data = Column(JSON, default=dict)  # Renamed from metadata
    team_id = Column(String(36), nullable=True, index=True)

    __table_args__ = (
        Index("idx_conversations_user", "user_id", "created_at"),
    )


class MemoryEntryDB(Base):
    """
    Stores individual memory entries (messages) in conversations.
    Phase 7: Conversation Memory
    """
    __tablename__ = "memory_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    memory_type = Column(String(20), default="short_term")  # short_term, long_term, semantic
    importance = Column(Float, default=0.5)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    extra_data = Column(JSON, default=dict)  # Renamed from metadata

    __table_args__ = (
        Index("idx_memory_conversation", "conversation_id", "timestamp"),
        Index("idx_memory_user_type", "user_id", "memory_type"),
    )


class UserDB(Base):
    """
    Stores user accounts for authentication.
    Phase 8: Security & Auth
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # admin, user, readonly
    created_at = Column(DateTime, default=utc_now, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSON, default=dict)  # Renamed from metadata
    team_id = Column(String(36), nullable=True, index=True)


class APIKeyDB(Base):
    """
    Stores API keys for service authentication.
    Phase 8: Security & Auth
    """
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key_hash = Column(String(255), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(String(36), nullable=False, index=True)
    scopes = Column(JSON, default=list)  # ["read", "write", "admin"]
    created_at = Column(DateTime, default=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class AuditLogDB(Base):
    """
    Stores security audit logs.
    Phase 8: Security & Auth
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(JSON, default=dict)
    severity = Column(String(20), default="info")  # info, warning, error, critical

    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
    )


class CacheEntryDB(Base):
    """
    Stores persistent cache entries (Redis backup).
    Phase 9: Scalability
    """
    __tablename__ = "cache_entries"

    key = Column(String(255), primary_key=True)
    value = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    hits = Column(Integer, default=0)


class TaskDB(Base):
    """
    Stores background task records.
    Phase 9: Scalability
    """
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(20), default="pending", index=True)  # pending, running, completed, failed
    priority = Column(Integer, default=2)  # 0=critical, 4=background
    created_at = Column(DateTime, default=utc_now, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    retries = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    extra_data = Column(JSON, default=dict)  # Renamed from metadata

    __table_args__ = (
        Index("idx_tasks_state_priority", "state", "priority"),
    )


class HealthCheckDB(Base):
    """
    Stores health check history.
    Phase 10: Reliability
    """
    __tablename__ = "health_checks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # healthy, degraded, unhealthy
    response_time_ms = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    details = Column(JSON, default=dict)


class MetricDB(Base):
    """
    Stores application metrics for monitoring.
    Phase 10: Reliability
    """
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    labels = Column(JSON, default=dict)
    metric_type = Column(String(20), default="gauge")  # counter, gauge, histogram

    __table_args__ = (
        Index("idx_metrics_name_time", "name", "timestamp"),
    )


class FeedbackDB(Base):
    """
    Stores AI response feedback for evaluation.
    Phase 3: Evaluation & Feedback
    """
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    response_id = Column(String(100), nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5
    feedback_type = Column(String(20), default="thumbs")  # thumbs, rating, text
    is_correct = Column(Boolean, nullable=True)
    user_feedback = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    user_id = Column(String(36), nullable=True, index=True)
    extra_data = Column(JSON, default=dict)  # Renamed from metadata


class PatternDB(Base):
    """
    Stores detected patterns for similarity matching.
    Phase 4: Pattern Matching
    """
    __tablename__ = "patterns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    pattern_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    events = Column(JSON, default=list)  # List of event IDs
    confidence = Column(Float, default=0.0)
    detected_at = Column(DateTime, default=utc_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(Text, nullable=True)
    extra_data = Column(JSON, default=dict)  # Renamed from metadata
    team_id = Column(String(36), nullable=True, index=True)


# ============================================================================
# MODEL UTILITIES
# ============================================================================


def create_all_tables(engine):
    """
    Create all database tables.
    
    Args:
        engine: SQLAlchemy engine instance
    
    Example:
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://user:pass@localhost/flowsentinel')
        create_all_tables(engine)
    """
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """
    Drop all database tables (USE WITH CAUTION).
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Create SQLite database
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create engine (SQLite for demo, use PostgreSQL in production)
    engine = create_engine("sqlite:///flowsentinel.db", echo=True)

    # Create all tables
    create_all_tables(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create sample team
    team = TeamDB(
        name="Demo Team",
        description="A demo team for testing",
        members=["user1@example.com", "user2@example.com"],
        settings={"notifications_enabled": True, "slack_channel": "#general"},
    )
    session.add(team)
    session.commit()

    # Create sample event
    event = EventDB(
        source="slack",
        type="message",
        timestamp=datetime.utcnow(),
        data={
            "channel": "#engineering",
            "user": "john_doe",
            "message": "Backend is blocked waiting on design schema",
        },
        team_id=team.id,
    )
    session.add(event)
    session.commit()

    print(f"✅ Created team: {team}")
    print(f"✅ Created event: {event}")

    # Query examples
    print("\n📊 Query Examples:")
    print(f"Total events: {session.query(EventDB).count()}")
    print(f"Unprocessed events: {session.query(EventDB).filter_by(processed=False).count()}")
    print(f"Team events: {session.query(EventDB).filter_by(team_id=team.id).count()}")

    session.close()
