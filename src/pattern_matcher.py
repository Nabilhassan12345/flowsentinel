"""
FlowSentinel Pattern Matcher

Finds similar historical patterns in project events to provide
insights from past experiences.

Features:
- Semantic similarity matching using embeddings
- Pattern clustering and categorization
- Outcome tracking (what worked, what didn't)
- Recommendation generation based on past patterns

This helps answer: "Has this happened before? What did we do?"
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our RAG components
try:
    from rag import RAGPipeline, get_rag_pipeline
    from vector_store import VectorStore, get_vector_store
    from embeddings import EmbeddingService, get_embedding_service
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAG components not available for pattern matching")


class PatternType(str, Enum):
    """Types of patterns we can identify"""
    BLOCKER = "blocker"           # Something blocking progress
    RISK = "risk"                 # Potential risk identified
    SUCCESS = "success"           # Successful completion
    DELAY = "delay"               # Timeline slippage
    CONFLICT = "conflict"         # Team/resource conflict
    ESCALATION = "escalation"     # Issue escalated
    RESOLUTION = "resolution"     # Issue resolved
    RECURRING = "recurring"       # Recurring issue
    UNKNOWN = "unknown"


class OutcomeType(str, Enum):
    """Outcome of a pattern"""
    POSITIVE = "positive"     # Pattern led to good outcome
    NEGATIVE = "negative"     # Pattern led to bad outcome
    NEUTRAL = "neutral"       # No clear outcome
    PENDING = "pending"       # Outcome not yet known


@dataclass
class Pattern:
    """Represents a detected pattern"""
    id: str
    type: PatternType
    description: str
    events: List[Dict[str, Any]]
    detected_at: datetime
    confidence: float  # 0.0 to 1.0
    keywords: List[str] = field(default_factory=list)
    team_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "event_count": len(self.events),
            "detected_at": self.detected_at.isoformat(),
            "confidence": self.confidence,
            "keywords": self.keywords,
            "team_id": self.team_id
        }


@dataclass
class PatternMatch:
    """A match between current situation and historical pattern"""
    pattern: Pattern
    similarity: float  # 0.0 to 1.0
    outcome: OutcomeType
    actions_taken: List[Dict[str, Any]]
    outcome_description: str
    time_to_resolve: Optional[timedelta] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern.to_dict(),
            "similarity": self.similarity,
            "outcome": self.outcome.value,
            "actions_taken": self.actions_taken,
            "outcome_description": self.outcome_description,
            "days_to_resolve": self.time_to_resolve.days if self.time_to_resolve else None
        }


@dataclass
class Recommendation:
    """Recommendation based on pattern analysis"""
    action: str
    reasoning: str
    confidence: float
    based_on_patterns: int
    success_rate: float
    priority: str  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "based_on_patterns": self.based_on_patterns,
            "success_rate": self.success_rate,
            "priority": self.priority
        }


class PatternDetector:
    """
    Detects patterns in project events.
    
    Uses keyword matching and semantic analysis to identify
    common patterns like blockers, risks, delays, etc.
    """
    
    # Keywords for pattern detection
    PATTERN_KEYWORDS = {
        PatternType.BLOCKER: [
            "blocked", "blocking", "blocker", "waiting on", "depends on",
            "can't proceed", "stuck", "held up", "dependency"
        ],
        PatternType.RISK: [
            "risk", "concern", "worried", "might", "could impact",
            "potential issue", "warning", "careful", "risky"
        ],
        PatternType.DELAY: [
            "delayed", "postponed", "pushed back", "slipped",
            "behind schedule", "late", "overdue", "missed deadline"
        ],
        PatternType.SUCCESS: [
            "completed", "done", "shipped", "merged", "released",
            "finished", "deployed", "launched", "achieved"
        ],
        PatternType.CONFLICT: [
            "conflict", "disagreement", "misalignment", "different views",
            "tension", "competing priorities", "resource conflict"
        ],
        PatternType.ESCALATION: [
            "escalate", "escalation", "urgent", "critical",
            "needs attention", "manager", "leadership", "priority 1"
        ],
        PatternType.RESOLUTION: [
            "resolved", "fixed", "addressed", "solved",
            "unblocked", "issue closed", "working now"
        ]
    }
    
    def detect(self, events: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in a list of events"""
        patterns = []
        
        for event in events:
            pattern = self._analyze_event(event)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_event(self, event: Dict[str, Any]) -> Optional[Pattern]:
        """Analyze a single event for patterns"""
        # Get text content from event
        text = self._extract_text(event)
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Check each pattern type
        best_match = (PatternType.UNKNOWN, 0.0, [])
        
        for pattern_type, keywords in self.PATTERN_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                confidence = min(1.0, len(matches) / 3)  # 3+ matches = 100%
                if confidence > best_match[1]:
                    best_match = (pattern_type, confidence, matches)
        
        if best_match[1] < 0.1:  # No significant match
            return None
        
        pattern_type, confidence, keywords = best_match
        
        return Pattern(
            id=self._generate_id(event),
            type=pattern_type,
            description=text[:200],
            events=[event],
            detected_at=datetime.utcnow(),
            confidence=confidence,
            keywords=keywords,
            team_id=event.get("team_id")
        )
    
    def _extract_text(self, event: Dict[str, Any]) -> str:
        """Extract text content from event"""
        data = event.get("data", {})
        
        # Try various text fields
        text_parts = []
        
        for field in ["message", "summary", "title", "description", "body", "content"]:
            if field in data and data[field]:
                text_parts.append(str(data[field]))
        
        # Also check nested structures
        if "comment" in data and isinstance(data["comment"], dict):
            text_parts.append(data["comment"].get("body", ""))
        
        return " ".join(text_parts)
    
    def _generate_id(self, event: Dict[str, Any]) -> str:
        """Generate a unique pattern ID"""
        content = json.dumps(event, sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()[:12]


class PatternMatcher:
    """
    Finds similar historical patterns.
    
    Combines semantic search with pattern detection to find
    relevant historical experiences.
    """
    
    def __init__(
        self,
        vector_store: Optional[Any] = None,
        embedding_service: Optional[Any] = None
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.detector = PatternDetector()
        
        # Pattern history (in production, this would be in database)
        self._patterns: List[Pattern] = []
        self._outcomes: Dict[str, PatternMatch] = {}  # pattern_id -> match
    
    def find_similar(
        self,
        query: str,
        limit: int = 5,
        min_similarity: float = 0.6
    ) -> List[PatternMatch]:
        """
        Find patterns similar to the current situation.
        
        Args:
            query: Description of current situation
            limit: Maximum patterns to return
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of similar pattern matches
        """
        matches = []
        
        # Use vector search if available
        if RAG_AVAILABLE and self.vector_store:
            try:
                results = self.vector_store.search_similar(query, limit=limit * 2)
                
                for result in results:
                    if result.get("score", 0) < min_similarity:
                        continue
                    
                    # Find or create pattern for this result
                    event = result.get("metadata", {})
                    pattern = self._get_or_create_pattern(event)
                    
                    if pattern:
                        match = self._create_match(pattern, result.get("score", 0.5))
                        matches.append(match)
                
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
        
        # Also search stored patterns
        pattern_matches = self._search_stored_patterns(query, limit, min_similarity)
        matches.extend(pattern_matches)
        
        # Deduplicate and sort by similarity
        seen_ids = set()
        unique_matches = []
        for match in sorted(matches, key=lambda m: m.similarity, reverse=True):
            if match.pattern.id not in seen_ids:
                seen_ids.add(match.pattern.id)
                unique_matches.append(match)
        
        return unique_matches[:limit]
    
    def _get_or_create_pattern(self, event: Dict[str, Any]) -> Optional[Pattern]:
        """Get existing pattern or create new one from event"""
        patterns = self.detector.detect([event])
        return patterns[0] if patterns else None
    
    def _create_match(
        self,
        pattern: Pattern,
        similarity: float
    ) -> PatternMatch:
        """Create a pattern match with outcome info"""
        # Look up stored outcome
        stored = self._outcomes.get(pattern.id)
        
        if stored:
            return PatternMatch(
                pattern=pattern,
                similarity=similarity,
                outcome=stored.outcome,
                actions_taken=stored.actions_taken,
                outcome_description=stored.outcome_description,
                time_to_resolve=stored.time_to_resolve
            )
        
        # Create default match (outcome unknown)
        return PatternMatch(
            pattern=pattern,
            similarity=similarity,
            outcome=OutcomeType.PENDING,
            actions_taken=[],
            outcome_description="Outcome not yet recorded"
        )
    
    def _search_stored_patterns(
        self,
        query: str,
        limit: int,
        min_similarity: float
    ) -> List[PatternMatch]:
        """Search stored patterns using keyword matching"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        matches = []
        
        for pattern in self._patterns:
            # Calculate keyword overlap
            pattern_words = set(pattern.description.lower().split())
            pattern_words.update(pattern.keywords)
            
            overlap = len(query_words & pattern_words)
            if overlap == 0:
                continue
            
            # Calculate similarity based on overlap
            similarity = overlap / max(len(query_words), len(pattern_words))
            
            if similarity >= min_similarity:
                match = self._create_match(pattern, similarity)
                matches.append(match)
        
        return sorted(matches, key=lambda m: m.similarity, reverse=True)[:limit]
    
    def record_pattern(
        self,
        pattern: Pattern,
        outcome: OutcomeType = OutcomeType.PENDING,
        actions_taken: Optional[List[Dict[str, Any]]] = None,
        outcome_description: str = "",
        time_to_resolve: Optional[timedelta] = None
    ) -> None:
        """Record a pattern and its outcome"""
        self._patterns.append(pattern)
        
        self._outcomes[pattern.id] = PatternMatch(
            pattern=pattern,
            similarity=1.0,
            outcome=outcome,
            actions_taken=actions_taken or [],
            outcome_description=outcome_description,
            time_to_resolve=time_to_resolve
        )
        
        logger.info(f"Recorded pattern: {pattern.id} ({pattern.type.value})")
    
    def update_outcome(
        self,
        pattern_id: str,
        outcome: OutcomeType,
        outcome_description: str,
        actions_taken: Optional[List[Dict[str, Any]]] = None,
        time_to_resolve: Optional[timedelta] = None
    ) -> bool:
        """Update the outcome of a recorded pattern"""
        if pattern_id not in self._outcomes:
            return False
        
        match = self._outcomes[pattern_id]
        self._outcomes[pattern_id] = PatternMatch(
            pattern=match.pattern,
            similarity=match.similarity,
            outcome=outcome,
            actions_taken=actions_taken or match.actions_taken,
            outcome_description=outcome_description,
            time_to_resolve=time_to_resolve
        )
        
        return True
    
    def get_recommendations(
        self,
        query: str,
        limit: int = 3
    ) -> List[Recommendation]:
        """
        Get recommendations based on similar patterns.
        
        Analyzes what worked in similar situations and generates
        actionable recommendations.
        """
        # Find similar patterns
        matches = self.find_similar(query, limit=10, min_similarity=0.5)
        
        if not matches:
            return [Recommendation(
                action="Monitor the situation",
                reasoning="No similar historical patterns found",
                confidence=0.3,
                based_on_patterns=0,
                success_rate=0.0,
                priority="low"
            )]
        
        # Analyze actions from positive outcomes
        action_stats = defaultdict(lambda: {"positive": 0, "negative": 0, "total": 0})
        
        for match in matches:
            for action in match.actions_taken:
                action_type = action.get("type", "unknown")
                action_stats[action_type]["total"] += 1
                
                if match.outcome == OutcomeType.POSITIVE:
                    action_stats[action_type]["positive"] += 1
                elif match.outcome == OutcomeType.NEGATIVE:
                    action_stats[action_type]["negative"] += 1
        
        # Generate recommendations
        recommendations = []
        
        for action_type, stats in action_stats.items():
            if stats["total"] == 0:
                continue
            
            success_rate = stats["positive"] / stats["total"]
            confidence = min(1.0, stats["total"] / 5)  # More examples = higher confidence
            
            if success_rate >= 0.5:  # Only recommend if >=50% success rate
                priority = "high" if success_rate >= 0.8 else "medium" if success_rate >= 0.6 else "low"
                
                recommendations.append(Recommendation(
                    action=action_type,
                    reasoning=f"This action led to positive outcomes in {stats['positive']}/{stats['total']} similar cases",
                    confidence=confidence,
                    based_on_patterns=stats["total"],
                    success_rate=success_rate,
                    priority=priority
                ))
        
        # Sort by success rate * confidence
        recommendations.sort(
            key=lambda r: r.success_rate * r.confidence,
            reverse=True
        )
        
        return recommendations[:limit]
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about stored patterns"""
        if not self._patterns:
            return {"total_patterns": 0}
        
        type_counts = defaultdict(int)
        outcome_counts = defaultdict(int)
        
        for pattern in self._patterns:
            type_counts[pattern.type.value] += 1
        
        for match in self._outcomes.values():
            outcome_counts[match.outcome.value] += 1
        
        return {
            "total_patterns": len(self._patterns),
            "by_type": dict(type_counts),
            "by_outcome": dict(outcome_counts),
            "outcomes_recorded": len(self._outcomes)
        }


# Global matcher instance
_matcher: Optional[PatternMatcher] = None


def get_pattern_matcher() -> PatternMatcher:
    """Get or create the global pattern matcher"""
    global _matcher
    if _matcher is None:
        vector_store = get_vector_store() if RAG_AVAILABLE else None
        embedding_service = get_embedding_service() if RAG_AVAILABLE else None
        _matcher = PatternMatcher(
            vector_store=vector_store,
            embedding_service=embedding_service
        )
    return _matcher
