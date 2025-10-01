# Development Guide

This guide helps developers understand the Callaiag architecture and contribute to the project.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Adding New Features](#adding-new-features)
- [Contributing](#contributing)

## Architecture Overview

### System Architecture

Callaiag follows a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│         Web Dashboard (Flask)           │
├─────────────────────────────────────────┤
│       Core System Orchestrator          │
├──────────┬──────────┬──────────┬────────┤
│  Speech  │Asterisk  │Conversation│Emotion│
│Processing│Integration│Management │Analysis│
├──────────┴──────────┴──────────┴────────┤
│        Database Repository              │
└─────────────────────────────────────────┘
```

### Key Components

1. **Core Module** (`callaiag/core/`)
   - System orchestration
   - Configuration management
   - Component lifecycle

2. **Speech Module** (`callaiag/speech/`)
   - Speech recognition (Whisper)
   - Speech synthesis (Mimic3/Coqui)
   - Audio processing

3. **Asterisk Module** (`callaiag/asterisk/`)
   - AMI client implementation
   - Call management
   - Event handling

4. **Conversation Module** (`callaiag/conversation/`)
   - State machine for conversation flow
   - Dynamic response generation
   - Template management

5. **Emotion Module** (`callaiag/emotion/`)
   - Audio-based emotion analysis
   - Text sentiment analysis
   - Multimodal fusion

6. **Database Module** (`callaiag/db/`)
   - SQLAlchemy models
   - Repository pattern
   - Data access layer

7. **Web Module** (`callaiag/web/`)
   - Dashboard interface
   - REST API
   - Real-time monitoring

## Development Setup

### Prerequisites

```bash
# Install development tools
sudo apt install -y git python3-dev

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Create Development Environment

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies with development extras
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### Run Development Server

```bash
# Initialize system
make init

# Start in development mode
python3 run.py start
```

## Project Structure

```
Callaiag/
├── callaiag/              # Main package
│   ├── __init__.py
│   ├── core/              # Core system components
│   │   ├── __init__.py
│   │   ├── system.py      # Main orchestrator
│   │   └── config.py      # Configuration management
│   ├── speech/            # Speech processing
│   │   ├── __init__.py
│   │   ├── recognition.py # STT with Whisper
│   │   ├── synthesis.py   # TTS engines
│   │   └── audio.py       # Audio utilities
│   ├── asterisk/          # Asterisk integration
│   │   ├── __init__.py
│   │   ├── ami.py         # AMI client
│   │   └── call_manager.py
│   ├── conversation/      # Conversation management
│   │   ├── __init__.py
│   │   ├── state_machine.py
│   │   └── response_generator.py
│   ├── emotion/           # Emotion recognition
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   └── models.py
│   ├── db/                # Database layer
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   └── repository.py  # Data access
│   └── web/               # Web dashboard
│       ├── __init__.py
│       ├── dashboard.py
│       ├── static/        # CSS, JS files
│       └── templates/     # HTML templates
├── config/                # Configuration files
│   └── default_config.yml
├── examples/              # Example scripts
│   ├── complete_demo.py
│   └── asterisk_demo.py
├── docs/                  # Documentation
│   ├── INSTALL.md
│   ├── API.md
│   └── DEVELOPMENT.md
├── tests/                 # Unit tests (to be added)
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker setup
├── Makefile              # Development commands
└── run.py                # Main entry point
```

## Coding Standards

### Python Style Guide

Follow PEP 8 with these guidelines:

```python
# Use type hints
def process_text(text: str, language: str = 'de') -> Dict[str, Any]:
    """
    Process text input.
    
    Args:
        text: Input text to process
        language: Language code
        
    Returns:
        Dictionary with processing results
    """
    result = {'text': text, 'language': language}
    return result

# Use descriptive variable names
customer_name = "Max Mustermann"  # Good
cn = "Max Mustermann"  # Bad

# Use constants for magic values
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Document complex logic
# Calculate confidence score based on multiple factors
confidence = (audio_quality * 0.4 + 
              text_clarity * 0.3 + 
              context_match * 0.3)
```

### Module Organization

```python
#!/usr/bin/env python3
"""
Module description.

Detailed explanation of the module's purpose and functionality.
"""

# Standard library imports
import os
import logging
from typing import Dict, Any, Optional

# Third-party imports
import numpy as np
from sqlalchemy import create_engine

# Local imports
from callaiag.core.config import Config

# Module constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Logger setup
logger = logging.getLogger(__name__)

# Classes and functions
class MyClass:
    """Class description."""
    pass
```

### Error Handling

```python
# Use specific exceptions
try:
    result = process_audio(audio_path)
except FileNotFoundError:
    logger.error(f"Audio file not found: {audio_path}")
    raise
except ValueError as e:
    logger.error(f"Invalid audio format: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# Provide helpful error messages
if not os.path.exists(audio_path):
    raise FileNotFoundError(
        f"Audio file not found: {audio_path}. "
        f"Please ensure the file exists and the path is correct."
    )
```

## Testing

### Writing Tests

Create tests in the `tests/` directory:

```python
# tests/test_speech_recognition.py
import pytest
from callaiag.speech.recognition import SpeechRecognizer
from callaiag.core.config import Config

@pytest.fixture
def config():
    """Provide test configuration."""
    return Config()

@pytest.fixture
def recognizer(config):
    """Provide speech recognizer instance."""
    return SpeechRecognizer(config)

def test_recognizer_initialization(recognizer):
    """Test recognizer initializes correctly."""
    assert recognizer.model_name == 'medium'
    assert recognizer.language == 'de'

def test_recognition_result_format(recognizer):
    """Test recognition returns correct format."""
    # Mock the recognition (don't run actual model in tests)
    result = {
        'text': 'Test',
        'language': 'de',
        'confidence': 0.9,
        'success': True
    }
    
    assert 'text' in result
    assert 'confidence' in result
    assert isinstance(result['confidence'], float)
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_speech_recognition.py -v

# Run with coverage
pytest --cov=callaiag --cov-report=html

# Run specific test
pytest tests/test_speech_recognition.py::test_recognizer_initialization
```

## Adding New Features

### Adding a New Speech Engine

1. Create new synthesis class:

```python
# callaiag/speech/synthesis.py

class NewTTSEngine:
    """Implementation for new TTS engine."""
    
    def __init__(self, config):
        self.config = config
        # Initialize engine
    
    def synthesize(self, text: str, output_path: str) -> str:
        """Synthesize speech."""
        # Implementation
        return output_path
```

2. Update synthesizer to support new engine:

```python
def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
    if self.engine == 'new_engine':
        return self._synthesize_new_engine(text, output_path)
    # ... existing engines
```

3. Update configuration:

```yaml
# config/default_config.yml
speech:
  tts:
    engine: new_engine  # Add as option
```

4. Add tests:

```python
# tests/test_new_engine.py
def test_new_engine_synthesis():
    # Test implementation
    pass
```

### Adding Database Models

1. Define model:

```python
# callaiag/db/models.py

class NewModel(Base):
    """New data model."""
    __tablename__ = 'new_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

2. Add repository methods:

```python
# callaiag/db/repository.py

def create_new_model(self, name: str) -> NewModel:
    """Create new model instance."""
    with self.session_scope() as session:
        model = NewModel(name=name)
        session.add(model)
        session.flush()
        session.refresh(model)
        return model
```

3. Update schema initialization:

The schema will be automatically created when you run `initialize_schema()`.

## Contributing

### Git Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Create Pull Request

### Commit Messages

Follow conventional commits:

```
feat: Add new TTS engine support
fix: Resolve database connection issue
docs: Update installation guide
test: Add tests for emotion analyzer
refactor: Simplify state machine logic
```

### Code Review

Before submitting PR:

```bash
# Format code
make format

# Run linters
make lint

# Run tests
make test

# Check everything passes
```

### Documentation

Update documentation when adding features:

1. Update API.md with new APIs
2. Update INSTALL.md if setup changes
3. Add docstrings to all public functions
4. Update README.md if needed

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or in config:

```yaml
general:
  debug: true
  log_level: DEBUG
```

### Common Issues

1. **Import errors**: Check PYTHONPATH includes project root
2. **Database errors**: Ensure `make init` was run
3. **Audio errors**: Check audio library installation
4. **Asterisk errors**: Verify Asterisk is running and configured

## Performance Optimization

### Speech Processing

- Use smaller Whisper models on CPU: `tiny`, `base`, `small`
- Use GPU for large models: Set `device: cuda` in config
- Cache synthesized audio for repeated phrases

### Database

- Use connection pooling for high load
- Add indexes on frequently queried columns
- Use batch operations for bulk inserts

### Memory Management

- Clean up temporary audio files regularly
- Limit conversation history length
- Use generators for large result sets

## Release Process

1. Update version in `callaiag/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag: `git tag v0.2.0`
5. Push tag: `git push origin v0.2.0`
6. Create GitHub release

## Support

- GitHub Issues: For bugs and feature requests
- Discussions: For questions and ideas
- Email: For security issues
