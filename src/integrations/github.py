"""
GitHub Integration for FlowSentinel
====================================
Create issues, manage PRs, and interact with GitHub repositories.

Usage:
    from integrations.github import GitHubIntegration
    
    github = GitHubIntegration()
    await github.create_issue(
        repo="owner/repo",
        title="Bug found",
        body="Details here..."
    )
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """GitHub integration using REST API."""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.default_owner = os.getenv("GITHUB_OWNER", "")
        self.default_repo = os.getenv("GITHUB_REPO", "")
        
        self.is_configured = bool(self.token)
        self.base_url = "https://api.github.com"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _parse_repo(self, repo: Optional[str]) -> tuple:
        """Parse owner/repo string or use defaults."""
        if repo and "/" in repo:
            parts = repo.split("/")
            return parts[0], parts[1]
        return self.default_owner, self.default_repo or repo
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "configured": self.is_configured,
            "has_token": bool(self.token),
            "default_owner": self.default_owner,
            "default_repo": self.default_repo
        }
    
    async def create_issue(
        self,
        title: str,
        body: str,
        repo: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new GitHub issue.
        
        Args:
            title: Issue title
            body: Issue body (supports markdown)
            repo: Repository (owner/repo format)
            labels: List of label names
            assignees: List of usernames to assign
            milestone: Milestone number
            
        Returns:
            Created issue details with number and URL
        """
        if not self.is_configured:
            logger.warning("GitHub not configured - skipping create")
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        if not owner or not repo_name:
            return {"success": False, "error": "Repository not specified"}
        
        payload = {
            "title": title,
            "body": body
        }
        
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        if milestone:
            payload["milestone"] = milestone
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo_name}/issues",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "number": data.get("number"),
                        "url": data.get("html_url"),
                        "id": data.get("id")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"GitHub create issue failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_issue(
        self,
        issue_number: int,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get issue details.
        
        Args:
            issue_number: Issue number
            repo: Repository (owner/repo format)
        """
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo_name}/issues/{issue_number}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "number": data.get("number"),
                        "title": data.get("title"),
                        "state": data.get("state"),
                        "body": data.get("body"),
                        "labels": [l.get("name") for l in data.get("labels", [])],
                        "assignees": [a.get("login") for a in data.get("assignees", [])],
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "url": data.get("html_url")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_issue(
        self,
        issue_number: int,
        repo: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            issue_number: Issue number
            repo: Repository (owner/repo format)
            title: New title
            body: New body
            state: open or closed
            labels: New labels
            assignees: New assignees
        """
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        
        payload = {}
        if title:
            payload["title"] = title
        if body:
            payload["body"] = body
        if state:
            payload["state"] = state
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        
        if not payload:
            return {"success": False, "error": "No fields to update"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/repos/{owner}/{repo_name}/issues/{issue_number}",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "number": data.get("number"), "url": data.get("html_url")}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_comment(
        self,
        issue_number: int,
        body: str,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to an issue or PR.
        
        Args:
            issue_number: Issue/PR number
            body: Comment body (supports markdown)
            repo: Repository (owner/repo format)
        """
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo_name}/issues/{issue_number}/comments",
                    json={"body": body},
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {"success": True, "id": data.get("id"), "url": data.get("html_url")}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_issues(
        self,
        repo: Optional[str] = None,
        state: str = "open",
        labels: Optional[List[str]] = None,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        List issues in a repository.
        
        Args:
            repo: Repository (owner/repo format)
            state: open, closed, or all
            labels: Filter by labels
            per_page: Results per page
        """
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        
        params = {"state": state, "per_page": per_page}
        if labels:
            params["labels"] = ",".join(labels)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo_name}/issues",
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    issues = []
                    for issue in data:
                        if "pull_request" not in issue:  # Skip PRs
                            issues.append({
                                "number": issue.get("number"),
                                "title": issue.get("title"),
                                "state": issue.get("state"),
                                "labels": [l.get("name") for l in issue.get("labels", [])],
                                "assignees": [a.get("login") for a in issue.get("assignees", [])],
                                "url": issue.get("html_url")
                            })
                    return {"success": True, "count": len(issues), "issues": issues}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_pull_request(
        self,
        pr_number: int,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get pull request details.
        
        Args:
            pr_number: PR number
            repo: Repository (owner/repo format)
        """
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo_name}/pulls/{pr_number}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "number": data.get("number"),
                        "title": data.get("title"),
                        "state": data.get("state"),
                        "merged": data.get("merged"),
                        "draft": data.get("draft"),
                        "head": data.get("head", {}).get("ref"),
                        "base": data.get("base", {}).get("ref"),
                        "user": data.get("user", {}).get("login"),
                        "url": data.get("html_url"),
                        "mergeable": data.get("mergeable"),
                        "additions": data.get("additions"),
                        "deletions": data.get("deletions"),
                        "changed_files": data.get("changed_files")
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
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a blocker issue from FlowSentinel detection.
        
        Args:
            blocker: Blocker description
            impact: Impact description
            suggested_action: Recommended action
            repo: Repository (owner/repo format)
        """
        body = f"""## 🚨 Blocker Detected by FlowSentinel

**Issue:** {blocker}

### Impact
{impact}

### Suggested Action
{suggested_action}

---
*This issue was automatically created by FlowSentinel AI*
*Detected at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
        
        return await self.create_issue(
            title=f"🚨 [BLOCKER] {blocker[:80]}",
            body=body,
            repo=repo,
            labels=["blocker", "flowsentinel", "automated", "high-priority"]
        )
    
    async def get_repo_info(self, repo: Optional[str] = None) -> Dict[str, Any]:
        """Get repository information."""
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        owner, repo_name = self._parse_repo(repo)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo_name}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "name": data.get("name"),
                        "full_name": data.get("full_name"),
                        "description": data.get("description"),
                        "private": data.get("private"),
                        "default_branch": data.get("default_branch"),
                        "open_issues": data.get("open_issues_count"),
                        "stars": data.get("stargazers_count"),
                        "forks": data.get("forks_count"),
                        "url": data.get("html_url")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test GitHub connection."""
        if not self.is_configured:
            return {"success": False, "error": "GitHub not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "user": data.get("login"),
                        "name": data.get("name"),
                        "email": data.get("email")
                    }
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_github_instance: Optional[GitHubIntegration] = None


def get_github_integration() -> GitHubIntegration:
    """Get or create GitHub integration instance."""
    global _github_instance
    if _github_instance is None:
        _github_instance = GitHubIntegration()
    return _github_instance
