"""
Discord Integration for FlowSentinel
=====================================
Send messages and alerts to Discord channels via Webhooks.

Usage:
    from integrations.discord import DiscordIntegration
    
    discord = DiscordIntegration()
    await discord.send_message("Alert: Critical blocker detected!")
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DiscordIntegration:
    """Discord integration using Webhooks."""
    
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        self.is_configured = bool(self.webhook_url)
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "has_webhook": bool(self.webhook_url)
        }
    
    async def send_message(
        self,
        content: str,
        username: str = "FlowSentinel",
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a simple message to Discord.
        
        Args:
            content: Message content (supports Discord markdown)
            username: Bot username
            avatar_url: Bot avatar URL
            
        Returns:
            Result with success status
        """
        if not self.is_configured:
            logger.warning("Discord not configured - skipping send")
            return {"success": False, "error": "Discord not configured"}
        
        try:
            payload = {
                "content": content,
                "username": username
            }
            
            if avatar_url:
                payload["avatar_url"] = avatar_url
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                
                # Discord returns 204 No Content on success
                if response.status_code in (200, 204):
                    return {"success": True}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Discord send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_embed(
        self,
        title: str,
        description: str,
        color: int = 0x7289DA,
        fields: Optional[List[Dict[str, Any]]] = None,
        footer: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a rich embed message.
        
        Args:
            title: Embed title
            description: Embed description
            color: Embed color (hex)
            fields: List of {name, value, inline} field objects
            footer: Footer text
            thumbnail_url: Thumbnail image URL
        """
        if not self.is_configured:
            return {"success": False, "error": "Discord not configured"}
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if fields:
            embed["fields"] = [
                {"name": f["name"], "value": f["value"], "inline": f.get("inline", False)}
                for f in fields[:25]  # Max 25 fields
            ]
        
        if footer:
            embed["footer"] = {"text": footer}
        
        if thumbnail_url:
            embed["thumbnail"] = {"url": thumbnail_url}
        
        payload = {
            "username": "FlowSentinel",
            "embeds": [embed]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return {"success": response.status_code in (200, 204)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted alert embed.
        
        Args:
            title: Alert title
            message: Alert message
            severity: critical, warning, info
            details: Additional key-value details
        """
        colors = {
            "critical": 0xDC3545,  # Red
            "warning": 0xFFC107,   # Yellow
            "info": 0x17A2B8       # Blue
        }
        emojis = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        color = colors.get(severity, colors["info"])
        emoji = emojis.get(severity, "📢")
        
        fields = [
            {"name": "Severity", "value": severity.upper(), "inline": True},
            {"name": "Time", "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'), "inline": True}
        ]
        
        if details:
            fields.extend([
                {"name": k, "value": str(v), "inline": True}
                for k, v in details.items()
            ])
        
        return await self.send_embed(
            title=f"{emoji} {title}",
            description=message,
            color=color,
            fields=fields,
            footer="FlowSentinel Alert System"
        )
    
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
    
    async def send_code_block(
        self,
        code: str,
        language: str = "",
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a code block message.
        
        Args:
            code: Code content
            language: Syntax highlighting language
            title: Optional title before code
        """
        content = ""
        if title:
            content = f"**{title}**\n"
        
        content += f"```{language}\n{code}\n```"
        
        return await self.send_message(content)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Discord connection."""
        if not self.is_configured:
            return {"success": False, "error": "Discord not configured"}
        
        try:
            result = await self.send_embed(
                title="🧪 Connection Test",
                description="This is a test message from FlowSentinel!",
                color=0x00FF00,
                footer="FlowSentinel - AI-Powered Project Intelligence"
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_discord_instance: Optional[DiscordIntegration] = None


def get_discord_integration() -> DiscordIntegration:
    """Get or create Discord integration instance."""
    global _discord_instance
    if _discord_instance is None:
        _discord_instance = DiscordIntegration()
    return _discord_instance
