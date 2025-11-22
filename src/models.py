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

    # Multi-tenant support
    team_id = Column(String(36), nullable=True, index=True)

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
