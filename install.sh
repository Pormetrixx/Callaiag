#!/bin/bash

################################################################################
# Callaiag AI Agent - Automated Installation Script
# 
# This script automates the complete installation of the Callaiag system
# including all dependencies, services, and configuration.
#
# Tested on: Ubuntu Server 22.04 LTS
# Usage: sudo bash install.sh
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation configuration
INSTALL_DIR="/opt/callaiag"
VENV_DIR="/opt/callaiag/venv"
CONFIG_DIR="/etc/callaiag"
DATA_DIR="/var/lib/callaiag"
LOG_DIR="/var/log/callaiag"
SERVICE_USER="callaiag"
SERVICE_GROUP="callaiag"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Print banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       Callaiag AI Agent - Automated Installation         ║"
echo "║                   Version 0.1.0                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print status messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    print_status "Detecting operating system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        print_success "Detected: $PRETTY_NAME"
    else
        print_error "Cannot detect operating system"
        exit 1
    fi
    
    if [ "$OS" != "ubuntu" ] && [ "$OS" != "debian" ]; then
        print_warning "This script is optimized for Ubuntu/Debian. Other distributions may require manual adjustments."
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    apt-get update -qq
    apt-get upgrade -y -qq
    print_success "System packages updated"
}

# Install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        build-essential \
        ffmpeg \
        libsndfile1 \
        portaudio19-dev \
        libasound2-dev \
        libffi-dev \
        libssl-dev \
        sqlite3 \
        curl \
        wget \
        sudo \
        > /dev/null
    
    print_success "System dependencies installed"
}

# Install Asterisk (optional)
install_asterisk() {
    print_status "Checking for Asterisk installation..."
    
    if command_exists asterisk; then
        print_success "Asterisk already installed"
        return 0
    fi
    
    read -p "Install Asterisk PBX? (y/n) [recommended: y]: " install_ast
    
    if [[ $install_ast == "y" || $install_ast == "Y" ]]; then
        print_status "Installing Asterisk..."
        apt-get install -y -qq asterisk > /dev/null
        
        # Enable and start Asterisk
        systemctl enable asterisk > /dev/null 2>&1
        systemctl start asterisk
        
        print_success "Asterisk installed and started"
        
        # Configure AMI
        configure_asterisk_ami
    else
        print_warning "Skipping Asterisk installation"
    fi
}

# Configure Asterisk AMI
configure_asterisk_ami() {
    print_status "Configuring Asterisk Manager Interface..."
    
    AMI_CONF="/etc/asterisk/manager.conf"
    
    if [ ! -f "$AMI_CONF.backup" ]; then
        cp "$AMI_CONF" "$AMI_CONF.backup"
    fi
    
    # Add AMI user configuration
    cat >> "$AMI_CONF" << 'EOF'

[callaiag]
secret = callaiag123
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.0
read = system,call,log,verbose,command,agent,user,config
write = system,call,log,verbose,command,agent,user,config
EOF
    
    # Configure basic dialplan
    EXTENSIONS_CONF="/etc/asterisk/extensions.conf"
    
    if ! grep -q "\[outbound\]" "$EXTENSIONS_CONF"; then
        cat >> "$EXTENSIONS_CONF" << 'EOF'

[outbound]
exten => s,1,Answer()
exten => s,n,Wait(1)
exten => s,n,Playback(hello-world)
exten => s,n,Hangup()
EOF
    fi
    
    # Reload Asterisk configuration
    asterisk -rx "manager reload" > /dev/null 2>&1
    asterisk -rx "dialplan reload" > /dev/null 2>&1
    
    print_success "Asterisk AMI configured"
}

# Create service user and directories
create_user_and_directories() {
    print_status "Creating service user and directories..."
    
    # Create user if it doesn't exist
    if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
        useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
        print_success "Created user: $SERVICE_USER"
    else
        print_success "User $SERVICE_USER already exists"
    fi
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOG_DIR"
    
    print_success "Directories created"
}

# Copy application files
copy_application_files() {
    print_status "Copying application files..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Copy files to installation directory
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$DATA_DIR"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
    
    print_success "Application files copied"
}

# Create Python virtual environment
create_virtualenv() {
    print_status "Creating Python virtual environment..."
    
    # Create virtual environment as the service user
    sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"
    
    # Upgrade pip
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip > /dev/null
    
    print_success "Virtual environment created"
}

# Install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies (this may take a while)..."
    
    # Install requirements
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt" > /dev/null 2>&1
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping Python dependencies"
    fi
}

# Initialize configuration
initialize_configuration() {
    print_status "Initializing configuration..."
    
    # Copy default configuration if it doesn't exist
    if [ -f "$INSTALL_DIR/config/default_config.yml" ] && [ ! -f "$CONFIG_DIR/config.yml" ]; then
        cp "$INSTALL_DIR/config/default_config.yml" "$CONFIG_DIR/config.yml"
        
        # Update configuration with correct paths
        sed -i "s|./data/callaiag.db|$DATA_DIR/callaiag.db|g" "$CONFIG_DIR/config.yml"
        sed -i "s|./temp|$DATA_DIR/temp|g" "$CONFIG_DIR/config.yml"
        sed -i "s|./scripts|$DATA_DIR/scripts|g" "$CONFIG_DIR/config.yml"
        sed -i "s|./faqs|$DATA_DIR/faqs|g" "$CONFIG_DIR/config.yml"
        sed -i "s|./models|$DATA_DIR/models|g" "$CONFIG_DIR/config.yml"
        
        chown "$SERVICE_USER:$SERVICE_GROUP" "$CONFIG_DIR/config.yml"
        chmod 640 "$CONFIG_DIR/config.yml"
        
        print_success "Configuration initialized"
    else
        print_success "Configuration already exists"
    fi
    
    # Create required subdirectories
    sudo -u "$SERVICE_USER" mkdir -p "$DATA_DIR"/{temp,scripts,faqs,models,logs}
}

# Initialize database
initialize_database() {
    print_status "Initializing database..."
    
    # Run initialization
    cd "$INSTALL_DIR"
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/python3" run.py init > /dev/null 2>&1 || true
    
    print_success "Database initialized"
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/callaiag.service << EOF
[Unit]
Description=Callaiag AI Agent
After=network.target asterisk.service
Wants=asterisk.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_DIR/bin/python3 $INSTALL_DIR/run.py start
Restart=on-failure
RestartSec=10
StandardOutput=append:$LOG_DIR/callaiag.log
StandardError=append:$LOG_DIR/callaiag-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    systemctl enable callaiag > /dev/null 2>&1
    
    print_success "Systemd service created"
}

# Configure firewall (optional)
configure_firewall() {
    if command_exists ufw; then
        print_status "Configuring firewall..."
        
        # Allow dashboard port
        ufw allow 8080/tcp > /dev/null 2>&1
        
        # Allow Asterisk AMI port (only from localhost)
        ufw allow from 127.0.0.1 to any port 5038 > /dev/null 2>&1
        
        print_success "Firewall configured"
    fi
}

# Print final instructions
print_final_instructions() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Installation completed successfully!             ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Installation Summary:${NC}"
    echo "  • Installation directory: $INSTALL_DIR"
    echo "  • Configuration directory: $CONFIG_DIR"
    echo "  • Data directory: $DATA_DIR"
    echo "  • Log directory: $LOG_DIR"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Edit configuration: sudo nano $CONFIG_DIR/config.yml"
    echo "  2. Validate setup: sudo -u $SERVICE_USER $VENV_DIR/bin/python3 $INSTALL_DIR/run.py validate"
    echo "  3. Start service: sudo systemctl start callaiag"
    echo "  4. Check status: sudo systemctl status callaiag"
    echo "  5. View logs: sudo tail -f $LOG_DIR/callaiag.log"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "  • Start:   sudo systemctl start callaiag"
    echo "  • Stop:    sudo systemctl stop callaiag"
    echo "  • Restart: sudo systemctl restart callaiag"
    echo "  • Status:  sudo systemctl status callaiag"
    echo "  • Logs:    sudo journalctl -u callaiag -f"
    echo ""
    echo -e "${BLUE}Web Dashboard:${NC}"
    echo "  • URL: http://$(hostname -I | awk '{print $1}'):8080"
    echo "  • Default credentials: admin / admin123"
    echo "  • ${YELLOW}IMPORTANT: Change the default password!${NC}"
    echo ""
    
    if command_exists asterisk; then
        echo -e "${BLUE}Asterisk Configuration:${NC}"
        echo "  • AMI Port: 5038"
        echo "  • AMI User: callaiag"
        echo "  • AMI Password: callaiag123 (change in $CONFIG_DIR/config.yml)"
        echo ""
    fi
    
    echo -e "${YELLOW}Security Recommendations:${NC}"
    echo "  • Change default passwords in $CONFIG_DIR/config.yml"
    echo "  • Configure firewall rules for production use"
    echo "  • Review and adjust Asterisk security settings"
    echo "  • Enable HTTPS for the web dashboard"
    echo ""
}

# Main installation flow
main() {
    detect_os
    update_system
    install_system_dependencies
    install_asterisk
    create_user_and_directories
    copy_application_files
    create_virtualenv
    install_python_dependencies
    initialize_configuration
    initialize_database
    create_systemd_service
    configure_firewall
    print_final_instructions
}

# Run main installation
main
