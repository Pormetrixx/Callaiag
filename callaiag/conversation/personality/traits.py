"""
Personality traits for the AI agent.

This module defines and manages personality characteristics.
"""

import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class TraitType(Enum):
    """Enumeration of personality trait types."""
    FRIENDLINESS = "friendliness"
    PROFESSIONALISM = "professionalism"
    ENTHUSIASM = "enthusiasm"
    PATIENCE = "patience"
    ASSERTIVENESS = "assertiveness"
    EMPATHY = "empathy"


class PersonalityTraits:
    """
    Manages personality traits for the AI agent.
    
    Defines and maintains personality characteristics that influence
    conversation style and responses.
    
    Attributes:
        traits: Dictionary of trait values (0.0 to 1.0)
        
    Example:
        >>> personality = PersonalityTraits()
        >>> personality.set_trait(TraitType.FRIENDLINESS, 0.8)
        >>> friendliness = personality.get_trait(TraitType.FRIENDLINESS)
    """
    
    DEFAULT_TRAITS: Dict[TraitType, float] = {
        TraitType.FRIENDLINESS: 0.7,
        TraitType.PROFESSIONALISM: 0.8,
        TraitType.ENTHUSIASM: 0.6,
        TraitType.PATIENCE: 0.7,
        TraitType.ASSERTIVENESS: 0.5,
        TraitType.EMPATHY: 0.7,
    }
    
    def __init__(self, custom_traits: Dict[TraitType, float] = None) -> None:
        """
        Initialize personality traits.
        
        Args:
            custom_traits: Optional custom trait values
        """
        self.traits: Dict[TraitType, float] = self.DEFAULT_TRAITS.copy()
        
        if custom_traits:
            for trait_type, value in custom_traits.items():
                self.set_trait(trait_type, value)
        
        logger.info("PersonalityTraits initialized")
    
    def set_trait(self, trait_type: TraitType, value: float) -> None:
        """
        Set a personality trait value.
        
        Args:
            trait_type: Type of trait to set
            value: Value between 0.0 and 1.0
            
        Raises:
            ValueError: If value is not between 0.0 and 1.0
            
        Example:
            >>> personality.set_trait(TraitType.ENTHUSIASM, 0.9)
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Trait value must be between 0.0 and 1.0, got {value}")
        
        self.traits[trait_type] = value
        logger.debug(f"Set trait {trait_type.value} = {value}")
    
    def get_trait(self, trait_type: TraitType) -> float:
        """
        Get a personality trait value.
        
        Args:
            trait_type: Type of trait to retrieve
            
        Returns:
            Trait value between 0.0 and 1.0
            
        Example:
            >>> patience = personality.get_trait(TraitType.PATIENCE)
        """
        return self.traits.get(trait_type, 0.5)
    
    def adjust_trait(self, trait_type: TraitType, delta: float) -> None:
        """
        Adjust a trait value by a delta.
        
        Args:
            trait_type: Type of trait to adjust
            delta: Amount to adjust (positive or negative)
            
        Example:
            >>> personality.adjust_trait(TraitType.ASSERTIVENESS, 0.1)
        """
        current = self.get_trait(trait_type)
        new_value = max(0.0, min(1.0, current + delta))
        self.set_trait(trait_type, new_value)
    
    def get_personality_profile(self) -> Dict[str, float]:
        """
        Get the complete personality profile.
        
        Returns:
            Dictionary mapping trait names to values
        """
        return {
            trait.value: value
            for trait, value in self.traits.items()
        }
    
    def apply_preset(self, preset: str) -> None:
        """
        Apply a personality preset.
        
        Args:
            preset: Name of the preset (friendly, professional, assertive)
            
        Raises:
            ValueError: If preset is not recognized
            
        Example:
            >>> personality.apply_preset("friendly")
        """
        presets = {
            "friendly": {
                TraitType.FRIENDLINESS: 0.9,
                TraitType.PROFESSIONALISM: 0.6,
                TraitType.ENTHUSIASM: 0.8,
                TraitType.PATIENCE: 0.8,
                TraitType.ASSERTIVENESS: 0.4,
                TraitType.EMPATHY: 0.9,
            },
            "professional": {
                TraitType.FRIENDLINESS: 0.6,
                TraitType.PROFESSIONALISM: 0.9,
                TraitType.ENTHUSIASM: 0.5,
                TraitType.PATIENCE: 0.7,
                TraitType.ASSERTIVENESS: 0.6,
                TraitType.EMPATHY: 0.6,
            },
            "assertive": {
                TraitType.FRIENDLINESS: 0.5,
                TraitType.PROFESSIONALISM: 0.8,
                TraitType.ENTHUSIASM: 0.7,
                TraitType.PATIENCE: 0.5,
                TraitType.ASSERTIVENESS: 0.9,
                TraitType.EMPATHY: 0.5,
            },
        }
        
        if preset not in presets:
            raise ValueError(f"Unknown preset: {preset}. Available: {list(presets.keys())}")
        
        for trait_type, value in presets[preset].items():
            self.set_trait(trait_type, value)
        
        logger.info(f"Applied personality preset: {preset}")
