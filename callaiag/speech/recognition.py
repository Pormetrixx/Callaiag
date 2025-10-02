#!/usr/bin/env python3
"""
Speech recognition module for Callaiag.

This module provides local speech-to-text capabilities using OpenAI Whisper
for privacy-focused, offline speech recognition.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """
    Speech-to-text recognition using OpenAI Whisper.
    
    This class provides local speech recognition capabilities without
    requiring cloud services, ensuring privacy and low latency.
    """
    
    def __init__(self, config):
        """
        Initialize the speech recognizer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model = None
        self.model_name = config.get('speech', 'stt', 'whisper_model', default='medium')
        self.language = config.get('speech', 'stt', 'language', default='de')
        self.device = config.get('speech', 'stt', 'device', default='cpu')
        
        logger.info(f"Speech recognizer initialized with model: {self.model_name}")
    
    def load_model(self):
        """
        Load the Whisper model.
        
        Models: tiny, base, small, medium, large
        """
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def recognize(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Recognize speech from audio file.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'de', 'en')
            
        Returns:
            Dictionary containing:
            - text: Transcribed text
            - language: Detected language
            - confidence: Recognition confidence
            - segments: Detailed segment information
        """
        if not self.model:
            self.load_model()
        
        try:
            lang = language or self.language
            logger.debug(f"Recognizing speech from {audio_path} (language: {lang})")
            
            # Transcribe audio
            result = self.model.transcribe(
                audio_path,
                language=lang,
                task='transcribe',
                verbose=False
            )
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', lang),
                'confidence': self._calculate_confidence(result),
                'segments': result.get('segments', []),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error recognizing speech: {e}")
            return {
                'text': '',
                'language': language or self.language,
                'confidence': 0.0,
                'segments': [],
                'success': False,
                'error': str(e)
            }
    
    def _calculate_confidence(self, result: Dict) -> float:
        """
        Calculate average confidence from Whisper result.
        
        Args:
            result: Whisper transcription result
            
        Returns:
            Average confidence score (0.0 to 1.0)
        """
        segments = result.get('segments', [])
        if not segments:
            return 0.0
        
        # Whisper doesn't provide direct confidence scores,
        # so we use a heuristic based on segment properties
        total_confidence = 0.0
        for segment in segments:
            # Use no_speech_prob as inverse confidence indicator
            no_speech_prob = segment.get('no_speech_prob', 0.5)
            total_confidence += (1.0 - no_speech_prob)
        
        return total_confidence / len(segments) if segments else 0.0
    
    def recognize_streaming(self, audio_stream):
        """
        Recognize speech from audio stream (for future implementation).
        
        Args:
            audio_stream: Audio stream object
            
        Returns:
            Dictionary with recognition results
        """
        # Placeholder for streaming recognition
        logger.warning("Streaming recognition not yet implemented")
        return {
            'text': '',
            'language': self.language,
            'confidence': 0.0,
            'success': False,
            'error': 'Streaming not implemented'
        }
    
    def get_supported_languages(self):
        """
        Get list of supported languages.
        
        Returns:
            List of language codes
        """
        # Whisper supports many languages
        return [
            'de', 'en', 'es', 'fr', 'it', 'pt', 'nl', 'pl', 'ru',
            'ja', 'ko', 'zh', 'ar', 'tr', 'sv', 'da', 'no', 'fi'
        ]
