"""
FlowSentinel Database Configuration

SQLAlchemy engine and session management.
Supports PostgreSQL (production) and SQLite (development).
"""

import os
import sys
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Load environment variables
load_dotenv()

# Import models with proper path handling
try:
    from src.models import Base
except ModuleNotFoundError:
    # If running directly, add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.models import Base


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get database URL from environment
# Default: SQLite for easy local testing
# PostgreSQL: postgresql://user:pass@localhost:5432/flowsentinel
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./flowsentinel.db",
)

# Create engine with appropriate configuration
if "sqlite" in DATABASE_URL:
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for debugging
        connect_args={"check_same_thread": False},  # Needed for SQLite
    )
else:
    # PostgreSQL/MySQL configuration (production)
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for debugging
        pool_size=5,  # Connection pool size
        max_overflow=10,  # Max overflow connections
        pool_pre_ping=True,  # Verify connections before using
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(ItemDB).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE UTILITIES
# ============================================================================


def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def reset_db():
    """Drop all tables and recreate (for testing)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("🔄 Database reset")


def get_db_sync() -> Session:
    """Get database session synchronously (for scripts)."""
    return SessionLocal()


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection successful, False otherwise.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# ============================================================================
# CONTEXT MANAGER (BONUS)
# ============================================================================


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


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print(f"📊 Database URL: {DATABASE_URL}")
    
    # Initialize database
    init_db()
    
    # Test connection
    if test_connection():
        # Example: Create a session and query
        with get_db_context() as db:
            from src.models import EventDB
            
            # Count events
            count = db.query(EventDB).count()
            print(f"📈 Total events in database: {count}")
    else:
        print("❌ Cannot query database - connection failed")
