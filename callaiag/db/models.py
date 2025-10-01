#!/usr/bin/env python3
"""
Database models for Callaiag.

This module defines SQLAlchemy models for storing call data, customer information,
conversation logs, and training data.
"""

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class Customer(Base):
    """Customer information model."""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), unique=True, nullable=False)
    email = Column(String(255))
    company = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calls = relationship('Call', back_populates='customer')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'company': self.company,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Call(Base):
    """Call information model."""
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String(100), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    phone_number = Column(String(50), nullable=False)
    
    # Call details
    state = Column(String(50))
    channel = Column(String(100))
    start_time = Column(DateTime)
    answer_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Float)
    
    # Call outcome
    outcome = Column(String(50))  # success, failure, no_answer, busy, etc.
    sentiment = Column(String(50))  # positive, negative, neutral
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship('Customer', back_populates='calls')
    conversation_logs = relationship('ConversationLog', back_populates='call')
    emotion_logs = relationship('EmotionLog', back_populates='call')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'customer_id': self.customer_id,
            'phone_number': self.phone_number,
            'state': self.state,
            'channel': self.channel,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'answer_time': self.answer_time.isoformat() if self.answer_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'outcome': self.outcome,
            'sentiment': self.sentiment,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConversationLog(Base):
    """Conversation log model for storing dialogue."""
    __tablename__ = 'conversation_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(Integer, ForeignKey('calls.id'))
    
    # Message details
    speaker = Column(String(20))  # 'agent' or 'customer'
    text = Column(Text, nullable=False)
    state = Column(String(50))  # conversation state at time of message
    
    # Audio reference
    audio_path = Column(String(500))
    
    # Analysis
    emotion = Column(String(50))
    confidence = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship('Call', back_populates='conversation_logs')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'speaker': self.speaker,
            'text': self.text,
            'state': self.state,
            'audio_path': self.audio_path,
            'emotion': self.emotion,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class EmotionLog(Base):
    """Emotion analysis log model."""
    __tablename__ = 'emotion_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(Integer, ForeignKey('calls.id'))
    
    # Emotion data
    emotion = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    all_emotions = Column(JSON)  # Store all emotion scores
    modality = Column(String(20))  # 'audio', 'text', 'multimodal'
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship('Call', back_populates='emotion_logs')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'emotion': self.emotion,
            'confidence': self.confidence,
            'all_emotions': self.all_emotions,
            'modality': self.modality,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Script(Base):
    """Conversation script template model."""
    __tablename__ = 'scripts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    script_type = Column(String(50), nullable=False)  # greeting, pitch, closing, etc.
    template = Column(Text, nullable=False)
    language = Column(String(10), default='de')
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'script_type': self.script_type,
            'template': self.template,
            'language': self.language,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FAQ(Base):
    """FAQ model for storing frequently asked questions."""
    __tablename__ = 'faqs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_type = Column(String(100), unique=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(JSON)  # List of keywords for matching
    language = Column(String(10), default='de')
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'question_type': self.question_type,
            'question': self.question,
            'answer': self.answer,
            'keywords': self.keywords,
            'language': self.language,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TrainingData(Base):
    """Training data model for continuous learning."""
    __tablename__ = 'training_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String(100))
    
    # Input data
    input_text = Column(Text)
    input_audio_path = Column(String(500))
    
    # Expected output
    expected_response = Column(Text)
    actual_response = Column(Text)
    
    # Outcome
    success = Column(Boolean)
    feedback_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'input_text': self.input_text,
            'input_audio_path': self.input_audio_path,
            'expected_response': self.expected_response,
            'actual_response': self.actual_response,
            'success': self.success,
            'feedback_score': self.feedback_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
