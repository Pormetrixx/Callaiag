"""
Hesitation simulation for natural speech patterns.

This module simulates hesitations and speech disfluencies.
"""

import logging
import random
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class HesitationSimulator:
    """
    Simulates speech hesitations and disfluencies.
    
    Adds realistic hesitation patterns like word repetitions, false starts,
    and self-corrections to make speech sound more natural.
    
    Attributes:
        frequency: How often to add hesitations (0.0 to 1.0)
        language: Language code for hesitation patterns
        
    Example:
        >>> simulator = HesitationSimulator(frequency=0.10)
        >>> text = simulator.add_hesitation("Ich möchte Ihnen etwas erzählen")
        >>> print(text)
    """
    
    HESITATION_PATTERNS: dict = {
        "de": {
            "word_repetition": ["ich ich", "das das", "und und", "also also"],
            "false_starts": [
                ("Ich möchte", "Ich würde gerne"),
                ("Das ist", "Das wäre"),
                ("Wir haben", "Wir bieten"),
            ],
            "self_corrections": [
                "... oder besser gesagt",
                "... ich meine",
                "... also genauer",
            ]
        },
        "en": {
            "word_repetition": ["I I", "the the", "and and", "so so"],
            "false_starts": [
                ("I want", "I would like"),
                ("This is", "This would be"),
                ("We have", "We offer"),
            ],
            "self_corrections": [
                "... or rather",
                "... I mean",
                "... more specifically",
            ]
        }
    }
    
    def __init__(
        self,
        frequency: float = 0.10,
        language: str = "de"
    ) -> None:
        """
        Initialize the hesitation simulator.
        
        Args:
            frequency: Frequency of hesitation insertion (0.0 to 1.0)
            language: Language code (de, en)
            
        Raises:
            ValueError: If frequency is not between 0.0 and 1.0
        """
        if not 0.0 <= frequency <= 1.0:
            raise ValueError("Frequency must be between 0.0 and 1.0")
        
        self.frequency: float = frequency
        self.language: str = language
        self._patterns: dict = self.HESITATION_PATTERNS.get(
            language,
            self.HESITATION_PATTERNS["de"]
        )
        
        logger.info(f"HesitationSimulator initialized: frequency={frequency}, language={language}")
    
    def add_hesitation(self, text: str) -> str:
        """
        Add hesitation patterns to text.
        
        Args:
            text: Input text
            
        Returns:
            Text with hesitation patterns added
            
        Example:
            >>> text = simulator.add_hesitation("Das ist wichtig")
            >>> print(text)  # Might be "Das das ist wichtig"
        """
        if random.random() > self.frequency:
            return text
        
        # Choose a random hesitation type
        hesitation_type = random.choice([
            "word_repetition",
            "false_start",
            "self_correction"
        ])
        
        if hesitation_type == "word_repetition":
            text = self._add_word_repetition(text)
        elif hesitation_type == "false_start":
            text = self._add_false_start(text)
        elif hesitation_type == "self_correction":
            text = self._add_self_correction(text)
        
        logger.debug(f"Added hesitation ({hesitation_type}): '{text[:50]}...'")
        return text
    
    def _add_word_repetition(self, text: str) -> str:
        """
        Add word repetition to text.
        
        Args:
            text: Input text
            
        Returns:
            Text with word repetition
        """
        words = text.split()
        if len(words) < 2:
            return text
        
        # Repeat first or second word
        repeat_index = random.choice([0, 1]) if len(words) > 1 else 0
        words.insert(repeat_index, words[repeat_index])
        
        return " ".join(words)
    
    def _add_false_start(self, text: str) -> str:
        """
        Add false start to text.
        
        Args:
            text: Input text
            
        Returns:
            Text with false start
        """
        false_starts = self._patterns["false_starts"]
        
        for original, replacement in false_starts:
            if text.startswith(original):
                # Add false start
                return f"{original}... {replacement}{text[len(original):]}"
        
        return text
    
    def _add_self_correction(self, text: str) -> str:
        """
        Add self-correction to text.
        
        Args:
            text: Input text
            
        Returns:
            Text with self-correction
        """
        words = text.split()
        if len(words) < 3:
            return text
        
        # Insert correction phrase in the middle
        insert_pos = len(words) // 2
        correction = random.choice(self._patterns["self_corrections"])
        
        words.insert(insert_pos, correction)
        return " ".join(words)
    
    def should_add_hesitation(self) -> bool:
        """
        Determine if hesitation should be added.
        
        Returns:
            True if hesitation should be added based on frequency
            
        Example:
            >>> if simulator.should_add_hesitation():
            ...     text = simulator.add_hesitation(text)
        """
        return random.random() < self.frequency
    
    def add_pause_markers(self, text: str) -> str:
        """
        Add pause markers to text.
        
        Args:
            text: Input text
            
        Returns:
            Text with pause markers (...)
            
        Example:
            >>> text = simulator.add_pause_markers("Ich denke das ist gut")
            >>> print(text)  # "Ich denke... das ist gut"
        """
        if random.random() > self.frequency:
            return text
        
        words = text.split()
        if len(words) < 3:
            return text
        
        # Add pause marker in the middle
        pause_pos = len(words) // 2
        words.insert(pause_pos, "...")
        
        return " ".join(words)
    
    def get_hesitation_statistics(self) -> dict:
        """
        Get statistics about available hesitation patterns.
        
        Returns:
            Dictionary with pattern counts
        """
        return {
            "word_repetitions": len(self._patterns.get("word_repetition", [])),
            "false_starts": len(self._patterns.get("false_starts", [])),
            "self_corrections": len(self._patterns.get("self_corrections", [])),
            "frequency": self.frequency,
        }
