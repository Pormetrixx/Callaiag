"""
Conversation state machine for managing dialogue flow.

This module manages the state transitions during a conversation.
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Enumeration of conversation states."""
    IDLE = "idle"
    GREETING = "greeting"
    INTRODUCTION = "introduction"
    MAIN_CONVERSATION = "main_conversation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    ENDED = "ended"
    ERROR = "error"


class StateMachine:
    """
    Finite state machine for conversation flow.
    
    Manages state transitions and maintains conversation context throughout
    the dialogue.
    
    Attributes:
        current_state: Current conversation state
        previous_state: Previous conversation state
        context: Conversation context dictionary
        
    Example:
        >>> sm = StateMachine()
        >>> sm.transition_to(ConversationState.GREETING)
        >>> print(sm.current_state)
    """
    
    def __init__(self) -> None:
        """Initialize the state machine."""
        self.current_state: ConversationState = ConversationState.IDLE
        self.previous_state: Optional[ConversationState] = None
        self.context: Dict[str, Any] = {}
        self.transition_history: list = []
        self._state_handlers: Dict[ConversationState, Callable] = {}
        
        logger.info("StateMachine initialized")
    
    def transition_to(
        self,
        new_state: ConversationState,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Transition to a new conversation state.
        
        Args:
            new_state: Target state to transition to
            context: Optional context information for the transition
            
        Example:
            >>> sm.transition_to(ConversationState.GREETING, {"name": "John"})
        """
        if context:
            self.context.update(context)
        
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Record transition
        self.transition_history.append({
            "from": self.previous_state,
            "to": new_state,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        })
        
        logger.info(f"State transition: {self.previous_state.value} -> {new_state.value}")
        
        # Call state handler if registered
        if new_state in self._state_handlers:
            self._state_handlers[new_state](self.context)
    
    def register_handler(
        self,
        state: ConversationState,
        handler: Callable
    ) -> None:
        """
        Register a handler function for a state.
        
        Args:
            state: State to register handler for
            handler: Callable that handles the state
            
        Example:
            >>> def handle_greeting(context):
            ...     print(f"Hello {context.get('name', 'there')}!")
            >>> sm.register_handler(ConversationState.GREETING, handle_greeting)
        """
        self._state_handlers[state] = handler
        logger.debug(f"Registered handler for state: {state.value}")
    
    def can_transition_to(self, target_state: ConversationState) -> bool:
        """
        Check if transition to target state is valid.
        
        Args:
            target_state: State to check transition validity for
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            ConversationState.IDLE: [ConversationState.GREETING],
            ConversationState.GREETING: [ConversationState.INTRODUCTION, ConversationState.ENDED],
            ConversationState.INTRODUCTION: [
                ConversationState.MAIN_CONVERSATION,
                ConversationState.OBJECTION_HANDLING,
                ConversationState.ENDED
            ],
            ConversationState.MAIN_CONVERSATION: [
                ConversationState.OBJECTION_HANDLING,
                ConversationState.CLOSING,
                ConversationState.ENDED
            ],
            ConversationState.OBJECTION_HANDLING: [
                ConversationState.MAIN_CONVERSATION,
                ConversationState.CLOSING,
                ConversationState.ENDED
            ],
            ConversationState.CLOSING: [ConversationState.ENDED],
            ConversationState.ENDED: [ConversationState.IDLE],
            ConversationState.ERROR: [ConversationState.IDLE, ConversationState.ENDED]
        }
        
        # Any state can transition to ERROR
        if target_state == ConversationState.ERROR:
            return True
        
        allowed = valid_transitions.get(self.current_state, [])
        return target_state in allowed
    
    def reset(self) -> None:
        """
        Reset the state machine to initial state.
        
        Clears context and transition history.
        """
        self.current_state = ConversationState.IDLE
        self.previous_state = None
        self.context = {}
        self.transition_history = []
        logger.info("StateMachine reset to initial state")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the conversation context.
        
        Args:
            key: Context key to retrieve
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        return self.context.get(key, default)
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Set a value in the conversation context.
        
        Args:
            key: Context key to set
            value: Value to store
        """
        self.context[key] = value
        logger.debug(f"Set context: {key} = {value}")
