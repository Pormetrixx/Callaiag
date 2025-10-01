"""
Topic tracking for conversations.

This module tracks conversation topics and detects topic changes.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class Topic:
    """
    Represents a conversation topic.
    
    Attributes:
        name: Topic name
        keywords: Keywords associated with this topic
        confidence: Confidence score for topic detection
    """
    
    def __init__(
        self,
        name: str,
        keywords: List[str],
        confidence: float = 0.0
    ) -> None:
        """
        Initialize a topic.
        
        Args:
            name: Topic name
            keywords: List of keywords
            confidence: Confidence score
        """
        self.name: str = name
        self.keywords: List[str] = [k.lower() for k in keywords]
        self.confidence: float = confidence
        self.first_mentioned: datetime = datetime.now()
        self.last_mentioned: datetime = datetime.now()
        self.mention_count: int = 0


class TopicTracker:
    """
    Tracks conversation topics and detects topic changes.
    
    Monitors the conversation to identify active topics and detect when
    the conversation shifts to a new topic.
    
    Attributes:
        active_topics: Currently active topics
        topic_history: History of topics discussed
        
    Example:
        >>> tracker = TopicTracker()
        >>> tracker.add_predefined_topic("pricing", ["price", "cost", "fee"])
        >>> topic = tracker.detect_topic("What's the price?")
        >>> print(topic.name)
    """
    
    def __init__(self) -> None:
        """Initialize the topic tracker."""
        self.predefined_topics: Dict[str, Topic] = {}
        self.active_topics: List[Topic] = []
        self.topic_history: List[Dict[str, Any]] = []
        
        logger.info("TopicTracker initialized")
    
    def add_predefined_topic(
        self,
        name: str,
        keywords: List[str]
    ) -> None:
        """
        Add a predefined topic.
        
        Args:
            name: Topic name
            keywords: List of keywords associated with the topic
            
        Example:
            >>> tracker.add_predefined_topic("pricing", ["price", "cost", "payment"])
        """
        topic = Topic(name, keywords)
        self.predefined_topics[name] = topic
        logger.debug(f"Added predefined topic: {name}")
    
    def detect_topic(self, text: str) -> Optional[Topic]:
        """
        Detect the topic of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected topic or None if no match
            
        Example:
            >>> topic = tracker.detect_topic("How much does it cost?")
            >>> if topic:
            ...     print(f"Detected topic: {topic.name}")
        """
        text_lower = text.lower()
        best_match: Optional[Topic] = None
        max_score = 0.0
        
        for topic_name, topic in self.predefined_topics.items():
            # Count keyword matches
            matches = sum(1 for keyword in topic.keywords if keyword in text_lower)
            
            if matches > 0:
                # Calculate confidence score
                score = matches / len(topic.keywords)
                
                if score > max_score:
                    max_score = score
                    best_match = topic
        
        if best_match:
            best_match.confidence = max_score
            best_match.last_mentioned = datetime.now()
            best_match.mention_count += 1
            
            # Update active topics
            self._update_active_topics(best_match)
            
            logger.debug(f"Detected topic: {best_match.name} (confidence={max_score:.2f})")
        
        return best_match
    
    def _update_active_topics(self, topic: Topic) -> None:
        """
        Update the list of active topics.
        
        Args:
            topic: Topic to add or update
        """
        # Remove if already in active topics
        self.active_topics = [t for t in self.active_topics if t.name != topic.name]
        
        # Add to front of list
        self.active_topics.insert(0, topic)
        
        # Keep only recent topics (e.g., last 5)
        self.active_topics = self.active_topics[:5]
        
        # Record in history
        self.topic_history.append({
            "topic": topic.name,
            "timestamp": datetime.now().isoformat(),
            "confidence": topic.confidence
        })
    
    def get_current_topic(self) -> Optional[Topic]:
        """
        Get the current active topic.
        
        Returns:
            The most recent active topic or None
        """
        if self.active_topics:
            return self.active_topics[0]
        return None
    
    def get_topic_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about discussed topics.
        
        Returns:
            Dictionary with topic statistics
        """
        topic_counts = Counter(
            entry["topic"] for entry in self.topic_history
        )
        
        return {
            "total_topics_discussed": len(set(topic_counts.keys())),
            "topic_counts": dict(topic_counts),
            "most_discussed": topic_counts.most_common(1)[0] if topic_counts else None,
            "current_topic": self.get_current_topic().name if self.get_current_topic() else None
        }
    
    def has_topic_changed(self, window: int = 3) -> bool:
        """
        Check if the topic has changed recently.
        
        Args:
            window: Number of recent history entries to check
            
        Returns:
            True if topic has changed within the window
        """
        if len(self.topic_history) < window:
            return False
        
        recent = self.topic_history[-window:]
        topics = [entry["topic"] for entry in recent]
        
        # Check if there are different topics
        return len(set(topics)) > 1
    
    def reset(self) -> None:
        """Reset the topic tracker."""
        self.active_topics.clear()
        self.topic_history.clear()
        
        # Reset mention counts for predefined topics
        for topic in self.predefined_topics.values():
            topic.mention_count = 0
            topic.confidence = 0.0
        
        logger.info("TopicTracker reset")
