#!/bin/bash

################################################################################
# Callaiag AI Agent - System Administration Script
# 
# This script provides convenient management commands for the Callaiag service
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect installation type
if [ -d "/opt/callaiag" ]; then
    INSTALL_DIR="/opt/callaiag"
    VENV_BIN="/opt/callaiag/venv/bin"
    CONFIG_DIR="/etc/callaiag"
    LOG_DIR="/var/log/callaiag"
    SERVICE_NAME="callaiag"
    USE_SYSTEMD=true
else
    INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    VENV_BIN="$INSTALL_DIR/venv/bin"
    CONFIG_DIR="$INSTALL_DIR/config"
    LOG_DIR="$INSTALL_DIR/logs"
    SERVICE_NAME=""
    USE_SYSTEMD=false
fi

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./admin.sh [status|start|stop|restart|logs|validate|update]"
    exit 1
fi

# Function to check if systemd service exists
check_systemd() {
    if [ "$USE_SYSTEMD" = true ] && systemctl list-units --type=service | grep -q "$SERVICE_NAME"; then
        return 0
    else
        return 1
    fi
}

# Function to print status
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

# Command handlers
cmd_status() {
    print_status "Checking Callaiag system status..."
    echo ""
    
    if check_systemd; then
        # Systemd service status
        sudo systemctl status "$SERVICE_NAME" --no-pager
    else
        # Check for running process
        if pgrep -f "python3.*run.py start" > /dev/null; then
            print_success "Callaiag is running"
            ps aux | grep "python3.*run.py start" | grep -v grep
        else
            print_warning "Callaiag is not running"
        fi
    fi
    
    echo ""
    
    # Check Asterisk if installed
    if command -v asterisk >/dev/null 2>&1; then
        if systemctl is-active --quiet asterisk; then
            print_success "Asterisk PBX is running"
        else
            print_warning "Asterisk PBX is not running"
        fi
    fi
}

cmd_start() {
    print_status "Starting Callaiag system..."
    
    if check_systemd; then
        sudo systemctl start "$SERVICE_NAME"
        if [ $? -eq 0 ]; then
            print_success "Callaiag service started"
        else
            print_error "Failed to start Callaiag service"
            exit 1
        fi
    else
        # Start manually
        if [ ! -d "$VENV_BIN" ]; then
            print_error "Virtual environment not found. Run 'make install' first."
            exit 1
        fi
        
        cd "$INSTALL_DIR"
        nohup "$VENV_BIN/python3" run.py start > "$LOG_DIR/callaiag.log" 2>&1 &
        
        sleep 2
        if pgrep -f "python3.*run.py start" > /dev/null; then
            print_success "Callaiag started"
        else
            print_error "Failed to start Callaiag"
            exit 1
        fi
    fi
}

cmd_stop() {
    print_status "Stopping Callaiag system..."
    
    if check_systemd; then
        sudo systemctl stop "$SERVICE_NAME"
        if [ $? -eq 0 ]; then
            print_success "Callaiag service stopped"
        else
            print_error "Failed to stop Callaiag service"
            exit 1
        fi
    else
        # Stop manually
        pkill -f "python3.*run.py start"
        sleep 2
        
        if ! pgrep -f "python3.*run.py start" > /dev/null; then
            print_success "Callaiag stopped"
        else
            print_error "Failed to stop Callaiag"
            exit 1
        fi
    fi
}

cmd_restart() {
    print_status "Restarting Callaiag system..."
    
    if check_systemd; then
        sudo systemctl restart "$SERVICE_NAME"
        if [ $? -eq 0 ]; then
            print_success "Callaiag service restarted"
        else
            print_error "Failed to restart Callaiag service"
            exit 1
        fi
    else
        cmd_stop
        sleep 2
        cmd_start
    fi
}

cmd_logs() {
    print_status "Showing Callaiag logs (Ctrl+C to exit)..."
    echo ""
    
    if check_systemd; then
        sudo journalctl -u "$SERVICE_NAME" -f
    else
        if [ -f "$LOG_DIR/callaiag.log" ]; then
            tail -f "$LOG_DIR/callaiag.log"
        else
            print_error "Log file not found: $LOG_DIR/callaiag.log"
            exit 1
        fi
    fi
}

cmd_validate() {
    print_status "Validating Callaiag setup..."
    echo ""
    
    cd "$INSTALL_DIR"
    
    if [ -f "$VENV_BIN/python3" ]; then
        "$VENV_BIN/python3" run.py validate
    else
        python3 run.py validate
    fi
}

cmd_update() {
    print_status "Updating Callaiag system..."
    
    # Stop service
    cmd_stop
    
    # Pull latest changes
    cd "$INSTALL_DIR"
    print_status "Pulling latest changes..."
    git pull
    
    # Update dependencies
    print_status "Updating dependencies..."
    if [ -f "$VENV_BIN/pip" ]; then
        "$VENV_BIN/pip" install -r requirements.txt --upgrade
    else
        pip3 install -r requirements.txt --upgrade
    fi
    
    # Run any migrations
    print_status "Running migrations..."
    if [ -f "$VENV_BIN/python3" ]; then
        "$VENV_BIN/python3" run.py init
    else
        python3 run.py init
    fi
    
    # Start service
    cmd_start
    
    print_success "Update completed"
}

# Main command dispatcher
case "$1" in
    status)
        cmd_status
        ;;
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    logs)
        cmd_logs
        ;;
    validate)
        cmd_validate
        ;;
    update)
        cmd_update
        ;;
    *)
        echo "Invalid command. Use: status|start|stop|restart|logs|validate|update"
        exit 1
        ;;
esac
