"""
FlowSentinel Team Endpoints

Multi-tenant team management endpoints.
Allows organizations to manage multiple teams with isolated data.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import ActionDB, EventDB, ProjectStateDB, TeamDB


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class TeamCreate(BaseModel):
    """Schema for creating a new team."""

    name: str = Field(..., min_length=1, max_length=200, description="Team name")
    description: Optional[str] = Field(None, max_length=500, description="Team description")
    members: List[str] = Field(default_factory=list, description="List of member email addresses")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Team settings")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Engineering Team",
                "description": "Core engineering team",
                "members": ["alice@example.com", "bob@example.com"],
                "settings": {
                    "notifications_enabled": True,
                    "slack_channel": "#engineering"
                }
            }
        }


class TeamUpdate(BaseModel):
    """Schema for updating team information."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    members: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Team Name",
                "description": "Updated description",
                "members": ["alice@example.com", "bob@example.com", "charlie@example.com"],
                "settings": {
                    "notifications_enabled": False
                }
            }
        }


class TeamResponse(BaseModel):
    """Schema for team response."""

    id: str
    name: str
    description: Optional[str]
    members: List[str]
    member_count: int
    settings: Dict[str, Any]
    created_at: str
    updated_at: str
    event_count: int
    action_count: int
    latest_status: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "team_123",
                "name": "Engineering Team",
                "description": "Core engineering team",
                "members": ["alice@example.com", "bob@example.com"],
                "member_count": 2,
                "settings": {"notifications_enabled": True},
                "created_at": "2025-11-22T10:00:00",
                "updated_at": "2025-11-22T15:00:00",
                "event_count": 150,
                "action_count": 45,
                "latest_status": "GREEN"
            }
        }


class TeamStats(BaseModel):
    """Detailed team statistics."""

    team_id: str
    team_name: str
    total_events: int
    events_by_source: Dict[str, int]
    total_actions: int
    unprocessed_events: int
    latest_status: Optional[str]
    blockers_count: int
    risks_count: int
    last_activity: Optional[str]


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/teams", tags=["Teams"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_team_by_id(db: Session, team_id: str) -> TeamDB:
    """
    Get team by ID or raise 404.
    
    Args:
        db: Database session
        team_id: Team identifier
        
    Returns:
        TeamDB instance
        
    Raises:
        HTTPException: If team not found
    """
    team = db.query(TeamDB).filter_by(id=team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")
    return team


def validate_team_name_unique(db: Session, name: str, exclude_id: Optional[str] = None):
    """
    Validate that team name is unique.
    
    Args:
        db: Database session
        name: Team name to validate
        exclude_id: Team ID to exclude (for updates)
        
    Raises:
        HTTPException: If name already exists
    """
    query = db.query(TeamDB).filter_by(name=name)
    if exclude_id:
        query = query.filter(TeamDB.id != exclude_id)
    
    if query.first():
        raise HTTPException(
            status_code=400,
            detail=f"Team name already exists: {name}"
        )


def build_team_response(db: Session, team: TeamDB) -> TeamResponse:
    """
    Build TeamResponse with stats from team.
    
    Args:
        db: Database session
        team: TeamDB instance
        
    Returns:
        TeamResponse with computed stats
    """
    # Count events for team
    event_count = db.query(EventDB).filter_by(team_id=team.id).count()
    
    # Count actions for team
    action_count = db.query(ActionDB).filter_by(team_id=team.id).count()
    
    # Get latest status
    latest_state = (
        db.query(ProjectStateDB)
        .filter_by(team_id=team.id)
        .order_by(ProjectStateDB.last_updated.desc())
        .first()
    )
    latest_status = latest_state.status if latest_state else None
    
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        members=team.members if team.members else [],
        member_count=len(team.members) if team.members else 0,
        settings=team.settings if team.settings else {},
        created_at=team.created_at.isoformat(),
        updated_at=team.updated_at.isoformat(),
        event_count=event_count,
        action_count=action_count,
        latest_status=latest_status,
    )


# ============================================================================
# TEAM ENDPOINTS
# ============================================================================


@router.post("", response_model=TeamResponse, status_code=201)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new team.
    
    Creates a new team with unique name and optional members.
    Team ID is automatically generated as UUID.
    
    Args:
        team_data: Team creation data
        db: Database session
        
    Returns:
        Created team with stats
        
    Raises:
        HTTPException 400: If team name already exists
    """
    try:
        # Validate team name is unique
        validate_team_name_unique(db, team_data.name)
        
        # Create team
        team = TeamDB(
            id=str(uuid.uuid4()),
            name=team_data.name,
            description=team_data.description,
            members=team_data.members if team_data.members else [],
            settings=team_data.settings if team_data.settings else {},
        )
        
        db.add(team)
        db.commit()
        db.refresh(team)
        
        return build_team_response(db, team)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create team: {str(e)}")


@router.get("", response_model=List[TeamResponse])
def list_teams(
    limit: int = Query(100, ge=1, le=1000, description="Maximum teams to return"),
    offset: int = Query(0, ge=0, description="Number of teams to skip"),
    db: Session = Depends(get_db)
):
    """
    List all teams with statistics.
    
    Returns all teams with event counts, action counts, and latest status.
    Supports pagination via limit and offset parameters.
    
    Args:
        limit: Maximum number of teams to return
        offset: Number of teams to skip
        db: Database session
        
    Returns:
        List of teams with stats
    """
    try:
        # Query teams with pagination
        teams = (
            db.query(TeamDB)
            .order_by(TeamDB.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        # Build response for each team
        return [build_team_response(db, team) for team in teams]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list teams: {str(e)}")


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: str,
    db: Session = Depends(get_db)
):
    """
    Get team details by ID.
    
    Returns detailed information about a specific team including
    event count, action count, and latest project status.
    
    Args:
        team_id: Team identifier
        db: Database session
        
    Returns:
        Team details with stats
        
    Raises:
        HTTPException 404: If team not found
    """
    try:
        team = get_team_by_id(db, team_id)
        return build_team_response(db, team)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team: {str(e)}")


@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: Session = Depends(get_db)
):
    """
    Update team information.
    
    Updates team name, description, members, or settings.
    Only provided fields are updated (partial update).
    
    Args:
        team_id: Team identifier
        team_data: Fields to update
        db: Database session
        
    Returns:
        Updated team with stats
        
    Raises:
        HTTPException 404: If team not found
        HTTPException 400: If new name already exists
    """
    try:
        # Get team
        team = get_team_by_id(db, team_id)
        
        # Validate name if changing
        if team_data.name and team_data.name != team.name:
            validate_team_name_unique(db, team_data.name, exclude_id=team_id)
            team.name = team_data.name
        
        # Update description
        if team_data.description is not None:
            team.description = team_data.description
        
        # Update members
        if team_data.members is not None:
            team.members = team_data.members
        
        # Update settings
        if team_data.settings is not None:
            # Merge with existing settings
            current_settings = team.settings if team.settings else {}
            current_settings.update(team_data.settings)
            team.settings = current_settings
        
        # Update timestamp
        team.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(team)
        
        return build_team_response(db, team)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update team: {str(e)}")


@router.delete("/{team_id}")
def delete_team(
    team_id: str,
    hard_delete: bool = Query(False, description="Permanently delete team and all data"),
    db: Session = Depends(get_db)
):
    """
    Delete team.
    
    By default, performs soft delete (marks as inactive but keeps data).
    Use hard_delete=true to permanently remove team and all associated data.
    
    ⚠️  WARNING: Hard delete cannot be undone!
    
    Args:
        team_id: Team identifier
        hard_delete: If true, permanently delete all data
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If team not found
    """
    try:
        # Get team
        team = get_team_by_id(db, team_id)
        
        if hard_delete:
            # Hard delete: Remove all team data
            # Delete associated data first
            db.query(EventDB).filter_by(team_id=team_id).delete()
            db.query(ActionDB).filter_by(team_id=team_id).delete()
            db.query(ProjectStateDB).filter_by(team_id=team_id).delete()
            
            # Delete team
            db.delete(team)
            db.commit()
            
            return {
                "success": True,
                "message": f"Team '{team.name}' and all associated data permanently deleted",
                "team_id": team_id,
                "deleted": True
            }
        else:
            # Soft delete: Mark as inactive
            if not team.settings:
                team.settings = {}
            team.settings["deleted"] = True
            team.settings["deleted_at"] = datetime.utcnow().isoformat()
            team.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Team '{team.name}' marked as inactive (data preserved)",
                "team_id": team_id,
                "deleted": False,
                "note": "Use hard_delete=true to permanently delete"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete team: {str(e)}")


@router.get("/{team_id}/events")
def get_team_events(
    team_id: str,
    limit: int = Query(50, ge=1, le=1000, description="Maximum events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    source: Optional[str] = Query(None, description="Filter by event source"),
    processed: Optional[bool] = Query(None, description="Filter by processed status"),
    db: Session = Depends(get_db)
):
    """
    Get all events for a team.
    
    Returns events filtered by team ID with optional filtering by source
    and processing status. Supports pagination.
    
    Args:
        team_id: Team identifier
        limit: Maximum events to return
        offset: Number of events to skip
        source: Filter by source (slack, jira, github, calendar)
        processed: Filter by processed status
        db: Database session
        
    Returns:
        List of events and metadata
        
    Raises:
        HTTPException 404: If team not found
    """
    try:
        # Verify team exists
        get_team_by_id(db, team_id)
        
        # Build query
        query = db.query(EventDB).filter_by(team_id=team_id)
        
        # Apply filters
        if source:
            query = query.filter_by(source=source)
        if processed is not None:
            query = query.filter_by(processed=processed)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        events = (
            query
            .order_by(EventDB.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        # Convert to dict
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "source": event.source,
                "type": event.type,
                "timestamp": event.timestamp.isoformat(),
                "processed": event.processed,
                "data": event.data,
                "created_at": event.created_at.isoformat(),
            })
        
        return {
            "team_id": team_id,
            "events": events_data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "returned": len(events_data),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team events: {str(e)}")


@router.get("/{team_id}/state")
def get_team_state(
    team_id: str,
    db: Session = Depends(get_db)
):
    """
    Get latest project state for team.
    
    Returns the most recent project state analysis including status,
    blockers, risks, and completed work.
    
    Args:
        team_id: Team identifier
        db: Database session
        
    Returns:
        Latest project state
        
    Raises:
        HTTPException 404: If team or state not found
    """
    try:
        # Verify team exists
        team = get_team_by_id(db, team_id)
        
        # Get latest state
        state = (
            db.query(ProjectStateDB)
            .filter_by(team_id=team_id)
            .order_by(ProjectStateDB.last_updated.desc())
            .first()
        )
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"No project state found for team: {team.name}"
            )
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "state": {
                "id": state.id,
                "status": state.status,
                "blockers": state.blockers if state.blockers else [],
                "risks": state.risks if state.risks else [],
                "completed_today": state.completed_today if state.completed_today else [],
                "next_deadline": state.next_deadline,
                "last_updated": state.last_updated.isoformat(),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team state: {str(e)}")


@router.get("/{team_id}/analytics", response_model=TeamStats)
def get_team_analytics(
    team_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analytics for specific team.
    
    Returns comprehensive statistics including event counts by source,
    action counts, processing rates, and current project status.
    
    Args:
        team_id: Team identifier
        db: Database session
        
    Returns:
        Team analytics and statistics
        
    Raises:
        HTTPException 404: If team not found
    """
    try:
        # Verify team exists
        team = get_team_by_id(db, team_id)
        
        # Count total events
        total_events = db.query(EventDB).filter_by(team_id=team_id).count()
        
        # Events by source
        events_by_source = {}
        for source in ["slack", "jira", "github", "calendar"]:
            count = db.query(EventDB).filter_by(team_id=team_id, source=source).count()
            events_by_source[source] = count
        
        # Count actions
        total_actions = db.query(ActionDB).filter_by(team_id=team_id).count()
        
        # Count unprocessed events
        unprocessed = db.query(EventDB).filter_by(team_id=team_id, processed=False).count()
        
        # Get latest state
        latest_state = (
            db.query(ProjectStateDB)
            .filter_by(team_id=team_id)
            .order_by(ProjectStateDB.last_updated.desc())
            .first()
        )
        
        latest_status = None
        blockers_count = 0
        risks_count = 0
        
        if latest_state:
            latest_status = latest_state.status
            blockers_count = len(latest_state.blockers) if latest_state.blockers else 0
            risks_count = len(latest_state.risks) if latest_state.risks else 0
        
        # Get last activity
        last_event = (
            db.query(EventDB)
            .filter_by(team_id=team_id)
            .order_by(EventDB.timestamp.desc())
            .first()
        )
        last_activity = last_event.timestamp.isoformat() if last_event else None
        
        return TeamStats(
            team_id=team_id,
            team_name=team.name,
            total_events=total_events,
            events_by_source=events_by_source,
            total_actions=total_actions,
            unprocessed_events=unprocessed,
            latest_status=latest_status,
            blockers_count=blockers_count,
            risks_count=risks_count,
            last_activity=last_activity,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team analytics: {str(e)}")
