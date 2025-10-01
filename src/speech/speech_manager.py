#!/usr/bin/env python3
"""
Speech processing module for Callaiag
Handles speech recognition and synthesis
"""

import os
import tempfile
import logging
import subprocess
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Union

import whisper
import numpy as np
import sounddevice as sd
import soundfile as sf
import wave
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class SpeechManager:
    """Handles speech recognition and synthesis"""
    
    def __init__(self, config):
        """
        Initialize the speech manager
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.whisper_model = None
        self.tts_engine = None
        self.recording = False
        self.temp_dir = Path(config.get('speech', 'audio', 'temp_dir', default='./temp'))
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Audio settings
        self.sample_rate = config.get('speech', 'audio', 'sample_rate', default=16000)
        self.channels = config.get('speech', 'audio', 'channels', default=1)
    
    def initialize(self):
        """Initialize speech processing components"""
        # Load Whisper model for STT
        model_name = self.config.get('speech', 'stt', 'whisper_model', default='medium')
        device = self.config.get('speech', 'stt', 'device', default='cpu')
        
        logger.info(f"Loading Whisper model '{model_name}' on {device}")
        self.whisper_model = whisper.load_model(model_name, device=device)
        
        # Initialize TTS engine
        tts_engine = self.config.get('speech', 'tts', 'engine', default='mimic3')
        logger.info(f"Initializing TTS engine '{tts_engine}'")
        
        if tts_engine == 'mimic3':
            self._initialize_mimic3()
        elif tts_engine == 'coqui':
            self._initialize_coqui()
        else:
            logger.warning(f"Unknown TTS engine '{tts_engine}', falling back to mimic3")
            self._initialize_mimic3()
    
    def _initialize_mimic3(self):
        """Initialize Mimic3 TTS engine"""
        # This would typically involve checking if mimic3 is installed
        # and setting up any necessary configuration
        try:
            # Check if mimic3 is installed by running a simple command
            result = subprocess.run(['mimic3', '--version'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
            if result.returncode == 0:
                logger.info(f"Mimic3 initialized: {result.stdout.strip()}")
                self.tts_engine = 'mimic3'
            else:
                logger.warning("Mimic3 not found or failed to initialize")
                logger.warning("TTS functionality will be limited")
        except Exception as e:
            logger.error(f"Error initializing Mimic3: {e}")
            logger.warning("TTS functionality will be limited")
    
    def _initialize_coqui(self):
        """Initialize Coqui TTS engine"""
        # This would involve importing and initializing Coqui TTS
        # For now, we'll just log that it would be initialized
        try:
            # Import lazily to avoid dependencies if not used
            import TTS
            logger.info(f"Coqui TTS initialized")
            self.tts_engine = 'coqui'
        except ImportError:
            logger.warning("Coqui TTS not installed")
            logger.warning("Falling back to mimic3")
            self._initialize_mimic3()
    
    def recognize_speech(self, audio_path: str) -> Dict[str, Any]:
        """
        Recognize speech in audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with recognition results
        """
        if not self.whisper_model:
            logger.error("Whisper model not initialized")
            return {"text": "", "error": "Model not initialized"}
        
        try:
            # Process audio with Whisper
            language = self.config.get('speech', 'stt', 'language', default='de')
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                task="transcribe"
            )
            
            logger.debug(f"Speech recognition result: {result['text']}")
            return result
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}", exc_info=True)
            return {"text": "", "error": str(e)}
    
    def synthesize_speech(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file
        """
        if not output_path:
            output_path = str(self.temp_dir / f"{next(tempfile._get_candidate_names())}.wav")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        try:
            tts_engine = self.tts_engine or self.config.get('speech', 'tts', 'engine', default='mimic3')
            
            if tts_engine == 'mimic3':
                return self._synthesize_mimic3(text, output_path)
            elif tts_engine == 'coqui':
                return self._synthesize_coqui(text, output_path)
            else:
                logger.warning(f"Unknown TTS engine '{tts_engine}', falling back to mimic3")
                return self._synthesize_mimic3(text, output_path)
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}", exc_info=True)
            return ""
    
    def _synthesize_mimic3(self, text: str, output_path: str) -> str:
        """Synthesize speech using Mimic3
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            
        Returns:
            Path to generated audio file
        """
        try:
            voice = self.config.get('speech', 'tts', 'voice', default='de_DE/thorsten-emotional')
            
            # Call mimic3 to generate speech
            cmd = [
                'mimic3', 
                '--voice', voice,
                '--output', output_path,
                text
            ]
            
            subprocess.run(cmd, check=True)
            
            logger.debug(f"Generated speech with mimic3: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error in mimic3 synthesis: {e}", exc_info=True)
            return ""
    
    def _synthesize_coqui(self, text: str, output_path: str) -> str:
        """Synthesize speech using Coqui TTS
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            
        Returns:
            Path to generated audio file
        """
        try:
            # Import lazily to avoid dependencies if not used
            from TTS.api import TTS
            
            # Initialize TTS with German model
            tts = TTS("tts_models/de/thorsten/tacotron2-DDC")
            
            # Generate speech
            tts.tts_to_file(text=text, file_path=output_path)
            
            logger.debug(f"Generated speech with coqui: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error in coqui synthesis: {e}", exc_info=True)
            logger.warning("Falling back to mimic3")
            return self._synthesize_mimic3(text, output_path)
    
    def play_audio(self, audio_path: str):
        """Play audio file using platform-specific player
        
        Args:
            audio_path: Path to audio file
        """
        try:
            platform = os.name
            
            if platform == 'posix':
                # Linux/macOS
                if os.path.exists('/usr/bin/aplay'):
                    # Linux
                    subprocess.Popen(['aplay', audio_path])
                elif os.path.exists('/usr/bin/afplay'):
                    # macOS
                    subprocess.Popen(['afplay', audio_path])
                else:
                    # Fallback to sounddevice
                    self._play_with_sounddevice(audio_path)
            elif platform == 'nt':
                # Windows
                import winsound
                winsound.PlaySound(audio_path, winsound.SND_FILENAME)
            else:
                # Unknown platform, use sounddevice
                self._play_with_sounddevice(audio_path)
                
            logger.debug(f"Playing audio: {audio_path}")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def _play_with_sounddevice(self, audio_path: str):
        """Play audio file using sounddevice
        
        Args:
            audio_path: Path to audio file
        """
        try:
            data, fs = sf.read(audio_path)
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            logger.error(f"Error playing audio with sounddevice: {e}")
    
    def start_recording(self, duration: Optional[float] = None) -> threading.Thread:
        """Start recording audio
        
        Args:
            duration: Optional recording duration in seconds
            
        Returns:
            Recording thread
        """
        if self.recording:
            logger.warning("Recording already in progress")
            return None
        
        self.recording = True
        self.recorded_frames = []
        
        # Start recording in a separate thread
        thread = threading.Thread(target=self._record_audio, args=(duration,))
        thread.start()
        
        return thread
    
    def _record_audio(self, duration: Optional[float] = None):
        """Record audio from microphone
        
        Args:
            duration: Optional recording duration in seconds
        """
        try:
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio recording status: {status}")
                self.recorded_frames.append(indata.copy())
            
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback):
                if duration:
                    sd.sleep(int(duration * 1000))
                else:
                    # Keep recording until stop_recording is called
                    while self.recording:
                        sd.sleep(100)
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            self.recording = False
    
    def stop_recording(self) -> str:
        """Stop recording and save to file
        
        Returns:
            Path to recorded audio file
        """
        if not self.recording:
            logger.warning("No recording in progress")
            return ""
        
        self.recording = False
        
        # Wait for recording thread to finish
        import time
        time.sleep(0.5)
        
        try:
            if not self.recorded_frames:
                logger.warning("No audio frames recorded")
                return ""
            
            # Create output file
            output_path = str(self.temp_dir / f"{next(tempfile._get_candidate_names())}.wav")
            
            # Save recorded audio to file
            with sf.SoundFile(output_path, mode='w', samplerate=self.sample_rate,
                             channels=self.channels) as file:
                for frame in self.recorded_frames:
                    file.write(frame)
            
            logger.debug(f"Saved recorded audio to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving recorded audio: {e}")
            return ""
    
    def convert_audio_format(self, input_path: str, output_format: str = 'wav') -> str:
        """Convert audio to specified format
        
        Args:
            input_path: Path to input audio file
            output_format: Target format (wav, mp3, etc.)
            
        Returns:
            Path to converted file
        """
        try:
            # Generate output path
            output_path = str(self.temp_dir / f"{next(tempfile._get_candidate_names())}.{output_format}")
            
            # Convert using pydub
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=output_format)
            
            logger.debug(f"Converted audio to {output_format}: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return input_path  # Return original if conversion fails
    
    def normalize_audio(self, input_path: str, target_db: float = -20.0) -> str:
        """Normalize audio volume
        
        Args:
            input_path: Path to input audio file
            target_db: Target dB level
            
        Returns:
            Path to normalized file
        """
        try:
            # Generate output path
            file_ext = os.path.splitext(input_path)[1]
            output_path = str(self.temp_dir / f"{next(tempfile._get_candidate_names())}{file_ext}")
            
            # Normalize using pydub
            audio = AudioSegment.from_file(input_path)
            change_in_db = target_db - audio.dBFS
            normalized_audio = audio.apply_gain(change_in_db)
            normalized_audio.export(output_path, format=file_ext.lstrip('.'))
            
            logger.debug(f"Normalized audio: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return input_path  # Return original if normalization fails
    
    def resample_audio(self, input_path: str, target_sr: int = 16000) -> str:
        """Resample audio to target sample rate
        
        Args:
            input_path: Path to input audio file
            target_sr: Target sample rate
            
        Returns:
            Path to resampled file
        """
        try:
            # Generate output path
            file_ext = os.path.splitext(input_path)[1]
            output_path = str(self.temp_dir / f"{next(tempfile._get_candidate_names())}{file_ext}")
            
            # Resample using pydub
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_frame_rate(target_sr)
            audio.export(output_path, format=file_ext.lstrip('.'))
            
            logger.debug(f"Resampled audio to {target_sr}Hz: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            return input_path  # Return original if resampling fails
    
    def shutdown(self):
        """Clean up resources"""
        logger.info("Shutting down speech manager")
        
        # Clean up temporary files
        if os.path.exists(self.temp_dir):
            try:
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
            except Exception as e:
                logger.error(f"Error cleaning up temp files: {e}")
