#!/bin/bash

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./admin.sh [status|start|stop|restart]"
    exit 1
fi

case "$1" in
    status)
        echo "Checking system status..."
        ;;
    start)
        echo "Starting the system..."
        ;;
    stop)
        echo "Stopping the system..."
        ;;
    restart)
        echo "Restarting the system..."
        ;;
    *)
        echo "Invalid command. Use: status|start|stop|restart"
        exit 1
        ;;
esac
