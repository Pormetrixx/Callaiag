"""
Unit tests for human simulation module.

Tests natural delays, fillers, and hesitation patterns.
"""

import pytest
from callaiag.human_simulation.natural_delays import DelaySimulator
from callaiag.human_simulation.speech_patterns.fillers import FillerGenerator
from callaiag.human_simulation.speech_patterns.hesitation import HesitationSimulator


class TestDelaySimulator:
    """Test suite for DelaySimulator class."""
    
    def test_delay_simulator_initialization(self):
        """Test DelaySimulator initialization."""
        simulator = DelaySimulator(min_delay=0.5, max_delay=2.0)
        assert simulator.min_delay == 0.5
        assert simulator.max_delay == 2.0
    
    def test_calculate_response_delay(self):
        """Test response delay calculation."""
        simulator = DelaySimulator()
        delay = simulator.calculate_response_delay("Hello there")
        
        assert delay >= simulator.min_delay
        assert delay <= simulator.max_delay
    
    def test_get_word_delay(self):
        """Test word delay calculation."""
        simulator = DelaySimulator(typing_speed_wpm=60)
        word_delay = simulator.get_word_delay()
        
        assert word_delay == 1.0  # 60 words per minute = 1 second per word


class TestFillerGenerator:
    """Test suite for FillerGenerator class."""
    
    def test_filler_generator_initialization(self):
        """Test FillerGenerator initialization."""
        generator = FillerGenerator(language="de", frequency=0.2)
        assert generator.language == "de"
        assert generator.frequency == 0.2
    
    def test_filler_generator_invalid_frequency(self):
        """Test invalid frequency raises error."""
        with pytest.raises(ValueError):
            FillerGenerator(frequency=1.5)
    
    def test_get_random_filler(self):
        """Test getting random filler."""
        generator = FillerGenerator()
        filler = generator.get_random_filler()
        
        assert filler in generator.get_available_fillers()
    
    def test_add_fillers(self):
        """Test adding fillers to text."""
        generator = FillerGenerator(frequency=1.0)
        text = "Das ist ein Test"
        result = generator.add_fillers(text)
        
        # With frequency 1.0, should have fillers
        assert len(result.split()) > len(text.split())


class TestHesitationSimulator:
    """Test suite for HesitationSimulator class."""
    
    def test_hesitation_simulator_initialization(self):
        """Test HesitationSimulator initialization."""
        simulator = HesitationSimulator(frequency=0.15)
        assert simulator.frequency == 0.15
    
    def test_hesitation_simulator_invalid_frequency(self):
        """Test invalid frequency raises error."""
        with pytest.raises(ValueError):
            HesitationSimulator(frequency=2.0)
    
    def test_should_add_hesitation(self):
        """Test hesitation decision."""
        simulator = HesitationSimulator(frequency=0.0)
        assert not simulator.should_add_hesitation()
        
        simulator = HesitationSimulator(frequency=1.0)
        assert simulator.should_add_hesitation()
    
    def test_get_hesitation_statistics(self):
        """Test getting hesitation statistics."""
        simulator = HesitationSimulator()
        stats = simulator.get_hesitation_statistics()
        
        assert "frequency" in stats
        assert stats["frequency"] == simulator.frequency
