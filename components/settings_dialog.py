"""
Settings Dialog Module

This module provides a dialog for configuring application settings,
including AWS credentials and cloud storage options.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from managers.config_manager import ConfigManager
import os
from dotenv import set_key, load_dotenv
from pathlib import Path

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedWidth(500)  # Set dialog width to 500px
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # AWS Credentials Group
        aws_group = QGroupBox("AWS Credentials")
        aws_layout = QVBoxLayout()
        aws_group.setLayout(aws_layout)

        # AWS Access Key ID
        self.aws_key_id = self._create_input_field("AWS Access Key ID:")
        aws_layout.addWidget(self.aws_key_id.label)
        aws_layout.addWidget(self.aws_key_id.field)

        # AWS Secret Access Key
        self.aws_secret_key = self._create_input_field("AWS Secret Access Key:")
        aws_layout.addWidget(self.aws_secret_key.label)
        aws_layout.addWidget(self.aws_secret_key.field)

        # AWS Region
        self.aws_region = self._create_input_field("AWS Region:")
        aws_layout.addWidget(self.aws_region.label)
        aws_layout.addWidget(self.aws_region.field)

        layout.addWidget(aws_group)

        # Cloud Storage Configuration Group
        storage_group = QGroupBox("Cloud Storage Configuration")
        storage_layout = QVBoxLayout()
        storage_group.setLayout(storage_layout)

        # S3 Bucket Name
        self.s3_bucket = self._create_input_field("S3 Bucket Name:")
        storage_layout.addWidget(self.s3_bucket.label)
        storage_layout.addWidget(self.s3_bucket.field)

        # S3 Subfolder
        self.s3_subfolder = self._create_input_field("S3 Subfolder Path:")
        storage_layout.addWidget(self.s3_subfolder.label)
        storage_layout.addWidget(self.s3_subfolder.field)

        # CloudFront Base URL
        self.cloudfront_url = self._create_input_field("CloudFront Base URL:")
        storage_layout.addWidget(self.cloudfront_url.label)
        storage_layout.addWidget(self.cloudfront_url.field)

        layout.addWidget(storage_group)

        # Test Connection Button
        test_button = QPushButton("Test AWS Connection")
        test_button.clicked.connect(self.test_aws_connection)
        layout.addWidget(test_button)

        # Dialog Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def _create_input_field(self, label_text):
        """Create a labeled input field."""
        label = QLabel(label_text)
        field = QLineEdit()
        return type('InputField', (), {'label': label, 'field': field})

    def load_settings(self):
        """Load current settings into the dialog."""
        # Load .env settings
        load_dotenv()
        self.aws_key_id.field.setText(os.getenv("AWS_ACCESS_KEY_ID", ""))
        self.aws_secret_key.field.setText(os.getenv("AWS_SECRET_ACCESS_KEY", ""))
        self.aws_region.field.setText(os.getenv("AWS_REGION", ""))

        # Load config.yaml settings
        self.s3_bucket.field.setText(self.config_manager.get("s3_bucket_name", ""))
        self.s3_subfolder.field.setText(self.config_manager.get("s3_subfolder", ""))
        self.cloudfront_url.field.setText(self.config_manager.get("cloudfront_base_url", ""))

    def save_settings(self):
        """Save settings to .env and config.yaml."""
        try:
            # Update .env file
            env_path = Path('.env')
            env_path.touch(exist_ok=True)

            set_key(env_path, "AWS_ACCESS_KEY_ID", self.aws_key_id.field.text())
            set_key(env_path, "AWS_SECRET_ACCESS_KEY", self.aws_secret_key.field.text())
            set_key(env_path, "AWS_REGION", self.aws_region.field.text())

            # Update config.yaml through ConfigManager
            self.config_manager.config.update({
                "s3_bucket_name": self.s3_bucket.field.text(),
                "s3_subfolder": self.s3_subfolder.field.text(),
                "cloudfront_base_url": self.cloudfront_url.field.text()
            })
            self.config_manager.save_config()

            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def test_aws_connection(self):
        """Test AWS connection with current credentials."""
        try:
            # Create temporary boto3 session with current field values
            import boto3
            session = boto3.Session(
                aws_access_key_id=self.aws_key_id.field.text(),
                aws_secret_access_key=self.aws_secret_key.field.text(),
                region_name=self.aws_region.field.text()
            )
            s3 = session.client('s3')
            s3.list_buckets()  # Test connection
            QMessageBox.information(self, "Success", "AWS connection test successful!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"AWS connection test failed: {str(e)}")
