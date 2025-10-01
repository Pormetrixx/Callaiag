# API Documentation

This document describes the API and main components of the Callaiag AI Agent system.

## Table of Contents

- [Core System](#core-system)
- [Speech Processing](#speech-processing)
- [Asterisk Integration](#asterisk-integration)
- [Conversation Management](#conversation-management)
- [Emotion Recognition](#emotion-recognition)
- [Database Operations](#database-operations)
- [Web Dashboard](#web-dashboard)

## Core System

### CallaiagSystem

Main orchestrator for the entire system.

```python
from callaiag.core.system import CallaiagSystem

# Initialize system
system = CallaiagSystem(config_path='config/default_config.yml')

# Initialize configuration and database
system.initialize()

# Validate setup
system.validate()

# Start the agent
system.start()

# Stop the agent
system.stop()
```

### Config

Configuration management with multiple source support.

```python
from callaiag.core.config import Config

# Load configuration
config = Config('config/default_config.yml')

# Get configuration values
db_type = config.get('database', 'type', default='sqlite')
whisper_model = config.get('speech', 'stt', 'whisper_model', default='medium')

# Create default configuration
config.create_default_config('config/my_config.yml')
```

## Speech Processing

### SpeechRecognizer

Local speech-to-text using Whisper.

```python
from callaiag.speech.recognition import SpeechRecognizer

recognizer = SpeechRecognizer(config)

# Load model (done automatically on first use)
recognizer.load_model()

# Recognize speech from audio file
result = recognizer.recognize('audio.wav', language='de')

# Result contains:
# - text: Transcribed text
# - language: Detected language
# - confidence: Recognition confidence
# - segments: Detailed segments
print(f"Text: {result['text']}")
print(f"Confidence: {result['confidence']}")
```

### SpeechSynthesizer

Text-to-speech synthesis.

```python
from callaiag.speech.synthesis import SpeechSynthesizer

synthesizer = SpeechSynthesizer(config)

# Synthesize speech
audio_path = synthesizer.synthesize(
    "Guten Tag, hier spricht der AI Agent.",
    output_path='output.wav'
)

# Get available voices
voices = synthesizer.get_available_voices()
```

### AudioProcessor

Audio capture and processing utilities.

```python
from callaiag.speech.audio import AudioProcessor

processor = AudioProcessor(config)

# Record audio
audio_path = processor.record(duration=5.0)

# Play audio
processor.play('audio.wav')

# Convert format
wav_path = processor.convert_format('input.mp3', 'wav')

# Resample
resampled = processor.resample('audio.wav', target_rate=16000)

# Normalize volume
normalized = processor.normalize('audio.wav', target_db=-20.0)

# Get audio info
info = processor.get_audio_info('audio.wav')
print(f"Duration: {info['duration']}s")
```

## Asterisk Integration

### AsteriskManagerInterface

Low-level AMI client.

```python
from callaiag.asterisk.ami import AsteriskManagerInterface

ami = AsteriskManagerInterface(config)

# Connect to Asterisk
ami.connect()

# Originate call
action_id = ami.originate_call(
    number='+49123456789',
    context='outbound',
    caller_id='Callaiag <1000>'
)

# Register event handler
def on_hangup(event):
    print(f"Call ended: {event}")

ami.register_event_handler('Hangup', on_hangup)

# Hangup call
ami.hangup_call('SIP/trunk-00000001')

# Disconnect
ami.disconnect()
```

### CallManager

High-level call management.

```python
from callaiag.asterisk.call_manager import CallManager

call_manager = CallManager(config, ami)

# Make a call
def on_call_event(call_id, event_type, data):
    print(f"Call {call_id}: {event_type}")

call_id = call_manager.make_call(
    number='+49123456789',
    callback=on_call_event
)

# Get call info
call = call_manager.get_call(call_id)
print(f"State: {call.state.value}")
print(f"Duration: {call.duration}s")

# Hangup call
call_manager.hangup_call(call_id)

# Get all active calls
active_calls = call_manager.get_active_calls()
```

## Conversation Management

### ConversationStateMachine

Manages conversation flow and state transitions.

```python
from callaiag.conversation.state_machine import ConversationStateMachine

state_machine = ConversationStateMachine(config)

# Start conversation
state_machine.start_conversation({
    'customer_name': 'Max Mustermann',
    'agent_name': 'Sarah'
})

# Process user input
response = state_machine.process_input(
    "Ja, ich bin interessiert.",
    metadata={'emotion': 'positive', 'confidence': 0.8}
)

print(f"Agent: {response}")
print(f"State: {state_machine.get_state().value}")

# Get conversation history
history = state_machine.get_history()

# Reset state machine
state_machine.reset()
```

### ResponseGenerator

Generates dynamic responses based on context.

```python
from callaiag.conversation.response_generator import ResponseGenerator

generator = ResponseGenerator(config)

# Generate response
response = generator.generate_response(
    'greeting',
    context={
        'customer_name': 'Max Mustermann',
        'agent_name': 'Sarah',
        'company': 'Example GmbH'
    },
    emotion='positive'
)

# Get FAQ response
faq_type = generator.detect_question_type("Was kostet das?")
response = generator.get_faq_response(faq_type, {'price': '99'})

# Add custom template
generator.add_script_template('greeting', 'Hallo {customer_name}!')

# Add custom FAQ
generator.add_faq('custom_question', 'Antwort auf die Frage')
```

## Emotion Recognition

### EmotionAnalyzer

Multi-modal emotion analysis.

```python
from callaiag.emotion.analyzer import EmotionAnalyzer

analyzer = EmotionAnalyzer(config)

# Analyze from audio
result = analyzer.analyze_audio('audio.wav')
print(f"Emotion: {result['emotion']}")
print(f"Confidence: {result['confidence']}")

# Analyze from text
result = analyzer.analyze_text("Das ist großartig!")
print(f"Emotion: {result['emotion']}")

# Multimodal analysis
result = analyzer.analyze_multimodal(
    audio_path='audio.wav',
    text='Das ist interessant.'
)

# Check if response should be adapted
should_adapt = analyzer.should_adapt_response(
    emotion='angry',
    confidence=0.8
)
```

## Database Operations

### Repository

Data access layer using repository pattern.

```python
from callaiag.db.repository import Repository

repo = Repository(config)

# Connect to database
repo.connect()

# Initialize schema
repo.initialize_schema()

# Customer operations
customer = repo.create_customer(
    name='Max Mustermann',
    phone='+49123456789',
    email='max@example.com'
)

customer = repo.get_customer_by_phone('+49123456789')
repo.update_customer(customer.id, notes='VIP customer')
customers = repo.list_customers(limit=100)

# Call operations
call = repo.create_call(
    call_id='call-001',
    phone_number='+49123456789',
    customer_id=customer.id
)

repo.update_call('call-001', outcome='success', duration=120.5)
calls = repo.list_calls(limit=50)

# Conversation logs
repo.add_conversation_log(
    call_id=call.id,
    speaker='agent',
    text='Guten Tag!',
    state='greeting'
)

logs = repo.get_conversation_logs('call-001')

# Emotion logs
repo.add_emotion_log(
    call_id=call.id,
    emotion='positive',
    confidence=0.8,
    all_emotions={'positive': 0.8, 'neutral': 0.2}
)

# Scripts and FAQs
script = repo.create_script(
    name='greeting_v1',
    script_type='greeting',
    template='Hallo {customer_name}!'
)

faq = repo.create_faq(
    question_type='preis',
    question='Was kostet das?',
    answer='Der Preis beträgt {price} Euro.'
)

# Cleanup
repo.disconnect()
```

## Web Dashboard

### Dashboard

Web interface for system management.

```python
from callaiag.web.dashboard import Dashboard

dashboard = Dashboard(config, system)

# Start dashboard server
dashboard.start()

# Check if running
if dashboard.is_running():
    print(f"Dashboard URL: {dashboard.get_url()}")

# Stop dashboard
dashboard.stop()
```

### Dashboard API Endpoints

When running, the dashboard exposes REST API endpoints:

- `GET /` - Dashboard index page
- `GET /api/calls` - List recent calls
- `GET /api/customers` - List customers
- `GET /api/scripts` - List conversation scripts
- `GET /api/faqs` - List FAQs
- `GET /api/stats` - Get system statistics

Example API usage:

```python
import requests

# Get statistics
response = requests.get('http://localhost:8080/api/stats')
stats = response.json()
print(f"Total calls: {stats['total_calls']}")

# Get calls
response = requests.get('http://localhost:8080/api/calls')
calls = response.json()['calls']
```

## Error Handling

All API methods raise exceptions on errors. Use try-except blocks:

```python
try:
    result = recognizer.recognize('audio.wav')
except FileNotFoundError:
    print("Audio file not found")
except Exception as e:
    print(f"Recognition error: {e}")
```

## Logging

The system uses Python's logging module:

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Get logger for specific module
logger = logging.getLogger('callaiag.speech')
logger.setLevel(logging.DEBUG)
```

## Best Practices

1. **Always use context managers for database operations:**
   ```python
   with repo.session_scope() as session:
       # Database operations
       pass
   ```

2. **Handle cleanup properly:**
   ```python
   try:
       system.start()
   finally:
       system.stop()
   ```

3. **Check configuration before use:**
   ```python
   if config.get('asterisk', 'enabled'):
       ami.connect()
   ```

4. **Use appropriate models based on hardware:**
   ```python
   # Use smaller Whisper model on CPU
   config.set('speech', 'stt', 'whisper_model', 'small')
   ```

## Examples

See the `examples/` directory for complete working examples:
- `complete_demo.py` - Full system demonstration
- `asterisk_demo.py` - Asterisk integration examples
