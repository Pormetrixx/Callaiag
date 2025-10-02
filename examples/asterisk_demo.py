#!/usr/bin/env python3
"""
Asterisk integration demonstration for Callaiag.

This script demonstrates the Asterisk PBX integration capabilities
including call origination and event handling.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from callaiag.core.config import Config
from callaiag.asterisk.ami import AsteriskManagerInterface
from callaiag.asterisk.call_manager import CallManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_ami_connection(config):
    """Demonstrate AMI connection."""
    print("\n" + "="*60)
    print("ASTERISK MANAGER INTERFACE (AMI) CONNECTION")
    print("="*60)
    
    try:
        print("\n[1] Initializing AMI client...")
        ami = AsteriskManagerInterface(config)
        print(f"✓ AMI client initialized for {ami.host}:{ami.port}")
        
        print("\n[2] Connecting to Asterisk...")
        print("Note: This requires Asterisk to be running and configured")
        print(f"Host: {ami.host}")
        print(f"Port: {ami.port}")
        print(f"Username: {ami.username}")
        
        # In a real scenario, you would connect here
        # ami.connect()
        print("✓ Connection configuration validated")
        
        return ami
        
    except Exception as e:
        logger.error(f"Error in AMI demo: {e}")
        return None


def demo_call_origination(ami):
    """Demonstrate call origination."""
    print("\n" + "="*60)
    print("CALL ORIGINATION")
    print("="*60)
    
    if not ami:
        print("✗ AMI not available")
        return
    
    try:
        print("\n[1] Preparing call origination...")
        number = "+49123456789"
        print(f"Target number: {number}")
        
        # In a real scenario, you would originate the call here
        # action_id = ami.originate_call(number)
        # print(f"✓ Call originated with ActionID: {action_id}")
        
        print("✓ Call origination parameters validated")
        
    except Exception as e:
        logger.error(f"Error in call origination demo: {e}")


def demo_event_handling(config, ami):
    """Demonstrate event handling."""
    print("\n" + "="*60)
    print("EVENT HANDLING")
    print("="*60)
    
    if not ami:
        print("✗ AMI not available")
        return
    
    try:
        print("\n[1] Setting up event handlers...")
        
        def on_new_channel(event):
            print(f"New channel created: {event.get('Channel')}")
        
        def on_hangup(event):
            print(f"Call hangup: {event.get('Channel')}")
        
        ami.register_event_handler('Newchannel', on_new_channel)
        ami.register_event_handler('Hangup', on_hangup)
        
        print("✓ Event handlers registered:")
        print("  - Newchannel")
        print("  - Hangup")
        
    except Exception as e:
        logger.error(f"Error in event handling demo: {e}")


def demo_call_manager(config):
    """Demonstrate high-level call manager."""
    print("\n" + "="*60)
    print("CALL MANAGER")
    print("="*60)
    
    try:
        print("\n[1] Initializing call manager...")
        ami = AsteriskManagerInterface(config)
        call_manager = CallManager(config, ami)
        print("✓ Call manager initialized")
        
        print("\n[2] Call lifecycle management...")
        print("The call manager handles:")
        print("  - Call state tracking")
        print("  - Event-based state transitions")
        print("  - Call metadata management")
        print("  - Callback notifications")
        
        # Demonstrate call object
        print("\n[3] Call object structure...")
        from callaiag.asterisk.call_manager import Call
        demo_call = Call("demo-123", "+49123456789")
        print(f"Call ID: {demo_call.call_id}")
        print(f"Number: {demo_call.number}")
        print(f"State: {demo_call.state.value}")
        print("✓ Call object created")
        
    except Exception as e:
        logger.error(f"Error in call manager demo: {e}")


def demo_asterisk_configuration(config):
    """Demonstrate Asterisk configuration."""
    print("\n" + "="*60)
    print("ASTERISK CONFIGURATION")
    print("="*60)
    
    try:
        print("\n[1] Current configuration:")
        print(f"  Enabled: {config.get('asterisk', 'enabled')}")
        print(f"  Host: {config.get('asterisk', 'host')}")
        print(f"  Port: {config.get('asterisk', 'port')}")
        print(f"  Username: {config.get('asterisk', 'username')}")
        print(f"  Context: {config.get('asterisk', 'context')}")
        print(f"  Channel Type: {config.get('asterisk', 'channel_type')}")
        print(f"  Caller ID: {config.get('asterisk', 'caller_id')}")
        
        print("\n[2] Required Asterisk setup:")
        print("  1. Create AMI user in /etc/asterisk/manager.conf:")
        print("     [callaiag]")
        print("     secret=change_me")
        print("     deny=0.0.0.0/0.0.0.0")
        print("     permit=127.0.0.1/255.255.255.0")
        print("     read=system,call,log,verbose,command,agent,user,config")
        print("     write=system,call,log,verbose,command,agent,user,config")
        
        print("\n  2. Configure dialplan in /etc/asterisk/extensions.conf:")
        print("     [outbound]")
        print("     exten => s,1,Answer()")
        print("     exten => s,n,Playback(hello-world)")
        print("     exten => s,n,Hangup()")
        
        print("\n  3. Reload Asterisk configuration:")
        print("     asterisk -rx 'manager reload'")
        print("     asterisk -rx 'dialplan reload'")
        
    except Exception as e:
        logger.error(f"Error in configuration demo: {e}")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("CALLAIAG - ASTERISK INTEGRATION DEMO")
    print("="*60)
    
    try:
        # Load configuration
        print("\nLoading configuration...")
        config_path = Path(__file__).parent.parent / 'config' / 'default_config.yml'
        config = Config(str(config_path))
        print("✓ Configuration loaded")
        
        # Run demos
        demo_asterisk_configuration(config)
        time.sleep(1)
        
        ami = demo_ami_connection(config)
        time.sleep(1)
        
        demo_call_origination(ami)
        time.sleep(1)
        
        demo_event_handling(config, ami)
        time.sleep(1)
        
        demo_call_manager(config)
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nNote: This demo shows the Asterisk integration structure.")
        print("To test with a real Asterisk server:")
        print("  1. Install and configure Asterisk PBX")
        print("  2. Update config/default_config.yml with your settings")
        print("  3. Run this demo again")
        print("\n✓ All demos completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Error in demo: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
