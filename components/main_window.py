# components/main_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QProgressBar, QTextEdit, QFileDialog, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread
from components.file_list_view import FileListView
from managers.task_manager import TaskManager

class MainWindow(QMainWindow):
    def __init__(self, config_manager, theme_manager):
        super().__init__()
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.task_manager = TaskManager(config_manager)

        # Set main window properties
        self.setWindowTitle("ObsidianCloudMigrate")
        self.setGeometry(100, 100, 1000, 600)

        # Set application icon
        self.setWindowIcon(QIcon("./assets/appicon.png"))

        # Apply dark title bar theme (Windows only)
        self.theme_manager.enable_dark_title_bar(self)

        # Initialize UI components
        self.init_ui()

        # Initialize worker-related variables
        self.image_thread = None
        self.video_thread = None
        self.image_worker = None
        self.video_worker = None

    def init_ui(self):
        # Main central widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.main_widget)

        # Directory selector button
        self.select_dir_button = QPushButton("Select Vault Directory")
        self.select_dir_button.clicked.connect(self.select_directory)
        self.main_layout.addWidget(self.select_dir_button)

        # Currently selected directory label
        self.selected_dir_label = QLabel()
        initial_directory = self.config_manager.get("vault_directory", "")
        if initial_directory:
            self.selected_dir_label.setText(f"Current Directory: {initial_directory}")
        self.main_layout.addWidget(self.selected_dir_label)

        # File list view
        self.file_list_view = FileListView()
        if initial_directory:
            self.file_list_view.load_files(initial_directory)
        self.main_layout.addWidget(self.file_list_view)

        # Upload button
        self.upload_button = QPushButton("Upload to S3")
        self.upload_button.clicked.connect(self.compress_and_upload)
        self.main_layout.addWidget(self.upload_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.main_layout.addWidget(self.progress_bar)

        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.main_layout.addWidget(self.log_viewer)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.main_layout.addWidget(self.settings_button)

    def select_directory(self):
        current_directory = self.config_manager.get("vault_directory", "")
        directory = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault Directory", current_directory)
        if directory:
            # Load files from the selected directory
            self.file_list_view.load_files(directory)

            # Update the vault directory in config manager
            self.config_manager.set_vault_directory(directory)

            # Update the label to show the selected directory
            self.selected_dir_label.setText(f"Current Directory: {directory}")

    def compress_and_upload(self):
        current_directory = self.config_manager.get("vault_directory", "")
        if current_directory:
            self.log_viewer.append("Compressing images and videos in the selected directory...")

            # Create and start the worker thread for image compression
            self.image_thread = QThread()
            self.image_worker = self.task_manager.create_worker(current_directory, "images")
            self.image_worker.moveToThread(self.image_thread)

            self.image_thread.started.connect(self.image_worker.run)
            self.image_worker.progress.connect(self.update_log)
            self.image_worker.finished.connect(self.image_thread.quit)
            self.image_worker.finished.connect(self.image_worker.deleteLater)
            self.image_thread.finished.connect(self.image_thread.deleteLater)
            self.image_worker.finished.connect(lambda: self.start_video_compression(current_directory))

            self.image_thread.start()
        else:
            self.log_viewer.append("No directory selected. Please select a directory first.")

    def start_video_compression(self, directory):
        # Create and start the worker thread for video compression
        self.video_thread = QThread()
        self.video_worker = self.task_manager.create_worker(directory, "videos")
        self.video_worker.moveToThread(self.video_thread)

        self.video_thread.started.connect(self.video_worker.run)
        self.video_worker.progress.connect(self.update_log)
        self.video_worker.finished.connect(self.video_thread.quit)
        self.video_worker.finished.connect(self.video_worker.deleteLater)
        self.video_thread.finished.connect(self.video_thread.deleteLater)

        self.video_thread.start()

    def update_log(self, message):
        self.log_viewer.append(message)

    def upload_files(self):
        # Placeholder function for uploading files
        self.log_viewer.append("Uploading files to S3... (Feature to be implemented)")

    def open_settings_dialog(self):
        # Placeholder function for opening settings dialog
        self.log_viewer.append("Opening settings dialog... (Feature to be implemented)")
