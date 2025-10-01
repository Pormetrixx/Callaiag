"""
Unit tests for speech recognition module.

Tests WhisperEngine and speech processing components.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from callaiag.speech.recognition.whisper_engine import WhisperEngine
from callaiag.speech.recognition.speech_processor import SpeechProcessor


class TestWhisperEngine:
    """Test suite for WhisperEngine class."""
    
    def test_whisper_engine_initialization(self):
        """Test WhisperEngine initialization."""
        engine = WhisperEngine(model_name="base", language="en")
        assert engine.model_name == "base"
        assert engine.language == "en"
        assert engine.device == "cpu"
        assert not engine._initialized
    
    def test_whisper_engine_not_initialized_error(self):
        """Test that recognition fails if engine not initialized."""
        engine = WhisperEngine()
        
        with pytest.raises(RuntimeError, match="not initialized"):
            engine.recognize("test.wav")
    
    def test_whisper_engine_file_not_found(self):
        """Test recognition with non-existent file."""
        engine = WhisperEngine()
        engine._initialized = True
        engine.model = Mock()
        
        with pytest.raises(FileNotFoundError):
            engine.recognize("nonexistent.wav")


class TestSpeechProcessor:
    """Test suite for SpeechProcessor class."""
    
    def test_speech_processor_initialization(self):
        """Test SpeechProcessor initialization."""
        processor = SpeechProcessor()
        assert processor is not None
    
    def test_preprocess_file_not_found(self):
        """Test preprocessing with non-existent file."""
        processor = SpeechProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.preprocess("nonexistent.wav")
