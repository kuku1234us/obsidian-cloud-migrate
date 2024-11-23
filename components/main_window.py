from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QFileDialog, QTextEdit, QApplication
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from components.file_list_view import FileListView
from components.work_progress import WorkProgress
from components.settings_dialog import SettingsDialog
from components.system_tray import SystemTray
from utils.logger import Logger
import os
import sys

def get_asset_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self, config_manager, task_manager, file_manager):
        super().__init__()
        self.setWindowTitle("Vault Manager")
        self.config_manager = config_manager
        self.task_manager = task_manager
        self.file_manager = file_manager
        self.logger = Logger()  # Initialize singleton logger

        # Connect task manager signals
        self.task_manager.progress.connect(self.on_progress_update)
        self.task_manager.error.connect(self.on_error)
        self.task_manager.all_tasks_completed.connect(self.on_all_tasks_completed)

        # Set main window properties
        self.setGeometry(100, 100, 1000, 600)
        icon_path = get_asset_path("assets/appicon.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Initialize UI components
        self.init_ui()
        self.minimize_to_tray = True  # New flag for tray behavior
        self.settings_dialog = None  # Keep track of settings dialog

        # Initialize system tray
        self.tray_icon = SystemTray(self)
        self.tray_icon.show()

    def init_ui(self):
        # Main central widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Directory selector button
        self.select_dir_button = QPushButton("Select Vault Directory")
        self.select_dir_button.clicked.connect(self.select_vault)
        self.main_layout.addWidget(self.select_dir_button)

        # Currently selected directory label
        self.selected_dir_label = QLabel()
        initial_directory = self.config_manager.get("vault_directory", "")
        if initial_directory:
            self.selected_dir_label.setText(f"Current Directory: {initial_directory}")
            self.task_manager.set_vault_path(initial_directory)
        self.main_layout.addWidget(self.selected_dir_label)

        # File list view
        self.file_list_view = FileListView()
        if initial_directory:
            self.file_list_view.load_files(initial_directory)
        self.main_layout.addWidget(self.file_list_view)

        # Upload button
        self.upload_button = QPushButton("Upload to S3")
        self.upload_button.clicked.connect(self.start_processing)
        self.upload_button.setEnabled(bool(initial_directory))
        self.main_layout.addWidget(self.upload_button)

        # Work progress component
        self.work_progress = WorkProgress()
        self.main_layout.addWidget(self.work_progress)

        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.main_layout.addWidget(self.log_viewer)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.main_layout.addWidget(self.settings_button)

    def select_vault(self):
        """Handle vault directory selection"""
        current_directory = self.config_manager.get("vault_directory", "")
        directory = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault Directory", current_directory)
        if directory:
            self.file_list_view.load_files(directory)
            self.config_manager.set_vault_directory(directory)
            self.selected_dir_label.setText(f"Current Directory: {directory}")
            self.task_manager.set_vault_path(directory)
            self.upload_button.setEnabled(True)
            self.log_viewer.append(f"Selected vault directory: {directory}")

    def start_processing(self):
        """Start the processing workflow"""
        # Get current vault directory
        current_directory = self.config_manager.get("vault_directory", "")
        if not current_directory:
            self.log_viewer.append("No vault directory selected. Please select a directory first.")
            return

        # Get workload first
        workload = self.file_manager.get_media_workload(current_directory)
        if not workload:
            self.log_viewer.append("No media files found in the selected directory.")
            return

        # Set up progress tracking
        self.work_progress.set_work(workload)
        self.upload_button.setEnabled(False)
        
        # Start processing
        self.task_manager.start_processing()

    def on_progress_update(self, item, status):
        """Handle progress updates from task manager"""
        if status == "start":
            message = f"Starting to process {item['type']}: {item['path']}"
            self.logger.info(message)
            self.log_viewer.append(message)
        elif status in ["compression_complete", "upload_complete", "link_complete"]:
            message = f"Completed {status.replace('_complete', '')} for {item['type']}: {item['path']}"
            self.logger.info(message)
            self.log_viewer.append(message)
            self.work_progress.update_progress(item, status)

    def on_error(self, error_message):
        """Handle error messages from task manager"""
        message = f"Error: {error_message}"
        self.logger.error(message)
        self.log_viewer.append(message)
        self.upload_button.setEnabled(True)

    def on_all_tasks_completed(self):
        """Handle completion of all tasks"""
        message = "All tasks completed successfully!"
        self.logger.info(message)
        self.log_viewer.append(message)
        self.upload_button.setEnabled(True)

    def open_settings_dialog(self):
        """Open the settings configuration dialog"""
        self.show_settings()

    def show_settings(self):
        """Show settings dialog without showing main window"""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self)  # Use self as parent for proper lifecycle management
            self.settings_dialog.finished.connect(self.on_settings_dialog_closed)
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()

    def on_settings_dialog_closed(self, result):
        """Handle settings dialog closure"""
        if result:  # If OK was clicked
            self.config_manager.load_config()
            self.logger.info("Settings updated successfully")
        self.settings_dialog = None

    def closeEvent(self, event):
        """Handle window close event"""
        if self.minimize_to_tray:
            event.ignore()
            self.hide()
        else:
            self.quit()

    def quit(self):
        """Quit the application"""
        # Clean up any open dialogs
        if self.settings_dialog:
            self.settings_dialog.close()
            self.settings_dialog = None

        # Hide tray icon before quitting
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon.setParent(None)  # Remove parent to prevent ghost process
            self.tray_icon = None

        # Quit the application
        QApplication.instance().quit()
