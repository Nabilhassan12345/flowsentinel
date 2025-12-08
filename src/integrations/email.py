"""
Email Integration for FlowSentinel
===================================
Send email notifications via SMTP or SendGrid.

Usage:
    from integrations.email import EmailIntegration
    
    email = EmailIntegration()
    await email.send_alert(
        to="user@example.com",
        subject="Critical Alert",
        message="A blocker was detected..."
    )
"""

import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailIntegration:
    """Email integration using SMTP or SendGrid."""
    
    def __init__(self):
        # SMTP settings
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_user)
        
        # SendGrid settings (alternative)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        
        # Check if configured
        self.use_sendgrid = bool(self.sendgrid_api_key)
        self.is_configured = bool(self.smtp_user and self.smtp_password) or self.use_sendgrid
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "provider": "sendgrid" if self.use_sendgrid else "smtp",
            "from_email": self.from_email,
            "smtp_host": self.smtp_host if not self.use_sendgrid else None
        }
    
    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Plain text body
            html: Optional HTML body
            
        Returns:
            Result with success status
        """
        if not self.is_configured:
            logger.warning("Email not configured - skipping send")
            return {"success": False, "error": "Email not configured"}
        
        if isinstance(to, str):
            to = [to]
        
        try:
            if self.use_sendgrid:
                return await self._send_via_sendgrid(to, subject, body, html)
            else:
                return await self._send_via_smtp(to, subject, body, html)
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_via_smtp(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP."""
        def _send():
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to)
            
            # Add plain text
            msg.attach(MIMEText(body, "plain"))
            
            # Add HTML if provided
            if html:
                msg.attach(MIMEText(html, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to, msg.as_string())
            
            return {"success": True, "recipients": to}
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _send)
    
    async def _send_via_sendgrid(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email via SendGrid API."""
        import httpx
        
        payload = {
            "personalizations": [{"to": [{"email": email} for email in to]}],
            "from": {"email": self.from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
        
        if html:
            payload["content"].append({"type": "text/html", "value": html})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.sendgrid_api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code in [200, 202]:
                return {"success": True, "recipients": to}
            else:
                return {"success": False, "error": response.text}
    
    async def send_alert(
        self,
        to: str | List[str],
        title: str,
        message: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted alert email.
        
        Args:
            to: Recipient email(s)
            title: Alert title
            message: Alert message
            severity: critical, warning, info
            details: Additional details
        """
        colors = {
            "critical": "#dc3545",
            "warning": "#ffc107", 
            "info": "#17a2b8"
        }
        color = colors.get(severity, colors["info"])
        
        subject = f"[FlowSentinel {severity.upper()}] {title}"
        
        # Plain text version
        body = f"""
FlowSentinel Alert
==================

{title}

{message}

Severity: {severity.upper()}
Time: {datetime.utcnow().isoformat()}

"""
        if details:
            body += "Details:\n"
            for key, value in details.items():
                body += f"  - {key}: {value}\n"
        
        # HTML version
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .header {{ background: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; }}
        .severity {{ display: inline-block; padding: 4px 12px; border-radius: 4px; background: {color}; color: white; }}
        .details {{ background: white; padding: 15px; border-radius: 4px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 FlowSentinel Alert</h1>
    </div>
    <div class="content">
        <h2>{title}</h2>
        <p>{message}</p>
        <p><span class="severity">{severity.upper()}</span></p>
        <p><small>Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</small></p>
        {"<div class='details'><h4>Details:</h4><ul>" + "".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in (details or {}).items()) + "</ul></div>" if details else ""}
    </div>
</body>
</html>
"""
        
        return await self.send_email(to, subject, body, html)
    
    async def send_daily_summary(
        self,
        to: str | List[str],
        summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send daily project summary email."""
        subject = f"[FlowSentinel] Daily Summary - {datetime.utcnow().strftime('%Y-%m-%d')}"
        
        body = f"""
FlowSentinel Daily Summary
==========================

Project Status: {summary.get('status', 'Unknown')}

Events Today: {summary.get('events_count', 0)}
Blockers: {summary.get('blockers_count', 0)}
Actions Taken: {summary.get('actions_count', 0)}

Top Issues:
{chr(10).join(f"  - {issue}" for issue in summary.get('top_issues', []))}

Recommendations:
{chr(10).join(f"  - {rec}" for rec in summary.get('recommendations', []))}

View Dashboard: {summary.get('dashboard_url', 'https://flowsentinel.netlify.app')}
"""
        
        return await self.send_email(to, subject, body)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test email configuration."""
        if not self.is_configured:
            return {"success": False, "error": "Email not configured"}
        
        try:
            if self.use_sendgrid:
                return {"success": True, "provider": "sendgrid", "message": "SendGrid API key is set"}
            else:
                # Test SMTP connection
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                return {"success": True, "provider": "smtp", "host": self.smtp_host}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_email_instance: Optional[EmailIntegration] = None


def get_email_integration() -> EmailIntegration:
    """Get or create email integration instance."""
    global _email_instance
    if _email_instance is None:
        _email_instance = EmailIntegration()
    return _email_instance
