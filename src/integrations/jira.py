"""
Jira Integration for FlowSentinel
==================================
Create issues, update status, and sync with Jira projects.

Usage:
    from integrations.jira import JiraIntegration
    
    jira = JiraIntegration()
    await jira.create_issue(
        project="PROJ",
        summary="Critical bug found",
        description="Details here...",
        issue_type="Bug"
    )
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import base64

logger = logging.getLogger(__name__)


class JiraIntegration:
    """Jira integration using REST API."""
    
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL", "")  # e.g., https://yourcompany.atlassian.net
        self.email = os.getenv("JIRA_EMAIL", "")
        self.api_token = os.getenv("JIRA_API_TOKEN", "")
        self.default_project = os.getenv("JIRA_DEFAULT_PROJECT", "")
        
        self.is_configured = bool(self.base_url and self.email and self.api_token)
        
        # Create auth header
        if self.is_configured:
            credentials = f"{self.email}:{self.api_token}"
            self.auth_header = base64.b64encode(credentials.encode()).decode()
        else:
            self.auth_header = ""
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication."""
        return {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "has_base_url": bool(self.base_url),
            "has_credentials": bool(self.email and self.api_token),
            "default_project": self.default_project
        }
    
    async def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        project: Optional[str] = None,
        priority: str = "Medium",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue.
        
        Args:
            summary: Issue title
            description: Issue description
            issue_type: Task, Bug, Story, Epic
            project: Project key (uses default if not specified)
            priority: Highest, High, Medium, Low, Lowest
            labels: List of labels
            assignee: Account ID of assignee
            
        Returns:
            Created issue details with key and URL
        """
        if not self.is_configured:
            logger.warning("Jira not configured - skipping create")
            return {"success": False, "error": "Jira not configured"}
        
        project_key = project or self.default_project
        if not project_key:
            return {"success": False, "error": "No project specified"}
        
        # Build issue payload
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority}
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels
        
        if assignee:
            payload["fields"]["assignee"] = {"accountId": assignee}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/3/issue",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "key": data.get("key"),
                        "id": data.get("id"),
                        "url": f"{self.base_url}/browse/{data.get('key')}"
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Jira create issue failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue details.
        
        Args:
            issue_key: Issue key (e.g., PROJ-123)
        """
        if not self.is_configured:
            return {"success": False, "error": "Jira not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    fields = data.get("fields", {})
                    return {
                        "success": True,
                        "key": data.get("key"),
                        "summary": fields.get("summary"),
                        "status": fields.get("status", {}).get("name"),
                        "priority": fields.get("priority", {}).get("name"),
                        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                        "created": fields.get("created"),
                        "updated": fields.get("updated")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            issue_key: Issue key (e.g., PROJ-123)
            summary: New summary
            description: New description
            priority: New priority
            labels: New labels
        """
        if not self.is_configured:
            return {"success": False, "error": "Jira not configured"}
        
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}]
                }]
            }
        if priority:
            fields["priority"] = {"name": priority}
        if labels:
            fields["labels"] = labels
        
        if not fields:
            return {"success": False, "error": "No fields to update"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}",
                    json={"fields": fields},
                    headers=self._get_headers()
                )
                
                if response.status_code == 204:
                    return {"success": True, "key": issue_key}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def transition_issue(
        self,
        issue_key: str,
        transition_name: str
    ) -> Dict[str, Any]:
        """
        Transition issue to a new status.
        
        Args:
            issue_key: Issue key (e.g., PROJ-123)
            transition_name: Transition name (e.g., "Done", "In Progress")
        """
        if not self.is_configured:
            return {"success": False, "error": "Jira not configured"}
        
        try:
            # First get available transitions
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions",
                    headers=self._get_headers()
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "Could not get transitions"}
                
                transitions = response.json().get("transitions", [])
                transition_id = None
                
                for t in transitions:
                    if t.get("name", "").lower() == transition_name.lower():
                        transition_id = t.get("id")
                        break
                
                if not transition_id:
                    available = [t.get("name") for t in transitions]
                    return {"success": False, "error": f"Transition not found. Available: {available}"}
                
                # Perform transition
                response = await client.post(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions",
                    json={"transition": {"id": transition_id}},
                    headers=self._get_headers()
                )
                
                if response.status_code == 204:
                    return {"success": True, "key": issue_key, "status": transition_name}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_comment(
        self,
        issue_key: str,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add a comment to an issue.
        
        Args:
            issue_key: Issue key (e.g., PROJ-123)
            comment: Comment text
        """
        if not self.is_configured:
            return {"success": False, "error": "Jira not configured"}
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}]
                }]
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    return {"success": True, "key": issue_key}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_issues(
        self,
        jql: str,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Search issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum results to return
        """
        if not self.is_configured:
            return {"success": False, "error": "Jira not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/search",
                    params={"jql": jql, "maxResults": max_results},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    issues = []
                    for issue in data.get("issues", []):
                        fields = issue.get("fields", {})
                        issues.append({
                            "key": issue.get("key"),
                            "summary": fields.get("summary"),
                            "status": fields.get("status", {}).get("name"),
                            "priority": fields.get("priority", {}).get("name"),
                            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None
                        })
                    return {
                        "success": True,
                        "total": data.get("total"),
                        "issues": issues
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_blocker_issue(
        self,
        blocker: str,
        impact: str,
        suggested_action: str,
        project: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a blocker issue from FlowSentinel detection.
        
        Args:
            blocker: Blocker description
            impact: Impact description
            suggested_action: Recommended action
            project: Project key
        """
        description = f"""
🚨 **Blocker Detected by FlowSentinel**

**Issue:** {blocker}

**Impact:** {impact}

**Suggested Action:** {suggested_action}

---
*This issue was automatically created by FlowSentinel AI*
*Detected at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
        
        return await self.create_issue(
            summary=f"[BLOCKER] {blocker[:80]}",
            description=description,
            issue_type="Bug",
            project=project,
            priority="Highest",
            labels=["blocker", "flowsentinel", "automated"]
        )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Jira connection."""
        if not self.is_configured:
            return {"success": False, "error": "Jira not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/myself",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "user": data.get("displayName"),
                        "email": data.get("emailAddress")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_jira_instance: Optional[JiraIntegration] = None


def get_jira_integration() -> JiraIntegration:
    """Get or create Jira integration instance."""
    global _jira_instance
    if _jira_instance is None:
        _jira_instance = JiraIntegration()
    return _jira_instance
