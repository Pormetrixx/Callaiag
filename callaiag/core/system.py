"""
Main system orchestration for Callaiag.

This module provides the main CallaiagSystem class that coordinates all components.
"""

import logging
import time
import signal
import sys
from typing import Optional
from pathlib import Path

from callaiag.core.config import Config
from callaiag.core.logging_setup import setup_logging

logger = logging.getLogger(__name__)


class CallaiagSystem:
    """
    Main system class that orchestrates all Callaiag components.
    
    This class manages the lifecycle of the entire system including:
    - Configuration management
    - Component initialization
    - Graceful shutdown
    
    Attributes:
        config: Configuration manager instance
        running: Boolean indicating if the system is running
        
    Example:
        >>> system = CallaiagSystem()
        >>> system.initialize()
        >>> system.start()
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the Callaiag system.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config: Optional[Config] = None
        self.running: bool = False
        self._config_path: Optional[str] = config_path
        self._shutdown_handlers_registered: bool = False
        
        # Set up signal handlers for graceful shutdown
        self._register_shutdown_handlers()
        
        logger.info("Callaiag System created")
    
    def _register_shutdown_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        if not self._shutdown_handlers_registered:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self._shutdown_handlers_registered = True
    
    def _signal_handler(self, signum: int, frame) -> None:
        """
        Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def initialize(self) -> None:
        """
        Initialize the system configuration.
        
        Creates a default configuration file if it doesn't exist.
        
        Raises:
            Exception: If initialization fails
        """
        try:
            logger.info("Initializing Callaiag system...")
            
            # Load or create configuration
            self.config = Config(self._config_path)
            
            # Set up logging based on configuration
            log_level = self.config.get('general', 'log_level', default='INFO')
            log_file = self.config.get('general', 'log_file', default='callaiag.log')
            log_dir = self.config.get('general', 'log_dir', default='./logs')
            
            setup_logging(level=log_level, log_file=log_file, log_dir=log_dir)
            
            # Create default config file if it doesn't exist
            if not self.config.config_path:
                config_path = self.config.create_default_config()
                logger.info(f"Created default configuration at {config_path}")
            
            logger.info("Callaiag system initialized successfully")
            print(f"✅ System initialized")
            if self.config.config_path:
                print(f"   Configuration: {self.config.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}", exc_info=True)
            raise
    
    def validate(self) -> None:
        """
        Validate the system configuration and dependencies.
        
        Checks that all required components are properly configured.
        
        Raises:
            Exception: If validation fails
        """
        try:
            logger.info("Validating Callaiag system...")
            
            # Load configuration if not already loaded
            if not self.config:
                self.config = Config(self._config_path)
            
            # Validate configuration
            self.config.validate()
            print("✅ Configuration is valid")
            
            # Check that required directories exist or can be created
            directories = [
                self.config.get('general', 'log_dir', default='./logs'),
                self.config.get('speech', 'audio', 'temp_dir', default='./temp'),
                self.config.get('conversation', 'scripts_dir', default='./scripts'),
                self.config.get('conversation', 'faqs_dir', default='./faqs'),
            ]
            
            for directory in directories:
                if directory:
                    dir_path = Path(directory)
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Verified directory: {directory}")
            
            print("✅ Required directories verified")
            
            # TODO: Validate database connection
            # TODO: Validate Asterisk connection
            # TODO: Validate speech processing
            
            logger.info("System validation completed successfully")
            print("\n✅ Validation successful! System is ready to run.")
            
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            print(f"\n❌ Validation failed: {e}")
            raise
    
    def start(self) -> None:
        """
        Start the Callaiag system.
        
        This method starts all system components and enters the main loop.
        
        Raises:
            Exception: If startup fails
        """
        try:
            logger.info("Starting Callaiag system...")
            
            # Load configuration if not already loaded
            if not self.config:
                self.config = Config(self._config_path)
                
                # Set up logging based on configuration
                log_level = self.config.get('general', 'log_level', default='INFO')
                log_file = self.config.get('general', 'log_file', default='callaiag.log')
                log_dir = self.config.get('general', 'log_dir', default='./logs')
                
                setup_logging(level=log_level, log_file=log_file, log_dir=log_dir)
            
            # TODO: Initialize speech manager
            # TODO: Initialize conversation manager
            # TODO: Initialize human simulation
            # TODO: Connect to Asterisk (if enabled)
            # TODO: Connect to database
            
            self.running = True
            logger.info("Callaiag system started successfully")
            print("✅ System started successfully")
            print("   Press Ctrl+C to stop")
            
            # Main loop
            while self.running:
                time.sleep(1)
                # TODO: Process incoming calls
                # TODO: Monitor system health
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.stop()
        except Exception as e:
            logger.error(f"Error starting system: {e}", exc_info=True)
            self.stop()
            raise
    
    def stop(self) -> None:
        """
        Stop the Callaiag system gracefully.
        
        Shuts down all components in the correct order.
        """
        if not self.running:
            return
            
        logger.info("Stopping Callaiag system...")
        self.running = False
        
        try:
            # TODO: Shutdown conversation manager
            # TODO: Shutdown speech manager
            # TODO: Disconnect from Asterisk
            # TODO: Disconnect from database
            
            logger.info("Callaiag system stopped successfully")
            print("\n✅ System stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
            print(f"\n⚠️  Error during shutdown: {e}")
