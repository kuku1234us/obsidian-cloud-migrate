# managers/task_manager.py

import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from managers.file_manager import FileManager
from managers.link_manager import LinkManager
from managers.sound_manager import SoundManager
from utils.logger import Logger
from managers.config_manager import ConfigManager

class TaskManager(QObject):
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)
    task_completed = pyqtSignal(str)  # task_type
    all_tasks_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.sound_manager = SoundManager()
        self.link_manager = None
        self.workload = None
        self.logger = Logger()

    def set_vault_path(self, vault_path):
        """Initialize managers with vault path"""
        self.vault_path = vault_path
        self.link_manager = LinkManager(vault_path)
        self.logger.info(f"Initialized task manager with vault: {vault_path}")

    def get_workload(self, directory):
        """Get the total workload for processing"""
        return self.file_manager.get_media_workload(directory)

    def start_processing(self):
        """Start the media processing workflow"""
        if not hasattr(self, 'vault_path'):
            self.logger.error("No vault directory selected")
            self.error.emit("No vault directory selected")
            return

        # Get workload
        self.workload = self.file_manager.get_media_workload(self.vault_path)
        if not self.workload:
            self.logger.info("No media files found in vault")
            self.error.emit("No media files found in vault")
            return

        # Start with video processing
        self.process_videos()

    def process_videos(self):
        """Create and configure video worker"""
        self.video_worker = CompressionWorker(self.workload, self.file_manager, "video")
        self.video_worker.progress.connect(lambda item, status: self.progress.emit(item, status))
        self.video_worker.finished.connect(lambda: self._on_task_complete("video"))
        self.video_worker.error.connect(lambda msg: self.error.emit(msg))
        self.video_worker.start()

    def process_images(self):
        """Create and configure image worker"""
        self.image_worker = CompressionWorker(self.workload, self.file_manager, "image")
        self.image_worker.progress.connect(lambda item, status: self.progress.emit(item, status))
        self.image_worker.finished.connect(lambda: self._on_task_complete("image"))
        self.image_worker.error.connect(lambda msg: self.error.emit(msg))
        self.image_worker.start()

    def search_media_links(self):
        """Search for media links in markdown files and replace them with external URLs"""
        if not self.link_manager or not self.workload:
            self.logger.error("Link manager not initialized or no workload available")
            return

        self.logger.info("Starting to search for media links in vault...")
        results = self.link_manager.scan_vault(self.workload)
        
        # Log summary of found links
        total_files = len(results)
        total_links = sum(len(file_results) for file_results in results.values())
        self.logger.info(f"Found {total_links} media links in {total_files} markdown files")

        # Create mapping of original filenames to their compressed versions
        media_mapping = {}
        for item in self.workload:
            original_name = os.path.basename(item['path'])
            # Extract the compressed filename from the path
            compressed_path = os.path.join(os.path.dirname(item['path']), 
                item.get('compressed_filename', ''))
            if os.path.exists(compressed_path):
                compressed_name = os.path.basename(compressed_path)
                media_mapping[original_name] = compressed_name

        # Replace links in each markdown file
        for markdown_file, file_results in results.items():
            success, message = self.link_manager.replace_media_links(markdown_file, media_mapping)
            if success:
                self.logger.info(f"Successfully updated links in: {markdown_file}")
            else:
                self.logger.error(f"Failed to update links in {markdown_file}: {message}")

        # Play completion sound
        self.sound_manager.play_complete()
        
        # Signal completion of all tasks
        self.all_tasks_completed.emit()

    def _on_task_complete(self, task_type):
        """Handle completion of individual tasks"""
        self.task_completed.emit(task_type)
        
        if task_type == "video":
            self.process_images()
        elif task_type == "image":
            self.search_media_links()

class CompressionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)

    def __init__(self, workload, file_manager, task_type):
        super().__init__()
        self.workload = workload if workload is not None else []
        self.file_manager = file_manager
        self.task_type = task_type

    def start(self):
        """Start the worker in a new thread"""
        self.run()

    def run(self):
        if not self.workload:
            self.finished.emit()
            return
            
        filtered_workload = [item for item in self.workload if item['type'] == self.task_type]
        
        if not filtered_workload:
            self.finished.emit()
            return
            
        if self.task_type == "image":
            self.file_manager.compress_images_in_directory(
                filtered_workload,
                progress_callback=self.handle_progress
            )
        elif self.task_type == "video":
            self.file_manager.compress_videos_in_directory(
                filtered_workload,
                progress_callback=self.handle_progress
            )
        self.finished.emit()

    def handle_progress(self, item, status=None, error_message=None):
        if error_message:
            self.error.emit(error_message)
        elif item:
            self.progress.emit(item, status)
