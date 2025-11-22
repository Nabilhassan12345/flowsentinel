"""
FlowSentinel Database Configuration

SQLAlchemy engine and session management.
Supports PostgreSQL (production), MySQL, and SQLite (development).
"""

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from src.models import Base

# Load environment variables
load_dotenv()


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./flowsentinel.db",  # Default to SQLite for development
)

# Create engine
# For production PostgreSQL, use:
# postgresql://user:password@localhost:5432/flowsentinel
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL in debug mode
    poolclass=NullPool if "sqlite" in DATABASE_URL else None,  # SQLite doesn't need pooling
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Max connections (ignored for SQLite)
    max_overflow=20,  # Max overflow connections (ignored for SQLite)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# DATABASE UTILITIES
# ============================================================================


def init_db():
    """
    Initialize database (create all tables).
    Call this once when starting the application.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints.
    Provides a database session and ensures it's closed after use.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(ItemDB).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_context() as db:
            db.add(item)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """
    Drop and recreate all tables (USE WITH CAUTION).
    Only use in development/testing.
    """
    if os.getenv("ENVIRONMENT", "development") == "production":
        raise RuntimeError("❌ Cannot reset database in production!")
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset successfully")


# ============================================================================
# HEALTH CHECK
# ============================================================================


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    Returns True if connected, False otherwise.
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print(f"📊 Database URL: {DATABASE_URL}")
    
    # Initialize database
    init_db()
    
    # Check connection
    if check_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Example: Create a session and query
    with get_db_context() as db:
        from src.models import EventDB
        
        # Count events
        count = db.query(EventDB).count()
        print(f"📈 Total events in database: {count}")
