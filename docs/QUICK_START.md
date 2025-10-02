# Quick Start Guide - Callaiag AI Agent

This quick reference guide helps you get started with Callaiag in minutes.

## Installation Quick Start

### Option 1: Automated Installation (5-15 minutes)

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Run installation script
sudo bash install.sh

# Follow the prompts
# - Press 'y' when asked about Asterisk installation (recommended)
# - Wait for installation to complete
```

### Option 2: Manual Setup (15-30 minutes)

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg libsndfile1 portaudio19-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Initialize system
python3 run.py init

# Validate setup
python3 run.py validate

# Start the agent
python3 run.py start
```

### Option 3: Docker (5 minutes)

```bash
# Clone repository
git clone https://github.com/Pormetrixx/Callaiag.git
cd Callaiag

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

## After Installation

### 1. Access the Dashboard

Open your browser and navigate to:
```
http://YOUR_SERVER_IP:8080
```

Default credentials:
- **Username:** admin
- **Password:** admin123

**⚠️ IMPORTANT: Change the default password immediately!**

### 2. Configure the System

Edit the configuration file:

```bash
# System-wide installation
sudo nano /etc/callaiag/config.yml

# Local installation
nano config/default_config.yml
```

Key settings to update:
- Dashboard password
- Asterisk credentials (if using telephony)
- Database settings (if using MySQL/PostgreSQL)
- Whisper model size (based on your hardware)

### 3. Manage the Service

```bash
# Using systemd (automated installation)
sudo systemctl start callaiag
sudo systemctl stop callaiag
sudo systemctl restart callaiag
sudo systemctl status callaiag

# Using admin script
./admin.sh start
./admin.sh stop
./admin.sh restart
./admin.sh status
./admin.sh logs

# Using run.py directly
python3 run.py start
python3 run.py validate
```

## Common Tasks

### View Logs

```bash
# Systemd installation
sudo journalctl -u callaiag -f

# File logs
sudo tail -f /var/log/callaiag/callaiag.log

# Admin script
./admin.sh logs
```

### Run Examples

```bash
# Complete system demo
python3 examples/complete_demo.py

# Asterisk integration demo
python3 examples/asterisk_demo.py
```

### Update the System

```bash
# Using admin script
./admin.sh update

# Manual update
git pull
pip install -r requirements.txt --upgrade
python3 run.py init
sudo systemctl restart callaiag
```

## Troubleshooting

### Service won't start?

```bash
# Check logs
./admin.sh logs

# Validate configuration
python3 run.py validate

# Check permissions
sudo chown -R callaiag:callaiag /opt/callaiag
```

### Can't access dashboard?

```bash
# Check firewall
sudo ufw allow 8080/tcp

# Verify service is running
./admin.sh status

# Check what's listening on port 8080
sudo netstat -tlnp | grep 8080
```

### Asterisk connection fails?

```bash
# Check Asterisk is running
sudo systemctl status asterisk

# Test AMI connection
telnet localhost 5038

# Reload Asterisk configuration
sudo asterisk -rx "manager reload"
```

## Documentation

For detailed information, see:

- **[COMPLETE_INSTALLATION_GUIDE.md](COMPLETE_INSTALLATION_GUIDE.md)** - Comprehensive A-Z installation guide
- **[INSTALL.md](INSTALL.md)** - Installation methods and options
- **[API.md](API.md)** - API reference and code examples
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development and contribution guide

## Need Help?

1. Check the logs: `./admin.sh logs`
2. Run validation: `python3 run.py validate`
3. Review documentation in `docs/` directory
4. Check GitHub issues: https://github.com/Pormetrixx/Callaiag/issues

## Essential Commands Reference

```bash
# Installation
sudo bash install.sh                          # Automated installation
python3 run.py init                           # Initialize system
python3 run.py validate                       # Validate setup

# Service Management
./admin.sh start                              # Start service
./admin.sh stop                               # Stop service
./admin.sh restart                            # Restart service
./admin.sh status                             # Check status
./admin.sh logs                               # View logs

# System Commands
python3 run.py start                          # Start agent directly
make help                                     # Show available make commands
make init                                     # Initialize with make
make validate                                 # Validate with make

# Docker
docker-compose up -d                          # Start containers
docker-compose down                           # Stop containers
docker-compose logs -f                        # View logs
docker-compose ps                             # Check status
```

## Security Checklist

Before going to production:

- [ ] Change dashboard admin password
- [ ] Update Asterisk AMI password
- [ ] Configure firewall rules
- [ ] Enable HTTPS for dashboard
- [ ] Set up regular backups
- [ ] Review and restrict file permissions
- [ ] Update all packages to latest versions

---

**Ready to dive deeper?** Check out the [Complete Installation Guide](COMPLETE_INSTALLATION_GUIDE.md) for comprehensive instructions!
