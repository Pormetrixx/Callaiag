"""
Unit tests for conversation module.

Tests state machine, memory, and context management.
"""

import pytest
from callaiag.conversation.state_machine import StateMachine, ConversationState
from callaiag.conversation.context.memory import ConversationMemory
from callaiag.conversation.context.topic_tracker import TopicTracker


class TestStateMachine:
    """Test suite for StateMachine class."""
    
    def test_state_machine_initialization(self):
        """Test StateMachine initialization."""
        sm = StateMachine()
        assert sm.current_state == ConversationState.IDLE
        assert sm.previous_state is None
        assert sm.context == {}
    
    def test_state_transition(self):
        """Test state transition."""
        sm = StateMachine()
        sm.transition_to(ConversationState.GREETING)
        
        assert sm.current_state == ConversationState.GREETING
        assert sm.previous_state == ConversationState.IDLE
    
    def test_can_transition(self):
        """Test transition validation."""
        sm = StateMachine()
        
        # Valid transition
        assert sm.can_transition_to(ConversationState.GREETING)
        
        # Invalid transition
        assert not sm.can_transition_to(ConversationState.CLOSING)
    
    def test_state_machine_reset(self):
        """Test state machine reset."""
        sm = StateMachine()
        sm.transition_to(ConversationState.GREETING)
        sm.set_context("test", "value")
        
        sm.reset()
        
        assert sm.current_state == ConversationState.IDLE
        assert sm.context == {}


class TestConversationMemory:
    """Test suite for ConversationMemory class."""
    
    def test_memory_initialization(self):
        """Test ConversationMemory initialization."""
        memory = ConversationMemory(max_turns=50)
        assert memory.max_turns == 50
        assert len(memory.turns) == 0
    
    def test_add_turn(self):
        """Test adding conversation turns."""
        memory = ConversationMemory()
        memory.add_turn("agent", "Hello")
        memory.add_turn("user", "Hi there")
        
        assert len(memory.turns) == 2
    
    def test_get_recent_turns(self):
        """Test getting recent turns."""
        memory = ConversationMemory()
        for i in range(10):
            memory.add_turn("agent", f"Turn {i}")
        
        recent = memory.get_recent_turns(5)
        assert len(recent) == 5
    
    def test_search_turns(self):
        """Test searching for turns."""
        memory = ConversationMemory()
        memory.add_turn("agent", "Hello there")
        memory.add_turn("user", "How are you?")
        memory.add_turn("agent", "I'm fine, thanks")
        
        results = memory.search_turns("Hello")
        assert len(results) == 1
        assert results[0].text == "Hello there"


class TestTopicTracker:
    """Test suite for TopicTracker class."""
    
    def test_topic_tracker_initialization(self):
        """Test TopicTracker initialization."""
        tracker = TopicTracker()
        assert len(tracker.active_topics) == 0
    
    def test_add_predefined_topic(self):
        """Test adding predefined topics."""
        tracker = TopicTracker()
        tracker.add_predefined_topic("pricing", ["price", "cost", "fee"])
        
        assert "pricing" in tracker.predefined_topics
    
    def test_detect_topic(self):
        """Test topic detection."""
        tracker = TopicTracker()
        tracker.add_predefined_topic("pricing", ["price", "cost"])
        
        topic = tracker.detect_topic("What is the price?")
        assert topic is not None
        assert topic.name == "pricing"
