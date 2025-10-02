#!/usr/bin/env python3
"""
Asterisk Manager Interface (AMI) module for Callaiag.

This module provides integration with Asterisk PBX through the Manager Interface
for real-time call control and event monitoring.
"""

import logging
import socket
import threading
import time
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


class AsteriskManagerInterface:
    """
    Asterisk Manager Interface (AMI) client.
    
    Provides connection to Asterisk PBX for:
    - Call origination
    - Event monitoring
    - Channel management
    - Real-time call control
    """
    
    def __init__(self, config):
        """
        Initialize AMI client.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.host = config.get('asterisk', 'host', default='localhost')
        self.port = config.get('asterisk', 'port', default=5038)
        self.username = config.get('asterisk', 'username', default='callaiag')
        self.password = config.get('asterisk', 'password', default='change_me')
        
        self.socket = None
        self.connected = False
        self.running = False
        self.event_thread = None
        self.action_id = 0
        self.pending_actions = {}
        self.event_handlers = {}
        
        logger.info(f"AMI client initialized for {self.host}:{self.port}")
    
    def connect(self):
        """
        Connect to Asterisk Manager Interface.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to AMI at {self.host}:{self.port}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Read welcome message
            welcome = self._read_response()
            logger.debug(f"AMI welcome: {welcome}")
            
            # Login
            self._send_action('Login', {
                'Username': self.username,
                'Secret': self.password
            })
            
            response = self._read_response()
            if 'Success' not in response.get('Response', ''):
                raise ConnectionError("AMI login failed")
            
            self.connected = True
            self.running = True
            
            # Start event listener thread
            self.event_thread = threading.Thread(target=self._event_listener, daemon=True)
            self.event_thread.start()
            
            logger.info("Connected to AMI successfully")
            
        except Exception as e:
            logger.error(f"Error connecting to AMI: {e}")
            self.disconnect()
            raise
    
    def disconnect(self):
        """Disconnect from AMI."""
        logger.info("Disconnecting from AMI")
        self.running = False
        self.connected = False
        
        try:
            if self.socket:
                # Send Logoff action
                self._send_action('Logoff', {})
                self.socket.close()
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        
        self.socket = None
        logger.info("Disconnected from AMI")
    
    def originate_call(self, number: str, context: Optional[str] = None,
                       extension: Optional[str] = None, caller_id: Optional[str] = None) -> str:
        """
        Originate a call through Asterisk.
        
        Args:
            number: Phone number to call
            context: Dialplan context
            extension: Dialplan extension
            caller_id: Caller ID to use
            
        Returns:
            Action ID for tracking the call
        """
        context = context or self.config.get('asterisk', 'context', default='outbound')
        extension = extension or self.config.get('asterisk', 'extension', default='s')
        caller_id = caller_id or self.config.get('asterisk', 'caller_id', default='Callaiag')
        channel_type = self.config.get('asterisk', 'channel_type', default='SIP')
        trunk = self.config.get('asterisk', 'trunk', default='trunk')
        
        channel = f"{channel_type}/{trunk}/{number}"
        
        action_id = self._send_action('Originate', {
            'Channel': channel,
            'Context': context,
            'Exten': extension,
            'Priority': '1',
            'CallerID': caller_id,
            'Timeout': '30000',
            'Async': 'true'
        })
        
        logger.info(f"Originated call to {number} (ActionID: {action_id})")
        return action_id
    
    def hangup_call(self, channel: str):
        """
        Hangup a call.
        
        Args:
            channel: Channel name to hangup
        """
        self._send_action('Hangup', {'Channel': channel})
        logger.info(f"Hangup requested for channel {channel}")
    
    def register_event_handler(self, event_type: str, callback: Callable):
        """
        Register callback for specific event type.
        
        Args:
            event_type: Asterisk event type (e.g., 'Newchannel', 'Hangup')
            callback: Callback function to handle event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(callback)
        logger.debug(f"Registered handler for event: {event_type}")
    
    def _send_action(self, action: str, params: Dict[str, str]) -> str:
        """
        Send AMI action.
        
        Args:
            action: Action name
            params: Action parameters
            
        Returns:
            Action ID
        """
        self.action_id += 1
        action_id = str(self.action_id)
        
        message = f"Action: {action}\r\n"
        message += f"ActionID: {action_id}\r\n"
        
        for key, value in params.items():
            message += f"{key}: {value}\r\n"
        
        message += "\r\n"
        
        self.socket.sendall(message.encode('utf-8'))
        return action_id
    
    def _read_response(self) -> Dict[str, str]:
        """
        Read AMI response.
        
        Returns:
            Dictionary with response data
        """
        response = {}
        buffer = ""
        
        while True:
            data = self.socket.recv(4096).decode('utf-8')
            if not data:
                break
            
            buffer += data
            
            if "\r\n\r\n" in buffer:
                lines = buffer.split("\r\n")
                for line in lines:
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        response[key] = value
                break
        
        return response
    
    def _event_listener(self):
        """Background thread for listening to AMI events."""
        logger.info("AMI event listener started")
        
        while self.running and self.connected:
            try:
                event = self._read_response()
                
                if not event:
                    time.sleep(0.1)
                    continue
                
                event_type = event.get('Event')
                if event_type and event_type in self.event_handlers:
                    for handler in self.event_handlers[event_type]:
                        try:
                            handler(event)
                        except Exception as e:
                            logger.error(f"Error in event handler: {e}")
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error in event listener: {e}")
                break
        
        logger.info("AMI event listener stopped")
    
    def get_channel_status(self, channel: str) -> Dict[str, Any]:
        """
        Get status of a channel.
        
        Args:
            channel: Channel name
            
        Returns:
            Dictionary with channel status
        """
        action_id = self._send_action('Status', {'Channel': channel})
        # Would need to wait for response in real implementation
        return {'action_id': action_id}
    
    def is_connected(self) -> bool:
        """Check if connected to AMI."""
        return self.connected
