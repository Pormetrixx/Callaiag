# Callaiag Package Structure

This document describes the enhanced package structure for the Callaiag AI Agent.

## Directory Structure

```
callaiag/
├── __init__.py
├── core/                      # Core system components
│   ├── __init__.py
│   ├── system.py             # Main system orchestration
│   ├── config.py             # Configuration management
│   └── logging_setup.py      # Logging configuration
├── speech/                    # Speech processing
│   ├── __init__.py
│   ├── recognition/          # Speech-to-text
│   │   ├── __init__.py
│   │   ├── whisper_engine.py    # Whisper STT engine
│   │   └── speech_processor.py  # Audio preprocessing
│   ├── synthesis/            # Text-to-speech
│   │   ├── __init__.py
│   │   ├── tts_engine.py        # TTS engine (Mimic3/Coqui)
│   │   └── voice_modifier.py    # Voice modification
│   └── processing/           # Audio processing
│       ├── __init__.py
│       ├── noise_reduction.py   # Noise reduction
│       └── voice_enhancement.py # Voice enhancement
├── conversation/              # Conversation management
│   ├── __init__.py
│   ├── state_machine.py      # Conversation flow
│   ├── context/              # Context management
│   │   ├── __init__.py
│   │   ├── memory.py            # Conversation history
│   │   └── topic_tracker.py     # Topic tracking
│   └── personality/          # Personality system
│       ├── __init__.py
│       ├── traits.py            # Personality traits
│       └── behavior_patterns.py # Behavior patterns
└── human_simulation/          # Human-like behavior
    ├── __init__.py
    ├── natural_delays.py     # Response timing
    └── speech_patterns/      # Speech patterns
        ├── __init__.py
        ├── fillers.py           # Filler words
        └── hesitation.py        # Hesitation patterns
```

## Module Descriptions

### Core Module (`callaiag.core`)

**System (`system.py`)**
- Main system orchestration
- Component lifecycle management
- Graceful shutdown handling

**Config (`config.py`)**
- Configuration loading from YAML
- Environment variable support
- Configuration validation
- Default value management

**Logging Setup (`logging_setup.py`)**
- Structured logging configuration
- File rotation support
- Multiple handler support

### Speech Module (`callaiag.speech`)

**Recognition**
- `WhisperEngine`: OpenAI Whisper-based speech recognition
- `SpeechProcessor`: Audio preprocessing utilities

**Synthesis**
- `TTSEngine`: Multi-engine text-to-speech (Mimic3, Coqui)
- `VoiceModifier`: Voice characteristic modification

**Processing**
- `NoiseReducer`: Audio noise reduction
- `VoiceEnhancer`: Voice quality enhancement

### Conversation Module (`callaiag.conversation`)

**State Machine (`state_machine.py`)**
- Conversation flow management
- State transition validation
- Context management

**Context**
- `ConversationMemory`: Conversation history tracking
- `TopicTracker`: Topic detection and tracking

**Personality**
- `PersonalityTraits`: Agent personality management
- `BehaviorPatterns`: Behavioral pattern definitions

### Human Simulation Module (`callaiag.human_simulation`)

**Natural Delays (`natural_delays.py`)**
- Response timing simulation
- Typing speed calculation
- Thinking pauses

**Speech Patterns**
- `FillerGenerator`: Filler word insertion
- `HesitationSimulator`: Speech hesitation patterns

## Usage Examples

### Basic System Initialization

```python
from callaiag import CallaiagSystem

system = CallaiagSystem()
system.initialize()
system.validate()
system.start()
```

### Configuration Management

```python
from callaiag.core import Config

config = Config("config.yaml")
log_level = config.get("general", "log_level", default="INFO")
config.set("general", "debug", value=True)
```

### Conversation Flow

```python
from callaiag.conversation import StateMachine
from callaiag.conversation.state_machine import ConversationState

sm = StateMachine()
sm.transition_to(ConversationState.GREETING)
```

### Speech Processing

```python
from callaiag.speech import WhisperEngine, TTSEngine

# Speech recognition
stt = WhisperEngine(model_name="medium", language="de")
stt.initialize()
result = stt.recognize("audio.wav")

# Speech synthesis
tts = TTSEngine(engine="mimic3", voice="de_DE/thorsten-emotional")
tts.initialize()
audio_file = tts.synthesize("Hallo, wie geht es Ihnen?")
```

### Human-like Behavior

```python
from callaiag.human_simulation import DelaySimulator
from callaiag.human_simulation.speech_patterns import FillerGenerator

# Natural delays
delay = DelaySimulator()
delay.apply_delay("This is my response")

# Filler words
fillers = FillerGenerator(language="de", frequency=0.15)
natural_text = fillers.add_fillers("Das ist ein Test")
```

## Configuration File

The system uses a YAML configuration file located at `config/default_config.yml`. Key sections include:

- **general**: Logging and language settings
- **database**: Database connection settings
- **asterisk**: Asterisk PBX integration
- **speech**: STT/TTS engine configuration
- **conversation**: Conversation management settings
- **human_simulation**: Natural behavior settings
- **personality**: Agent personality traits

## Development

### Running the System

```bash
# Initialize configuration
python run.py init

# Validate setup
python run.py validate

# Start the system
python run.py start
```

### Using Make Commands

```bash
make help       # Show available commands
make install    # Install dependencies
make test       # Run tests
make lint       # Run linters
make clean      # Clean temporary files
make docker-up  # Start with Docker
```

## Testing

Unit tests are provided in the `tests/` directory:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_config.py -v
```

## Key Features

✅ **Type Hints**: All functions have proper type annotations
✅ **Documentation**: Google-style docstrings with examples
✅ **Error Handling**: Comprehensive exception handling
✅ **Logging**: Structured logging throughout
✅ **Validation**: Configuration and input validation
✅ **Modularity**: Clean separation of concerns
✅ **Extensibility**: Easy to add new components

## Contributing

When adding new modules:
1. Follow the existing structure
2. Add proper type hints
3. Include Google-style docstrings
4. Add unit tests
5. Update this README
