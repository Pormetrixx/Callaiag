"""
Speech processing module for Callaiag.

This module handles speech recognition (STT) and speech synthesis (TTS)
using local processing with Whisper and various TTS engines.
"""

from callaiag.speech.recognition import SpeechRecognizer
from callaiag.speech.synthesis import SpeechSynthesizer
from callaiag.speech.audio import AudioProcessor

__all__ = ['SpeechRecognizer', 'SpeechSynthesizer', 'AudioProcessor']
