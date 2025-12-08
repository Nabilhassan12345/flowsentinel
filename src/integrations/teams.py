"""
Microsoft Teams Integration for FlowSentinel
=============================================
Send messages and alerts to Microsoft Teams channels via Webhooks.

Usage:
    from integrations.teams import TeamsIntegration
    
    teams = TeamsIntegration()
    await teams.send_message("Alert: Critical blocker detected!")
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TeamsIntegration:
    """Microsoft Teams integration using Incoming Webhooks."""
    
    def __init__(self):
        self.webhook_url = os.getenv("TEAMS_WEBHOOK_URL", "")
        self.is_configured = bool(self.webhook_url)
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "has_webhook": bool(self.webhook_url)
        }
    
    async def send_message(
        self,
        message: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a simple message to Teams.
        
        Args:
            message: Message text (supports markdown)
            title: Optional title
            
        Returns:
            Result with success status
        """
        if not self.is_configured:
            logger.warning("Teams not configured - skipping send")
            return {"success": False, "error": "Teams not configured"}
        
        try:
            # Simple message card format
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": title or "FlowSentinel Notification",
                "sections": [{
                    "activityTitle": title or "FlowSentinel",
                    "text": message,
                    "markdown": True
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                
                if response.status_code == 200:
                    return {"success": True}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Teams send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted alert card.
        
        Args:
            title: Alert title
            message: Alert message
            severity: critical, warning, info
            details: Additional facts to display
            actions: Optional action buttons [{name, url}]
        """
        if not self.is_configured:
            return {"success": False, "error": "Teams not configured"}
        
        colors = {
            "critical": "DC3545",
            "warning": "FFC107",
            "info": "17A2B8"
        }
        
        # Build facts section
        facts = [
            {"name": "Severity", "value": severity.upper()},
            {"name": "Time", "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        ]
        
        if details:
            facts.extend([{"name": k, "value": str(v)} for k, v in details.items()])
        
        # Build payload
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": colors.get(severity, colors["info"]),
            "summary": title,
            "sections": [{
                "activityTitle": f"🛡️ {title}",
                "activitySubtitle": "FlowSentinel Alert",
                "facts": facts,
                "text": message,
                "markdown": True
            }]
        }
        
        # Add actions if provided
        if actions:
            payload["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": action["name"],
                    "targets": [{"os": "default", "uri": action["url"]}]
                }
                for action in actions[:4]  # Max 4 actions
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return {"success": response.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_blocker_alert(
        self,
        blocker: str,
        impact: str,
        suggested_action: str
    ) -> Dict[str, Any]:
        """Send a blocker detection alert."""
        return await self.send_alert(
            title="🚨 Blocker Detected",
            message=blocker,
            severity="critical",
            details={
                "Impact": impact,
                "Suggested Action": suggested_action
            }
        )
    
    async def send_adaptive_card(
        self,
        card_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send an Adaptive Card for richer formatting.
        
        Args:
            card_content: Adaptive Card JSON content
        """
        if not self.is_configured:
            return {"success": False, "error": "Teams not configured"}
        
        payload = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_content
            }]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return {"success": response.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Teams connection."""
        if not self.is_configured:
            return {"success": False, "error": "Teams not configured"}
        
        try:
            result = await self.send_message(
                message="🧪 This is a test message from FlowSentinel!",
                title="Connection Test"
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_teams_instance: Optional[TeamsIntegration] = None


def get_teams_integration() -> TeamsIntegration:
    """Get or create Teams integration instance."""
    global _teams_instance
    if _teams_instance is None:
        _teams_instance = TeamsIntegration()
    return _teams_instance
