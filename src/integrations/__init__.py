"""
FlowSentinel Integrations Package
=================================
Real integrations with external services.
"""

from .email import EmailIntegration, get_email_integration
from .slack import SlackIntegration, get_slack_integration
from .teams import TeamsIntegration, get_teams_integration
from .discord import DiscordIntegration, get_discord_integration
from .jira import JiraIntegration, get_jira_integration
from .github import GitHubIntegration, get_github_integration
from .google_calendar import GoogleCalendarIntegration, get_google_calendar_integration

__all__ = [
    # Email
    "EmailIntegration",
    "get_email_integration",
    # Slack
    "SlackIntegration", 
    "get_slack_integration",
    # Microsoft Teams
    "TeamsIntegration",
    "get_teams_integration",
    # Discord
    "DiscordIntegration",
    "get_discord_integration",
    # Jira
    "JiraIntegration",
    "get_jira_integration",
    # GitHub
    "GitHubIntegration",
    "get_github_integration",
    # Google Calendar
    "GoogleCalendarIntegration",
    "get_google_calendar_integration",
]
