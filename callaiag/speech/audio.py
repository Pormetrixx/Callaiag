#!/usr/bin/env python3
"""
Audio processing module for Callaiag.

This module provides audio capture, playback, and processing utilities
for speech processing operations.
"""

import logging
import os
import wave
import tempfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Audio processing utilities for capture, playback, and manipulation.
    
    Handles audio I/O operations, format conversions, and preprocessing
    for speech recognition and synthesis.
    """
    
    def __init__(self, config):
        """
        Initialize the audio processor.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.sample_rate = config.get('speech', 'audio', 'sample_rate', default=16000)
        self.channels = config.get('speech', 'audio', 'channels', default=1)
        self.format = config.get('speech', 'audio', 'format', default='wav')
        self.input_device = config.get('speech', 'audio', 'input_device')
        self.output_device = config.get('speech', 'audio', 'output_device')
        self.temp_dir = Path(config.get('speech', 'audio', 'temp_dir', default='./temp'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.recording = False
        self.audio_data = []
        
        logger.info("Audio processor initialized")
    
    def record(self, duration: Optional[float] = None, 
               output_path: Optional[str] = None) -> str:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
            output_path: Optional output file path
            
        Returns:
            Path to recorded audio file
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            
            if not output_path:
                fd, output_path = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir)
                os.close(fd)
            
            logger.info(f"Recording audio for {duration}s..." if duration else "Recording audio...")
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate) if duration else -1,
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.input_device,
                dtype='float32'
            )
            
            if duration:
                sd.wait()  # Wait until recording is finished
            
            # Save to file
            sf.write(output_path, audio_data, self.sample_rate)
            
            logger.info(f"Audio recorded to {output_path}")
            return output_path
            
        except ImportError:
            logger.error("sounddevice/soundfile not installed. Install with: pip install sounddevice soundfile")
            raise
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise
    
    def play(self, audio_path: str):
        """
        Play audio file.
        
        Args:
            audio_path: Path to audio file
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            
            logger.debug(f"Playing audio: {audio_path}")
            
            # Load audio file
            data, samplerate = sf.read(audio_path)
            
            # Play audio
            sd.play(data, samplerate, device=self.output_device)
            sd.wait()  # Wait until playback is finished
            
            logger.debug("Audio playback completed")
            
        except ImportError:
            logger.error("sounddevice/soundfile not installed")
            raise
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            raise
    
    def convert_format(self, input_path: str, output_format: str = 'wav',
                       output_path: Optional[str] = None) -> str:
        """
        Convert audio file to different format.
        
        Args:
            input_path: Path to input audio file
            output_format: Target format (wav, mp3, etc.)
            output_path: Optional output file path
            
        Returns:
            Path to converted audio file
        """
        try:
            from pydub import AudioSegment
            
            if not output_path:
                fd, output_path = tempfile.mkstemp(suffix=f'.{output_format}', dir=self.temp_dir)
                os.close(fd)
            
            logger.debug(f"Converting {input_path} to {output_format}")
            
            # Load and convert audio
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=output_format)
            
            logger.debug(f"Audio converted to {output_path}")
            return output_path
            
        except ImportError:
            logger.error("pydub not installed. Install with: pip install pydub")
            raise
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            raise
    
    def resample(self, input_path: str, target_rate: int = 16000,
                 output_path: Optional[str] = None) -> str:
        """
        Resample audio to target sample rate.
        
        Args:
            input_path: Path to input audio file
            target_rate: Target sample rate in Hz
            output_path: Optional output file path
            
        Returns:
            Path to resampled audio file
        """
        try:
            from pydub import AudioSegment
            
            if not output_path:
                fd, output_path = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir)
                os.close(fd)
            
            logger.debug(f"Resampling {input_path} to {target_rate}Hz")
            
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Resample
            audio = audio.set_frame_rate(target_rate)
            audio.export(output_path, format='wav')
            
            logger.debug(f"Audio resampled to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            raise
    
    def normalize(self, input_path: str, target_db: float = -20.0,
                  output_path: Optional[str] = None) -> str:
        """
        Normalize audio volume.
        
        Args:
            input_path: Path to input audio file
            target_db: Target volume level in dB
            output_path: Optional output file path
            
        Returns:
            Path to normalized audio file
        """
        try:
            from pydub import AudioSegment
            
            if not output_path:
                fd, output_path = tempfile.mkstemp(suffix='.wav', dir=self.temp_dir)
                os.close(fd)
            
            logger.debug(f"Normalizing {input_path} to {target_db}dB")
            
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Normalize
            change_in_db = target_db - audio.dBFS
            normalized = audio.apply_gain(change_in_db)
            normalized.export(output_path, format='wav')
            
            logger.debug(f"Audio normalized to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            raise
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get information about audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        try:
            import soundfile as sf
            
            info = sf.info(audio_path)
            
            return {
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format,
                'subtype': info.subtype,
                'frames': info.frames
            }
            
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}
    
    def cleanup(self):
        """Clean up temporary audio files."""
        try:
            import glob
            temp_files = glob.glob(str(self.temp_dir / '*.wav'))
            for file in temp_files:
                try:
                    os.remove(file)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file}: {e}")
            logger.info("Temporary audio files cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
