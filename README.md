# Callaiag - AI Agent for Automated Cold Calling

A comprehensive AI agent system for automated cold calling with local speech processing, emotion recognition, and continuous learning capabilities.

## Key Features

### Speech Processing
- Local Speech Recognition using OpenAI Whisper
- Text-to-Speech support with Coqui TTS and Mimic3
- Audio processing utilities
- Real-time audio capture with PyAudio
- Cross-platform audio playback

### Asterisk PBX Integration
- Complete Asterisk Manager Interface (AMI) integration
- Real-time event handling
- Multi-channel support (SIP, PJSIP, IAX2)
- Call origination with configurable contexts
- Local server control

### Automated Installation & Management
- One-command installation system
- Automated Asterisk setup
- Database configuration
- Web server deployment
- System service management

### Web-Based Management Dashboard
- Real-time system monitoring
- Conversation script management
- FAQ database management
- Customer relationship management
- Call analytics and reporting

### Conversation Management
- State machine for conversation flow
- Dynamic response generation
- Real-time processing

### Emotion Recognition
- Multi-modal analysis
- Adaptive conversations
- Confidence-based decision making

### Database Architecture
- SQLAlchemy models
- Repository pattern
- Multi-database support

### Continuous Learning
- Automatic training data generation
- Performance analytics
- Adaptive improvement system

## Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Run automated installation
sudo bash install.sh

# System management
./admin.sh status
./admin.sh start
./admin.sh logs

# Access web dashboard
# http://your-server-ip:8080
# Login: admin / admin123 (CHANGE THIS!)
```

### Installation Guides

📖 **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running in 5 minutes  
📖 **[Complete Installation Guide A-Z](docs/COMPLETE_INSTALLATION_GUIDE.md)** - Comprehensive step-by-step instructions  
📖 **[Detailed Installation Options](docs/INSTALL.md)** - Manual, Docker, and advanced setups

### Alternative Setup Methods

**Manual Setup:**
```bash
# Install dependencies
sudo apt install -y python3 python3-pip python3-venv ffmpeg

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize system
python3 run.py init
python3 run.py validate
python3 run.py start
```

**Docker Setup:**
```bash
# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

## Development & Testing
```bash
# Run with Docker
docker-compose up -d

# Development commands
make help

# Run complete system demo
python3 examples/complete_demo.py

# Test Asterisk integration
python3 examples/asterisk_demo.py
```

## Dashboard Access
- URL: http://server-ip/aiagent
- Default Login: admin / admin123
- Features: Script management, FAQ editing, customer management, call analytics, system monitoring

## Technical Requirements
- Python 3.8+ compatibility
- Ubuntu Server 22.04 LTS optimization
- Local processing (no cloud dependencies)
- SQL database storage
- Proper error handling and structured logging
- Modular, scalable architecture
- Complete project infrastructure
- Real audio processing with Whisper and TTS engines
- Professional Asterisk PBX integration
- Training data analysis and performance metrics
