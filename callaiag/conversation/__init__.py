"""
Conversation management module for Callaiag.

This module handles conversation state management and dynamic response generation
for natural conversational interactions.
"""

from callaiag.conversation.state_machine import ConversationStateMachine
from callaiag.conversation.response_generator import ResponseGenerator

__all__ = ['ConversationStateMachine', 'ResponseGenerator']
