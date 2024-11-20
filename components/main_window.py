# components/main_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread
from components.file_list_view import FileListView
from components.work_progress import WorkProgress
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
        self.setWindowIcon(QIcon("./assets/appicon.png"))
        self.theme_manager.enable_dark_title_bar(self)

        # Initialize UI components
        self.init_ui()

        # Initialize worker-related variables
        self.image_thread = None
        self.video_thread = None
        self.image_worker = None
        self.video_worker = None
        self.current_workload = None

    def init_ui(self):
        # Main central widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
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

        # Work progress component
        self.work_progress = WorkProgress()
        self.work_progress.work_completed.connect(self.on_work_completed)
        self.main_layout.addWidget(self.work_progress)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.main_layout.addWidget(self.settings_button)

    def select_directory(self):
        current_directory = self.config_manager.get("vault_directory", "")
        directory = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault Directory", current_directory)
        if directory:
            self.file_list_view.load_files(directory)
            self.config_manager.set_vault_directory(directory)
            self.selected_dir_label.setText(f"Current Directory: {directory}")

    def compress_and_upload(self):
        current_directory = self.config_manager.get("vault_directory", "")
        if current_directory:
            # Get workload and set up progress tracking
            self.current_workload = self.task_manager.get_workload(current_directory)
            if not self.current_workload:
                self.work_progress.log_message("No media files found in the selected directory.")
                return

            self.work_progress.set_work(self.current_workload)
            self.upload_button.setEnabled(False)

            # Process images
            self.image_thread = QThread()
            self.image_worker = self.task_manager.create_worker(self.current_workload, "image")
            self.image_worker.moveToThread(self.image_thread)
            
            self.image_thread.started.connect(self.image_worker.run)
            self.image_worker.progress.connect(self.work_progress.update_progress)
            self.image_worker.error.connect(self.work_progress.log_message)
            self.image_worker.finished.connect(self.start_video_processing)
            self.image_worker.finished.connect(self.image_thread.quit)

            self.image_thread.start()

    def start_video_processing(self):
        # Process videos after images are done
        self.video_thread = QThread()
        self.video_worker = self.task_manager.create_worker(self.current_workload, "video")
        self.video_worker.moveToThread(self.video_thread)
        
        self.video_thread.started.connect(self.video_worker.run)
        self.video_worker.progress.connect(self.work_progress.update_progress)
        self.video_worker.error.connect(self.work_progress.log_message)
        self.video_worker.finished.connect(self.video_thread.quit)

        self.video_thread.start()

    def on_work_completed(self):
        self.upload_button.setEnabled(True)
        self.current_workload = None

    def open_settings_dialog(self):
        # TODO: Implement settings dialog
        pass
