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
        self.logger = Logger()  # Retrieve the Logger instance
        self.config = {}
        self.confidential_config = {}  # Store confidential information separately
        self.app_mode = self.config.get("app_mode", "production")
        self.logger.setup_logger(self)  # Pass self as config
        self.yaml = YAML()  # Use ruamel.yaml to load and dump YAML
        self._initialized = True

    def load_config(self):
        # Load .env file
        load_dotenv(override=True)

        # Load YAML configuration
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        with open(config_path, "r") as config_file:
            self.config = self.yaml.load(config_file)

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
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        with open(config_path, "w") as config_file:
            self.yaml.dump(self.config, config_file)
        self.logger.info(f"Vault directory updated to: {directory}")
