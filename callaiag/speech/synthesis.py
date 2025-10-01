#!/usr/bin/env python3
"""
Speech synthesis module for Callaiag.

This module provides local text-to-speech capabilities using various
TTS engines like Mimic3 and Coqui TTS.
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SpeechSynthesizer:
    """
    Text-to-speech synthesis using local TTS engines.
    
    Supports multiple TTS engines:
    - Mimic3: Fast, neural TTS
    - Coqui TTS: High-quality neural TTS
    """
    
    def __init__(self, config):
        """
        Initialize the speech synthesizer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.engine = config.get('speech', 'tts', 'engine', default='mimic3')
        self.voice = config.get('speech', 'tts', 'voice', default='de_DE/thorsten-emotional')
        self.rate = config.get('speech', 'tts', 'rate', default=1.0)
        self.pitch = config.get('speech', 'tts', 'pitch', default=0.0)
        self.volume = config.get('speech', 'tts', 'volume', default=1.0)
        self.temp_dir = Path(config.get('speech', 'audio', 'temp_dir', default='./temp'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Speech synthesizer initialized with engine: {self.engine}")
    
    def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Optional output file path
            
        Returns:
            Path to generated audio file
        """
        if not output_path:
            fd, output_path = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir)
            os.close(fd)
        
        try:
            logger.debug(f"Synthesizing text: {text[:50]}...")
            
            if self.engine == 'mimic3':
                return self._synthesize_mimic3(text, output_path)
            elif self.engine == 'coqui':
                return self._synthesize_coqui(text, output_path)
            else:
                logger.error(f"Unknown TTS engine: {self.engine}")
                raise ValueError(f"Unsupported TTS engine: {self.engine}")
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    def _synthesize_mimic3(self, text: str, output_path: str) -> str:
        """
        Synthesize speech using Mimic3 TTS.
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            
        Returns:
            Path to generated audio file
        """
        try:
            # Build Mimic3 command
            cmd = [
                'mimic3',
                '--voice', self.voice,
                '--output-file', output_path,
            ]
            
            if self.rate != 1.0:
                cmd.extend(['--length-scale', str(1.0 / self.rate)])
            
            # Run Mimic3
            result = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Mimic3 failed: {result.stderr.decode()}")
            
            logger.debug(f"Speech synthesized to {output_path}")
            return output_path
            
        except FileNotFoundError:
            logger.error("Mimic3 not found. Please install mimic3-tts.")
            raise
        except Exception as e:
            logger.error(f"Error in Mimic3 synthesis: {e}")
            raise
    
    def _synthesize_coqui(self, text: str, output_path: str) -> str:
        """
        Synthesize speech using Coqui TTS.
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            
        Returns:
            Path to generated audio file
        """
        try:
            # Build Coqui TTS command
            cmd = [
                'tts',
                '--text', text,
                '--out_path', output_path,
            ]
            
            if self.voice:
                cmd.extend(['--model_name', self.voice])
            
            # Run Coqui TTS
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Coqui TTS failed: {result.stderr.decode()}")
            
            logger.debug(f"Speech synthesized to {output_path}")
            return output_path
            
        except FileNotFoundError:
            logger.error("Coqui TTS not found. Please install TTS package.")
            raise
        except Exception as e:
            logger.error(f"Error in Coqui TTS synthesis: {e}")
            raise
    
    def get_available_voices(self):
        """
        Get list of available voices for current engine.
        
        Returns:
            List of voice names
        """
        if self.engine == 'mimic3':
            return self._get_mimic3_voices()
        elif self.engine == 'coqui':
            return self._get_coqui_voices()
        return []
    
    def _get_mimic3_voices(self):
        """Get available Mimic3 voices."""
        try:
            result = subprocess.run(
                ['mimic3', '--voices'],
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception as e:
            logger.error(f"Error getting Mimic3 voices: {e}")
        return []
    
    def _get_coqui_voices(self):
        """Get available Coqui TTS models."""
        try:
            result = subprocess.run(
                ['tts', '--list_models'],
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception as e:
            logger.error(f"Error getting Coqui TTS models: {e}")
        return []
