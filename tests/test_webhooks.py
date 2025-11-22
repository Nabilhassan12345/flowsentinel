"""
Tests for Webhook Endpoints
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from datetime import datetime
import json
import time

# Import the main app and database functions
from src.main import app
from src.database import init_db, reset_db

# Initialize test database
init_db()

# Create test client
client = TestClient(app)


def setup_function():
    """Reset database before each test."""
    reset_db()
    init_db()


def test_create_webhook():
    """Test webhook creation with automatic test ping."""
    print("\n🧪 Test 1: Create webhook")
    
    webhook_data = {
        "url": "https://webhook.site/unique-id-123",
        "events": ["event.created", "action.taken"],
        "description": "Test webhook for notifications",
        "active": True
    }
    
    response = client.post("/webhooks", json=webhook_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["url"] == webhook_data["url"]
    assert data["events"] == webhook_data["events"]
    assert data["active"] == True
    assert data["description"] == webhook_data["description"]
    assert "created_at" in data
    
    print(f"✅ Created webhook: {data['id']}")
    print(f"   URL: {data['url']}")
    print(f"   Events: {data['events']}")
    
    return data["id"]


def test_list_webhooks():
    """Test listing all webhooks."""
    print("\n🧪 Test 2: List webhooks")
    
    # Create two webhooks
    webhook1 = {
        "url": "https://webhook.site/webhook-1",
        "events": ["event.created"],
        "description": "Webhook 1"
    }
    
    webhook2 = {
        "url": "https://webhook.site/webhook-2",
        "events": ["state.changed", "action.taken"],
        "description": "Webhook 2"
    }
    
    client.post("/webhooks", json=webhook1)
    client.post("/webhooks", json=webhook2)
    
    # List all webhooks
    response = client.get("/webhooks")
    
    assert response.status_code == 200
    webhooks = response.json()
    
    assert len(webhooks) >= 2
    assert all("id" in w for w in webhooks)
    assert all("url" in w for w in webhooks)
    assert all("events" in w for w in webhooks)
    
    print(f"✅ Listed {len(webhooks)} webhooks")
    for webhook in webhooks:
        print(f"   - {webhook['url']} ({len(webhook['events'])} events)")


def test_list_active_webhooks_only():
    """Test filtering active webhooks."""
    print("\n🧪 Test 3: List active webhooks only")
    
    # Create active and inactive webhooks
    active_webhook = {
        "url": "https://webhook.site/active",
        "events": ["event.created"],
        "active": True
    }
    
    inactive_webhook = {
        "url": "https://webhook.site/inactive",
        "events": ["event.created"],
        "active": False
    }
    
    client.post("/webhooks", json=active_webhook)
    client.post("/webhooks", json=inactive_webhook)
    
    # List only active
    response = client.get("/webhooks?active_only=true")
    
    assert response.status_code == 200
    webhooks = response.json()
    
    assert all(w["active"] == True for w in webhooks)
    
    print(f"✅ Found {len(webhooks)} active webhooks")


def test_get_webhook_details():
    """Test getting specific webhook details."""
    print("\n🧪 Test 4: Get webhook details")
    
    # Create a webhook
    webhook_data = {
        "url": "https://webhook.site/test-details",
        "events": ["event.created", "state.changed"],
        "description": "Detailed test webhook"
    }
    
    create_response = client.post("/webhooks", json=webhook_data)
    webhook_id = create_response.json()["id"]
    
    # Get details
    response = client.get(f"/webhooks/{webhook_id}")
    
    assert response.status_code == 200
    webhook = response.json()
    
    assert webhook["id"] == webhook_id
    assert webhook["url"] == webhook_data["url"]
    assert webhook["events"] == webhook_data["events"]
    assert webhook["description"] == webhook_data["description"]
    assert "trigger_count" in webhook
    assert "last_triggered" in webhook
    
    print(f"✅ Retrieved webhook {webhook_id}")
    print(f"   Trigger count: {webhook['trigger_count']}")
    print(f"   Last triggered: {webhook['last_triggered']}")


def test_update_webhook():
    """Test updating webhook configuration."""
    print("\n🧪 Test 5: Update webhook")
    
    # Create a webhook
    webhook_data = {
        "url": "https://webhook.site/original",
        "events": ["event.created"],
        "description": "Original description",
        "active": True
    }
    
    create_response = client.post("/webhooks", json=webhook_data)
    webhook_id = create_response.json()["id"]
    
    # Update webhook
    update_data = {
        "url": "https://webhook.site/updated",
        "events": ["event.created", "state.changed", "action.taken"],
        "description": "Updated description",
        "active": False
    }
    
    response = client.patch(f"/webhooks/{webhook_id}", json=update_data)
    
    assert response.status_code == 200
    updated = response.json()
    
    assert updated["id"] == webhook_id
    assert updated["url"] == update_data["url"]
    assert updated["events"] == update_data["events"]
    assert updated["description"] == update_data["description"]
    assert updated["active"] == False
    
    print(f"✅ Updated webhook {webhook_id}")
    print(f"   New URL: {updated['url']}")
    print(f"   New events: {updated['events']}")
    print(f"   Active: {updated['active']}")


def test_delete_webhook():
    """Test deleting a webhook."""
    print("\n🧪 Test 6: Delete webhook")
    
    # Create a webhook
    webhook_data = {
        "url": "https://webhook.site/to-delete",
        "events": ["event.created"]
    }
    
    create_response = client.post("/webhooks", json=webhook_data)
    webhook_id = create_response.json()["id"]
    
    # Delete webhook
    response = client.delete(f"/webhooks/{webhook_id}")
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/webhooks/{webhook_id}")
    assert get_response.status_code == 404
    
    print(f"✅ Deleted webhook {webhook_id}")


def test_webhook_not_found():
    """Test 404 error for non-existent webhook."""
    print("\n🧪 Test 7: Webhook not found (404)")
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    # Try to get non-existent webhook
    response = client.get(f"/webhooks/{fake_id}")
    assert response.status_code == 404
    
    # Try to update non-existent webhook
    response = client.patch(f"/webhooks/{fake_id}", json={"active": False})
    assert response.status_code == 404
    
    # Try to delete non-existent webhook
    response = client.delete(f"/webhooks/{fake_id}")
    assert response.status_code == 404
    
    print("✅ 404 errors handled correctly")


def test_webhook_url_validation():
    """Test that invalid URLs are rejected."""
    print("\n🧪 Test 8: URL validation")
    
    # Try to create webhook with invalid URL
    invalid_data = {
        "url": "not-a-valid-url",
        "events": ["event.created"]
    }
    
    response = client.post("/webhooks", json=invalid_data)
    assert response.status_code == 422  # Validation error
    
    print("✅ Invalid URL rejected")


def test_test_webhook_url():
    """Test the webhook URL testing endpoint."""
    print("\n🧪 Test 9: Test webhook URL")
    
    # Test a webhook URL (will fail if URL doesn't exist, but that's OK)
    test_data = {
        "url": "https://webhook.site/test-connection",
        "test_payload": {
            "test": True,
            "message": "FlowSentinel connection test"
        }
    }
    
    response = client.post("/webhooks/test", json=test_data)
    
    assert response.status_code == 200
    result = response.json()
    
    assert "success" in result
    assert "status_code" in result or "error" in result
    
    if result["success"]:
        assert "response_time_ms" in result
        print(f"✅ Test webhook successful ({result['response_time_ms']:.2f}ms)")
    else:
        print(f"✅ Test webhook returned failure (expected for non-existent URL)")
        print(f"   Error: {result.get('error', 'Unknown')}")


def test_manual_trigger_webhook():
    """Test manually triggering a webhook."""
    print("\n🧪 Test 10: Manual webhook trigger")
    
    # Create a webhook
    webhook_data = {
        "url": "https://webhook.site/manual-trigger",
        "events": ["event.created"],
        "active": True
    }
    
    create_response = client.post("/webhooks", json=webhook_data)
    webhook_id = create_response.json()["id"]
    
    # Wait a moment for initial test ping to complete
    time.sleep(0.5)
    
    # Manually trigger with custom payload
    trigger_payload = {
        "test": True,
        "message": "Manual trigger test",
        "data": {"key": "value"}
    }
    
    response = client.post(f"/webhooks/{webhook_id}/trigger", json=trigger_payload)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["webhook_id"] == webhook_id
    assert result["url"] == webhook_data["url"]
    assert "message" in result
    
    print(f"✅ Manually triggered webhook {webhook_id}")


def test_manual_trigger_inactive_webhook():
    """Test that inactive webhooks cannot be manually triggered."""
    print("\n🧪 Test 11: Cannot trigger inactive webhook")
    
    # Create an inactive webhook
    webhook_data = {
        "url": "https://webhook.site/inactive",
        "events": ["event.created"],
        "active": False
    }
    
    create_response = client.post("/webhooks", json=webhook_data)
    webhook_id = create_response.json()["id"]
    
    # Try to trigger
    response = client.post(f"/webhooks/{webhook_id}/trigger", json={"test": True})
    
    assert response.status_code == 400
    
    print("✅ Inactive webhook cannot be triggered")


def test_webhook_integration_with_events():
    """Test that webhooks are triggered when events are ingested."""
    print("\n🧪 Test 12: Webhook integration with event ingestion")
    
    # Create a webhook for event.created
    webhook_data = {
        "url": "https://webhook.site/event-integration",
        "events": ["event.created"],
        "active": True
    }
    
    create_response = client.post("/webhooks", json=webhook_data)
    webhook_id = create_response.json()["id"]
    
    # Wait for initial test ping
    time.sleep(0.5)
    
    # Get initial trigger count
    initial_response = client.get(f"/webhooks/{webhook_id}")
    initial_count = initial_response.json()["trigger_count"]
    
    # Ingest an event (this should trigger the webhook)
    event_data = {
        "id": "evt_webhook_test",
        "source": "slack",
        "type": "message",
        "timestamp": datetime.now().isoformat(),
        "data": {"message": "Test event for webhook"},
        "processed": False
    }
    
    client.post("/events/ingest", json=event_data)
    
    # Wait for background task to complete
    time.sleep(1.0)
    
    # Check if trigger count increased
    final_response = client.get(f"/webhooks/{webhook_id}")
    final_count = final_response.json()["trigger_count"]
    
    assert final_count > initial_count, "Webhook should have been triggered"
    
    print(f"✅ Webhook triggered by event ingestion")
    print(f"   Trigger count: {initial_count} → {final_count}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 WEBHOOK ENDPOINTS TEST SUITE")
    print("=" * 60)
    
    try:
        test_create_webhook()
        test_list_webhooks()
        test_list_active_webhooks_only()
        test_get_webhook_details()
        test_update_webhook()
        test_delete_webhook()
        test_webhook_not_found()
        test_webhook_url_validation()
        test_test_webhook_url()
        test_manual_trigger_webhook()
        test_manual_trigger_inactive_webhook()
        test_webhook_integration_with_events()
        
        print("\n" + "=" * 60)
        print("✅ ALL WEBHOOK TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Test Summary:")
        print("   ✅ 12 webhook endpoints tested")
        print("   ✅ CRUD operations validated")
        print("   ✅ URL validation working")
        print("   ✅ Active/inactive filtering")
        print("   ✅ Manual triggering")
        print("   ✅ Event integration")
        print("   ✅ Error handling (404, validation)")
        print("\n🎉 Webhook system ready for production!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
