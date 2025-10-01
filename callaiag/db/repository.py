#!/usr/bin/env python3
"""
Repository pattern implementation for Callaiag database operations.

This module provides a data access layer using the repository pattern
for clean separation of business logic and data access.
"""

import logging
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from callaiag.db.models import Base, Customer, Call, ConversationLog, EmotionLog, Script, FAQ, TrainingData

logger = logging.getLogger(__name__)


class Repository:
    """
    Repository for database operations.
    
    Provides unified interface for all database operations with
    support for multiple database backends (SQLite, MySQL, PostgreSQL).
    """
    
    def __init__(self, config):
        """
        Initialize repository.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.engine = None
        self.session_factory = None
        self._build_connection_string()
        
        logger.info("Repository initialized")
    
    def _build_connection_string(self):
        """Build database connection string from config."""
        db_type = self.config.get('database', 'type', default='sqlite')
        
        if db_type == 'sqlite':
            db_path = self.config.get('database', 'path', default='./data/callaiag.db')
            self.connection_string = f'sqlite:///{db_path}'
        
        elif db_type == 'mysql':
            host = self.config.get('database', 'host', default='localhost')
            port = self.config.get('database', 'port', default=3306)
            name = self.config.get('database', 'name', default='callaiag')
            user = self.config.get('database', 'user', default='callaiag')
            password = self.config.get('database', 'password', default='change_me')
            self.connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{name}'
        
        elif db_type == 'postgresql':
            host = self.config.get('database', 'host', default='localhost')
            port = self.config.get('database', 'port', default=5432)
            name = self.config.get('database', 'name', default='callaiag')
            user = self.config.get('database', 'user', default='callaiag')
            password = self.config.get('database', 'password', default='change_me')
            self.connection_string = f'postgresql://{user}:{password}@{host}:{port}/{name}'
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        logger.debug(f"Connection string: {self.connection_string.split('@')[0]}@...")
    
    def connect(self):
        """Connect to database."""
        try:
            logger.info("Connecting to database...")
            self.engine = create_engine(self.connection_string, echo=False)
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from database."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def initialize_schema(self):
        """Create database tables."""
        try:
            logger.info("Initializing database schema...")
            Base.metadata.create_all(self.engine)
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            raise
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    # Customer operations
    
    def create_customer(self, name: str, phone: str, **kwargs) -> int:
        """Create a new customer. Returns customer ID."""
        with self.session_scope() as session:
            customer = Customer(name=name, phone=phone, **kwargs)
            session.add(customer)
            session.flush()
            customer_id = customer.id
            logger.info(f"Created customer: {customer_id} - {name}")
            return customer_id
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number."""
        with self.session_scope() as session:
            customer = session.query(Customer).filter(Customer.phone == phone).first()
            if customer:
                session.expunge(customer)
            return customer
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        with self.session_scope() as session:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                session.expunge(customer)
            return customer
    
    def update_customer(self, customer_id: int, **kwargs):
        """Update customer information."""
        with self.session_scope() as session:
            session.query(Customer).filter(Customer.id == customer_id).update(kwargs)
            logger.info(f"Updated customer: {customer_id}")
    
    def list_customers(self, limit: int = 100, offset: int = 0) -> List[Customer]:
        """List customers."""
        with self.session_scope() as session:
            customers = session.query(Customer).limit(limit).offset(offset).all()
            for customer in customers:
                session.expunge(customer)
            return customers
    
    # Call operations
    
    def create_call(self, call_id: str, phone_number: str, **kwargs) -> int:
        """Create a new call record. Returns database ID."""
        with self.session_scope() as session:
            call = Call(call_id=call_id, phone_number=phone_number, **kwargs)
            session.add(call)
            session.flush()
            db_id = call.id
            logger.info(f"Created call: {db_id} - {call_id}")
            return db_id
    
    def get_call(self, call_id: str) -> Optional[Call]:
        """Get call by call_id."""
        with self.session_scope() as session:
            call = session.query(Call).filter(Call.call_id == call_id).first()
            if call:
                session.expunge(call)
            return call
    
    def update_call(self, call_id: str, **kwargs):
        """Update call information."""
        with self.session_scope() as session:
            session.query(Call).filter(Call.call_id == call_id).update(kwargs)
            logger.info(f"Updated call: {call_id}")
    
    def list_calls(self, limit: int = 100, offset: int = 0) -> List[Call]:
        """List calls."""
        with self.session_scope() as session:
            calls = session.query(Call).order_by(Call.created_at.desc()).limit(limit).offset(offset).all()
            for call in calls:
                session.expunge(call)
            return calls
    
    # Conversation log operations
    
    def add_conversation_log(self, call_id: int, speaker: str, text: str, **kwargs):
        """Add conversation log entry."""
        with self.session_scope() as session:
            log = ConversationLog(call_id=call_id, speaker=speaker, text=text, **kwargs)
            session.add(log)
            logger.debug(f"Added conversation log for call {call_id}")
    
    def get_conversation_logs(self, call_id: int) -> List[ConversationLog]:
        """Get conversation logs for a call."""
        with self.session_scope() as session:
            # Get the call's database ID
            call = session.query(Call).filter(Call.call_id == call_id).first()
            if not call:
                return []
            
            logs = session.query(ConversationLog).filter(
                ConversationLog.call_id == call.id
            ).order_by(ConversationLog.timestamp).all()
            
            for log in logs:
                session.expunge(log)
            return logs
    
    # Emotion log operations
    
    def add_emotion_log(self, call_id: int, emotion: str, confidence: float, **kwargs):
        """Add emotion log entry."""
        with self.session_scope() as session:
            log = EmotionLog(call_id=call_id, emotion=emotion, confidence=confidence, **kwargs)
            session.add(log)
            logger.debug(f"Added emotion log for call {call_id}")
    
    def get_emotion_logs(self, call_id: int) -> List[EmotionLog]:
        """Get emotion logs for a call."""
        with self.session_scope() as session:
            # Get the call's database ID
            call = session.query(Call).filter(Call.call_id == call_id).first()
            if not call:
                return []
            
            logs = session.query(EmotionLog).filter(
                EmotionLog.call_id == call.id
            ).order_by(EmotionLog.timestamp).all()
            
            for log in logs:
                session.expunge(log)
            return logs
    
    # Script operations
    
    def create_script(self, name: str, script_type: str, template: str, **kwargs) -> int:
        """Create a new script. Returns script ID."""
        with self.session_scope() as session:
            script = Script(name=name, script_type=script_type, template=template, **kwargs)
            session.add(script)
            session.flush()
            script_id = script.id
            logger.info(f"Created script: {name}")
            return script_id
    
    def get_scripts_by_type(self, script_type: str) -> List[Script]:
        """Get scripts by type."""
        with self.session_scope() as session:
            scripts = session.query(Script).filter(
                Script.script_type == script_type,
                Script.active == True
            ).all()
            for script in scripts:
                session.expunge(script)
            return scripts
    
    # FAQ operations
    
    def create_faq(self, question_type: str, question: str, answer: str, **kwargs) -> int:
        """Create a new FAQ. Returns FAQ ID."""
        with self.session_scope() as session:
            faq = FAQ(question_type=question_type, question=question, answer=answer, **kwargs)
            session.add(faq)
            session.flush()
            faq_id = faq.id
            logger.info(f"Created FAQ: {question_type}")
            return faq_id
    
    def get_faq(self, question_type: str) -> Optional[FAQ]:
        """Get FAQ by type."""
        with self.session_scope() as session:
            faq = session.query(FAQ).filter(
                FAQ.question_type == question_type,
                FAQ.active == True
            ).first()
            if faq:
                session.expunge(faq)
            return faq
    
    def list_faqs(self) -> List[FAQ]:
        """List all active FAQs."""
        with self.session_scope() as session:
            faqs = session.query(FAQ).filter(FAQ.active == True).all()
            for faq in faqs:
                session.expunge(faq)
            return faqs
    
    # Training data operations
    
    def add_training_data(self, call_id: str, **kwargs):
        """Add training data entry."""
        with self.session_scope() as session:
            data = TrainingData(call_id=call_id, **kwargs)
            session.add(data)
            logger.debug(f"Added training data for call {call_id}")
    
    def get_training_data(self, limit: int = 1000) -> List[TrainingData]:
        """Get training data."""
        with self.session_scope() as session:
            data = session.query(TrainingData).limit(limit).all()
            for item in data:
                session.expunge(item)
            return data
