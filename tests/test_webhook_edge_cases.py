"""
Additional Webhook Edge Case Tests
Tests corner cases, error handling, and production scenarios.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from datetime import datetime
import time

from src.main import app
from src.database import init_db, reset_db

# Initialize test database
reset_db()
init_db()

# Create test client
client = TestClient(app)


def test_multiple_webhooks_same_event():
    """Test that multiple webhooks can listen to the same event."""
    print("\n🧪 Test 1: Multiple webhooks for same event type")
    
    # Create 3 webhooks for event.created
    webhooks = []
    for i in range(3):
        resp = client.post("/webhooks", json={
            "url": f"https://webhook.site/multi-{i}",
            "events": ["event.created"],
            "description": f"Webhook {i+1}",
            "active": True
        })
        webhooks.append(resp.json()["id"])
    
    time.sleep(0.5)
    
    # Get initial counts
    initial_counts = []
    for wid in webhooks:
        data = client.get(f"/webhooks/{wid}").json()
        initial_counts.append(data["trigger_count"])
    
    # Trigger one event
    client.post("/events/ingest", json={
        "id": "multi_test_1",
        "source": "slack",
        "type": "message",
        "timestamp": datetime.now().isoformat(),
        "data": {"test": "multiple webhooks"},
        "processed": False
    })
    
    time.sleep(1.0)
    
    # Check all webhooks were triggered
    triggered_count = 0
    for i, wid in enumerate(webhooks):
        data = client.get(f"/webhooks/{wid}").json()
        if data["trigger_count"] > initial_counts[i]:
            triggered_count += 1
    
    assert triggered_count == 3, f"Expected 3 webhooks triggered, got {triggered_count}"
    print(f"✅ All 3 webhooks triggered for same event")


def test_webhook_with_multiple_events():
    """Test webhook that listens to multiple event types."""
    print("\n🧪 Test 2: Single webhook listening to multiple events")
    
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/multi-event",
        "events": ["event.created", "state.changed", "action.taken"],
        "description": "Catches all events",
        "active": True
    })
    webhook_id = resp.json()["id"]
    
    time.sleep(0.5)
    
    initial = client.get(f"/webhooks/{webhook_id}").json()
    initial_count = initial["trigger_count"]
    
    # Trigger event.created
    client.post("/events/ingest", json={
        "id": "multi_event_test",
        "source": "github",
        "type": "pr_merged",
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "processed": False
    })
    
    time.sleep(1.0)
    
    final = client.get(f"/webhooks/{webhook_id}").json()
    assert final["trigger_count"] > initial_count
    
    print(f"✅ Webhook triggered: {initial_count} → {final['trigger_count']}")


def test_inactive_webhook_not_triggered():
    """Test that inactive webhooks don't get triggered."""
    print("\n🧪 Test 3: Inactive webhooks are not triggered")
    
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/inactive-test",
        "events": ["event.created"],
        "active": False  # Inactive!
    })
    webhook_id = resp.json()["id"]
    
    time.sleep(0.5)
    
    initial = client.get(f"/webhooks/{webhook_id}").json()
    initial_count = initial["trigger_count"]
    
    # Try to trigger
    client.post("/events/ingest", json={
        "id": "inactive_test",
        "source": "slack",
        "type": "message",
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "processed": False
    })
    
    time.sleep(1.0)
    
    final = client.get(f"/webhooks/{webhook_id}").json()
    assert final["trigger_count"] == initial_count, "Inactive webhook should not trigger"
    
    print(f"✅ Inactive webhook not triggered (count stayed at {initial_count})")


def test_webhook_different_event_not_triggered():
    """Test webhook only triggers on subscribed events."""
    print("\n🧪 Test 4: Webhook filters by event type")
    
    # Webhook only for state.changed
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/state-only",
        "events": ["state.changed"],  # Only this event
        "active": True
    })
    webhook_id = resp.json()["id"]
    
    time.sleep(0.5)
    
    initial = client.get(f"/webhooks/{webhook_id}").json()
    initial_count = initial["trigger_count"]
    
    # Trigger event.created (different event!)
    client.post("/events/ingest", json={
        "id": "wrong_event_test",
        "source": "slack",
        "type": "message",
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "processed": False
    })
    
    time.sleep(1.0)
    
    final = client.get(f"/webhooks/{webhook_id}").json()
    # Should NOT have triggered (event.created vs state.changed)
    assert final["trigger_count"] == initial_count
    
    print(f"✅ Webhook correctly ignored non-subscribed event")


def test_batch_event_ingestion():
    """Test webhooks trigger for batch event ingestion."""
    print("\n🧪 Test 5: Batch event ingestion triggers webhooks")
    
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/batch-test",
        "events": ["event.created"],
        "active": True
    })
    webhook_id = resp.json()["id"]
    
    time.sleep(0.5)
    
    initial = client.get(f"/webhooks/{webhook_id}").json()
    initial_count = initial["trigger_count"]
    
    # Batch ingest 3 events
    events = [
        {
            "id": f"batch_event_{i}",
            "source": "github",
            "type": "pr_merged",
            "timestamp": datetime.now().isoformat(),
            "data": {"pr": i},
            "processed": False
        }
        for i in range(3)
    ]
    
    client.post("/events/ingest/batch", json=events)
    
    time.sleep(1.5)
    
    final = client.get(f"/webhooks/{webhook_id}").json()
    triggered = final["trigger_count"] - initial_count
    
    # Should trigger 3 times (once per event)
    assert triggered == 3, f"Expected 3 triggers, got {triggered}"
    
    print(f"✅ Batch ingestion triggered webhook 3 times: {initial_count} → {final['trigger_count']}")


def test_webhook_url_with_special_characters():
    """Test webhook with complex URL."""
    print("\n🧪 Test 6: Webhook URL with query parameters")
    
    complex_url = "https://webhook.site/test-123?token=abc123&user=admin&project=flowsentinel"
    
    resp = client.post("/webhooks", json={
        "url": complex_url,
        "events": ["event.created"],
        "active": True
    })
    
    assert resp.status_code == 201
    data = resp.json()
    assert data["url"] == complex_url
    
    print(f"✅ Complex URL accepted: {complex_url[:50]}...")


def test_webhook_long_events_list():
    """Test webhook with many event types."""
    print("\n🧪 Test 7: Webhook with many event subscriptions")
    
    many_events = [
        "event.created",
        "event.updated",
        "event.deleted",
        "state.changed",
        "action.taken",
        "user.login",
        "user.logout",
        "system.error",
        "system.warning",
        "deployment.started"
    ]
    
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/many-events",
        "events": many_events,
        "active": True
    })
    
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["events"]) == 10
    
    print(f"✅ Webhook with {len(many_events)} event types created")


def test_update_webhook_events():
    """Test updating webhook to add/remove events."""
    print("\n🧪 Test 8: Update webhook event subscriptions")
    
    # Create with 1 event
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/update-events",
        "events": ["event.created"],
        "active": True
    })
    webhook_id = resp.json()["id"]
    
    # Update to add more events
    update_resp = client.patch(f"/webhooks/{webhook_id}", json={
        "events": ["event.created", "state.changed", "action.taken"]
    })
    
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert len(updated["events"]) == 3
    
    print(f"✅ Updated webhook events: 1 → 3 subscriptions")


def test_webhook_stats_accuracy():
    """Test that webhook statistics are accurate."""
    print("\n🧪 Test 9: Webhook statistics accuracy")
    
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/stats-test",
        "events": ["event.created"],
        "active": True
    })
    webhook_id = resp.json()["id"]
    
    time.sleep(0.5)
    
    # Manually trigger 3 times
    for i in range(3):
        client.post(f"/webhooks/{webhook_id}/trigger", json={"test": i})
        time.sleep(0.3)
    
    # Check stats
    final = client.get(f"/webhooks/{webhook_id}").json()
    
    # Should be: 1 (initial test) + 3 (manual triggers) = 4
    assert final["trigger_count"] >= 4
    assert final["last_triggered"] is not None
    
    print(f"✅ Statistics accurate: {final['trigger_count']} triggers recorded")


def test_webhook_description_update():
    """Test updating webhook description."""
    print("\n🧪 Test 10: Update webhook description")
    
    resp = client.post("/webhooks", json={
        "url": "https://webhook.site/desc-test",
        "events": ["event.created"],
        "description": "Original description",
        "active": True
    })
    webhook_id = resp.json()["id"]
    
    # Update description
    update_resp = client.patch(f"/webhooks/{webhook_id}", json={
        "description": "Updated description with more details"
    })
    
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["description"] == "Updated description with more details"
    
    print(f"✅ Description updated successfully")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 WEBHOOK EDGE CASES TEST SUITE")
    print("=" * 60)
    
    try:
        test_multiple_webhooks_same_event()
        test_webhook_with_multiple_events()
        test_inactive_webhook_not_triggered()
        test_webhook_different_event_not_triggered()
        test_batch_event_ingestion()
        test_webhook_url_with_special_characters()
        test_webhook_long_events_list()
        test_update_webhook_events()
        test_webhook_stats_accuracy()
        test_webhook_description_update()
        
        print("\n" + "=" * 60)
        print("✅ ALL EDGE CASE TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Test Summary:")
        print("   ✅ 10 edge case scenarios tested")
        print("   ✅ Multiple webhooks per event")
        print("   ✅ Multiple events per webhook")
        print("   ✅ Inactive webhook filtering")
        print("   ✅ Event type filtering")
        print("   ✅ Batch ingestion support")
        print("   ✅ Complex URL handling")
        print("   ✅ Large event lists")
        print("   ✅ Dynamic updates")
        print("   ✅ Statistics tracking")
        print("\n🎉 Webhook system production-ready!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
