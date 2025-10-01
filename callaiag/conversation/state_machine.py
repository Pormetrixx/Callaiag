#!/usr/bin/env python3
"""
Conversation state machine for Callaiag.

This module implements a finite state machine for managing conversation flow
during calls, handling different stages of the conversation.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation state enumeration."""
    IDLE = "idle"
    GREETING = "greeting"
    INTRODUCTION = "introduction"
    PITCH = "pitch"
    OBJECTION_HANDLING = "objection_handling"
    FAQ = "faq"
    CLOSING = "closing"
    FOLLOWUP = "followup"
    ENDED = "ended"


class ConversationStateMachine:
    """
    Finite state machine for conversation management.
    
    Manages conversation flow through different states with transitions
    based on customer responses and conversation context.
    """
    
    def __init__(self, config):
        """
        Initialize conversation state machine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.current_state = ConversationState.IDLE
        self.conversation_history = []
        self.context = {}
        self.state_handlers = self._initialize_handlers()
        self.transitions = self._initialize_transitions()
        
        logger.info("Conversation state machine initialized")
    
    def _initialize_handlers(self) -> Dict[ConversationState, Callable]:
        """Initialize state handlers."""
        return {
            ConversationState.GREETING: self._handle_greeting,
            ConversationState.INTRODUCTION: self._handle_introduction,
            ConversationState.PITCH: self._handle_pitch,
            ConversationState.OBJECTION_HANDLING: self._handle_objection,
            ConversationState.FAQ: self._handle_faq,
            ConversationState.CLOSING: self._handle_closing,
            ConversationState.FOLLOWUP: self._handle_followup,
        }
    
    def _initialize_transitions(self) -> Dict[ConversationState, list]:
        """Initialize valid state transitions."""
        return {
            ConversationState.IDLE: [ConversationState.GREETING],
            ConversationState.GREETING: [ConversationState.INTRODUCTION, ConversationState.ENDED],
            ConversationState.INTRODUCTION: [ConversationState.PITCH, ConversationState.FAQ, ConversationState.ENDED],
            ConversationState.PITCH: [ConversationState.OBJECTION_HANDLING, ConversationState.FAQ, ConversationState.CLOSING, ConversationState.ENDED],
            ConversationState.OBJECTION_HANDLING: [ConversationState.PITCH, ConversationState.FAQ, ConversationState.CLOSING, ConversationState.ENDED],
            ConversationState.FAQ: [ConversationState.PITCH, ConversationState.CLOSING, ConversationState.ENDED],
            ConversationState.CLOSING: [ConversationState.FOLLOWUP, ConversationState.ENDED],
            ConversationState.FOLLOWUP: [ConversationState.ENDED],
        }
    
    def start_conversation(self, context: Optional[Dict[str, Any]] = None):
        """
        Start a new conversation.
        
        Args:
            context: Initial conversation context
        """
        self.current_state = ConversationState.GREETING
        self.conversation_history = []
        self.context = context or {}
        logger.info("Conversation started")
    
    def process_input(self, user_input: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process user input and generate response.
        
        Args:
            user_input: User's speech input
            metadata: Optional metadata (emotion, confidence, etc.)
            
        Returns:
            Agent's response
        """
        # Add to history
        self.conversation_history.append({
            'type': 'user',
            'text': user_input,
            'state': self.current_state.value,
            'metadata': metadata or {}
        })
        
        # Get current state handler
        handler = self.state_handlers.get(self.current_state)
        
        if handler:
            response, next_state = handler(user_input, metadata)
            
            # Transition to next state
            if next_state:
                self.transition_to(next_state)
            
            # Add response to history
            self.conversation_history.append({
                'type': 'agent',
                'text': response,
                'state': self.current_state.value
            })
            
            return response
        
        return "I'm not sure how to respond to that."
    
    def transition_to(self, new_state: ConversationState):
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
        """
        # Check if transition is valid
        valid_transitions = self.transitions.get(self.current_state, [])
        
        if new_state not in valid_transitions:
            logger.warning(f"Invalid transition from {self.current_state.value} to {new_state.value}")
            return
        
        logger.info(f"State transition: {self.current_state.value} -> {new_state.value}")
        self.current_state = new_state
    
    def _handle_greeting(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle greeting state."""
        # Check for negative response
        negative_keywords = ['nein', 'no', 'nicht', 'keine zeit', 'busy']
        if any(kw in user_input.lower() for kw in negative_keywords):
            return "Verstehe. Danke für Ihre Zeit. Auf Wiedersehen.", ConversationState.ENDED
        
        # Move to introduction
        return None, ConversationState.INTRODUCTION
    
    def _handle_introduction(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle introduction state."""
        response = "Kurz zu mir: Ich rufe an, um Ihnen unser neues Produkt vorzustellen, das Ihnen helfen kann..."
        return response, ConversationState.PITCH
    
    def _handle_pitch(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle pitch state."""
        # Check for questions (FAQ)
        question_keywords = ['wie', 'was', 'wann', 'wo', 'warum', 'kosten', 'preis']
        if any(kw in user_input.lower() for kw in question_keywords):
            return None, ConversationState.FAQ
        
        # Check for objections
        objection_keywords = ['aber', 'jedoch', 'teuer', 'nicht sicher', 'zweifel']
        if any(kw in user_input.lower() for kw in objection_keywords):
            return None, ConversationState.OBJECTION_HANDLING
        
        # Check for interest
        interest_keywords = ['interessant', 'ja', 'gerne', 'mehr', 'details']
        if any(kw in user_input.lower() for kw in interest_keywords):
            return "Das freut mich zu hören! Lassen Sie uns zum nächsten Schritt übergehen...", ConversationState.CLOSING
        
        return "Haben Sie weitere Fragen dazu?", None
    
    def _handle_objection(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle objection handling state."""
        response = "Ich verstehe Ihre Bedenken. Lassen Sie mich das erklären..."
        return response, ConversationState.PITCH
    
    def _handle_faq(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle FAQ state."""
        response = "Das ist eine gute Frage. Hier ist die Antwort..."
        return response, ConversationState.PITCH
    
    def _handle_closing(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle closing state."""
        # Check for agreement
        agreement_keywords = ['ja', 'okay', 'einverstanden', 'gerne']
        if any(kw in user_input.lower() for kw in agreement_keywords):
            return "Wunderbar! Ich werde die Details für Sie vorbereiten...", ConversationState.FOLLOWUP
        
        return "Möchten Sie mehr darüber erfahren?", None
    
    def _handle_followup(self, user_input: str, metadata: Optional[Dict]) -> tuple:
        """Handle followup state."""
        response = "Vielen Dank für Ihre Zeit. Ich werde mich bald bei Ihnen melden. Auf Wiedersehen!"
        return response, ConversationState.ENDED
    
    def get_state(self) -> ConversationState:
        """Get current conversation state."""
        return self.current_state
    
    def get_history(self) -> list:
        """Get conversation history."""
        return self.conversation_history
    
    def reset(self):
        """Reset state machine to initial state."""
        self.current_state = ConversationState.IDLE
        self.conversation_history = []
        self.context = {}
        logger.info("Conversation state machine reset")
