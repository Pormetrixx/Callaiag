#!/usr/bin/env python3
"""
Call manager module for Callaiag.

This module provides high-level call management functionality built on top
of the Asterisk Manager Interface.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class CallState(Enum):
    """Call state enumeration."""
    IDLE = "idle"
    DIALING = "dialing"
    RINGING = "ringing"
    CONNECTED = "connected"
    TALKING = "talking"
    HANGUP = "hangup"
    FAILED = "failed"


class Call:
    """
    Represents a single call session.
    """
    
    def __init__(self, call_id: str, number: str):
        """
        Initialize call object.
        
        Args:
            call_id: Unique call identifier
            number: Phone number
        """
        self.call_id = call_id
        self.number = number
        self.state = CallState.IDLE
        self.channel = None
        self.start_time = None
        self.answer_time = None
        self.end_time = None
        self.duration = 0
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert call to dictionary."""
        return {
            'call_id': self.call_id,
            'number': self.number,
            'state': self.state.value,
            'channel': self.channel,
            'start_time': self.start_time,
            'answer_time': self.answer_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'metadata': self.metadata
        }


class CallManager:
    """
    High-level call management for Callaiag.
    
    Manages call lifecycle, state tracking, and provides simplified
    interface for call operations.
    """
    
    def __init__(self, config, ami):
        """
        Initialize call manager.
        
        Args:
            config: Configuration object
            ami: AsteriskManagerInterface instance
        """
        self.config = config
        self.ami = ami
        self.active_calls = {}
        self.call_callbacks = {}
        
        # Register AMI event handlers
        self._register_handlers()
        
        logger.info("Call manager initialized")
    
    def _register_handlers(self):
        """Register AMI event handlers."""
        self.ami.register_event_handler('Newchannel', self._handle_new_channel)
        self.ami.register_event_handler('Newstate', self._handle_state_change)
        self.ami.register_event_handler('Hangup', self._handle_hangup)
    
    def make_call(self, number: str, context: Optional[str] = None,
                  callback: Optional[Callable] = None) -> str:
        """
        Initiate a new call.
        
        Args:
            number: Phone number to call
            context: Optional Asterisk context
            callback: Optional callback for call events
            
        Returns:
            Call ID
        """
        try:
            # Originate call through AMI
            action_id = self.ami.originate_call(number, context)
            
            # Create call object
            call = Call(action_id, number)
            call.state = CallState.DIALING
            call.start_time = time.time()
            
            # Store call
            self.active_calls[action_id] = call
            
            if callback:
                self.call_callbacks[action_id] = callback
            
            logger.info(f"Call initiated: {action_id} -> {number}")
            return action_id
            
        except Exception as e:
            logger.error(f"Error making call to {number}: {e}")
            raise
    
    def hangup_call(self, call_id: str):
        """
        Hangup a call.
        
        Args:
            call_id: Call identifier
        """
        try:
            call = self.active_calls.get(call_id)
            if not call:
                logger.warning(f"Call {call_id} not found")
                return
            
            if call.channel:
                self.ami.hangup_call(call.channel)
            
            call.state = CallState.HANGUP
            call.end_time = time.time()
            
            if call.start_time:
                call.duration = call.end_time - call.start_time
            
            logger.info(f"Call hangup: {call_id}")
            
        except Exception as e:
            logger.error(f"Error hanging up call {call_id}: {e}")
    
    def get_call(self, call_id: str) -> Optional[Call]:
        """
        Get call by ID.
        
        Args:
            call_id: Call identifier
            
        Returns:
            Call object or None
        """
        return self.active_calls.get(call_id)
    
    def get_active_calls(self) -> Dict[str, Call]:
        """
        Get all active calls.
        
        Returns:
            Dictionary of active calls
        """
        return {
            cid: call for cid, call in self.active_calls.items()
            if call.state not in [CallState.HANGUP, CallState.FAILED]
        }
    
    def _handle_new_channel(self, event: Dict[str, str]):
        """
        Handle Newchannel AMI event.
        
        Args:
            event: AMI event data
        """
        try:
            channel = event.get('Channel')
            action_id = event.get('ActionID')
            
            if action_id in self.active_calls:
                call = self.active_calls[action_id]
                call.channel = channel
                logger.debug(f"Channel created for call {action_id}: {channel}")
                
                self._notify_callback(action_id, 'channel_created', event)
                
        except Exception as e:
            logger.error(f"Error handling Newchannel event: {e}")
    
    def _handle_state_change(self, event: Dict[str, str]):
        """
        Handle Newstate AMI event.
        
        Args:
            event: AMI event data
        """
        try:
            channel = event.get('Channel')
            channel_state = event.get('ChannelStateDesc', '').lower()
            
            # Find call by channel
            call = None
            for c in self.active_calls.values():
                if c.channel == channel:
                    call = c
                    break
            
            if not call:
                return
            
            # Update call state
            if 'ringing' in channel_state:
                call.state = CallState.RINGING
                self._notify_callback(call.call_id, 'ringing', event)
            elif 'up' in channel_state:
                call.state = CallState.CONNECTED
                call.answer_time = time.time()
                self._notify_callback(call.call_id, 'answered', event)
            
            logger.debug(f"Call {call.call_id} state: {call.state.value}")
            
        except Exception as e:
            logger.error(f"Error handling Newstate event: {e}")
    
    def _handle_hangup(self, event: Dict[str, str]):
        """
        Handle Hangup AMI event.
        
        Args:
            event: AMI event data
        """
        try:
            channel = event.get('Channel')
            cause = event.get('Cause', 'Unknown')
            
            # Find call by channel
            call = None
            call_id = None
            for cid, c in self.active_calls.items():
                if c.channel == channel:
                    call = c
                    call_id = cid
                    break
            
            if not call:
                return
            
            call.state = CallState.HANGUP
            call.end_time = time.time()
            
            if call.start_time:
                call.duration = call.end_time - call.start_time
            
            call.metadata['hangup_cause'] = cause
            
            logger.info(f"Call {call_id} ended (cause: {cause}, duration: {call.duration:.1f}s)")
            
            self._notify_callback(call_id, 'hangup', event)
            
        except Exception as e:
            logger.error(f"Error handling Hangup event: {e}")
    
    def _notify_callback(self, call_id: str, event_type: str, event_data: Dict):
        """
        Notify callback about call event.
        
        Args:
            call_id: Call identifier
            event_type: Event type
            event_data: Event data
        """
        if call_id in self.call_callbacks:
            try:
                callback = self.call_callbacks[call_id]
                callback(call_id, event_type, event_data)
            except Exception as e:
                logger.error(f"Error in call callback: {e}")
    
    def cleanup_old_calls(self, max_age: int = 3600):
        """
        Clean up old completed calls.
        
        Args:
            max_age: Maximum age in seconds to keep calls
        """
        current_time = time.time()
        to_remove = []
        
        for call_id, call in self.active_calls.items():
            if call.state in [CallState.HANGUP, CallState.FAILED]:
                if call.end_time and (current_time - call.end_time) > max_age:
                    to_remove.append(call_id)
        
        for call_id in to_remove:
            del self.active_calls[call_id]
            if call_id in self.call_callbacks:
                del self.call_callbacks[call_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old calls")
