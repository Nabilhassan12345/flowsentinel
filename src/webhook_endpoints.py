"""
Webhook Endpoints for FlowSentinel
Handles external integrations and notifications.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Any, Optional
import httpx
import asyncio
import json
from datetime import datetime
import uuid

try:
    from .database import get_db
    from .models import WebhookDB, EventDB, ActionDB
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from database import get_db
    from models import WebhookDB, EventDB, ActionDB


# ============================================================
# Pydantic Models
# ============================================================

class WebhookCreate(BaseModel):
    """Model for creating a new webhook."""
    url: HttpUrl
    events: List[str] = Field(
        ...,
        description="Event types to trigger on (e.g., 'event.created', 'action.taken', 'state.changed')"
    )
    description: Optional[str] = Field(None, description="Optional description of webhook purpose")
    active: bool = Field(True, description="Whether webhook is active")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://api.example.com/webhooks/flowsentinel",
                "events": ["event.created", "action.taken"],
                "description": "Slack notification webhook",
                "active": True
            }
        }


class WebhookUpdate(BaseModel):
    """Model for updating a webhook."""
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    description: Optional[str] = None
    active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "active": False,
                "description": "Temporarily disabled for maintenance"
            }
        }


class WebhookResponse(BaseModel):
    """Model for webhook response."""
    id: str
    url: str
    events: List[str]
    active: bool
    description: Optional[str]
    created_at: str
    last_triggered: Optional[str]
    trigger_count: int
    last_status: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "https://api.example.com/webhooks",
                "events": ["event.created", "action.taken"],
                "active": True,
                "description": "Production webhook",
                "created_at": "2025-11-22T10:00:00",
                "last_triggered": "2025-11-22T15:30:00",
                "trigger_count": 42,
                "last_status": "success"
            }
        }


class WebhookTestRequest(BaseModel):
    """Model for testing a webhook URL."""
    url: HttpUrl
    test_payload: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://api.example.com/webhooks",
                "test_payload": {"test": True, "message": "FlowSentinel test"}
            }
        }


class WebhookTestResponse(BaseModel):
    """Model for webhook test result."""
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "response_time_ms": 145.3,
                "error": None
            }
        }


# ============================================================
# Router Setup
# ============================================================

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ============================================================
# Helper Functions
# ============================================================

async def send_webhook(
    webhook_url: str,
    payload: Dict[str, Any],
    timeout: float = 5.0
) -> tuple[bool, Optional[int], Optional[str]]:
    """
    Send webhook POST request.
    
    Args:
        webhook_url: The URL to send the webhook to
        payload: The JSON payload to send
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success, status_code, error_message)
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "FlowSentinel-Webhook/1.0"
                }
            )
            success = response.status_code < 400
            return success, response.status_code, None if success else response.text
    except httpx.TimeoutException:
        return False, None, "Request timeout"
    except httpx.RequestError as e:
        return False, None, f"Request error: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"


def build_webhook_response(webhook: WebhookDB) -> WebhookResponse:
    """Build WebhookResponse from WebhookDB."""
    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events if isinstance(webhook.events, list) else json.loads(webhook.events),
        active=webhook.active,
        description=webhook.description,
        created_at=webhook.created_at.isoformat() if webhook.created_at else datetime.now().isoformat(),
        last_triggered=webhook.last_triggered.isoformat() if webhook.last_triggered else None,
        trigger_count=webhook.trigger_count or 0,
        last_status=webhook.last_status
    )


async def trigger_webhooks(
    event_type: str,
    payload: Dict[str, Any],
    db: Session
) -> None:
    """
    Trigger all webhooks registered for this event type.
    
    This runs in the background and doesn't block the main request.
    
    Args:
        event_type: The type of event (e.g., 'event.created', 'action.taken')
        payload: The event data to send
        db: Database session
    """
    try:
        # Query active webhooks that are registered for this event type
        webhooks = db.query(WebhookDB).filter(
            WebhookDB.active == True
        ).all()
        
        # Filter webhooks that have this event type in their events list
        matching_webhooks = []
        for webhook in webhooks:
            events_list = webhook.events if isinstance(webhook.events, list) else json.loads(webhook.events or "[]")
            if event_type in events_list:
                matching_webhooks.append(webhook)
        
        # Send webhooks concurrently
        tasks = []
        for webhook in matching_webhooks:
            tasks.append(send_webhook(webhook.url, payload))
        
        # Wait for all webhooks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update webhook stats
        for webhook, result in zip(matching_webhooks, results):
            try:
                if isinstance(result, Exception):
                    webhook.last_status = "error"
                else:
                    success, status_code, error = result
                    webhook.last_status = "success" if success else "failed"
                
                webhook.trigger_count = (webhook.trigger_count or 0) + 1
                webhook.last_triggered = datetime.now()
                db.commit()
            except Exception as e:
                # Don't let one webhook failure affect others
                db.rollback()
                print(f"Error updating webhook {webhook.id}: {e}")
                
    except Exception as e:
        print(f"Error triggering webhooks: {e}")
        db.rollback()


# ============================================================
# Endpoints
# ============================================================

@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook: WebhookCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new webhook.
    
    The webhook will be tested immediately with a ping payload.
    If the test fails, the webhook is still created but marked as inactive.
    """
    # Generate UUID
    webhook_id = str(uuid.uuid4())
    
    # Convert events list to JSON string for storage
    events_json = json.dumps(webhook.events)
    
    # Create webhook record
    db_webhook = WebhookDB(
        id=webhook_id,
        url=str(webhook.url),
        events=events_json,
        description=webhook.description,
        active=webhook.active,
        created_at=datetime.now(),
        trigger_count=0
    )
    
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    
    # Test webhook immediately in background
    test_payload = {
        "event_type": "webhook.ping",
        "timestamp": datetime.now().isoformat(),
        "webhook_id": webhook_id,
        "message": "FlowSentinel webhook test"
    }
    
    async def test_and_update():
        success, status_code, error = await send_webhook(str(webhook.url), test_payload, timeout=5.0)
        db_webhook.last_status = "success" if success else "failed"
        db_webhook.last_triggered = datetime.now()
        db_webhook.trigger_count = 1
        db.commit()
    
    background_tasks.add_task(test_and_update)
    
    return build_webhook_response(db_webhook)


@router.get("", response_model=List[WebhookResponse])
def list_webhooks(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all webhooks with stats.
    
    Query parameters:
    - active_only: If True, only return active webhooks
    """
    query = db.query(WebhookDB)
    
    if active_only:
        query = query.filter(WebhookDB.active == True)
    
    webhooks = query.order_by(WebhookDB.created_at.desc()).all()
    
    return [build_webhook_response(webhook) for webhook in webhooks]


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: str,
    db: Session = Depends(get_db)
):
    """Get webhook details with full stats."""
    webhook = db.query(WebhookDB).filter(WebhookDB.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found"
        )
    
    return build_webhook_response(webhook)


@router.patch("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: str,
    webhook_update: WebhookUpdate,
    db: Session = Depends(get_db)
):
    """
    Update webhook configuration.
    
    Can update:
    - URL
    - Events list
    - Description
    - Active status
    """
    webhook = db.query(WebhookDB).filter(WebhookDB.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found"
        )
    
    # Update fields
    if webhook_update.url is not None:
        webhook.url = str(webhook_update.url)
    
    if webhook_update.events is not None:
        webhook.events = json.dumps(webhook_update.events)
    
    if webhook_update.description is not None:
        webhook.description = webhook_update.description
    
    if webhook_update.active is not None:
        webhook.active = webhook_update.active
    
    db.commit()
    db.refresh(webhook)
    
    return build_webhook_response(webhook)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db)
):
    """Delete a webhook."""
    webhook = db.query(WebhookDB).filter(WebhookDB.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    return None


@router.post("/test", response_model=WebhookTestResponse)
async def test_webhook_url(test_request: WebhookTestRequest):
    """
    Test a webhook URL before registering.
    
    Sends a test POST request to verify the endpoint is reachable.
    """
    # Default test payload
    test_payload = test_request.test_payload or {
        "event_type": "webhook.test",
        "timestamp": datetime.now().isoformat(),
        "message": "FlowSentinel webhook connection test"
    }
    
    # Measure response time
    start_time = datetime.now()
    success, status_code, error = await send_webhook(str(test_request.url), test_payload, timeout=10.0)
    end_time = datetime.now()
    
    response_time_ms = (end_time - start_time).total_seconds() * 1000
    
    return WebhookTestResponse(
        success=success,
        status_code=status_code,
        response_time_ms=response_time_ms if success else None,
        error=error
    )


@router.post("/{webhook_id}/trigger")
async def manual_trigger_webhook(
    webhook_id: str,
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger a specific webhook with custom payload.
    
    Useful for testing and debugging.
    """
    webhook = db.query(WebhookDB).filter(WebhookDB.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found"
        )
    
    if not webhook.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook is not active"
        )
    
    # Add metadata to payload
    enriched_payload = {
        **payload,
        "webhook_id": webhook_id,
        "triggered_at": datetime.now().isoformat(),
        "manual_trigger": True
    }
    
    # Send webhook in background
    async def send_and_update():
        success, status_code, error = await send_webhook(webhook.url, enriched_payload)
        webhook.last_status = "success" if success else "failed"
        webhook.last_triggered = datetime.now()
        webhook.trigger_count = (webhook.trigger_count or 0) + 1
        db.commit()
    
    background_tasks.add_task(send_and_update)
    
    return {
        "message": "Webhook triggered",
        "webhook_id": webhook_id,
        "url": webhook.url
    }


# ============================================================
# Export
# ============================================================

__all__ = ["router", "trigger_webhooks", "send_webhook"]
