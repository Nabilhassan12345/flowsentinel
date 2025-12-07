"""
FlowSentinel Pattern Matching API Endpoints

FastAPI router for finding similar historical patterns.

Endpoints:
- POST /patterns/find-similar - Find similar patterns
- GET /patterns/recommendations - Get recommendations
- POST /patterns/record - Record a new pattern
- PUT /patterns/{pattern_id}/outcome - Update pattern outcome
- GET /patterns/stats - Get pattern statistics
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from pattern_matcher import (
    PatternMatcher,
    PatternType,
    OutcomeType,
    Pattern,
    get_pattern_matcher,
)

router = APIRouter(prefix="/patterns", tags=["patterns"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class FindSimilarRequest(BaseModel):
    """Request to find similar patterns"""
    query: str = Field(..., description="Description of current situation")
    limit: int = Field(default=5, le=20, description="Maximum patterns to return")
    min_similarity: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold"
    )


class PatternInfo(BaseModel):
    """Pattern information"""
    id: str
    type: str
    description: str
    confidence: float
    keywords: List[str]
    detected_at: str


class PatternMatchResponse(BaseModel):
    """Response for a pattern match"""
    pattern: PatternInfo
    similarity: float
    outcome: str
    actions_taken: List[Dict[str, Any]]
    outcome_description: str
    days_to_resolve: Optional[int]


class RecommendationResponse(BaseModel):
    """Response for a recommendation"""
    action: str
    reasoning: str
    confidence: float
    based_on_patterns: int
    success_rate: float
    priority: str


class RecordPatternRequest(BaseModel):
    """Request to record a new pattern"""
    type: str = Field(
        ...,
        description="Pattern type: blocker, risk, delay, success, conflict, escalation, resolution"
    )
    description: str = Field(..., description="Description of the pattern")
    keywords: List[str] = Field(default_factory=list, description="Keywords for matching")
    events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Related events"
    )
    team_id: Optional[str] = Field(default=None, description="Team identifier")


class UpdateOutcomeRequest(BaseModel):
    """Request to update pattern outcome"""
    outcome: str = Field(
        ...,
        description="Outcome: positive, negative, neutral, pending"
    )
    outcome_description: str = Field(..., description="Description of the outcome")
    actions_taken: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Actions that were taken"
    )
    days_to_resolve: Optional[int] = Field(
        default=None,
        description="Days it took to resolve"
    )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/find-similar",
    response_model=List[PatternMatchResponse],
    summary="Find similar patterns",
    description="Find historical patterns similar to the current situation."
)
async def find_similar_patterns(request: FindSimilarRequest):
    """
    Find patterns similar to the current situation.
    
    Uses semantic similarity and keyword matching to find
    relevant historical experiences and their outcomes.
    """
    try:
        matcher = get_pattern_matcher()
        
        matches = matcher.find_similar(
            query=request.query,
            limit=request.limit,
            min_similarity=request.min_similarity
        )
        
        return [
            PatternMatchResponse(
                pattern=PatternInfo(
                    id=m.pattern.id,
                    type=m.pattern.type.value,
                    description=m.pattern.description,
                    confidence=m.pattern.confidence,
                    keywords=m.pattern.keywords,
                    detected_at=m.pattern.detected_at.isoformat()
                ),
                similarity=m.similarity,
                outcome=m.outcome.value,
                actions_taken=m.actions_taken,
                outcome_description=m.outcome_description,
                days_to_resolve=m.time_to_resolve.days if m.time_to_resolve else None
            )
            for m in matches
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/recommendations",
    response_model=List[RecommendationResponse],
    summary="Get recommendations",
    description="Get action recommendations based on similar patterns."
)
async def get_recommendations(
    query: str = Query(..., description="Description of current situation"),
    limit: int = Query(default=3, le=10, description="Maximum recommendations")
):
    """
    Get recommendations based on historical patterns.
    
    Analyzes what worked in similar situations and
    generates actionable recommendations.
    """
    try:
        matcher = get_pattern_matcher()
        
        recommendations = matcher.get_recommendations(
            query=query,
            limit=limit
        )
        
        return [
            RecommendationResponse(
                action=r.action,
                reasoning=r.reasoning,
                confidence=r.confidence,
                based_on_patterns=r.based_on_patterns,
                success_rate=r.success_rate,
                priority=r.priority
            )
            for r in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/record",
    summary="Record a new pattern",
    description="Record a new pattern for future matching."
)
async def record_pattern(request: RecordPatternRequest):
    """
    Record a new pattern.
    
    This adds a pattern to the pattern database for future
    similarity matching and recommendation generation.
    """
    try:
        # Validate pattern type
        try:
            pattern_type = PatternType(request.type)
        except ValueError:
            valid_types = [t.value for t in PatternType]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid pattern type. Must be one of: {valid_types}"
            )
        
        import uuid
        
        pattern = Pattern(
            id=str(uuid.uuid4())[:12],
            type=pattern_type,
            description=request.description,
            events=request.events,
            detected_at=datetime.utcnow(),
            confidence=1.0,  # User-recorded patterns have full confidence
            keywords=request.keywords,
            team_id=request.team_id
        )
        
        matcher = get_pattern_matcher()
        matcher.record_pattern(pattern)
        
        return {
            "success": True,
            "message": "Pattern recorded successfully",
            "pattern": pattern.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{pattern_id}/outcome",
    summary="Update pattern outcome",
    description="Update the outcome of a recorded pattern."
)
async def update_pattern_outcome(
    pattern_id: str,
    request: UpdateOutcomeRequest
):
    """
    Update the outcome of a pattern.
    
    Recording outcomes helps improve future recommendations
    by learning what actions led to positive results.
    """
    try:
        # Validate outcome
        try:
            outcome = OutcomeType(request.outcome)
        except ValueError:
            valid_outcomes = [o.value for o in OutcomeType]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid outcome. Must be one of: {valid_outcomes}"
            )
        
        time_to_resolve = None
        if request.days_to_resolve:
            time_to_resolve = timedelta(days=request.days_to_resolve)
        
        matcher = get_pattern_matcher()
        
        success = matcher.update_outcome(
            pattern_id=pattern_id,
            outcome=outcome,
            outcome_description=request.outcome_description,
            actions_taken=request.actions_taken,
            time_to_resolve=time_to_resolve
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Pattern not found: {pattern_id}"
            )
        
        return {
            "success": True,
            "message": f"Outcome updated for pattern {pattern_id}",
            "outcome": outcome.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    summary="Get pattern statistics",
    description="Get statistics about stored patterns."
)
async def get_pattern_stats():
    """
    Get pattern statistics.
    
    Returns counts of patterns by type and outcome,
    useful for understanding the pattern database.
    """
    try:
        matcher = get_pattern_matcher()
        stats = matcher.get_pattern_stats()
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/types",
    summary="List pattern types",
    description="Get information about pattern types."
)
async def list_pattern_types():
    """List all pattern types with descriptions."""
    types = {
        "blocker": {
            "name": "Blocker",
            "description": "Something blocking progress",
            "keywords": ["blocked", "waiting on", "stuck"]
        },
        "risk": {
            "name": "Risk",
            "description": "Potential risk identified",
            "keywords": ["risk", "concern", "might impact"]
        },
        "delay": {
            "name": "Delay",
            "description": "Timeline slippage",
            "keywords": ["delayed", "behind schedule", "late"]
        },
        "success": {
            "name": "Success",
            "description": "Successful completion",
            "keywords": ["completed", "shipped", "merged"]
        },
        "conflict": {
            "name": "Conflict",
            "description": "Team/resource conflict",
            "keywords": ["conflict", "disagreement", "competing"]
        },
        "escalation": {
            "name": "Escalation",
            "description": "Issue escalated",
            "keywords": ["escalate", "urgent", "critical"]
        },
        "resolution": {
            "name": "Resolution",
            "description": "Issue resolved",
            "keywords": ["resolved", "fixed", "unblocked"]
        }
    }
    
    return {"types": types}


@router.post(
    "/analyze",
    summary="Analyze text for patterns",
    description="Analyze text to detect patterns."
)
async def analyze_for_patterns(
    text: str = Query(..., description="Text to analyze")
):
    """
    Analyze text to detect patterns.
    
    Useful for understanding what kind of pattern
    a message or event represents.
    """
    try:
        from pattern_matcher import PatternDetector
        
        detector = PatternDetector()
        
        # Create a mock event for analysis
        event = {
            "data": {"message": text},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        patterns = detector.detect([event])
        
        if not patterns:
            return {
                "detected": False,
                "message": "No clear pattern detected in the text"
            }
        
        pattern = patterns[0]
        
        return {
            "detected": True,
            "type": pattern.type.value,
            "confidence": pattern.confidence,
            "keywords_found": pattern.keywords,
            "description": pattern.description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
