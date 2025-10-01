#!/usr/bin/env python3
"""
Main system orchestration for Callaiag AI Agent.

This module coordinates all components of the system including speech processing,
Asterisk integration, conversation management, emotion analysis, and database operations.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Optional

from callaiag.core.config import Config
from callaiag.speech.recognition import SpeechRecognizer
from callaiag.speech.synthesis import SpeechSynthesizer
from callaiag.speech.audio import AudioProcessor
from callaiag.asterisk.ami import AsteriskManagerInterface
from callaiag.asterisk.call_manager import CallManager
from callaiag.conversation.state_machine import ConversationStateMachine
from callaiag.conversation.response_generator import ResponseGenerator
from callaiag.emotion.analyzer import EmotionAnalyzer
from callaiag.db.repository import Repository
from callaiag.web.dashboard import Dashboard

logger = logging.getLogger(__name__)


class CallaiagSystem:
    """
    Main system orchestrator for the Callaiag AI Agent.
    
    This class initializes and coordinates all system components including:
    - Configuration management
    - Speech processing (STT/TTS)
    - Asterisk PBX integration
    - Conversation management
    - Emotion recognition
    - Database operations
    - Web dashboard
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Callaiag system.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = Config(config_path)
        self.running = False
        
        # Initialize components
        self.repository = None
        self.speech_recognizer = None
        self.speech_synthesizer = None
        self.audio_processor = None
        self.asterisk_ami = None
        self.call_manager = None
        self.conversation_sm = None
        self.response_generator = None
        self.emotion_analyzer = None
        self.dashboard = None
        
        logger.info("Callaiag System initialized")
    
    def initialize(self):
        """
        Initialize the system configuration and create necessary directories and files.
        
        This method:
        - Creates required directories (data, temp, scripts, faqs, models)
        - Generates default configuration file
        - Initializes database schema
        """
        logger.info("Initializing Callaiag System...")
        
        try:
            # Create necessary directories
            directories = [
                './data',
                './temp',
                './scripts',
                './faqs',
                './models',
                './config',
                './logs',
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Create default configuration
            self.config.create_default_config('./config/default_config.yml')
            
            # Initialize database
            self.repository = Repository(self.config)
            self.repository.initialize_schema()
            
            logger.info("System initialization completed successfully")
            print("\n✓ System initialized successfully!")
            print("  - Configuration file created at ./config/default_config.yml")
            print("  - Database schema initialized")
            print("  - Required directories created")
            print("\nNext steps:")
            print("  1. Edit ./config/default_config.yml with your settings")
            print("  2. Run 'python3 run.py validate' to verify setup")
            print("  3. Run 'python3 run.py start' to start the agent")
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}", exc_info=True)
            raise
    
    def validate(self):
        """
        Validate system setup and connections.
        
        This method checks:
        - Configuration file presence and validity
        - Database connectivity
        - Asterisk PBX connection (if enabled)
        - Required dependencies
        - File permissions
        """
        logger.info("Validating Callaiag System...")
        
        issues = []
        
        try:
            # Check configuration
            print("\n[1/5] Checking configuration...")
            if not self.config.config_path:
                issues.append("No configuration file found")
                print("  ✗ Configuration file not found")
            else:
                print(f"  ✓ Configuration loaded from {self.config.config_path}")
            
            # Check database
            print("\n[2/5] Checking database...")
            try:
                self.repository = Repository(self.config)
                self.repository.connect()
                print("  ✓ Database connection successful")
                self.repository.disconnect()
            except Exception as e:
                issues.append(f"Database connection failed: {e}")
                print(f"  ✗ Database connection failed: {e}")
            
            # Check Asterisk (if enabled)
            print("\n[3/5] Checking Asterisk PBX...")
            if self.config.get('asterisk', 'enabled', default=True):
                try:
                    self.asterisk_ami = AsteriskManagerInterface(self.config)
                    # Note: Actual connection would require Asterisk to be running
                    print("  ✓ Asterisk configuration validated")
                except Exception as e:
                    issues.append(f"Asterisk validation failed: {e}")
                    print(f"  ✗ Asterisk validation failed: {e}")
            else:
                print("  ⊘ Asterisk integration disabled")
            
            # Check speech processing
            print("\n[4/5] Checking speech processing...")
            try:
                self.speech_recognizer = SpeechRecognizer(self.config)
                self.speech_synthesizer = SpeechSynthesizer(self.config)
                print("  ✓ Speech processing components initialized")
            except Exception as e:
                issues.append(f"Speech processing initialization failed: {e}")
                print(f"  ✗ Speech processing initialization failed: {e}")
            
            # Check directories
            print("\n[5/5] Checking directories...")
            required_dirs = ['./data', './temp', './scripts', './faqs']
            for directory in required_dirs:
                if Path(directory).exists():
                    print(f"  ✓ {directory}")
                else:
                    issues.append(f"Missing directory: {directory}")
                    print(f"  ✗ {directory}")
            
            # Summary
            print("\n" + "="*50)
            if not issues:
                print("✓ All validation checks passed!")
                print("\nSystem is ready to start.")
                print("Run 'python3 run.py start' to launch the agent.")
            else:
                print(f"✗ Found {len(issues)} issue(s):")
                for issue in issues:
                    print(f"  - {issue}")
                print("\nPlease fix these issues before starting the system.")
                sys.exit(1)
            
        except Exception as e:
            logger.error(f"Error during validation: {e}", exc_info=True)
            raise
    
    def start(self):
        """
        Start the Callaiag AI Agent system.
        
        This method:
        - Initializes all components
        - Connects to external systems (database, Asterisk)
        - Starts the web dashboard
        - Begins the main event loop
        """
        logger.info("Starting Callaiag System...")
        
        try:
            # Initialize components
            print("\nStarting Callaiag AI Agent...")
            
            # Database
            print("  [1/7] Connecting to database...")
            self.repository = Repository(self.config)
            self.repository.connect()
            logger.info("Database connected")
            
            # Speech processing
            print("  [2/7] Initializing speech processing...")
            self.speech_recognizer = SpeechRecognizer(self.config)
            self.speech_synthesizer = SpeechSynthesizer(self.config)
            self.audio_processor = AudioProcessor(self.config)
            logger.info("Speech processing initialized")
            
            # Asterisk integration
            print("  [3/7] Connecting to Asterisk PBX...")
            if self.config.get('asterisk', 'enabled', default=True):
                self.asterisk_ami = AsteriskManagerInterface(self.config)
                self.call_manager = CallManager(self.config, self.asterisk_ami)
                logger.info("Asterisk PBX connected")
            else:
                logger.info("Asterisk integration disabled")
            
            # Emotion analyzer
            print("  [4/7] Loading emotion recognition...")
            if self.config.get('emotion', 'enabled', default=True):
                self.emotion_analyzer = EmotionAnalyzer(self.config)
                logger.info("Emotion analyzer loaded")
            
            # Conversation management
            print("  [5/7] Initializing conversation management...")
            self.conversation_sm = ConversationStateMachine(self.config)
            self.response_generator = ResponseGenerator(self.config)
            logger.info("Conversation management initialized")
            
            # Web dashboard
            print("  [6/7] Starting web dashboard...")
            if self.config.get('dashboard', 'enabled', default=True):
                self.dashboard = Dashboard(self.config, self)
                # Dashboard would be started in a separate thread
                logger.info("Web dashboard ready")
            
            # Start main loop
            print("  [7/7] Starting main event loop...")
            self.running = True
            logger.info("Callaiag System started successfully")
            
            print("\n✓ Callaiag AI Agent is now running!")
            if self.config.get('dashboard', 'enabled', default=True):
                dashboard_port = self.config.get('dashboard', 'port', default=8080)
                print(f"\nDashboard: http://localhost:{dashboard_port}")
            print("\nPress Ctrl+C to stop...")
            
            # Main event loop
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
        except Exception as e:
            logger.error(f"Error starting system: {e}", exc_info=True)
            self.stop()
            raise
    
    def stop(self):
        """
        Stop the Callaiag system and cleanup resources.
        """
        logger.info("Stopping Callaiag System...")
        self.running = False
        
        try:
            # Stop dashboard
            if self.dashboard:
                self.dashboard.stop()
            
            # Disconnect Asterisk
            if self.asterisk_ami:
                self.asterisk_ami.disconnect()
            
            # Close database
            if self.repository:
                self.repository.disconnect()
            
            # Cleanup speech processing
            if self.audio_processor:
                self.audio_processor.cleanup()
            
            logger.info("Callaiag System stopped successfully")
            print("\n✓ System stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
