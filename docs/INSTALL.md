# Installation Guide

This guide provides detailed installation instructions for the Callaiag AI Agent system.

## System Requirements

### Minimum Requirements
- **Operating System**: Ubuntu Server 22.04 LTS (recommended) or compatible Linux distribution
- **Python**: Version 3.8 or higher
- **CPU**: 2 cores minimum (4+ recommended)
- **RAM**: 4 GB minimum (8+ GB recommended for Whisper)
- **Disk Space**: 10 GB minimum (more for audio storage and models)

### Optional Requirements
- **Asterisk PBX**: Version 18+ (for telephony integration)
- **Database**: MySQL 8.0+ or PostgreSQL 15+ (optional, SQLite included)
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster speech processing)

## Installation Methods

### Method 1: Automated Installation (Recommended)

The automated installation script sets up everything including Asterisk, database, and web server:

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Run automated installation
sudo bash install.sh

# Manage the system
./admin.sh status
./admin.sh start
./admin.sh stop
```

The automated installation will:
- Install system dependencies
- Set up Python virtual environment
- Install Asterisk PBX
- Configure database
- Set up web server
- Create systemd services
- Configure firewall rules

### Method 2: Manual Installation

#### Step 1: Install System Dependencies

```bash
# Update package lists
sudo apt update

# Install Python and build tools
sudo apt install -y python3 python3-pip python3-venv

# Install audio libraries
sudo apt install -y ffmpeg libsndfile1 portaudio19-dev

# Install development tools
sudo apt install -y build-essential git
```

#### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 3: Install Speech Processing Components

```bash
# Install Whisper models (will download on first use)
# Models: tiny (39M), base (74M), small (244M), medium (769M), large (1550M)

# Install TTS engine (choose one or both)

# Option 1: Mimic3 (recommended)
pip install mimic3-tts[all]

# Option 2: Coqui TTS
pip install TTS
```

#### Step 4: Install Asterisk PBX (Optional)

```bash
# Install Asterisk
sudo apt install -y asterisk

# Start Asterisk
sudo systemctl start asterisk
sudo systemctl enable asterisk

# Verify Asterisk is running
sudo asterisk -rx "core show version"
```

#### Step 5: Configure Asterisk

Edit `/etc/asterisk/manager.conf`:

```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[callaiag]
secret = change_me
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.0
read = system,call,log,verbose,command,agent,user,config
write = system,call,log,verbose,command,agent,user,config
```

Edit `/etc/asterisk/extensions.conf`:

```ini
[outbound]
exten => s,1,Answer()
exten => s,n,Wait(1)
exten => s,n,Playback(hello-world)
exten => s,n,Hangup()
```

Reload Asterisk:

```bash
sudo asterisk -rx "manager reload"
sudo asterisk -rx "dialplan reload"
```

#### Step 6: Initialize Callaiag

```bash
# Initialize system
python3 run.py init

# Validate setup
python3 run.py validate

# Start the agent
python3 run.py start
```

### Method 3: Docker Installation

```bash
# Build Docker image
docker build -t callaiag:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## Configuration

### Edit Configuration File

Edit `config/default_config.yml` to customize settings:

```yaml
# Database (SQLite is default)
database:
  type: sqlite
  path: ./data/callaiag.db

# For MySQL
database:
  type: mysql
  host: localhost
  port: 3306
  name: callaiag
  user: callaiag
  password: your_password

# Asterisk settings
asterisk:
  enabled: true
  host: localhost
  port: 5038
  username: callaiag
  password: change_me

# Speech settings
speech:
  stt:
    whisper_model: medium  # tiny, base, small, medium, large
    language: de
  tts:
    engine: mimic3
    voice: de_DE/thorsten-emotional
```

## Verification

### Test Speech Processing

```bash
# Test synthesis
python3 -c "
from callaiag.speech.synthesis import SpeechSynthesizer
from callaiag.core.config import Config

config = Config('config/default_config.yml')
synth = SpeechSynthesizer(config)
audio = synth.synthesize('Hallo Welt')
print(f'Audio created: {audio}')
"
```

### Test Database

```bash
# Test database connection
python3 -c "
from callaiag.db.repository import Repository
from callaiag.core.config import Config

config = Config('config/default_config.yml')
repo = Repository(config)
repo.connect()
print('Database connected successfully')
repo.disconnect()
"
```

### Access Dashboard

Open your browser and navigate to:
- URL: http://localhost:8080
- Username: admin
- Password: admin123

## Troubleshooting

### Python Dependencies

If you encounter issues installing dependencies:

```bash
# Install system packages first
sudo apt install -y python3-dev libffi-dev libssl-dev

# Try installing requirements again
pip install -r requirements.txt
```

### Audio Issues

If audio recording/playback doesn't work:

```bash
# Install additional audio packages
sudo apt install -y libasound2-dev

# Test audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

### Asterisk Connection

If Asterisk connection fails:

```bash
# Check Asterisk is running
sudo systemctl status asterisk

# Check AMI is listening
netstat -an | grep 5038

# Test AMI connection
telnet localhost 5038
```

### Database Issues

For SQLite permission issues:

```bash
# Ensure data directory exists
mkdir -p data

# Set proper permissions
chmod 755 data
```

## Next Steps

After successful installation:

1. Read [API Documentation](API.md) to understand the system
2. Read [Development Guide](DEVELOPMENT.md) for customization
3. Run example demos:
   ```bash
   python3 examples/complete_demo.py
   python3 examples/asterisk_demo.py
   ```
4. Start building your call scripts and FAQs

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/Pormetrixx/Callaiag/issues)
- Review the documentation
- Contact the development team
