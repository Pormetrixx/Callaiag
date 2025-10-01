"""
Whisper speech recognition engine for Callaiag.

This module provides speech-to-text capabilities using OpenAI's Whisper model.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WhisperEngine:
    """
    Whisper-based speech recognition engine.
    
    Provides speech-to-text conversion using OpenAI's Whisper model with
    support for multiple languages and model sizes.
    
    Attributes:
        model_name: Name of the Whisper model to use
        language: Language code for recognition
        device: Device to run the model on (cpu/cuda)
        model: Loaded Whisper model instance
        
    Example:
        >>> engine = WhisperEngine(model_name="medium", language="de")
        >>> engine.initialize()
        >>> result = engine.recognize("audio.wav")
        >>> print(result["text"])
    """
    
    def __init__(
        self,
        model_name: str = "medium",
        language: str = "de",
        device: str = "cpu"
    ) -> None:
        """
        Initialize the Whisper engine.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code for recognition (de, en, etc.)
            device: Device to run on (cpu, cuda)
        """
        self.model_name: str = model_name
        self.language: str = language
        self.device: str = device
        self.model: Optional[Any] = None
        self._initialized: bool = False
        
        logger.info(
            f"WhisperEngine created: model={model_name}, "
            f"language={language}, device={device}"
        )
    
    def initialize(self) -> None:
        """
        Initialize the Whisper model.
        
        Loads the model into memory for recognition.
        
        Raises:
            ImportError: If whisper package is not installed
            Exception: If model loading fails
        """
        if self._initialized:
            logger.warning("WhisperEngine already initialized")
            return
        
        try:
            import whisper
            
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            self._initialized = True
            
            logger.info(f"Whisper model '{self.model_name}' loaded successfully")
            
        except ImportError:
            logger.error("Whisper package not installed")
            raise ImportError(
                "Whisper is not installed. Install with: pip install openai-whisper"
            )
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
            raise
    
    def recognize(self, audio_path: str) -> Dict[str, Any]:
        """
        Recognize speech from an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing recognition results with keys:
                - text: Recognized text
                - language: Detected language
                - confidence: Confidence score (if available)
                
        Raises:
            RuntimeError: If engine is not initialized
            FileNotFoundError: If audio file doesn't exist
            Exception: If recognition fails
            
        Example:
            >>> result = engine.recognize("recording.wav")
            >>> print(f"Text: {result['text']}")
        """
        if not self._initialized or self.model is None:
            raise RuntimeError("WhisperEngine not initialized. Call initialize() first.")
        
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            logger.debug(f"Recognizing speech from: {audio_path}")
            
            # Transcribe audio
            result = self.model.transcribe(
                str(audio_path),
                language=self.language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            text = result.get("text", "").strip()
            detected_language = result.get("language", self.language)
            
            logger.info(f"Recognition complete: '{text[:50]}...'")
            
            return {
                "text": text,
                "language": detected_language,
                "confidence": 1.0,  # Whisper doesn't provide per-word confidence
            }
            
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}", exc_info=True)
            raise
    
    def shutdown(self) -> None:
        """
        Shutdown the Whisper engine.
        
        Releases model resources.
        """
        if self._initialized:
            logger.info("Shutting down WhisperEngine")
            self.model = None
            self._initialized = False
