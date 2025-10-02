#!/usr/bin/env python3
"""
Emotion analyzer for Callaiag.

This module provides emotion recognition from voice and text to enable
adaptive conversations based on customer emotional state.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """
    Multi-modal emotion analysis.
    
    Analyzes customer emotions from:
    - Voice characteristics (tone, pitch, energy)
    - Text sentiment analysis
    - Conversation patterns
    """
    
    def __init__(self, config):
        """
        Initialize emotion analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.enabled = config.get('emotion', 'enabled', default=True)
        self.model_path = config.get('emotion', 'model_path', default='./models/emotion')
        self.confidence_threshold = config.get('emotion', 'confidence_threshold', default=0.6)
        
        self.emotion_model = None
        self.sentiment_analyzer = None
        
        if self.enabled:
            self._initialize_models()
        
        logger.info(f"Emotion analyzer initialized (enabled: {self.enabled})")
    
    def _initialize_models(self):
        """Initialize emotion recognition models."""
        try:
            # In production, would load actual ML models here
            # For now, using placeholder
            logger.info("Emotion recognition models initialized")
        except Exception as e:
            logger.error(f"Error initializing emotion models: {e}")
            self.enabled = False
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze emotion from audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing:
            - emotion: Primary emotion detected
            - confidence: Detection confidence (0-1)
            - all_emotions: All detected emotions with scores
            - features: Extracted audio features
        """
        if not self.enabled:
            return self._get_neutral_result()
        
        try:
            # Extract audio features
            features = self._extract_audio_features(audio_path)
            
            # Analyze emotions
            emotions = self._predict_emotion_from_audio(features)
            
            # Get primary emotion
            primary_emotion = max(emotions.items(), key=lambda x: x[1])
            
            result = {
                'emotion': primary_emotion[0],
                'confidence': primary_emotion[1],
                'all_emotions': emotions,
                'features': features,
                'modality': 'audio'
            }
            
            logger.debug(f"Audio emotion: {result['emotion']} ({result['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing audio emotion: {e}")
            return self._get_neutral_result()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotion from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with emotion analysis results
        """
        if not self.enabled:
            return self._get_neutral_result()
        
        try:
            # Analyze text sentiment
            sentiment = self._analyze_sentiment(text)
            
            # Map sentiment to emotion
            emotion_mapping = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral'
            }
            
            emotions = {
                'positive': sentiment.get('positive', 0.33),
                'negative': sentiment.get('negative', 0.33),
                'neutral': sentiment.get('neutral', 0.34),
            }
            
            primary_emotion = max(emotions.items(), key=lambda x: x[1])
            
            result = {
                'emotion': primary_emotion[0],
                'confidence': primary_emotion[1],
                'all_emotions': emotions,
                'sentiment': sentiment,
                'modality': 'text'
            }
            
            logger.debug(f"Text emotion: {result['emotion']} ({result['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing text emotion: {e}")
            return self._get_neutral_result()
    
    def analyze_multimodal(self, audio_path: Optional[str] = None,
                          text: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze emotion using multiple modalities.
        
        Args:
            audio_path: Optional path to audio file
            text: Optional text to analyze
            
        Returns:
            Combined emotion analysis
        """
        results = []
        
        if audio_path:
            audio_result = self.analyze_audio(audio_path)
            results.append(audio_result)
        
        if text:
            text_result = self.analyze_text(text)
            results.append(text_result)
        
        if not results:
            return self._get_neutral_result()
        
        # Combine results (simple average for now)
        combined_emotions = {}
        for result in results:
            for emotion, score in result['all_emotions'].items():
                if emotion not in combined_emotions:
                    combined_emotions[emotion] = []
                combined_emotions[emotion].append(score)
        
        # Average scores
        averaged_emotions = {
            emotion: sum(scores) / len(scores)
            for emotion, scores in combined_emotions.items()
        }
        
        primary_emotion = max(averaged_emotions.items(), key=lambda x: x[1])
        
        return {
            'emotion': primary_emotion[0],
            'confidence': primary_emotion[1],
            'all_emotions': averaged_emotions,
            'modality': 'multimodal',
            'sources': results
        }
    
    def _extract_audio_features(self, audio_path: str) -> Dict[str, float]:
        """
        Extract features from audio for emotion recognition.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary of audio features
        """
        # Placeholder - would use librosa or similar in production
        features = {
            'pitch_mean': 0.5,
            'pitch_std': 0.1,
            'energy_mean': 0.6,
            'energy_std': 0.15,
            'tempo': 120.0,
            'mfcc_mean': 0.5,
        }
        return features
    
    def _predict_emotion_from_audio(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Predict emotion from audio features.
        
        Args:
            features: Audio features
            
        Returns:
            Dictionary of emotion scores
        """
        # Placeholder - would use trained model in production
        emotions = {
            'neutral': 0.5,
            'positive': 0.3,
            'negative': 0.2,
            'angry': 0.1,
            'happy': 0.2,
            'sad': 0.1,
            'confused': 0.15,
        }
        return emotions
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment scores
        """
        # Simple keyword-based sentiment (placeholder)
        positive_words = ['gut', 'toll', 'super', 'danke', 'ja', 'gerne', 'interessant']
        negative_words = ['schlecht', 'nein', 'nicht', 'keine', 'aber', 'problem']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count + 1  # +1 to avoid division by zero
        
        return {
            'positive': positive_count / total,
            'negative': negative_count / total,
            'neutral': 1 / total
        }
    
    def _get_neutral_result(self) -> Dict[str, Any]:
        """Get neutral emotion result."""
        return {
            'emotion': 'neutral',
            'confidence': 1.0,
            'all_emotions': {'neutral': 1.0},
            'modality': 'none'
        }
    
    def get_emotion_intensity(self, emotion: str, score: float) -> str:
        """
        Get intensity label for emotion score.
        
        Args:
            emotion: Emotion name
            score: Emotion score (0-1)
            
        Returns:
            Intensity label (low, medium, high)
        """
        if score < 0.4:
            return 'low'
        elif score < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def should_adapt_response(self, emotion: str, confidence: float) -> bool:
        """
        Determine if response should be adapted based on emotion.
        
        Args:
            emotion: Detected emotion
            confidence: Detection confidence
            
        Returns:
            True if response should be adapted
        """
        # Adapt for strong negative emotions
        if confidence > self.confidence_threshold:
            if emotion in ['angry', 'frustrated', 'sad', 'negative']:
                return True
        return False
