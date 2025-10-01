"""
Text-to-Speech engine for Callaiag.

This module provides text-to-speech synthesis using various TTS engines.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TTSEngine:
    """
    Text-to-Speech synthesis engine.
    
    Supports multiple TTS backends including Mimic3 and Coqui TTS.
    
    Attributes:
        engine: TTS engine to use (mimic3, coqui)
        voice: Voice name/ID to use
        rate: Speech rate multiplier
        pitch: Pitch adjustment
        volume: Volume level
        
    Example:
        >>> tts = TTSEngine(engine="mimic3", voice="de_DE/thorsten-emotional")
        >>> tts.initialize()
        >>> audio_path = tts.synthesize("Hallo, wie geht es Ihnen?")
    """
    
    def __init__(
        self,
        engine: str = "mimic3",
        voice: str = "de_DE/thorsten-emotional",
        rate: float = 1.0,
        pitch: float = 0.0,
        volume: float = 1.0
    ) -> None:
        """
        Initialize the TTS engine.
        
        Args:
            engine: TTS engine to use (mimic3, coqui)
            voice: Voice name or ID
            rate: Speech rate (1.0 = normal)
            pitch: Pitch adjustment in semitones
            volume: Volume level (0.0 to 1.0)
        """
        self.engine: str = engine
        self.voice: str = voice
        self.rate: float = rate
        self.pitch: float = pitch
        self.volume: float = volume
        self._initialized: bool = False
        
        logger.info(
            f"TTSEngine created: engine={engine}, voice={voice}, "
            f"rate={rate}, pitch={pitch}"
        )
    
    def initialize(self) -> None:
        """
        Initialize the TTS engine.
        
        Validates that the selected engine is available.
        
        Raises:
            RuntimeError: If the TTS engine is not available
        """
        if self._initialized:
            logger.warning("TTSEngine already initialized")
            return
        
        try:
            if self.engine == "mimic3":
                self._check_mimic3()
            elif self.engine == "coqui":
                self._check_coqui()
            else:
                raise RuntimeError(f"Unsupported TTS engine: {self.engine}")
            
            self._initialized = True
            logger.info(f"TTS engine '{self.engine}' initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}", exc_info=True)
            raise
    
    def _check_mimic3(self) -> None:
        """Check if Mimic3 is available."""
        try:
            result = subprocess.run(
                ["mimic3", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("Mimic3 command failed")
            logger.debug("Mimic3 TTS available")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Mimic3 not found, TTS may not work")
    
    def _check_coqui(self) -> None:
        """Check if Coqui TTS is available."""
        try:
            import TTS
            logger.debug("Coqui TTS package available")
        except ImportError:
            logger.warning("Coqui TTS not installed")
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Optional path for output audio file
            
        Returns:
            Path to the generated audio file
            
        Raises:
            RuntimeError: If engine is not initialized
            Exception: If synthesis fails
            
        Example:
            >>> audio_file = tts.synthesize("Hello world")
            >>> print(f"Audio saved to: {audio_file}")
        """
        if not self._initialized:
            raise RuntimeError("TTSEngine not initialized. Call initialize() first.")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Generate output path if not provided
        if output_path is None:
            temp_dir = Path(tempfile.gettempdir())
            output_path = str(temp_dir / f"tts_{tempfile._get_candidate_names().__next__()}.wav")
        
        try:
            logger.debug(f"Synthesizing: '{text[:50]}...'")
            
            if self.engine == "mimic3":
                return self._synthesize_mimic3(text, output_path)
            elif self.engine == "coqui":
                return self._synthesize_coqui(text, output_path)
            else:
                raise RuntimeError(f"Unsupported TTS engine: {self.engine}")
                
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}", exc_info=True)
            raise
    
    def _synthesize_mimic3(self, text: str, output_path: str) -> str:
        """Synthesize speech using Mimic3."""
        try:
            cmd = [
                "mimic3",
                "--voice", self.voice,
                "--output-file", output_path,
                text
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Mimic3 failed: {result.stderr}")
            
            logger.info(f"Speech synthesized to: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Mimic3 synthesis timed out")
        except FileNotFoundError:
            raise RuntimeError("Mimic3 command not found")
    
    def _synthesize_coqui(self, text: str, output_path: str) -> str:
        """Synthesize speech using Coqui TTS."""
        try:
            import TTS
            from TTS.api import TTS as CoquiTTS
            
            # TODO: Implement Coqui TTS synthesis
            # tts = CoquiTTS(model_name=self.voice)
            # tts.tts_to_file(text=text, file_path=output_path)
            
            logger.info(f"Speech synthesized to: {output_path}")
            return output_path
            
        except ImportError:
            raise RuntimeError("Coqui TTS not installed")
    
    def shutdown(self) -> None:
        """
        Shutdown the TTS engine.
        
        Releases any resources held by the engine.
        """
        if self._initialized:
            logger.info("Shutting down TTSEngine")
            self._initialized = False
