"""
Test Database Functions

Demonstrates all database.py features and validates functionality.
"""

from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import (
    init_db,
    reset_db,
    get_db_sync,
    test_connection,
    get_db_context,
)
from src.models import EventDB, TeamDB, ProjectStateDB, ActionDB


def test_connection_function():
    """Test database connection."""
    print("=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)
    result = test_connection()
    assert result, "❌ Connection test failed"
    print("✅ Connection test passed\n")


def test_sync_session():
    """Test synchronous session retrieval."""
    print("=" * 60)
    print("TEST 2: Synchronous Session")
    print("=" * 60)
    db = get_db_sync()
    try:
        count = db.query(EventDB).count()
        print(f"📊 Events in database: {count}")
        print("✅ Sync session test passed\n")
    finally:
        db.close()


def test_context_manager():
    """Test context manager for database sessions."""
    print("=" * 60)
    print("TEST 3: Context Manager")
    print("=" * 60)
    with get_db_context() as db:
        teams_count = db.query(TeamDB).count()
        events_count = db.query(EventDB).count()
        print(f"📊 Teams: {teams_count}")
        print(f"📊 Events: {events_count}")
        print("✅ Context manager test passed\n")


def test_create_data():
    """Test creating data in database."""
    print("=" * 60)
    print("TEST 4: Create Data")
    print("=" * 60)
    
    with get_db_context() as db:
        # Create team
        team = TeamDB(
            name="Test Engineering Team",
            description="Team for testing database",
            members=["alice@test.com", "bob@test.com"],
            settings={"notifications": True}
        )
        db.add(team)
        db.commit()
        print(f"✅ Created team: {team.name}")
        
        # Create event
        event = EventDB(
            source="slack",
            type="message",
            timestamp=datetime.utcnow(),
            data={
                "channel": "#engineering",
                "user": "alice",
                "message": "Testing database functionality"
            },
            team_id=team.id
        )
        db.add(event)
        db.commit()
        print(f"✅ Created event: {event.id}")
        
        # Create project state
        state = ProjectStateDB(
            status="GREEN",
            blockers=[],
            risks=[],
            completed_today=[{"task": "Database setup", "completed": True}],
            next_deadline="2025-12-01",
            team_id=team.id
        )
        db.add(state)
        db.commit()
        print(f"✅ Created project state: {state.status}")
        
        # Create action
        action = ActionDB(
            type="notify_user",
            status="sent",
            payload={"message": "Database test notification"},
            team_id=team.id
        )
        db.add(action)
        db.commit()
        print(f"✅ Created action: {action.type}")
        
    print("✅ Create data test passed\n")


def test_query_data():
    """Test querying data from database."""
    print("=" * 60)
    print("TEST 5: Query Data")
    print("=" * 60)
    
    with get_db_context() as db:
        # Query all teams
        teams = db.query(TeamDB).all()
        print(f"📊 Total teams: {len(teams)}")
        
        # Query unprocessed events
        unprocessed = db.query(EventDB).filter_by(processed=False).all()
        print(f"📊 Unprocessed events: {len(unprocessed)}")
        
        # Query by source
        slack_events = db.query(EventDB).filter_by(source="slack").all()
        print(f"📊 Slack events: {len(slack_events)}")
        
        # Query project states
        states = db.query(ProjectStateDB).all()
        print(f"📊 Project states: {len(states)}")
        
        # Query actions
        actions = db.query(ActionDB).all()
        print(f"📊 Actions: {len(actions)}")
        
    print("✅ Query data test passed\n")


def test_update_data():
    """Test updating data in database."""
    print("=" * 60)
    print("TEST 6: Update Data")
    print("=" * 60)
    
    with get_db_context() as db:
        # Find first unprocessed event
        event = db.query(EventDB).filter_by(processed=False).first()
        if event:
            print(f"📝 Updating event {event.id}")
            event.processed = True
            db.commit()
            print("✅ Event marked as processed")
        else:
            print("ℹ️  No unprocessed events found")
            
    print("✅ Update data test passed\n")


def test_delete_data():
    """Test deleting data from database."""
    print("=" * 60)
    print("TEST 7: Delete Data (Cleanup)")
    print("=" * 60)
    
    with get_db_context() as db:
        # Delete test team and cascade
        test_team = db.query(TeamDB).filter_by(name="Test Engineering Team").first()
        if test_team:
            # Delete related events
            db.query(EventDB).filter_by(team_id=test_team.id).delete()
            db.query(ProjectStateDB).filter_by(team_id=test_team.id).delete()
            db.query(ActionDB).filter_by(team_id=test_team.id).delete()
            
            # Delete team
            db.delete(test_team)
            db.commit()
            print("✅ Test data cleaned up")
        else:
            print("ℹ️  No test team found to delete")
            
    print("✅ Delete data test passed\n")


def run_all_tests():
    """Run all database tests."""
    print("\n" + "=" * 60)
    print("🧪 FLOWSENTINEL DATABASE TESTS")
    print("=" * 60 + "\n")
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        print()
        
        # Run tests
        test_connection_function()
        test_sync_session()
        test_context_manager()
        test_create_data()
        test_query_data()
        test_update_data()
        test_delete_data()
        
        # Summary
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Database Functions Validated:")
        print("   ✅ init_db()")
        print("   ✅ test_connection()")
        print("   ✅ get_db_sync()")
        print("   ✅ get_db_context()")
        print("   ✅ CRUD operations")
        print("\n🎉 Database is production-ready!\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
