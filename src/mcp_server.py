"""
FlowSentinel MCP Server

Model Context Protocol (MCP) server implementation.
Exposes FlowSentinel capabilities as MCP tools that can be used
by AI assistants like Claude, Cursor, VS Code Copilot, etc.

This follows the official MCP specification:
https://modelcontextprotocol.io/

Exposed Tools:
- flowsentinel_get_project_status: Get current project health
- flowsentinel_query_events: Query project events
- flowsentinel_ask_question: Ask questions about the project
- flowsentinel_find_similar: Find similar historical patterns
- flowsentinel_create_task: Create a new task
- flowsentinel_send_notification: Send a notification

Resources:
- project://status: Current project status
- events://recent: Recent project events
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server")


@dataclass
class MCPTool:
    """Definition of an MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPResource:
    """Definition of an MCP resource"""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }


class FlowSentinelMCPServer:
    """
    MCP Server for FlowSentinel.
    
    Implements the Model Context Protocol to expose
    FlowSentinel capabilities to external AI systems.
    """
    
    def __init__(self):
        self.tools = self._register_tools()
        self.resources = self._register_resources()
        
        # Mock data for standalone operation
        self._mock_events = [
            {
                "id": "evt-001",
                "source": "slack",
                "type": "message",
                "data": {"channel": "#engineering", "message": "Backend API ready for testing"},
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "evt-002",
                "source": "jira",
                "type": "task_completed",
                "data": {"key": "FLOW-123", "summary": "Implement authentication"},
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "evt-003",
                "source": "github",
                "type": "pr_merged",
                "data": {"title": "Add RAG pipeline", "author": "nabil"},
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        self._project_status = {
            "status": "YELLOW",
            "blockers": [{"title": "API rate limiting issue", "severity": "medium"}],
            "risks": [{"title": "Timeline might slip", "likelihood": "medium"}],
            "completed_today": [{"title": "Authentication module", "type": "task"}],
            "next_deadline": (datetime.utcnow() + timedelta(days=3)).isoformat()
        }
    
    def _register_tools(self) -> List[MCPTool]:
        """Register all MCP tools"""
        return [
            MCPTool(
                name="flowsentinel_get_project_status",
                description="Get the current project health status including blockers, risks, and recent completions. Returns overall status (GREEN/YELLOW/RED), active blockers, identified risks, and upcoming deadlines.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "include_history": {
                            "type": "boolean",
                            "description": "Include status history from past 24 hours",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            MCPTool(
                name="flowsentinel_query_events",
                description="Query project events from Slack, Jira, GitHub, and Calendar. Filter by source, type, or time range to find specific events.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Event source: slack, jira, github, calendar, or all",
                            "enum": ["slack", "jira", "github", "calendar", "all"]
                        },
                        "hours_ago": {
                            "type": "integer",
                            "description": "Only get events from the last N hours",
                            "default": 24
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                            "default": 10
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Optional search query to filter events"
                        }
                    },
                    "required": []
                }
            ),
            MCPTool(
                name="flowsentinel_ask_question",
                description="Ask a question about the project. Uses RAG (Retrieval-Augmented Generation) to find relevant context and provide accurate answers based on project history.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask about the project"
                        }
                    },
                    "required": ["question"]
                }
            ),
            MCPTool(
                name="flowsentinel_find_similar",
                description="Find similar historical patterns. Searches past events for situations similar to the current one and provides insights on what worked and what didn't.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": "Description of the current situation to find patterns for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum similar patterns to return",
                            "default": 5
                        }
                    },
                    "required": ["situation"]
                }
            ),
            MCPTool(
                name="flowsentinel_create_task",
                description="Create a new task or action item in the project tracking system.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed task description"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Task priority",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Person to assign the task to"
                        }
                    },
                    "required": ["title", "description", "priority"]
                }
            ),
            MCPTool(
                name="flowsentinel_send_notification",
                description="Send a notification to team members about important updates or actions needed.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of recipients or 'all' for everyone"
                        },
                        "message": {
                            "type": "string",
                            "description": "Notification message"
                        },
                        "urgency": {
                            "type": "string",
                            "description": "Urgency level",
                            "enum": ["low", "normal", "high", "urgent"]
                        }
                    },
                    "required": ["recipients", "message"]
                }
            ),
            MCPTool(
                name="flowsentinel_get_recommendations",
                description="Get AI-powered recommendations based on similar historical patterns and their outcomes.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": "Description of the situation to get recommendations for"
                        }
                    },
                    "required": ["situation"]
                }
            )
        ]
    
    def _register_resources(self) -> List[MCPResource]:
        """Register MCP resources"""
        return [
            MCPResource(
                uri="project://status",
                name="Project Status",
                description="Current project health status, blockers, and risks"
            ),
            MCPResource(
                uri="events://recent",
                name="Recent Events",
                description="Recent project events from all sources"
            ),
            MCPResource(
                uri="project://metrics",
                name="Project Metrics",
                description="Key project metrics and statistics"
            )
        ]
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": [t.to_dict() for t in self.tools]
        }
    
    async def handle_list_resources(self) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": [r.to_dict() for r in self.resources]
        }
    
    async def handle_read_resource(self, uri: str) -> Dict[str, Any]:
        """Handle resources/read request"""
        if uri == "project://status":
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(self._project_status, indent=2)
                }]
            }
        elif uri == "events://recent":
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(self._mock_events, indent=2)
                }]
            }
        elif uri == "project://metrics":
            metrics = {
                "total_events": len(self._mock_events),
                "blockers": len(self._project_status["blockers"]),
                "risks": len(self._project_status["risks"]),
                "completed_today": len(self._project_status["completed_today"])
            }
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(metrics, indent=2)
                }]
            }
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    async def handle_call_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle tools/call request"""
        handlers = {
            "flowsentinel_get_project_status": self._tool_get_status,
            "flowsentinel_query_events": self._tool_query_events,
            "flowsentinel_ask_question": self._tool_ask_question,
            "flowsentinel_find_similar": self._tool_find_similar,
            "flowsentinel_create_task": self._tool_create_task,
            "flowsentinel_send_notification": self._tool_send_notification,
            "flowsentinel_get_recommendations": self._tool_get_recommendations
        }
        
        handler = handlers.get(name)
        if not handler:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {name}"
                }],
                "isError": True
            }
        
        try:
            result = await handler(arguments)
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }]
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error executing tool: {str(e)}"
                }],
                "isError": True
            }
    
    # ========================================================================
    # TOOL IMPLEMENTATIONS
    # ========================================================================
    
    async def _tool_get_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get project status"""
        return {
            "status": self._project_status["status"],
            "summary": f"Project is {self._project_status['status']} with {len(self._project_status['blockers'])} blocker(s)",
            "blockers": self._project_status["blockers"],
            "risks": self._project_status["risks"],
            "completed_today": self._project_status["completed_today"],
            "next_deadline": self._project_status["next_deadline"]
        }
    
    async def _tool_query_events(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Query events"""
        source = args.get("source", "all")
        limit = args.get("limit", 10)
        search = args.get("search_query", "")
        
        events = self._mock_events
        
        if source != "all":
            events = [e for e in events if e["source"] == source]
        
        if search:
            search_lower = search.lower()
            events = [
                e for e in events
                if search_lower in json.dumps(e).lower()
            ]
        
        return {
            "count": len(events[:limit]),
            "events": events[:limit]
        }
    
    async def _tool_ask_question(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Answer a question using RAG"""
        question = args.get("question", "")
        
        # Simulate RAG answer
        question_lower = question.lower()
        
        if "status" in question_lower or "how" in question_lower:
            answer = f"Based on project events, the current status is {self._project_status['status']}. There are {len(self._project_status['blockers'])} active blockers that need attention."
        elif "blocker" in question_lower:
            blockers = self._project_status["blockers"]
            answer = f"There are {len(blockers)} blockers: " + ", ".join([b["title"] for b in blockers])
        elif "risk" in question_lower:
            risks = self._project_status["risks"]
            answer = f"Identified risks: " + ", ".join([r["title"] for r in risks])
        else:
            answer = "I've analyzed the project history. Based on recent events, the team has been making progress on the backend API and authentication modules. Let me know if you need more specific information."
        
        return {
            "question": question,
            "answer": answer,
            "sources_used": len(self._mock_events),
            "confidence": 0.85
        }
    
    async def _tool_find_similar(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Find similar patterns"""
        situation = args.get("situation", "")
        limit = args.get("limit", 5)
        
        # Simulate pattern matching
        patterns = [
            {
                "description": "Similar API issue occurred 2 weeks ago",
                "outcome": "Resolved by increasing timeout",
                "similarity": 0.82
            },
            {
                "description": "Timeline pressure led to scope reduction",
                "outcome": "Successfully delivered core features",
                "similarity": 0.75
            }
        ]
        
        return {
            "situation": situation,
            "patterns_found": len(patterns),
            "patterns": patterns[:limit]
        }
    
    async def _tool_create_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task"""
        task = {
            "id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": args.get("title"),
            "description": args.get("description"),
            "priority": args.get("priority", "medium"),
            "assignee": args.get("assignee"),
            "status": "created",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Task created: {task['id']}",
            "task": task
        }
    
    async def _tool_send_notification(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification"""
        notification = {
            "id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "recipients": args.get("recipients", []),
            "message": args.get("message"),
            "urgency": args.get("urgency", "normal"),
            "sent_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Notification sent to {len(notification['recipients'])} recipients",
            "notification": notification
        }
    
    async def _tool_get_recommendations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations"""
        situation = args.get("situation", "")
        
        recommendations = [
            {
                "action": "Schedule a sync meeting",
                "reasoning": "Similar situations benefited from team alignment",
                "priority": "high",
                "success_rate": 0.85
            },
            {
                "action": "Create tracking task",
                "reasoning": "Helps maintain visibility of the issue",
                "priority": "medium",
                "success_rate": 0.78
            }
        ]
        
        return {
            "situation": situation,
            "recommendations": recommendations
        }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP message"""
        method = message.get("method", "")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "flowsentinel-mcp",
                        "version": "1.0.0"
                    }
                }
            elif method == "tools/list":
                result = await self.handle_list_tools()
            elif method == "tools/call":
                result = await self.handle_call_tool(
                    params.get("name", ""),
                    params.get("arguments", {})
                )
            elif method == "resources/list":
                result = await self.handle_list_resources()
            elif method == "resources/read":
                result = await self.handle_read_resource(params.get("uri", ""))
            else:
                result = {"error": f"Unknown method: {method}"}
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run_stdio(self):
        """Run the MCP server using stdio transport"""
        logger.info("FlowSentinel MCP Server starting...")
        
        while True:
            try:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                # Parse JSON-RPC message
                message = json.loads(line.strip())
                
                # Handle message
                response = await self.handle_message(message)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")


def main():
    """Main entry point for MCP server"""
    server = FlowSentinelMCPServer()
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
