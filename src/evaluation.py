"""
FlowSentinel Evaluation System

Evaluation and feedback system for AI responses.
Implements multiple evaluation strategies:

1. LLM-as-Judge: Uses watsonx.ai to evaluate response quality
2. Rule-Based: Checks for specific criteria (relevance, completeness)
3. User Feedback: Tracks explicit user ratings
4. Implicit Signals: Tracks actions taken after responses

Metrics tracked:
- Response relevance
- Answer completeness
- Action helpfulness
- User satisfaction
- Response latency
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for IBM watsonx.ai
try:
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.credentials import Credentials
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False


class EvaluationDimension(str, Enum):
    """Dimensions for evaluation"""
    RELEVANCE = "relevance"        # How relevant is the response to the query
    COMPLETENESS = "completeness"  # Does the response fully answer the question
    ACCURACY = "accuracy"          # Is the information correct
    HELPFULNESS = "helpfulness"    # Was the response helpful for the user
    CLARITY = "clarity"            # Is the response clear and understandable
    ACTIONABILITY = "actionability" # Does it provide actionable insights


class FeedbackType(str, Enum):
    """Types of user feedback"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"  # 1-5 scale
    COMMENT = "comment"
    ACTION_TAKEN = "action_taken"  # User took the suggested action


@dataclass
class EvaluationScore:
    """Score for a single evaluation dimension"""
    dimension: EvaluationDimension
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "score": self.score,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


@dataclass
class EvaluationResult:
    """Complete evaluation result"""
    id: str
    response_id: str
    query: str
    response: str
    scores: List[EvaluationScore]
    overall_score: float
    evaluation_method: str
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "response_id": self.response_id,
            "query": self.query,
            "response": self.response[:200] + "..." if len(self.response) > 200 else self.response,
            "scores": [s.to_dict() for s in self.scores],
            "overall_score": self.overall_score,
            "evaluation_method": self.evaluation_method,
            "evaluated_at": self.evaluated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass 
class UserFeedback:
    """User feedback on a response"""
    id: str
    response_id: str
    feedback_type: FeedbackType
    value: Any  # thumbs_up=True, rating=1-5, comment=str
    user_id: Optional[str] = None
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "response_id": self.response_id,
            "feedback_type": self.feedback_type.value,
            "value": self.value,
            "user_id": self.user_id,
            "submitted_at": self.submitted_at.isoformat()
        }


class LLMJudge:
    """
    Uses an LLM to evaluate response quality.
    
    Implements the "LLM-as-Judge" pattern for automated evaluation.
    """
    
    EVALUATION_PROMPT = """You are an expert evaluator for an AI project intelligence assistant.

Evaluate the following response based on these criteria:
1. RELEVANCE (0-1): How relevant is the response to the query?
2. COMPLETENESS (0-1): Does the response fully address the question?
3. ACCURACY (0-1): Is the information likely to be correct?
4. HELPFULNESS (0-1): Is this response useful for the user?
5. CLARITY (0-1): Is the response clear and easy to understand?

Query: {query}

Response: {response}

Context: {context}

Provide your evaluation in this exact JSON format:
{{
    "relevance": {{"score": 0.0, "reasoning": "..."}},
    "completeness": {{"score": 0.0, "reasoning": "..."}},
    "accuracy": {{"score": 0.0, "reasoning": "..."}},
    "helpfulness": {{"score": 0.0, "reasoning": "..."}},
    "clarity": {{"score": 0.0, "reasoning": "..."}}
}}"""

    def __init__(self):
        self.model = self._init_model()
    
    def _init_model(self) -> Optional[Any]:
        """Initialize watsonx.ai model for evaluation"""
        if not WATSONX_AVAILABLE:
            return None
        
        api_key = os.getenv("WATSONX_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        
        if not api_key or not project_id:
            return None
        
        try:
            credentials = Credentials(
                url="https://us-south.ml.cloud.ibm.com",
                api_key=api_key
            )
            
            return ModelInference(
                model_id="ibm/granite-3-8b-instruct",
                credentials=credentials,
                project_id=project_id,
                params={
                    "max_new_tokens": 512,
                    "temperature": 0.1
                }
            )
        except Exception as e:
            logger.error(f"Failed to init evaluation model: {e}")
            return None
    
    def evaluate(
        self,
        query: str,
        response: str,
        context: Optional[str] = None
    ) -> List[EvaluationScore]:
        """Evaluate a response using LLM-as-Judge"""
        
        if not self.model:
            return self._fallback_evaluate(query, response)
        
        try:
            prompt = self.EVALUATION_PROMPT.format(
                query=query,
                response=response,
                context=context or "No additional context"
            )
            
            result = self.model.generate(prompt)
            text = result.get("results", [{}])[0].get("generated_text", "")
            
            # Parse JSON response
            scores = self._parse_evaluation(text)
            return scores
            
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            return self._fallback_evaluate(query, response)
    
    def _parse_evaluation(self, text: str) -> List[EvaluationScore]:
        """Parse LLM evaluation response"""
        try:
            # Extract JSON
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end]
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end]
            
            data = json.loads(text)
            
            scores = []
            dimension_map = {
                "relevance": EvaluationDimension.RELEVANCE,
                "completeness": EvaluationDimension.COMPLETENESS,
                "accuracy": EvaluationDimension.ACCURACY,
                "helpfulness": EvaluationDimension.HELPFULNESS,
                "clarity": EvaluationDimension.CLARITY
            }
            
            for key, dim in dimension_map.items():
                if key in data:
                    scores.append(EvaluationScore(
                        dimension=dim,
                        score=float(data[key].get("score", 0.5)),
                        confidence=0.8,  # LLM evaluation confidence
                        reasoning=data[key].get("reasoning", "")
                    ))
            
            return scores
            
        except Exception as e:
            logger.error(f"Failed to parse evaluation: {e}")
            return []
    
    def _fallback_evaluate(
        self,
        query: str,
        response: str
    ) -> List[EvaluationScore]:
        """Rule-based fallback evaluation"""
        scores = []
        
        # Relevance: Check for keyword overlap
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words) / max(len(query_words), 1)
        
        scores.append(EvaluationScore(
            dimension=EvaluationDimension.RELEVANCE,
            score=min(1.0, overlap * 2),
            confidence=0.5,
            reasoning="Based on keyword overlap"
        ))
        
        # Completeness: Check response length relative to query
        length_ratio = len(response) / max(len(query) * 3, 1)
        completeness = min(1.0, length_ratio)
        
        scores.append(EvaluationScore(
            dimension=EvaluationDimension.COMPLETENESS,
            score=completeness,
            confidence=0.4,
            reasoning="Based on response length"
        ))
        
        # Clarity: Check for structure (sentences, paragraphs)
        has_periods = response.count(".") >= 1
        has_structure = len(response) > 50
        clarity = 0.5 + (0.25 if has_periods else 0) + (0.25 if has_structure else 0)
        
        scores.append(EvaluationScore(
            dimension=EvaluationDimension.CLARITY,
            score=clarity,
            confidence=0.4,
            reasoning="Based on text structure"
        ))
        
        return scores


class RuleBasedEvaluator:
    """
    Rule-based evaluation for specific criteria.
    
    Fast and deterministic, good for baseline checks.
    """
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[Dict[str, Any]]:
        """Initialize evaluation rules"""
        return [
            {
                "name": "min_length",
                "dimension": EvaluationDimension.COMPLETENESS,
                "check": lambda r: len(r) >= 20,
                "weight": 0.3,
                "description": "Response has minimum length"
            },
            {
                "name": "no_error_message",
                "dimension": EvaluationDimension.HELPFULNESS,
                "check": lambda r: "error" not in r.lower() and "failed" not in r.lower(),
                "weight": 0.2,
                "description": "Response doesn't contain error indicators"
            },
            {
                "name": "actionable_content",
                "dimension": EvaluationDimension.ACTIONABILITY,
                "check": lambda r: any(w in r.lower() for w in ["should", "recommend", "suggest", "try", "consider"]),
                "weight": 0.3,
                "description": "Response contains actionable language"
            },
            {
                "name": "specific_details",
                "dimension": EvaluationDimension.ACCURACY,
                "check": lambda r: any(char.isdigit() for char in r) or "@" in r or "/" in r,
                "weight": 0.2,
                "description": "Response contains specific details"
            }
        ]
    
    def evaluate(self, response: str) -> List[EvaluationScore]:
        """Evaluate response against rules"""
        scores_by_dimension = defaultdict(list)
        
        for rule in self.rules:
            passed = rule["check"](response)
            score = 1.0 if passed else 0.0
            
            scores_by_dimension[rule["dimension"]].append({
                "score": score,
                "weight": rule["weight"],
                "name": rule["name"]
            })
        
        # Aggregate scores by dimension
        result = []
        for dimension, rule_scores in scores_by_dimension.items():
            total_weight = sum(s["weight"] for s in rule_scores)
            weighted_score = sum(s["score"] * s["weight"] for s in rule_scores) / total_weight
            
            result.append(EvaluationScore(
                dimension=dimension,
                score=weighted_score,
                confidence=0.6,  # Rule-based is moderately confident
                reasoning=f"Based on {len(rule_scores)} rules"
            ))
        
        return result


class FeedbackCollector:
    """
    Collects and stores user feedback.
    
    Supports multiple feedback types and aggregates ratings.
    """
    
    def __init__(self):
        self._feedback: List[UserFeedback] = []
        self._response_feedback: Dict[str, List[UserFeedback]] = defaultdict(list)
    
    def submit(
        self,
        response_id: str,
        feedback_type: FeedbackType,
        value: Any,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> UserFeedback:
        """Submit user feedback"""
        import uuid
        
        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            response_id=response_id,
            feedback_type=feedback_type,
            value=value,
            user_id=user_id,
            context=context or {}
        )
        
        self._feedback.append(feedback)
        self._response_feedback[response_id].append(feedback)
        
        logger.info(f"Feedback collected: {feedback_type.value} for {response_id}")
        
        return feedback
    
    def get_feedback(self, response_id: str) -> List[UserFeedback]:
        """Get all feedback for a response"""
        return self._response_feedback.get(response_id, [])
    
    def get_aggregate_rating(self, response_id: str) -> Optional[float]:
        """Get aggregate rating for a response"""
        feedback = self._response_feedback.get(response_id, [])
        
        scores = []
        for fb in feedback:
            if fb.feedback_type == FeedbackType.THUMBS_UP:
                scores.append(1.0 if fb.value else 0.0)
            elif fb.feedback_type == FeedbackType.RATING:
                scores.append(fb.value / 5.0)  # Normalize to 0-1
        
        return statistics.mean(scores) if scores else None
    
    def get_statistics(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get feedback statistics"""
        feedback = self._feedback
        
        if time_range:
            cutoff = datetime.utcnow() - time_range
            feedback = [f for f in feedback if f.submitted_at > cutoff]
        
        if not feedback:
            return {"total": 0}
        
        # Count by type
        type_counts = defaultdict(int)
        for fb in feedback:
            type_counts[fb.feedback_type.value] += 1
        
        # Calculate positive rate
        thumbs = [f for f in feedback if f.feedback_type == FeedbackType.THUMBS_UP]
        positive_rate = sum(1 for f in thumbs if f.value) / len(thumbs) if thumbs else None
        
        # Calculate average rating
        ratings = [f.value for f in feedback if f.feedback_type == FeedbackType.RATING]
        avg_rating = statistics.mean(ratings) if ratings else None
        
        return {
            "total": len(feedback),
            "by_type": dict(type_counts),
            "positive_rate": positive_rate,
            "average_rating": avg_rating,
            "responses_with_feedback": len(self._response_feedback)
        }


class EvaluationService:
    """
    Main service for evaluating AI responses.
    
    Combines multiple evaluation methods for comprehensive assessment.
    """
    
    def __init__(self):
        self.llm_judge = LLMJudge()
        self.rule_evaluator = RuleBasedEvaluator()
        self.feedback_collector = FeedbackCollector()
        
        self._evaluations: List[EvaluationResult] = []
    
    def evaluate(
        self,
        response_id: str,
        query: str,
        response: str,
        context: Optional[str] = None,
        methods: Optional[List[str]] = None
    ) -> EvaluationResult:
        """
        Evaluate a response using multiple methods.
        
        Args:
            response_id: Unique ID of the response
            query: Original user query
            response: AI response to evaluate
            context: Optional context
            methods: Which methods to use (llm, rules, or both)
        
        Returns:
            EvaluationResult with scores
        """
        import uuid
        
        methods = methods or ["llm", "rules"]
        all_scores = []
        
        if "llm" in methods:
            llm_scores = self.llm_judge.evaluate(query, response, context)
            for score in llm_scores:
                score.metadata = {"method": "llm"}
            all_scores.extend(llm_scores)
        
        if "rules" in methods:
            rule_scores = self.rule_evaluator.evaluate(response)
            for score in rule_scores:
                score.metadata = {"method": "rules"}
            all_scores.extend(rule_scores)
        
        # Calculate overall score
        if all_scores:
            overall = statistics.mean([s.score for s in all_scores])
        else:
            overall = 0.5
        
        result = EvaluationResult(
            id=str(uuid.uuid4()),
            response_id=response_id,
            query=query,
            response=response,
            scores=all_scores,
            overall_score=overall,
            evaluation_method="+".join(methods),
            metadata={"context_provided": context is not None}
        )
        
        self._evaluations.append(result)
        
        logger.info(f"Evaluated response {response_id}: overall={overall:.2f}")
        
        return result
    
    def submit_feedback(
        self,
        response_id: str,
        feedback_type: str,
        value: Any,
        user_id: Optional[str] = None
    ) -> UserFeedback:
        """Submit user feedback for a response"""
        fb_type = FeedbackType(feedback_type)
        return self.feedback_collector.submit(
            response_id=response_id,
            feedback_type=fb_type,
            value=value,
            user_id=user_id
        )
    
    def get_evaluation(self, response_id: str) -> Optional[EvaluationResult]:
        """Get evaluation for a specific response"""
        for eval in self._evaluations:
            if eval.response_id == response_id:
                return eval
        return None
    
    def get_metrics(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get evaluation metrics"""
        evaluations = self._evaluations
        
        if time_range:
            cutoff = datetime.utcnow() - time_range
            evaluations = [e for e in evaluations if e.evaluated_at > cutoff]
        
        if not evaluations:
            return {"total_evaluations": 0}
        
        # Calculate averages by dimension
        dimension_scores = defaultdict(list)
        for eval in evaluations:
            for score in eval.scores:
                dimension_scores[score.dimension.value].append(score.score)
        
        dimension_averages = {
            dim: statistics.mean(scores)
            for dim, scores in dimension_scores.items()
        }
        
        # Overall metrics
        overall_scores = [e.overall_score for e in evaluations]
        
        return {
            "total_evaluations": len(evaluations),
            "overall_average": statistics.mean(overall_scores),
            "overall_min": min(overall_scores),
            "overall_max": max(overall_scores),
            "by_dimension": dimension_averages,
            "feedback_stats": self.feedback_collector.get_statistics(time_range)
        }
    
    def get_low_quality_responses(
        self,
        threshold: float = 0.5,
        limit: int = 10
    ) -> List[EvaluationResult]:
        """Get responses with low quality scores for review"""
        low_quality = [
            e for e in self._evaluations
            if e.overall_score < threshold
        ]
        
        # Sort by score ascending (worst first)
        low_quality.sort(key=lambda e: e.overall_score)
        
        return low_quality[:limit]


# Global service instance
_evaluation_service: Optional[EvaluationService] = None


def get_evaluation_service() -> EvaluationService:
    """Get the global evaluation service"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service
