#!/usr/bin/env python3
"""
Response generator for Callaiag.

This module generates dynamic responses based on conversation context,
customer information, and emotion analysis.
"""

import logging
import random
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Dynamic response generation for conversations.
    
    Generates contextually appropriate responses based on:
    - Conversation state
    - Customer emotion
    - Previous interactions
    - Script templates
    """
    
    def __init__(self, config):
        """
        Initialize response generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.scripts_dir = Path(config.get('conversation', 'scripts_dir', default='./scripts'))
        self.faqs_dir = Path(config.get('conversation', 'faqs_dir', default='./faqs'))
        self.scripts = self._load_scripts()
        self.faqs = self._load_faqs()
        
        logger.info("Response generator initialized")
    
    def _load_scripts(self) -> Dict[str, Any]:
        """Load conversation scripts from files."""
        scripts = {
            'greeting': [
                "Guten Tag! Mein Name ist {agent_name} von {company}. Spreche ich mit {customer_name}?",
                "Hallo! Hier spricht {agent_name} von {company}. Ist das {customer_name}?",
            ],
            'introduction': [
                "Ich rufe an, weil wir ein spannendes Angebot für Sie haben.",
                "Der Grund meines Anrufs ist unser neues Produkt, das perfekt zu Ihren Bedürfnissen passt.",
            ],
            'pitch': [
                "Unser Produkt bietet {benefit1}, {benefit2} und {benefit3}.",
                "Sie können damit {benefit1} erreichen und gleichzeitig {benefit2}.",
            ],
            'closing': [
                "Möchten Sie mehr über unser Angebot erfahren?",
                "Würden Sie gerne einen Termin für eine ausführliche Präsentation vereinbaren?",
            ],
            'goodbye': [
                "Vielen Dank für Ihre Zeit. Auf Wiedersehen!",
                "Ich danke Ihnen für das Gespräch. Bis bald!",
            ]
        }
        
        # Would load from files in production
        logger.info("Scripts loaded")
        return scripts
    
    def _load_faqs(self) -> Dict[str, str]:
        """Load FAQs from files."""
        faqs = {
            'preis': "Der Preis beginnt bei {price} Euro pro Monat.",
            'vertrag': "Die Vertragslaufzeit beträgt {contract_duration} Monate.",
            'kündigung': "Sie können jederzeit mit einer Frist von {notice_period} kündigen.",
            'lieferung': "Die Lieferung erfolgt innerhalb von {delivery_time} Werktagen.",
        }
        
        # Would load from files in production
        logger.info("FAQs loaded")
        return faqs
    
    def generate_response(self, response_type: str, context: Optional[Dict[str, Any]] = None,
                         emotion: Optional[str] = None) -> str:
        """
        Generate a response based on type and context.
        
        Args:
            response_type: Type of response (greeting, pitch, closing, etc.)
            context: Context dictionary with variables for template
            emotion: Detected customer emotion
            
        Returns:
            Generated response text
        """
        context = context or {}
        
        # Get script templates for this type
        templates = self.scripts.get(response_type, [])
        
        if not templates:
            logger.warning(f"No templates found for response type: {response_type}")
            return "Entschuldigung, ich bin mir nicht sicher, wie ich darauf antworten soll."
        
        # Select template (could be more sophisticated based on emotion)
        template = self._select_template(templates, emotion)
        
        # Fill template with context
        try:
            response = template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context variable: {e}")
            response = template
        
        # Adjust for emotion if needed
        response = self._adjust_for_emotion(response, emotion)
        
        return response
    
    def _select_template(self, templates: List[str], emotion: Optional[str] = None) -> str:
        """
        Select appropriate template based on emotion.
        
        Args:
            templates: List of template options
            emotion: Detected emotion
            
        Returns:
            Selected template
        """
        # For now, just select randomly
        # Could be more sophisticated based on emotion
        return random.choice(templates)
    
    def _adjust_for_emotion(self, response: str, emotion: Optional[str] = None) -> str:
        """
        Adjust response based on detected emotion.
        
        Args:
            response: Original response
            emotion: Detected emotion
            
        Returns:
            Adjusted response
        """
        if not emotion:
            return response
        
        # Adjust tone based on emotion
        if emotion in ['angry', 'frustrated']:
            # Add empathy
            response = f"Ich verstehe, dass dies wichtig ist. {response}"
        elif emotion in ['confused', 'uncertain']:
            # Add clarification
            response = f"Lassen Sie mich das klarer erklären. {response}"
        elif emotion in ['interested', 'positive']:
            # Add enthusiasm
            response = f"{response} Das freut mich sehr!"
        
        return response
    
    def get_faq_response(self, question_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get FAQ response for a specific question type.
        
        Args:
            question_type: Type of question (preis, vertrag, etc.)
            context: Context for filling template
            
        Returns:
            FAQ response
        """
        context = context or {}
        
        # Get FAQ template
        template = self.faqs.get(question_type)
        
        if not template:
            logger.warning(f"No FAQ found for: {question_type}")
            return "Das ist eine gute Frage. Lassen Sie mich die Informationen für Sie finden."
        
        # Fill template
        try:
            response = template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing FAQ context variable: {e}")
            response = template
        
        return response
    
    def detect_question_type(self, user_input: str) -> Optional[str]:
        """
        Detect question type from user input.
        
        Args:
            user_input: User's question
            
        Returns:
            Question type or None
        """
        user_input_lower = user_input.lower()
        
        keywords = {
            'preis': ['preis', 'kosten', 'geld', 'bezahlen', 'euro'],
            'vertrag': ['vertrag', 'laufzeit', 'bindung'],
            'kündigung': ['kündigung', 'kündigen', 'beenden'],
            'lieferung': ['lieferung', 'versand', 'liefern', 'bekommen'],
        }
        
        for question_type, words in keywords.items():
            if any(word in user_input_lower for word in words):
                return question_type
        
        return None
    
    def add_script_template(self, response_type: str, template: str):
        """
        Add a new script template.
        
        Args:
            response_type: Type of response
            template: Template string
        """
        if response_type not in self.scripts:
            self.scripts[response_type] = []
        self.scripts[response_type].append(template)
        logger.info(f"Added template for {response_type}")
    
    def add_faq(self, question_type: str, response: str):
        """
        Add a new FAQ.
        
        Args:
            question_type: Type of question
            response: FAQ response
        """
        self.faqs[question_type] = response
        logger.info(f"Added FAQ for {question_type}")
    
    def get_available_response_types(self) -> List[str]:
        """Get list of available response types."""
        return list(self.scripts.keys())
    
    def get_available_faq_types(self) -> List[str]:
        """Get list of available FAQ types."""
        return list(self.faqs.keys())
