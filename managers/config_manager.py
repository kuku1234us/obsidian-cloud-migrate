# Configuration Manager Module

"""
Configuration Manager Module

This module provides centralized configuration management for the application.
It implements a singleton ConfigManager class that loads and provides access to application settings.
"""

import os
from ruamel.yaml import YAML
from dotenv import load_dotenv
from utils.logger import Logger
from PyQt6.QtGui import QFont

class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.config = {}
        self.confidential_config = {}  # Store confidential information separately
        self.app_mode = self.config.get("app_mode", "production")
        self.logger = Logger()  # Retrieve the Logger instance
        self.logger.setup_logger(self)  # Pass self as config
        
        # Initialize ruamel.yaml with proper settings
        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # Preserve quote style
        self.yaml.indent(mapping=2, sequence=4, offset=2)  # Maintain formatting
        self.yaml.width = 4096  # Prevent line wrapping
        self.yaml.preserve_comments = True  # Keep comments
        
        self._initialized = True

    def load_config(self):
        # Load .env file
        load_dotenv(override=True)

        # Load YAML configuration
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        try:
            with open(config_path, "r", encoding='utf-8') as config_file:
                self.config = self.yaml.load(config_file) or {}
        except FileNotFoundError:
            self.logger.warning(f"Config file not found at {config_path}, using defaults")
            self.config = {}

        # Add confidential information from environment variables
        self.confidential_config = {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "aws_region": os.getenv("AWS_REGION"),
        }

        # Get UI font information
        self.ui_font_family = self.config.get("ui", {}).get("font", {}).get("family", "Calibri")
        self.ui_font_size = self.config.get("ui", {}).get("font", {}).get("size", 10)

    def get(self, key, default=None):
        # First check in config, then in confidential config
        if key in self.config:
            return self.config.get(key, default)
        return self.confidential_config.get(key, default)

    def get_ui_font(self):
        return QFont(self.ui_font_family, self.ui_font_size)

    def set_vault_directory(self, directory):
        # Update the vault directory in config and persist to config.yaml
        self.config["vault_directory"] = directory
        self.save_config()
        self.logger.info(f"Vault directory updated to: {directory}")

    def save_config(self):
        """Save current configuration to config.yaml while preserving comments and structure."""
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        
        # If file exists, load existing structure first
        if os.path.exists(config_path):
            with open(config_path, "r", encoding='utf-8') as config_file:
                existing_config = self.yaml.load(config_file)
                
            # Update existing structure with new values
            def update_nested_dict(existing, new):
                for key, value in new.items():
                    if isinstance(value, dict) and key in existing and isinstance(existing[key], dict):
                        update_nested_dict(existing[key], value)
                    else:
                        existing[key] = value
                        
            update_nested_dict(existing_config, self.config)
            final_config = existing_config
        else:
            final_config = self.config
            
        # Save while preserving structure and comments
        with open(config_path, "w", encoding='utf-8') as config_file:
            self.yaml.dump(final_config, config_file)
