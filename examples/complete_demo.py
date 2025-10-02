#!/usr/bin/env python3
"""
Complete system demonstration for Callaiag.

This script demonstrates the full capabilities of the Callaiag AI Agent system
including speech processing, conversation management, and emotion recognition.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from callaiag.core.system import CallaiagSystem
from callaiag.core.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_speech_processing(system):
    """Demonstrate speech processing capabilities."""
    print("\n" + "="*60)
    print("SPEECH PROCESSING DEMO")
    print("="*60)
    
    try:
        # Text-to-Speech demo
        print("\n[1] Text-to-Speech Demo")
        text = "Guten Tag! Dies ist ein Test der Sprachsynthese."
        print(f"Synthesizing: {text}")
        
        if system.speech_synthesizer:
            audio_path = system.speech_synthesizer.synthesize(text)
            print(f"✓ Speech synthesized to: {audio_path}")
        else:
            print("✗ Speech synthesizer not available")
        
        # Speech Recognition demo (would need actual audio file)
        print("\n[2] Speech Recognition Demo")
        print("(Requires audio file for recognition)")
        
    except Exception as e:
        logger.error(f"Error in speech demo: {e}")


def demo_conversation_management(system):
    """Demonstrate conversation management."""
    print("\n" + "="*60)
    print("CONVERSATION MANAGEMENT DEMO")
    print("="*60)
    
    try:
        if not system.conversation_sm or not system.response_generator:
            print("✗ Conversation components not available")
            return
        
        # Start conversation
        print("\n[1] Starting Conversation")
        system.conversation_sm.start_conversation({
            'customer_name': 'Max Mustermann',
            'agent_name': 'Sarah',
            'company': 'Callaiag GmbH'
        })
        
        print(f"State: {system.conversation_sm.get_state().value}")
        
        # Generate greeting
        print("\n[2] Generating Greeting")
        greeting = system.response_generator.generate_response(
            'greeting',
            context={
                'customer_name': 'Max Mustermann',
                'agent_name': 'Sarah',
                'company': 'Callaiag GmbH'
            }
        )
        print(f"Agent: {greeting}")
        
        # Simulate customer response
        print("\n[3] Processing Customer Input")
        user_input = "Ja, hier spricht Max Mustermann."
        print(f"Customer: {user_input}")
        
        response = system.conversation_sm.process_input(user_input)
        if response:
            print(f"Agent: {response}")
        
        print(f"New State: {system.conversation_sm.get_state().value}")
        
    except Exception as e:
        logger.error(f"Error in conversation demo: {e}")


def demo_emotion_recognition(system):
    """Demonstrate emotion recognition."""
    print("\n" + "="*60)
    print("EMOTION RECOGNITION DEMO")
    print("="*60)
    
    try:
        if not system.emotion_analyzer:
            print("✗ Emotion analyzer not available")
            return
        
        # Analyze text emotion
        print("\n[1] Text Emotion Analysis")
        test_texts = [
            "Das ist großartig! Ich bin sehr interessiert.",
            "Ich bin mir nicht sicher. Das klingt kompliziert.",
            "Nein danke, ich habe kein Interesse."
        ]
        
        for text in test_texts:
            result = system.emotion_analyzer.analyze_text(text)
            print(f"\nText: {text}")
            print(f"Emotion: {result['emotion']} (confidence: {result['confidence']:.2f})")
        
    except Exception as e:
        logger.error(f"Error in emotion demo: {e}")


def demo_database_operations(system):
    """Demonstrate database operations."""
    print("\n" + "="*60)
    print("DATABASE OPERATIONS DEMO")
    print("="*60)
    
    try:
        if not system.repository:
            print("✗ Database repository not available")
            return
        
        # Create test customer
        print("\n[1] Creating Test Customer")
        customer_id = system.repository.create_customer(
            name="Max Mustermann",
            phone="+49123456789",
            email="max@example.com",
            company="Test GmbH"
        )
        print(f"✓ Created customer with ID: {customer_id}")
        
        # Create test call
        print("\n[2] Creating Test Call")
        call_db_id = system.repository.create_call(
            call_id="demo-call-001",
            phone_number="+49123456789",
            customer_id=customer_id,
            state="completed",
            outcome="success"
        )
        print(f"✓ Created call with DB ID: {call_db_id}")
        
        # Add conversation log
        print("\n[3] Adding Conversation Log")
        system.repository.add_conversation_log(
            call_id=call_db_id,
            speaker="agent",
            text="Guten Tag! Hier spricht Sarah von Callaiag.",
            state="greeting"
        )
        print("✓ Added conversation log")
        
        # Retrieve data
        print("\n[4] Retrieving Data")
        retrieved_customer = system.repository.get_customer(customer_id)
        print(f"✓ Retrieved customer: {retrieved_customer.name}")
        
    except Exception as e:
        logger.error(f"Error in database demo: {e}")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("CALLAIAG AI AGENT - COMPLETE SYSTEM DEMO")
    print("="*60)
    
    try:
        # Initialize system
        print("\nInitializing system...")
        config_path = Path(__file__).parent.parent / 'config' / 'default_config.yml'
        system = CallaiagSystem(str(config_path))
        
        # Initialize components
        print("Initializing components...")
        system.repository = system.repository or __import__('callaiag.db.repository', fromlist=['Repository']).Repository(system.config)
        system.repository.connect()
        
        system.speech_recognizer = __import__('callaiag.speech.recognition', fromlist=['SpeechRecognizer']).SpeechRecognizer(system.config)
        system.speech_synthesizer = __import__('callaiag.speech.synthesis', fromlist=['SpeechSynthesizer']).SpeechSynthesizer(system.config)
        system.conversation_sm = __import__('callaiag.conversation.state_machine', fromlist=['ConversationStateMachine']).ConversationStateMachine(system.config)
        system.response_generator = __import__('callaiag.conversation.response_generator', fromlist=['ResponseGenerator']).ResponseGenerator(system.config)
        system.emotion_analyzer = __import__('callaiag.emotion.analyzer', fromlist=['EmotionAnalyzer']).EmotionAnalyzer(system.config)
        
        print("✓ System initialized\n")
        
        # Run demos
        demo_speech_processing(system)
        time.sleep(1)
        
        demo_conversation_management(system)
        time.sleep(1)
        
        demo_emotion_recognition(system)
        time.sleep(1)
        
        demo_database_operations(system)
        
        # Cleanup
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        
        system.repository.disconnect()
        print("\n✓ All demos completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Error in demo: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
