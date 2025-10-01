"""
Conversation memory management.

This module maintains conversation history and context.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class ConversationTurn:
    """
    Represents a single turn in the conversation.
    
    Attributes:
        speaker: Who spoke (agent or user)
        text: What was said
        timestamp: When it was said
        metadata: Additional information
    """
    
    def __init__(
        self,
        speaker: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a conversation turn.
        
        Args:
            speaker: Speaker identifier (agent, user)
            text: Text of what was said
            metadata: Optional metadata about the turn
        """
        self.speaker: str = speaker
        self.text: str = text
        self.timestamp: datetime = datetime.now()
        self.metadata: Dict[str, Any] = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert turn to dictionary representation."""
        return {
            "speaker": self.speaker,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class ConversationMemory:
    """
    Maintains conversation history and context.
    
    Stores conversation turns and provides methods to retrieve context
    for generating appropriate responses.
    
    Attributes:
        turns: List of conversation turns
        max_turns: Maximum number of turns to keep in memory
        
    Example:
        >>> memory = ConversationMemory(max_turns=100)
        >>> memory.add_turn("agent", "Hello, how can I help you?")
        >>> memory.add_turn("user", "I'm interested in your service.")
        >>> recent = memory.get_recent_turns(n=5)
    """
    
    def __init__(self, max_turns: int = 100) -> None:
        """
        Initialize conversation memory.
        
        Args:
            max_turns: Maximum number of turns to keep in memory
        """
        self.max_turns: int = max_turns
        self.turns: deque = deque(maxlen=max_turns)
        self.session_data: Dict[str, Any] = {}
        
        logger.info(f"ConversationMemory initialized with max_turns={max_turns}")
    
    def add_turn(
        self,
        speaker: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a conversation turn to memory.
        
        Args:
            speaker: Speaker identifier
            text: Text of the turn
            metadata: Optional metadata
            
        Example:
            >>> memory.add_turn("user", "What's the price?", {"intent": "inquiry"})
        """
        turn = ConversationTurn(speaker, text, metadata)
        self.turns.append(turn)
        logger.debug(f"Added turn: {speaker}: {text[:50]}...")
    
    def get_recent_turns(self, n: int = 10) -> List[ConversationTurn]:
        """
        Get the most recent conversation turns.
        
        Args:
            n: Number of recent turns to retrieve
            
        Returns:
            List of recent conversation turns
            
        Example:
            >>> recent = memory.get_recent_turns(5)
            >>> for turn in recent:
            ...     print(f"{turn.speaker}: {turn.text}")
        """
        return list(self.turns)[-n:]
    
    def get_conversation_text(self, n: Optional[int] = None) -> str:
        """
        Get formatted conversation text.
        
        Args:
            n: Optional number of recent turns to include
            
        Returns:
            Formatted conversation as a string
        """
        turns = self.get_recent_turns(n) if n else list(self.turns)
        lines = [f"{turn.speaker}: {turn.text}" for turn in turns]
        return "\n".join(lines)
    
    def search_turns(self, keyword: str) -> List[ConversationTurn]:
        """
        Search for turns containing a keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching conversation turns
        """
        keyword_lower = keyword.lower()
        return [
            turn for turn in self.turns
            if keyword_lower in turn.text.lower()
        ]
    
    def get_speaker_turns(self, speaker: str) -> List[ConversationTurn]:
        """
        Get all turns from a specific speaker.
        
        Args:
            speaker: Speaker to filter by
            
        Returns:
            List of turns from the specified speaker
        """
        return [turn for turn in self.turns if turn.speaker == speaker]
    
    def set_session_data(self, key: str, value: Any) -> None:
        """
        Store session-level data.
        
        Args:
            key: Data key
            value: Data value
        """
        self.session_data[key] = value
        logger.debug(f"Set session data: {key}")
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """
        Retrieve session-level data.
        
        Args:
            key: Data key
            default: Default value if not found
            
        Returns:
            Session data value or default
        """
        return self.session_data.get(key, default)
    
    def clear(self) -> None:
        """
        Clear all conversation history and session data.
        """
        self.turns.clear()
        self.session_data.clear()
        logger.info("Conversation memory cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the conversation.
        
        Returns:
            Dictionary with conversation statistics
        """
        agent_turns = len(self.get_speaker_turns("agent"))
        user_turns = len(self.get_speaker_turns("user"))
        
        return {
            "total_turns": len(self.turns),
            "agent_turns": agent_turns,
            "user_turns": user_turns,
            "duration_minutes": self._calculate_duration(),
        }
    
    def _calculate_duration(self) -> float:
        """Calculate conversation duration in minutes."""
        if len(self.turns) < 2:
            return 0.0
        
        first_turn = self.turns[0]
        last_turn = self.turns[-1]
        duration = last_turn.timestamp - first_turn.timestamp
        return duration.total_seconds() / 60
