"""
Filler word generation for natural speech.

This module generates filler words and phrases for more natural speech patterns.
"""

import logging
import random
from typing import List, Optional

logger = logging.getLogger(__name__)


class FillerGenerator:
    """
    Generates filler words and phrases.
    
    Adds natural filler words to speech to make it sound more human-like,
    including words like "um", "äh", "also", etc.
    
    Attributes:
        language: Language code for fillers
        frequency: How often to insert fillers (0.0 to 1.0)
        
    Example:
        >>> generator = FillerGenerator(language="de", frequency=0.15)
        >>> text = generator.add_fillers("Das ist ein Test")
        >>> print(text)
    """
    
    FILLERS: dict = {
        "de": [
            "äh",
            "ähm",
            "also",
            "nun",
            "ja",
            "naja",
            "sozusagen",
            "gewissermaßen",
            "quasi",
        ],
        "en": [
            "um",
            "uh",
            "well",
            "you know",
            "like",
            "I mean",
            "actually",
            "basically",
        ]
    }
    
    def __init__(
        self,
        language: str = "de",
        frequency: float = 0.15
    ) -> None:
        """
        Initialize the filler generator.
        
        Args:
            language: Language code (de, en)
            frequency: Frequency of filler insertion (0.0 to 1.0)
            
        Raises:
            ValueError: If frequency is not between 0.0 and 1.0
        """
        if not 0.0 <= frequency <= 1.0:
            raise ValueError("Frequency must be between 0.0 and 1.0")
        
        self.language: str = language
        self.frequency: float = frequency
        self._fillers: List[str] = self.FILLERS.get(language, self.FILLERS["de"])
        
        logger.info(f"FillerGenerator initialized: language={language}, frequency={frequency}")
    
    def add_fillers(self, text: str, custom_frequency: Optional[float] = None) -> str:
        """
        Add filler words to text.
        
        Args:
            text: Input text
            custom_frequency: Optional custom frequency for this call
            
        Returns:
            Text with fillers added
            
        Example:
            >>> text = generator.add_fillers("Ich denke das ist gut")
            >>> print(text)  # "Ich denke, äh, das ist gut"
        """
        frequency = custom_frequency if custom_frequency is not None else self.frequency
        
        words = text.split()
        result: List[str] = []
        
        for i, word in enumerate(words):
            # Add word
            result.append(word)
            
            # Potentially add filler after word (but not at the end)
            if i < len(words) - 1 and random.random() < frequency:
                filler = self.get_random_filler()
                result.append(filler + ",")
        
        enhanced_text = " ".join(result)
        logger.debug(f"Added fillers: '{text[:30]}...' -> '{enhanced_text[:30]}...'")
        
        return enhanced_text
    
    def get_random_filler(self) -> str:
        """
        Get a random filler word.
        
        Returns:
            Random filler word
            
        Example:
            >>> filler = generator.get_random_filler()
            >>> print(filler)  # e.g., "äh"
        """
        return random.choice(self._fillers)
    
    def add_filler_at_start(self, text: str) -> str:
        """
        Add a filler at the beginning of text.
        
        Args:
            text: Input text
            
        Returns:
            Text with filler at start
            
        Example:
            >>> text = generator.add_filler_at_start("Das ist richtig")
            >>> print(text)  # "Äh, das ist richtig"
        """
        if random.random() < self.frequency:
            filler = self.get_random_filler()
            return f"{filler.capitalize()}, {text}"
        return text
    
    def should_add_filler(self) -> bool:
        """
        Determine if a filler should be added.
        
        Returns:
            True if filler should be added based on frequency
            
        Example:
            >>> if generator.should_add_filler():
            ...     text = generator.get_random_filler() + " " + text
        """
        return random.random() < self.frequency
    
    def add_custom_fillers(self, fillers: List[str]) -> None:
        """
        Add custom filler words.
        
        Args:
            fillers: List of custom filler words
            
        Example:
            >>> generator.add_custom_fillers(["gewissermaßen", "irgendwie"])
        """
        self._fillers.extend(fillers)
        logger.debug(f"Added {len(fillers)} custom fillers")
    
    def get_available_fillers(self) -> List[str]:
        """
        Get list of available filler words.
        
        Returns:
            List of filler words
        """
        return self._fillers.copy()
