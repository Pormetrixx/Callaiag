"""
Behavior patterns for the AI agent.

This module defines behavioral patterns that influence conversation flow.
"""

import logging
import random
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class BehaviorType(Enum):
    """Enumeration of behavior types."""
    GREETING = "greeting"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    INFORMATION_GATHERING = "information_gathering"
    EMPATHY_RESPONSE = "empathy_response"


class BehaviorPatterns:
    """
    Manages behavioral patterns for the AI agent.
    
    Defines how the agent behaves in different conversation scenarios,
    including response patterns and interaction styles.
    
    Attributes:
        patterns: Dictionary of behavior patterns
        
    Example:
        >>> behaviors = BehaviorPatterns()
        >>> greeting = behaviors.get_pattern(BehaviorType.GREETING)
        >>> response = behaviors.select_response(BehaviorType.GREETING)
    """
    
    DEFAULT_PATTERNS: Dict[BehaviorType, Dict[str, Any]] = {
        BehaviorType.GREETING: {
            "responses": [
                "Guten Tag! Mein Name ist {agent_name}.",
                "Hallo! Schön, dass ich Sie erreiche. Ich bin {agent_name}.",
                "Guten Tag! Hier spricht {agent_name}.",
            ],
            "follow_up": [
                "Wie geht es Ihnen heute?",
                "Haben Sie einen Moment Zeit?",
            ]
        },
        BehaviorType.OBJECTION_HANDLING: {
            "acknowledge": [
                "Ich verstehe Ihre Bedenken.",
                "Das ist ein wichtiger Punkt.",
                "Ich kann Ihre Perspektive nachvollziehen.",
            ],
            "reframe": [
                "Lassen Sie mich das anders erklären.",
                "Betrachten wir es aus einer anderen Perspektive.",
            ]
        },
        BehaviorType.CLOSING: {
            "responses": [
                "Vielen Dank für Ihre Zeit.",
                "Es war mir eine Freude, mit Ihnen zu sprechen.",
                "Danke für das Gespräch.",
            ],
            "call_to_action": [
                "Kann ich Ihnen weitere Informationen zusenden?",
                "Wann wäre ein guter Zeitpunkt für ein Folgegespräch?",
            ]
        },
        BehaviorType.INFORMATION_GATHERING: {
            "questions": [
                "Darf ich fragen, {question}?",
                "Können Sie mir mehr über {topic} erzählen?",
                "Was interessiert Sie besonders an {topic}?",
            ]
        },
        BehaviorType.EMPATHY_RESPONSE: {
            "responses": [
                "Ich verstehe, das muss {emotion} sein.",
                "Das kann ich gut nachvollziehen.",
                "Ich sehe, dass Ihnen das wichtig ist.",
            ]
        }
    }
    
    def __init__(self, custom_patterns: Optional[Dict[BehaviorType, Dict[str, Any]]] = None) -> None:
        """
        Initialize behavior patterns.
        
        Args:
            custom_patterns: Optional custom behavior patterns
        """
        self.patterns: Dict[BehaviorType, Dict[str, Any]] = {}
        
        # Load default patterns
        for behavior_type, pattern in self.DEFAULT_PATTERNS.items():
            self.patterns[behavior_type] = pattern.copy()
        
        # Override with custom patterns
        if custom_patterns:
            for behavior_type, pattern in custom_patterns.items():
                if behavior_type in self.patterns:
                    self.patterns[behavior_type].update(pattern)
                else:
                    self.patterns[behavior_type] = pattern
        
        logger.info("BehaviorPatterns initialized")
    
    def get_pattern(self, behavior_type: BehaviorType) -> Dict[str, Any]:
        """
        Get a behavior pattern.
        
        Args:
            behavior_type: Type of behavior pattern
            
        Returns:
            Dictionary containing the behavior pattern
            
        Example:
            >>> pattern = behaviors.get_pattern(BehaviorType.GREETING)
        """
        return self.patterns.get(behavior_type, {})
    
    def select_response(
        self,
        behavior_type: BehaviorType,
        category: str = "responses",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Select a response from a behavior pattern.
        
        Args:
            behavior_type: Type of behavior
            category: Category within the pattern (e.g., "responses", "follow_up")
            context: Optional context for formatting the response
            
        Returns:
            Selected response string
            
        Example:
            >>> response = behaviors.select_response(
            ...     BehaviorType.GREETING,
            ...     context={"agent_name": "Sarah"}
            ... )
        """
        pattern = self.get_pattern(behavior_type)
        
        if category not in pattern:
            logger.warning(f"Category '{category}' not found in {behavior_type.value}")
            return ""
        
        options = pattern[category]
        if not options:
            return ""
        
        # Select a random response
        response = random.choice(options)
        
        # Format with context if provided
        if context:
            try:
                response = response.format(**context)
            except KeyError as e:
                logger.warning(f"Missing context key for formatting: {e}")
        
        logger.debug(f"Selected {behavior_type.value} response: {response[:50]}...")
        return response
    
    def add_pattern(
        self,
        behavior_type: BehaviorType,
        category: str,
        responses: List[str]
    ) -> None:
        """
        Add responses to a behavior pattern.
        
        Args:
            behavior_type: Type of behavior
            category: Category to add to
            responses: List of response strings
            
        Example:
            >>> behaviors.add_pattern(
            ...     BehaviorType.GREETING,
            ...     "responses",
            ...     ["Hello there!", "Hi!"]
            ... )
        """
        if behavior_type not in self.patterns:
            self.patterns[behavior_type] = {}
        
        if category not in self.patterns[behavior_type]:
            self.patterns[behavior_type][category] = []
        
        self.patterns[behavior_type][category].extend(responses)
        logger.debug(f"Added {len(responses)} responses to {behavior_type.value}/{category}")
    
    def get_all_patterns(self) -> Dict[str, Any]:
        """
        Get all behavior patterns.
        
        Returns:
            Dictionary of all patterns with string keys
        """
        return {
            behavior.value: pattern
            for behavior, pattern in self.patterns.items()
        }
