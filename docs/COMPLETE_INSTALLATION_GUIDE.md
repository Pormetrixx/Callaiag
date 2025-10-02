# Complete A-Z Installation Guide for Callaiag AI Agent

This comprehensive guide walks you through the complete installation process from start to finish, covering all aspects of setting up the Callaiag AI Agent system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Preparation](#system-preparation)
3. [Installation Methods](#installation-methods)
4. [Post-Installation Configuration](#post-installation-configuration)
5. [Verification and Testing](#verification-and-testing)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [Maintenance](#maintenance)

---

## Prerequisites

### A. Hardware Requirements

**Minimum Configuration:**
- CPU: 2 cores (Intel/AMD 64-bit)
- RAM: 4 GB
- Storage: 10 GB free space
- Network: Internet connection for installation

**Recommended Configuration:**
- CPU: 4+ cores
- RAM: 8+ GB (for optimal Whisper performance)
- Storage: 20+ GB SSD
- Network: Stable broadband connection
- Optional: NVIDIA GPU with CUDA support (for faster speech processing)

### B. Software Requirements

**Operating System:**
- Ubuntu Server 22.04 LTS (Primary supported)
- Ubuntu Desktop 22.04 LTS
- Debian 11+ (Compatible)
- Other Linux distributions (May require adjustments)

**Required Software:**
- Python 3.8 or higher
- Git (for cloning repository)
- sudo privileges (for system-wide installation)

**Optional Software:**
- Docker and Docker Compose (for containerized deployment)
- MySQL 8.0+ or PostgreSQL 15+ (alternative databases)
- NGINX or Apache (for production web serving)

---

## System Preparation

### Step 1: Update Your System

```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git sudo
```

### Step 2: Verify Python Version

```bash
# Check Python version (must be 3.8+)
python3 --version

# Install pip if not present
sudo apt install -y python3-pip python3-venv
```

### Step 3: Create Installation User (Optional)

For better security, you can create a dedicated user:

```bash
# Create user (done automatically by install.sh)
sudo useradd -r -m -s /bin/bash callaiag

# Add to necessary groups
sudo usermod -aG audio,video callaiag
```

---

## Installation Methods

### Method 1: Automated Installation (Recommended)

This is the fastest and most reliable method.

#### A. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/Pormetrixx/Callaiag.git

# Navigate to directory
cd Callaiag

# Make install script executable
chmod +x install.sh
```

#### B. Run Installation Script

```bash
# Run with sudo (required)
sudo bash install.sh
```

The script will:
1. ✓ Detect your operating system
2. ✓ Update system packages
3. ✓ Install system dependencies (Python, FFmpeg, audio libraries)
4. ✓ Optionally install Asterisk PBX
5. ✓ Create service user and directories
6. ✓ Set up Python virtual environment
7. ✓ Install Python dependencies
8. ✓ Initialize configuration files
9. ✓ Create database schema
10. ✓ Set up systemd service
11. ✓ Configure firewall rules

**Installation prompts:**
- When asked "Install Asterisk PBX?", answer `y` if you need telephony features
- The process takes 5-15 minutes depending on your internet speed

#### C. Post-Installation

After successful installation, you'll see a summary with:
- Installation directories
- Service commands
- Dashboard URL
- Default credentials

---

### Method 2: Manual Installation

For those who prefer step-by-step control or are using non-Ubuntu systems.

#### A. Install System Dependencies

```bash
# Install Python and development tools
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git

# Install audio libraries
sudo apt install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    libasound2-dev

# Install additional dependencies
sudo apt install -y \
    libffi-dev \
    libssl-dev \
    sqlite3
```

#### B. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/Pormetrixx/Callaiag.git callaiag
cd /opt/callaiag
```

#### C. Create Virtual Environment

```bash
# Create virtual environment
sudo python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### D. Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

**Note:** This step may take 10-20 minutes as it downloads:
- OpenAI Whisper and PyTorch (large packages)
- SQLAlchemy and database drivers
- Audio processing libraries
- Web framework components

#### E. Install Asterisk (Optional)

```bash
# Install Asterisk
sudo apt install -y asterisk

# Enable and start service
sudo systemctl enable asterisk
sudo systemctl start asterisk

# Verify it's running
sudo systemctl status asterisk
```

#### F. Configure Asterisk AMI

```bash
# Backup original configuration
sudo cp /etc/asterisk/manager.conf /etc/asterisk/manager.conf.backup

# Edit manager.conf
sudo nano /etc/asterisk/manager.conf
```

Add this configuration:

```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[callaiag]
secret = callaiag123
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.0
read = system,call,log,verbose,command,agent,user,config
write = system,call,log,verbose,command,agent,user,config
```

Configure dialplan:

```bash
# Edit extensions.conf
sudo nano /etc/asterisk/extensions.conf
```

Add:

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

#### G. Initialize Callaiag

```bash
# Create configuration directory
sudo mkdir -p /etc/callaiag

# Copy default configuration
sudo cp config/default_config.yml /etc/callaiag/config.yml

# Create data directories
sudo mkdir -p /var/lib/callaiag/{data,temp,scripts,faqs,models,logs}

# Initialize system
python3 run.py init

# Validate setup
python3 run.py validate
```

#### H. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/callaiag.service
```

Add this content (adjust paths as needed):

```ini
[Unit]
Description=Callaiag AI Agent
After=network.target asterisk.service
Wants=asterisk.service

[Service]
Type=simple
User=callaiag
Group=callaiag
WorkingDirectory=/opt/callaiag
Environment="PATH=/opt/callaiag/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/callaiag/venv/bin/python3 /opt/callaiag/run.py start
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/callaiag/callaiag.log
StandardError=append:/var/log/callaiag/callaiag-error.log

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable callaiag

# Start service
sudo systemctl start callaiag

# Check status
sudo systemctl status callaiag
```

---

### Method 3: Docker Installation

For containerized deployment.

#### A. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install -y docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes
```

#### B. Clone and Build

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Build Docker image
docker-compose build

# Or use make command
make docker-build
```

#### C. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Post-Installation Configuration

### Step 1: Update Configuration File

```bash
# Edit configuration
sudo nano /etc/callaiag/config.yml

# Or for local installation
nano config/default_config.yml
```

**Key settings to configure:**

#### Database Configuration

```yaml
database:
  type: sqlite  # or mysql, postgresql
  path: /var/lib/callaiag/data/callaiag.db
  
  # For MySQL/PostgreSQL:
  # type: mysql
  # host: localhost
  # port: 3306
  # name: callaiag
  # user: callaiag
  # password: your_secure_password
```

#### Asterisk Configuration

```yaml
asterisk:
  enabled: true
  host: localhost
  port: 5038
  username: callaiag
  password: callaiag123  # CHANGE THIS!
  context: outbound
  channel_type: SIP
  caller_id: "Callaiag <1000>"
```

#### Speech Processing

```yaml
speech:
  stt:
    engine: whisper
    whisper_model: medium  # Options: tiny, base, small, medium, large
    language: de
    device: cpu  # or cuda if you have GPU
  
  tts:
    engine: mimic3  # or coqui
    voice: de_DE/thorsten-emotional
```

#### Dashboard Configuration

```yaml
dashboard:
  enabled: true
  port: 8080
  host: 0.0.0.0
  admin_user: admin
  admin_password: admin123  # CHANGE THIS!
```

### Step 2: Change Default Passwords

**IMPORTANT:** Change all default passwords before production use!

```bash
# Generate secure password
openssl rand -base64 32

# Update in config.yml:
# - dashboard.admin_password
# - asterisk.password
# - database.password (if using MySQL/PostgreSQL)
```

### Step 3: Configure Firewall

```bash
# If using UFW
sudo ufw allow 8080/tcp  # Dashboard
sudo ufw allow 22/tcp    # SSH
sudo ufw enable

# For Asterisk (if needed)
sudo ufw allow 5060/udp  # SIP
sudo ufw allow 5038/tcp  # AMI (only from localhost)
```

---

## Verification and Testing

### Step 1: Verify Installation

```bash
# Check service status
sudo systemctl status callaiag

# View recent logs
sudo journalctl -u callaiag -n 50

# Or for file logs
sudo tail -f /var/log/callaiag/callaiag.log
```

### Step 2: Run System Validation

```bash
# Activate virtual environment (if manual install)
source /opt/callaiag/venv/bin/activate

# Run validation
python3 run.py validate
```

Expected output:
```
[1/5] Checking configuration...
  ✓ Configuration loaded

[2/5] Checking database...
  ✓ Database connection successful

[3/5] Checking Asterisk PBX...
  ✓ Asterisk configuration validated

[4/5] Checking speech processing...
  ✓ Speech processing components initialized

[5/5] Checking directories...
  ✓ All directories present

✓ All validation checks passed!
```

### Step 3: Access Dashboard

```bash
# Get your server IP
hostname -I | awk '{print $1}'

# Open in browser:
# http://YOUR_IP:8080
```

Default credentials:
- Username: `admin`
- Password: `admin123` (change immediately!)

### Step 4: Run Demo Scripts

```bash
# Complete system demo
python3 examples/complete_demo.py

# Asterisk integration demo
python3 examples/asterisk_demo.py
```

### Step 5: Test Speech Processing

```bash
# Test TTS
python3 -c "
from callaiag.speech.synthesis import SpeechSynthesizer
from callaiag.core.config import Config

config = Config()
synth = SpeechSynthesizer(config)
audio = synth.synthesize('Hallo, dies ist ein Test.')
print(f'Audio created: {audio}')
"
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Service Won't Start

**Symptoms:**
```bash
sudo systemctl status callaiag
# Shows: Failed to start Callaiag AI Agent
```

**Solutions:**

```bash
# Check logs for errors
sudo journalctl -u callaiag -n 100

# Common causes:
# 1. Missing dependencies
pip install -r requirements.txt

# 2. Permission issues
sudo chown -R callaiag:callaiag /opt/callaiag
sudo chown -R callaiag:callaiag /var/lib/callaiag

# 3. Configuration errors
python3 run.py validate
```

#### Issue 2: Database Connection Failed

**Solutions:**

```bash
# Check database file exists
ls -la /var/lib/callaiag/data/callaiag.db

# Reinitialize if needed
python3 run.py init

# Check permissions
sudo chown callaiag:callaiag /var/lib/callaiag/data/callaiag.db
```

#### Issue 3: Asterisk Connection Failed

**Solutions:**

```bash
# Verify Asterisk is running
sudo systemctl status asterisk

# Test AMI connection
telnet localhost 5038

# Check manager.conf
sudo nano /etc/asterisk/manager.conf

# Reload Asterisk
sudo asterisk -rx "manager reload"
```

#### Issue 4: Audio Devices Not Found

**Solutions:**

```bash
# Install audio libraries
sudo apt install -y portaudio19-dev libasound2-dev

# Check audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Add user to audio group
sudo usermod -aG audio callaiag
```

#### Issue 5: Dashboard Not Accessible

**Solutions:**

```bash
# Check if service is listening
sudo netstat -tlnp | grep 8080

# Check firewall
sudo ufw status
sudo ufw allow 8080/tcp

# Check configuration
grep -A 3 "dashboard:" /etc/callaiag/config.yml
```

#### Issue 6: Python Module Import Errors

**Solutions:**

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python3 --version  # Must be 3.8+

# Verify virtual environment
which python3
# Should show: /opt/callaiag/venv/bin/python3
```

---

## Advanced Configuration

### Using MySQL Database

```bash
# Install MySQL
sudo apt install -y mysql-server

# Secure installation
sudo mysql_secure_installation

# Create database and user
sudo mysql << EOF
CREATE DATABASE callaiag;
CREATE USER 'callaiag'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON callaiag.* TO 'callaiag'@'localhost';
FLUSH PRIVILEGES;
EOF

# Update config.yml
nano /etc/callaiag/config.yml
```

```yaml
database:
  type: mysql
  host: localhost
  port: 3306
  name: callaiag
  user: callaiag
  password: secure_password
```

### Using PostgreSQL Database

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE callaiag;
CREATE USER callaiag WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE callaiag TO callaiag;
EOF

# Update config.yml
```

```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  name: callaiag
  user: callaiag
  password: secure_password
```

### Enabling GPU Acceleration

```bash
# Install NVIDIA drivers (if not installed)
sudo ubuntu-drivers autoinstall

# Install CUDA toolkit
sudo apt install -y nvidia-cuda-toolkit

# Reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update config.yml
```

```yaml
speech:
  stt:
    device: cuda  # Changed from cpu
```

### Setting Up HTTPS

```bash
# Install NGINX
sudo apt install -y nginx

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Configure NGINX as reverse proxy
sudo nano /etc/nginx/sites-available/callaiag
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/callaiag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Maintenance

### Regular Maintenance Tasks

#### Daily Tasks

```bash
# Check service status
sudo systemctl status callaiag

# Monitor logs
sudo tail -f /var/log/callaiag/callaiag.log
```

#### Weekly Tasks

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Check disk space
df -h /var/lib/callaiag

# Backup database
sudo cp /var/lib/callaiag/data/callaiag.db /backup/callaiag-$(date +%Y%m%d).db
```

#### Monthly Tasks

```bash
# Update Python dependencies
source /opt/callaiag/venv/bin/activate
pip list --outdated
pip install --upgrade package_name

# Clean old logs
find /var/log/callaiag -name "*.log" -mtime +30 -delete

# Optimize database (SQLite)
sqlite3 /var/lib/callaiag/data/callaiag.db "VACUUM;"
```

### Backup Procedures

```bash
# Full backup script
#!/bin/bash
BACKUP_DIR="/backup/callaiag"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /var/lib/callaiag/data/callaiag.db $BACKUP_DIR/callaiag-$DATE.db

# Backup configuration
cp /etc/callaiag/config.yml $BACKUP_DIR/config-$DATE.yml

# Backup scripts and FAQs
tar -czf $BACKUP_DIR/data-$DATE.tar.gz /var/lib/callaiag/{scripts,faqs}

echo "Backup completed: $BACKUP_DIR"
```

### Update Procedures

```bash
# Update Callaiag
cd /opt/callaiag

# Backup first!
sudo systemctl stop callaiag

# Pull latest changes
sudo git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run any migrations
python3 run.py init

# Restart service
sudo systemctl start callaiag
```

### Uninstallation

If you need to completely remove Callaiag:

```bash
# Stop service
sudo systemctl stop callaiag
sudo systemctl disable callaiag

# Remove systemd service
sudo rm /etc/systemd/system/callaiag.service
sudo systemctl daemon-reload

# Remove files
sudo rm -rf /opt/callaiag
sudo rm -rf /etc/callaiag
sudo rm -rf /var/lib/callaiag
sudo rm -rf /var/log/callaiag

# Remove user
sudo userdel callaiag

# Optional: Remove Asterisk
sudo apt remove --purge asterisk
```

---

## Support and Resources

### Getting Help

- **Documentation**: Check docs/ directory
- **GitHub Issues**: https://github.com/Pormetrixx/Callaiag/issues
- **Logs**: Always check `/var/log/callaiag/callaiag.log` first

### Useful Commands Reference

```bash
# Service Management
sudo systemctl start callaiag
sudo systemctl stop callaiag
sudo systemctl restart callaiag
sudo systemctl status callaiag

# Log Viewing
sudo journalctl -u callaiag -f
sudo tail -f /var/log/callaiag/callaiag.log

# Configuration
sudo nano /etc/callaiag/config.yml
python3 run.py validate

# Development
make help
make init
make validate
make test
```

---

## Conclusion

You should now have a fully functional Callaiag AI Agent system installed and configured. Remember to:

1. ✓ Change all default passwords
2. ✓ Configure firewall rules
3. ✓ Set up regular backups
4. ✓ Monitor logs regularly
5. ✓ Keep system updated

For additional help, refer to the other documentation files in the `docs/` directory.

---

**Document Version:** 1.0  
**Last Updated:** October 2024  
**Tested On:** Ubuntu Server 22.04 LTS
