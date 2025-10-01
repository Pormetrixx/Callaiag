"""
Natural delay simulation for human-like behavior.

This module simulates natural response delays and thinking pauses.
"""

import logging
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)


class DelaySimulator:
    """
    Simulates natural delays in conversation.
    
    Provides realistic response timing that mimics human conversation patterns,
    including thinking pauses and typing delays.
    
    Attributes:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
        typing_speed_wpm: Typing speed in words per minute
        
    Example:
        >>> simulator = DelaySimulator(min_delay=0.5, max_delay=2.0)
        >>> simulator.thinking_pause()
        >>> delay = simulator.calculate_response_delay("This is a test message")
    """
    
    def __init__(
        self,
        min_delay: float = 0.5,
        max_delay: float = 2.0,
        typing_speed_wpm: int = 40
    ) -> None:
        """
        Initialize the delay simulator.
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
            typing_speed_wpm: Typing speed in words per minute
        """
        self.min_delay: float = min_delay
        self.max_delay: float = max_delay
        self.typing_speed_wpm: int = typing_speed_wpm
        
        logger.info(
            f"DelaySimulator initialized: "
            f"delay={min_delay}-{max_delay}s, typing={typing_speed_wpm}wpm"
        )
    
    def thinking_pause(self, duration: Optional[float] = None) -> None:
        """
        Simulate a thinking pause.
        
        Args:
            duration: Optional specific duration in seconds. If not provided,
                     uses a random duration between min_delay and max_delay.
                     
        Example:
            >>> simulator.thinking_pause()  # Random pause
            >>> simulator.thinking_pause(1.5)  # 1.5 second pause
        """
        if duration is None:
            duration = random.uniform(self.min_delay, self.max_delay)
        
        logger.debug(f"Thinking pause: {duration:.2f}s")
        time.sleep(duration)
    
    def calculate_response_delay(self, text: str, base_delay: float = 0.3) -> float:
        """
        Calculate response delay based on text length.
        
        Simulates the time it would take to "think" and "type" the response.
        
        Args:
            text: Text to calculate delay for
            base_delay: Base thinking delay in seconds
            
        Returns:
            Total delay in seconds
            
        Example:
            >>> delay = simulator.calculate_response_delay("Hello there!")
            >>> print(f"Response delay: {delay:.2f}s")
        """
        # Calculate typing time based on word count
        word_count = len(text.split())
        typing_time = (word_count / self.typing_speed_wpm) * 60
        
        # Add base thinking delay
        total_delay = base_delay + typing_time
        
        # Add some randomness
        variation = random.uniform(0.8, 1.2)
        total_delay *= variation
        
        # Clamp to min/max delay
        total_delay = max(self.min_delay, min(self.max_delay, total_delay))
        
        logger.debug(f"Calculated response delay: {total_delay:.2f}s for {word_count} words")
        return total_delay
    
    def apply_delay(self, text: str, base_delay: float = 0.3) -> None:
        """
        Apply a calculated delay before responding.
        
        Args:
            text: Text that will be responded with
            base_delay: Base thinking delay in seconds
            
        Example:
            >>> simulator.apply_delay("I understand your concern.")
        """
        delay = self.calculate_response_delay(text, base_delay)
        time.sleep(delay)
    
    def random_pause(self) -> None:
        """
        Add a random pause within configured bounds.
        
        Example:
            >>> simulator.random_pause()
        """
        self.thinking_pause()
    
    def short_pause(self) -> None:
        """
        Add a short pause (0.2-0.5 seconds).
        
        Useful for brief hesitations or natural speech breaks.
        
        Example:
            >>> simulator.short_pause()
        """
        duration = random.uniform(0.2, 0.5)
        logger.debug(f"Short pause: {duration:.2f}s")
        time.sleep(duration)
    
    def long_pause(self) -> None:
        """
        Add a long pause (2.0-4.0 seconds).
        
        Useful for complex thinking or processing time.
        
        Example:
            >>> simulator.long_pause()
        """
        duration = random.uniform(2.0, 4.0)
        logger.debug(f"Long pause: {duration:.2f}s")
        time.sleep(duration)
    
    def get_word_delay(self) -> float:
        """
        Get delay for a single word based on typing speed.
        
        Returns:
            Delay in seconds for one word
        """
        return 60.0 / self.typing_speed_wpm
