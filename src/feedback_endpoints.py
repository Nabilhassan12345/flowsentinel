"""
FlowSentinel Feedback & Evaluation API Endpoints

FastAPI router for evaluation and feedback functionality.

Endpoints:
- POST /feedback/submit - Submit user feedback
- POST /feedback/evaluate - Evaluate a response
- GET /feedback/metrics - Get evaluation metrics
- GET /feedback/response/{response_id} - Get feedback for a response
- GET /feedback/low-quality - Get low quality responses for review
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from evaluation import (
    EvaluationService,
    EvaluationResult,
    UserFeedback,
    FeedbackType,
    EvaluationDimension,
    get_evaluation_service,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class SubmitFeedbackRequest(BaseModel):
    """Request to submit user feedback"""
    response_id: str = Field(..., description="ID of the response to provide feedback on")
    feedback_type: str = Field(
        ...,
        description="Type: thumbs_up, thumbs_down, rating, comment, action_taken"
    )
    value: Any = Field(
        ...,
        description="Feedback value (bool for thumbs, 1-5 for rating, str for comment)"
    )
    user_id: Optional[str] = Field(default=None, description="Optional user identifier")


class EvaluateRequest(BaseModel):
    """Request to evaluate a response"""
    response_id: str = Field(..., description="Unique ID for the response")
    query: str = Field(..., description="Original user query")
    response: str = Field(..., description="AI response to evaluate")
    context: Optional[str] = Field(default=None, description="Additional context")
    methods: Optional[List[str]] = Field(
        default=None,
        description="Evaluation methods: llm, rules, or both"
    )


class FeedbackResponse(BaseModel):
    """Response after submitting feedback"""
    id: str
    response_id: str
    feedback_type: str
    value: Any
    submitted_at: str


class EvaluationScoreModel(BaseModel):
    """Model for evaluation score"""
    dimension: str
    score: float
    confidence: float
    reasoning: str


class EvaluationResponse(BaseModel):
    """Response from evaluation"""
    id: str
    response_id: str
    overall_score: float
    scores: List[EvaluationScoreModel]
    evaluation_method: str
    evaluated_at: str


class MetricsResponse(BaseModel):
    """Evaluation metrics response"""
    total_evaluations: int
    overall_average: Optional[float]
    by_dimension: Dict[str, float]
    feedback_stats: Dict[str, Any]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/submit",
    response_model=FeedbackResponse,
    summary="Submit user feedback",
    description="Submit feedback on an AI response (thumbs up/down, rating, or comment)."
)
async def submit_feedback(request: SubmitFeedbackRequest):
    """
    Submit user feedback on a response.
    
    Feedback types:
    - thumbs_up: boolean (true/false)
    - thumbs_down: boolean (treated as inverse of thumbs_up)
    - rating: integer 1-5
    - comment: string
    - action_taken: boolean (user took the suggested action)
    """
    try:
        # Validate feedback type
        valid_types = ["thumbs_up", "thumbs_down", "rating", "comment", "action_taken"]
        if request.feedback_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid feedback type. Must be one of: {valid_types}"
            )
        
        # Handle thumbs_down as inverse thumbs_up
        if request.feedback_type == "thumbs_down":
            feedback_type = FeedbackType.THUMBS_UP
            value = False
        else:
            feedback_type = FeedbackType(request.feedback_type)
            value = request.value
        
        # Validate rating value
        if feedback_type == FeedbackType.RATING:
            if not isinstance(value, (int, float)) or value < 1 or value > 5:
                raise HTTPException(
                    status_code=400,
                    detail="Rating must be between 1 and 5"
                )
        
        service = get_evaluation_service()
        feedback = service.submit_feedback(
            response_id=request.response_id,
            feedback_type=feedback_type.value,
            value=value,
            user_id=request.user_id
        )
        
        return FeedbackResponse(
            id=feedback.id,
            response_id=feedback.response_id,
            feedback_type=feedback.feedback_type.value,
            value=feedback.value,
            submitted_at=feedback.submitted_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    summary="Evaluate a response",
    description="Evaluate an AI response for quality using LLM-as-Judge and/or rule-based methods."
)
async def evaluate_response(request: EvaluateRequest):
    """
    Evaluate an AI response.
    
    Uses multiple evaluation methods:
    - llm: LLM-as-Judge using watsonx.ai
    - rules: Rule-based evaluation (fast, deterministic)
    
    Evaluates on dimensions: relevance, completeness, accuracy, helpfulness, clarity.
    """
    try:
        service = get_evaluation_service()
        
        result = service.evaluate(
            response_id=request.response_id,
            query=request.query,
            response=request.response,
            context=request.context,
            methods=request.methods
        )
        
        return EvaluationResponse(
            id=result.id,
            response_id=result.response_id,
            overall_score=result.overall_score,
            scores=[
                EvaluationScoreModel(
                    dimension=s.dimension.value,
                    score=s.score,
                    confidence=s.confidence,
                    reasoning=s.reasoning
                )
                for s in result.scores
            ],
            evaluation_method=result.evaluation_method,
            evaluated_at=result.evaluated_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get evaluation metrics",
    description="Get aggregated metrics from evaluations and feedback."
)
async def get_metrics(
    hours: Optional[int] = Query(
        default=None,
        description="Filter to last N hours"
    )
):
    """
    Get evaluation and feedback metrics.
    
    Returns:
    - Total evaluations
    - Average overall score
    - Scores by dimension
    - Feedback statistics
    """
    try:
        service = get_evaluation_service()
        
        time_range = timedelta(hours=hours) if hours else None
        metrics = service.get_metrics(time_range)
        
        return MetricsResponse(
            total_evaluations=metrics.get("total_evaluations", 0),
            overall_average=metrics.get("overall_average"),
            by_dimension=metrics.get("by_dimension", {}),
            feedback_stats=metrics.get("feedback_stats", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/response/{response_id}",
    summary="Get feedback for a response",
    description="Get all feedback and evaluation data for a specific response."
)
async def get_response_feedback(response_id: str):
    """Get all feedback and evaluation for a response."""
    try:
        service = get_evaluation_service()
        
        # Get evaluation
        evaluation = service.get_evaluation(response_id)
        
        # Get user feedback
        feedback = service.feedback_collector.get_feedback(response_id)
        aggregate_rating = service.feedback_collector.get_aggregate_rating(response_id)
        
        return {
            "response_id": response_id,
            "evaluation": evaluation.to_dict() if evaluation else None,
            "feedback": [f.to_dict() for f in feedback],
            "aggregate_rating": aggregate_rating,
            "feedback_count": len(feedback)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/low-quality",
    summary="Get low quality responses",
    description="Get responses with low quality scores for human review."
)
async def get_low_quality_responses(
    threshold: float = Query(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Score threshold (responses below this are returned)"
    ),
    limit: int = Query(
        default=10,
        le=50,
        description="Maximum responses to return"
    )
):
    """
    Get low quality responses for review.
    
    Useful for identifying responses that need improvement
    or retraining of the AI system.
    """
    try:
        service = get_evaluation_service()
        
        low_quality = service.get_low_quality_responses(
            threshold=threshold,
            limit=limit
        )
        
        return {
            "threshold": threshold,
            "count": len(low_quality),
            "responses": [r.to_dict() for r in low_quality]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dimensions",
    summary="List evaluation dimensions",
    description="Get information about evaluation dimensions."
)
async def list_dimensions():
    """List all evaluation dimensions with descriptions."""
    dimensions = {
        "relevance": {
            "name": "Relevance",
            "description": "How relevant is the response to the query",
            "weight": 0.25
        },
        "completeness": {
            "name": "Completeness",
            "description": "Does the response fully answer the question",
            "weight": 0.2
        },
        "accuracy": {
            "name": "Accuracy",
            "description": "Is the information correct",
            "weight": 0.25
        },
        "helpfulness": {
            "name": "Helpfulness",
            "description": "Was the response helpful for the user",
            "weight": 0.2
        },
        "clarity": {
            "name": "Clarity",
            "description": "Is the response clear and understandable",
            "weight": 0.1
        },
        "actionability": {
            "name": "Actionability",
            "description": "Does it provide actionable insights",
            "weight": 0.0  # Optional dimension
        }
    }
    
    return {"dimensions": dimensions}


@router.post(
    "/batch-evaluate",
    summary="Batch evaluate responses",
    description="Evaluate multiple responses in a single request."
)
async def batch_evaluate(requests: List[EvaluateRequest]):
    """
    Evaluate multiple responses at once.
    
    Useful for bulk evaluation of historical responses.
    """
    try:
        service = get_evaluation_service()
        results = []
        
        for req in requests:
            result = service.evaluate(
                response_id=req.response_id,
                query=req.query,
                response=req.response,
                context=req.context,
                methods=req.methods
            )
            results.append(EvaluationResponse(
                id=result.id,
                response_id=result.response_id,
                overall_score=result.overall_score,
                scores=[
                    EvaluationScoreModel(
                        dimension=s.dimension.value,
                        score=s.score,
                        confidence=s.confidence,
                        reasoning=s.reasoning
                    )
                    for s in result.scores
                ],
                evaluation_method=result.evaluation_method,
                evaluated_at=result.evaluated_at.isoformat()
            ))
        
        return {
            "evaluated": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
