"""
Google Calendar Integration for FlowSentinel
=============================================
Create events, check availability, and manage calendar.

Usage:
    from integrations.google_calendar import GoogleCalendarIntegration
    
    calendar = GoogleCalendarIntegration()
    await calendar.create_event(
        summary="Team Standup",
        start="2024-01-15T09:00:00",
        end="2024-01-15T09:30:00"
    )
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class GoogleCalendarIntegration:
    """Google Calendar integration using REST API with OAuth2."""
    
    def __init__(self):
        # For service account or OAuth tokens
        self.access_token = os.getenv("GOOGLE_ACCESS_TOKEN", "")
        self.refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "")
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        
        # Service account credentials (alternative)
        self.service_account_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "")
        
        self.is_configured = bool(self.access_token or self.service_account_key)
        self.base_url = "https://www.googleapis.com/calendar/v3"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "has_access_token": bool(self.access_token),
            "has_service_account": bool(self.service_account_key),
            "calendar_id": self.calendar_id
        }
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token using refresh token."""
        if not self.refresh_token or not self.client_id or not self.client_secret:
            return {"success": False, "error": "Missing refresh credentials"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token", "")
                    return {"success": True}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_event(
        self,
        summary: str,
        start: str,
        end: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        timezone: str = "UTC",
        send_notifications: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            summary: Event title
            start: Start time (ISO format or datetime)
            end: End time (ISO format or datetime)
            description: Event description
            location: Event location
            attendees: List of email addresses
            timezone: Timezone (e.g., "America/New_York")
            send_notifications: Send email notifications to attendees
            
        Returns:
            Created event details with ID and link
        """
        if not self.is_configured:
            logger.warning("Google Calendar not configured - skipping create")
            return {"success": False, "error": "Google Calendar not configured"}
        
        # Build event payload
        event = {
            "summary": summary,
            "start": {
                "dateTime": start,
                "timeZone": timezone
            },
            "end": {
                "dateTime": end,
                "timeZone": timezone
            }
        }
        
        if description:
            event["description"] = description
        
        if location:
            event["location"] = location
        
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calendars/{self.calendar_id}/events",
                    json=event,
                    params={"sendNotifications": str(send_notifications).lower()},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "id": data.get("id"),
                        "summary": data.get("summary"),
                        "start": data.get("start", {}).get("dateTime"),
                        "end": data.get("end", {}).get("dateTime"),
                        "link": data.get("htmlLink")
                    }
                elif response.status_code == 401:
                    # Try refreshing token
                    refresh_result = await self.refresh_access_token()
                    if refresh_result.get("success"):
                        return await self.create_event(
                            summary, start, end, description,
                            location, attendees, timezone, send_notifications
                        )
                    return {"success": False, "error": "Authentication failed"}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Google Calendar create event failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get event details.
        
        Args:
            event_id: Event ID
        """
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calendars/{self.calendar_id}/events/{event_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "id": data.get("id"),
                        "summary": data.get("summary"),
                        "description": data.get("description"),
                        "start": data.get("start", {}).get("dateTime"),
                        "end": data.get("end", {}).get("dateTime"),
                        "location": data.get("location"),
                        "attendees": [a.get("email") for a in data.get("attendees", [])],
                        "status": data.get("status"),
                        "link": data.get("htmlLink")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Update an existing event.
        
        Args:
            event_id: Event ID
            summary: New title
            start: New start time
            end: New end time
            description: New description
            location: New location
            timezone: Timezone
        """
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        # First get existing event
        existing = await self.get_event(event_id)
        if not existing.get("success"):
            return existing
        
        # Build update payload
        event = {}
        if summary:
            event["summary"] = summary
        if start:
            event["start"] = {"dateTime": start, "timeZone": timezone}
        if end:
            event["end"] = {"dateTime": end, "timeZone": timezone}
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        
        if not event:
            return {"success": False, "error": "No fields to update"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/calendars/{self.calendar_id}/events/{event_id}",
                    json=event,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "id": data.get("id"), "link": data.get("htmlLink")}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """
        Delete an event.
        
        Args:
            event_id: Event ID
        """
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/calendars/{self.calendar_id}/events/{event_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 204:
                    return {"success": True}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 50,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List calendar events.
        
        Args:
            time_min: Start of time range (ISO format)
            time_max: End of time range (ISO format)
            max_results: Maximum events to return
            search_query: Free text search
        """
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        # Default to upcoming events
        if not time_min:
            time_min = datetime.utcnow().isoformat() + "Z"
        
        params = {
            "timeMin": time_min,
            "maxResults": max_results,
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        
        if time_max:
            params["timeMax"] = time_max
        if search_query:
            params["q"] = search_query
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calendars/{self.calendar_id}/events",
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    events = []
                    for event in data.get("items", []):
                        start = event.get("start", {})
                        end = event.get("end", {})
                        events.append({
                            "id": event.get("id"),
                            "summary": event.get("summary"),
                            "start": start.get("dateTime") or start.get("date"),
                            "end": end.get("dateTime") or end.get("date"),
                            "location": event.get("location"),
                            "status": event.get("status")
                        })
                    return {"success": True, "count": len(events), "events": events}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_availability(
        self,
        start: str,
        end: str,
        calendars: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check free/busy status for a time range.
        
        Args:
            start: Start time (ISO format)
            end: End time (ISO format)
            calendars: List of calendar IDs to check
        """
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        calendar_ids = calendars or [self.calendar_id]
        
        payload = {
            "timeMin": start,
            "timeMax": end,
            "items": [{"id": cal_id} for cal_id in calendar_ids]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/freeBusy",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    calendars_status = {}
                    for cal_id, info in data.get("calendars", {}).items():
                        busy_times = info.get("busy", [])
                        calendars_status[cal_id] = {
                            "busy": len(busy_times) > 0,
                            "busy_times": busy_times
                        }
                    return {"success": True, "calendars": calendars_status}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_meeting(
        self,
        summary: str,
        start: str,
        end: str,
        attendees: List[str],
        description: Optional[str] = None,
        add_meet_link: bool = True
    ) -> Dict[str, Any]:
        """
        Create a meeting with optional Google Meet link.
        
        Args:
            summary: Meeting title
            start: Start time
            end: End time
            attendees: List of attendee emails
            description: Meeting description
            add_meet_link: Add Google Meet video conferencing
        """
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        event = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "attendees": [{"email": email} for email in attendees]
        }
        
        if description:
            event["description"] = description
        
        if add_meet_link:
            event["conferenceData"] = {
                "createRequest": {"requestId": f"flowsentinel-{datetime.utcnow().timestamp()}"}
            }
        
        try:
            async with httpx.AsyncClient() as client:
                params = {"conferenceDataVersion": "1"} if add_meet_link else {}
                response = await client.post(
                    f"{self.base_url}/calendars/{self.calendar_id}/events",
                    json=event,
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "success": True,
                        "id": data.get("id"),
                        "summary": data.get("summary"),
                        "link": data.get("htmlLink")
                    }
                    
                    # Add Meet link if available
                    conf_data = data.get("conferenceData", {})
                    entry_points = conf_data.get("entryPoints", [])
                    for ep in entry_points:
                        if ep.get("entryPointType") == "video":
                            result["meet_link"] = ep.get("uri")
                            break
                    
                    return result
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Google Calendar connection."""
        if not self.is_configured:
            return {"success": False, "error": "Google Calendar not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calendars/{self.calendar_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "calendar": data.get("summary"),
                        "timezone": data.get("timeZone")
                    }
                elif response.status_code == 401:
                    # Try refreshing token
                    refresh_result = await self.refresh_access_token()
                    if refresh_result.get("success"):
                        return await self.test_connection()
                    return {"success": False, "error": "Authentication failed"}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_calendar_instance: Optional[GoogleCalendarIntegration] = None


def get_google_calendar_integration() -> GoogleCalendarIntegration:
    """Get or create Google Calendar integration instance."""
    global _calendar_instance
    if _calendar_instance is None:
        _calendar_instance = GoogleCalendarIntegration()
    return _calendar_instance
