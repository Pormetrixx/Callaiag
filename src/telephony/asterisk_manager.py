#!/usr/bin/env python3
"""
Asterisk Manager Interface (AMI) integration for Callaiag
Handles call control and event handling
"""

import logging
import socket
import threading
import time
from typing import Dict, Any, Callable, List, Optional

logger = logging.getLogger(__name__)

class AsteriskManager:
    """Asterisk Manager Interface (AMI) integration for Callaiag"""
    
    def __init__(self, config):
        """
        Initialize the Asterisk Manager
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.host = config.get('asterisk', 'host', default='localhost')
        self.port = config.get('asterisk', 'port', default=5038)
        self.username = config.get('asterisk', 'username', default='callaiag')
        self.password = config.get('asterisk', 'password', default='change_me')
        self.context = config.get('asterisk', 'context', default='outbound')
        self.extension = config.get('asterisk', 'extension', default='s')
        self.priority = config.get('asterisk', 'priority', default=1)
        self.channel_type = config.get('asterisk', 'channel_type', default='SIP')
        self.caller_id = config.get('asterisk', 'caller_id', default='Callaiag <1000>')
        self.trunk = config.get('asterisk', 'trunk', default='trunk')
        
        self.socket = None
        self.running = False
        self.event_thread = None
        self.last_action_id = 0
        self.pending_actions = {}
        self.event_handlers = {}
        self.call_status = {}  # Track call status by channel
        
    def connect(self):
        """Connect to the Asterisk Manager Interface"""
        logger.info(f"Connecting to Asterisk Manager Interface at {self.host}:{self.port}")
        
        try:
            # Create socket connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Login to AMI
            login_response = self._send_action({
                'Action': 'Login',
                'Username': self.username,
                'Secret': self.password
            })
            
            if login_response.get('Response') != 'Success':
                raise RuntimeError(f"Failed to login to Asterisk: {login_response.get('Message', 'Unknown error')}")
            
            # Start event handling thread
            self.running = True
            self.event_thread = threading.Thread(target=self._event_loop, daemon=True)
            self.event_thread.start()
            
            logger.info("Successfully connected to Asterisk Manager Interface")
            
        except Exception as e:
            logger.error(f"Error connecting to Asterisk: {e}", exc_info=True)
            self.disconnect()
            raise
    
    def disconnect(self):
        """Disconnect from the Asterisk Manager Interface"""
        logger.info("Disconnecting from Asterisk Manager Interface")
        
        self.running = False
        
        if self.socket:
            try:
                # Try to logout gracefully
                self._send_action({
                    'Action': 'Logoff'
                })
            except:
                pass
                
            try:
                self.socket.close()
            except:
                pass
                
            self.socket = None
            
        if self.event_thread and self.event_thread.is_alive():
            self.event_thread.join(timeout=1.0)
            
        logger.info("Disconnected from Asterisk Manager Interface")
        
    def register_event_handler(self, event_type: str, callback: Callable):
        """Register a callback function for a specific Asterisk event"""
        
        Args:
            event_type: The type of event to listen for (e.g., 'Hangup', 'NewChannel')
            callback: Function to call when this event occurs
        """
        logger.debug(f"Registering handler for event: {event_type}")
        
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(callback)
        
    def originate_call(self, number: str, variables: Optional[Dict[str, str]] = None) -> str:
        """Originate a call to a phone number"""
        
        Args:
            number: Phone number to call
            variables: Optional variables to set on the channel
            
        Returns:
            Unique ID of the originated call
        """
        logger.info(f"Originating call to {number}")
        
        if not self.socket:
            raise RuntimeError("Not connected to Asterisk")
            
        # Prepare channel string based on configuration
        if self.channel_type == 'SIP':
            channel = f"SIP/{self.trunk}/{number}"
        elif self.channel_type == 'PJSIP':
            channel = f"PJSIP/{number}@{self.trunk}"
        elif self.channel_type == 'IAX2':
            channel = f"IAX2/{self.trunk}/{number}"
        else:
            channel = f"{self.channel_type}/{number}"
            
        # Prepare action data
        action_data = {
            'Action': 'Originate',
            'Channel': channel,
            'Context': self.context,
            'Exten': self.extension,
            'Priority': self.priority,
            'CallerID': self.caller_id,
            'Async': 'true',
        }
        
        # Add variables if provided
        if variables:
            var_strings = [f"{key}={value}" for key, value in variables.items()]
            action_data['Variable'] = ','.join(var_strings)
        
        # Send action to Asterisk
        response = self._send_action(action_data)
        
        if response.get('Response') != 'Success':
            error_msg = response.get('Message', 'Unknown error')
            logger.error(f"Failed to originate call: {error_msg}")
            raise RuntimeError(f"Failed to originate call: {error_msg}")
            
        # Return unique ID from response
        unique_id = response.get('Uniqueid', '')
        logger.info(f"Call originated with ID: {unique_id}")
        
        # Initialize call status tracking
        self.call_status[unique_id] = {
            'status': 'dialing',
            'number': number,
            'start_time': time.time(),
            'channel': None
        }
        
        return unique_id
        
    def get_call_status(self, unique_id: str) -> Dict[str, Any]:
        """Get the status of a call"""
        
        Args:
            unique_id: Unique ID of the call
            
        Returns:
            Dictionary with call status information
        """
        return self.call_status.get(unique_id, {'status': 'unknown'})
        
    def hangup_call(self, channel: str) -> bool:
        """Hangup a specific channel"""
        
        Args:
            channel: Channel to hangup
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Hanging up channel: {channel}")
        
        try:
            response = self._send_action({
                'Action': 'Hangup',
                'Channel': channel
            })
            
            success = response.get('Response') == 'Success'
            if not success:
                logger.warning(f"Failed to hangup: {response.get('Message', 'Unknown error')}")
                
            return success
                
        except Exception as e:
            logger.error(f"Error hanging up call: {e}")
            return False
    
    def _send_action(self, action_data: Dict[str, Any]) -> Dict[str, str]:
        """Send an action to Asterisk and wait for a response"""
        
        Args:
            action_data: Dictionary of action parameters
            
        Returns:
            Response from Asterisk as a dictionary
        """
        if not self.socket:
            raise RuntimeError("Not connected to Asterisk")
            
        # Generate action ID
        self.last_action_id += 1
        action_id = f"callaiag-{self.last_action_id}"
        action_data['ActionID'] = action_id
        
        # Create future for response
        response_event = threading.Event()
        self.pending_actions[action_id] = {
            'event': response_event,
            'response': None
        }
        
        # Convert action to AMI format
        action_str = '\r\n'.join([f"{key}: {value}" for key, value in action_data.items()])
        action_str += '\r\n\r\n'
        
        # Send action
        self.socket.sendall(action_str.encode('utf-8'))
        
        # Wait for response
        if not response_event.wait(timeout=10.0):
            del self.pending_actions[action_id]
            raise TimeoutError("Timed out waiting for Asterisk response")
            
        # Get response
        response = self.pending_actions[action_id]['response']
        del self.pending_actions[action_id]
        
        return response
        
    def _event_loop(self):
        """Background thread for processing events from Asterisk"""
        logger.debug("Starting Asterisk event processing loop")
        
        buffer = ""
        
        while self.running:
            try:
                # Wait for data with timeout
                self.socket.settimeout(0.5)
                data = self.socket.recv(4096).decode('utf-8', errors='replace')
                
                if not data:
                    logger.warning("Empty data received from Asterisk, connection may be closed")
                    time.sleep(0.1)
                    continue
                    
                # Add to buffer and process complete messages
                buffer += data
                
                # Process complete messages (separated by double newlines)
                while '\r\n\r\n' in buffer:
                    message, buffer = buffer.split('\r\n\r\n', 1)
                    self._process_message(message)
                    
            except socket.timeout:
                # Normal timeout, just continue
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error in Asterisk event loop: {e}", exc_info=True)
                    time.sleep(1.0)
                
        logger.debug("Asterisk event processing loop ended")
        
    def _process_message(self, message: str):
        """Process a message received from Asterisk"""
        
        Args:
            message: Raw message string from Asterisk
        """
        # Parse message into a dictionary
        lines = message.strip().split('\r\n')
        message_dict = {}
        
        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                message_dict[key] = value
                
        # Check if it's a response to a pending action
        action_id = message_dict.get('ActionID', '')
        if action_id in self.pending_actions:
            self.pending_actions[action_id]['response'] = message_dict
            self.pending_actions[action_id]['event'].set()
            return
            
        # Handle events
        event_type = message_dict.get('Event')
        if event_type:
            self._handle_event(event_type, message_dict)
            
    def _handle_event(self, event_type: str, event_data: Dict[str, str]):
        """Handle an event from Asterisk"""
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
        """
        logger.debug(f"Received Asterisk event: {event_type}")
        
        # Update call status based on events
        self._update_call_status(event_type, event_data)
        
        # Call registered handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)
                
    def _update_call_status(self, event_type: str, event_data: Dict[str, str]):
        """Update internal call status tracking based on events"""
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
        """
        unique_id = event_data.get('Uniqueid')
        
        if not unique_id:
            return
            
        # Initialize status tracking for this call if not exists
        if unique_id not in self.call_status:
            self.call_status[unique_id] = {
                'status': 'unknown',
                'channel': event_data.get('Channel'),
                'start_time': time.time()
            }
            
        # Update channel information
        channel = event_data.get('Channel')
        if channel:
            self.call_status[unique_id]['channel'] = channel
            
        # Update status based on event type
        if event_type == 'Newchannel':
            self.call_status[unique_id]['status'] = 'new'
        elif event_type == 'Dial':
            self.call_status[unique_id]['status'] = 'dialing'
        elif event_type == 'DialBegin':
            self.call_status[unique_id]['status'] = 'dialing'
        elif event_type == 'DialEnd':
            dial_status = event_data.get('DialStatus')
            if dial_status == 'ANSWER':
                self.call_status[unique_id]['status'] = 'answered'
                self.call_status[unique_id]['answer_time'] = time.time()
            elif dial_status in ('BUSY', 'CONGESTION'):
                self.call_status[unique_id]['status'] = 'busy'
            elif dial_status == 'NOANSWER':
                self.call_status[unique_id]['status'] = 'noanswer'
            elif dial_status == 'CANCEL':
                self.call_status[unique_id]['status'] = 'cancelled'
        elif event_type == 'Bridge':
            self.call_status[unique_id]['status'] = 'bridged'
            self.call_status[unique_id]['bridged_to'] = event_data.get('SecondUniqueID')
        elif event_type == 'Hangup':
            self.call_status[unique_id]['status'] = 'hangup'
            self.call_status[unique_id]['hangup_cause'] = event_data.get('Cause')
            self.call_status[unique_id]['hangup_time'] = time.time()
            self.call_status[unique_id]['duration'] = (
                time.time() - self.call_status[unique_id].get('start_time', time.time())
            )
