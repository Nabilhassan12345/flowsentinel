"""
Slack Integration for FlowSentinel
===================================
Send messages and alerts to Slack channels.

Usage:
    from integrations.slack import SlackIntegration
    
    slack = SlackIntegration()
    await slack.send_message(
        channel="#alerts",
        message="Critical blocker detected!"
    )
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Slack integration using Webhooks and Bot API."""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        self.default_channel = os.getenv("SLACK_DEFAULT_CHANNEL", "#general")
        
        self.is_configured = bool(self.webhook_url or self.bot_token)
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "has_webhook": bool(self.webhook_url),
            "has_bot_token": bool(self.bot_token),
            "default_channel": self.default_channel
        }
    
    async def send_message(
        self,
        message: str,
        channel: Optional[str] = None,
        username: str = "FlowSentinel",
        icon_emoji: str = ":robot_face:"
    ) -> Dict[str, Any]:
        """
        Send a simple message to Slack.
        
        Args:
            message: Message text
            channel: Channel to post to (uses webhook channel if not specified)
            username: Bot username
            icon_emoji: Bot icon
            
        Returns:
            Result with success status
        """
        if not self.is_configured:
            logger.warning("Slack not configured - skipping send")
            return {"success": False, "error": "Slack not configured"}
        
        try:
            if self.webhook_url:
                return await self._send_via_webhook(message, username, icon_emoji)
            else:
                return await self._send_via_bot(message, channel or self.default_channel)
        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_via_webhook(
        self,
        message: str,
        username: str,
        icon_emoji: str
    ) -> Dict[str, Any]:
        """Send message via incoming webhook."""
        payload = {
            "text": message,
            "username": username,
            "icon_emoji": icon_emoji
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload)
            
            if response.status_code == 200:
                return {"success": True, "method": "webhook"}
            else:
                return {"success": False, "error": response.text}
    
    async def _send_via_bot(
        self,
        message: str,
        channel: str
    ) -> Dict[str, Any]:
        """Send message via Bot API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                json={"channel": channel, "text": message},
                headers={"Authorization": f"Bearer {self.bot_token}"}
            )
            
            data = response.json()
            if data.get("ok"):
                return {"success": True, "method": "bot", "ts": data.get("ts")}
            else:
                return {"success": False, "error": data.get("error")}
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted alert with rich blocks.
        
        Args:
            title: Alert title
            message: Alert message
            severity: critical, warning, info
            details: Additional key-value details
            channel: Target channel
        """
        colors = {
            "critical": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        emojis = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        color = colors.get(severity, colors["info"])
        emoji = emojis.get(severity, "📢")
        
        # Build blocks for rich message
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{emoji} {title}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message}
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"*Severity:* {severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"}
                ]
            }
        ]
        
        if details:
            fields = [{"type": "mrkdwn", "text": f"*{k}:* {v}"} for k, v in details.items()]
            blocks.append({"type": "section", "fields": fields[:10]})  # Max 10 fields
        
        blocks.append({"type": "divider"})
        
        # Send with blocks
        if self.webhook_url:
            payload = {
                "text": f"{emoji} {title}: {message}",
                "blocks": blocks,
                "username": "FlowSentinel",
                "icon_emoji": ":shield:"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return {"success": response.status_code == 200}
        else:
            # Fallback to simple message
            return await self.send_message(f"{emoji} *{title}*\n{message}")
    
    async def send_blocker_alert(
        self,
        blocker: str,
        impact: str,
        suggested_action: str
    ) -> Dict[str, Any]:
        """Send a blocker detection alert."""
        return await self.send_alert(
            title="Blocker Detected",
            message=blocker,
            severity="critical",
            details={
                "Impact": impact,
                "Suggested Action": suggested_action
            }
        )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Slack connection."""
        if not self.is_configured:
            return {"success": False, "error": "Slack not configured"}
        
        try:
            result = await self.send_message("🧪 FlowSentinel connection test - this is a test message!")
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_slack_instance: Optional[SlackIntegration] = None


def get_slack_integration() -> SlackIntegration:
    """Get or create Slack integration instance."""
    global _slack_instance
    if _slack_instance is None:
        _slack_instance = SlackIntegration()
    return _slack_instance
