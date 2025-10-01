#!/usr/bin/env python3
"""
Callaiag - AI Agent for Automated Cold Calling
Main application orchestration module
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from config import Config
from database.db_manager import DatabaseManager
from speech.speech_manager import SpeechManager
from telephony.asterisk_manager import AsteriskManager
from conversation.conversation_manager import ConversationManager
from conversation.emotion_analyzer import EmotionAnalyzer
from training.training_manager import TrainingManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('callaiag.log')
    ]
)
logger = logging.getLogger(__name__)

class CallaiagAgent:
    """Main AI Agent class that orchestrates all components"""
    
    def __init__(self, config_path=None):
        """Initialize the AI Agent with all necessary components"""
        self.config = Config(config_path)
        self.db_manager = DatabaseManager(self.config)
        self.speech_manager = SpeechManager(self.config)
        self.asterisk_manager = AsteriskManager(self.config)
        self.emotion_analyzer = EmotionAnalyzer(self.config)
        self.conversation_manager = ConversationManager(
            self.config, 
            self.speech_manager, 
            self.emotion_analyzer
        )
        self.training_manager = TrainingManager(self.config, self.db_manager)
        self.running = False
        
        logger.info("Callaiag Agent initialized")
        
    def start(self):
        """Start the AI Agent and all its components"""
        try:
            logger.info("Starting Callaiag Agent...")
            
            # Initialize database connection
            self.db_manager.connect()
            logger.info("Database connection established")
            
            # Connect to Asterisk PBX
            self.asterisk_manager.connect()
            logger.info("Connected to Asterisk PBX")
            
            # Initialize speech processing
            self.speech_manager.initialize()
            logger.info("Speech processing initialized")
            
            # Start the conversation manager
            self.conversation_manager.initialize()
            logger.info("Conversation manager initialized")
            
            # Register event handlers
            self.asterisk_manager.register_event_handler(
                'NewChannel', 
                self.conversation_manager.handle_new_call
            )
            self.asterisk_manager.register_event_handler(
                'Hangup', 
                self.conversation_manager.handle_call_ended
            )
            
            self.running = True
            logger.info("Callaiag Agent started successfully")
            
            # Main loop
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in Callaiag Agent: {e}", exc_info=True)
            self.stop()
            
    def stop(self):
        """Stop the AI Agent and all its components"""
        logger.info("Stopping Callaiag Agent...")
        self.running = False
        
        try:
            # Clean shutdown of components
            self.conversation_manager.shutdown()
            self.asterisk_manager.disconnect()
            self.speech_manager.shutdown()
            self.db_manager.disconnect()
            
            logger.info("Callaiag Agent stopped successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)


def init_config():
    """Initialize the configuration file"""
    config = Config()
    config.create_default_config()
    print(f"Configuration initialized at {config.config_path}")
    return 0


def validate_setup():
    """Validate the setup by testing connections"""
    try:
        config = Config()
        
        # Test database connection
        db = DatabaseManager(config)
        db.connect()
        db.disconnect()
        print("✅ Database connection successful")
        
        # Test Asterisk connection
        asterisk = AsteriskManager(config)
        asterisk.connect()
        asterisk.disconnect()
        print("✅ Asterisk connection successful")
        
        # Test speech processing
        speech = SpeechManager(config)
        speech.initialize()
        speech.shutdown()
        print("✅ Speech processing initialized successfully")
        
        print("\nSetup validation successful! The system is ready to run.")
        return 0
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='Callaiag - AI Agent for Automated Cold Calling')
    parser.add_argument('command', choices=['start', 'init', 'validate'], 
                       help='Command to execute (start, init, validate)')
    parser.add_argument('--config', '-c', default=None, 
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        return init_config()
    elif args.command == 'validate':
        return validate_setup()
    elif args.command == 'start':
        agent = CallaiagAgent(args.config)
        agent.start()
        return 0


if __name__ == "__main__":
    sys.exit(main())
