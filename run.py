#!/usr/bin/env python3

import sys
import logging
from callaiag.core import CallaiagSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run.py [init|validate|start]")
        sys.exit(1)

    command = sys.argv[1]
    system = CallaiagSystem()

    commands = {
        'init': system.initialize,
        'validate': system.validate,
        'start': system.start
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print("Available commands: init, validate, start")
        sys.exit(1)

    try:
        commands[command]()
    except Exception as e:
        logger.error(f"Error executing {command}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()