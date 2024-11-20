# managers/task_manager.py

import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from managers.file_manager import FileManager
from utils.logger import Logger

class CompressionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)

    def __init__(self, workload, file_manager, task_type):
        super().__init__()
        self.workload = workload if workload is not None else []
        self.file_manager = file_manager
        self.task_type = task_type

    def run(self):
        if not self.workload:  # Handle empty workload
            self.finished.emit()
            return
            
        filtered_workload = [item for item in self.workload if item['type'] == self.task_type]
        
        if not filtered_workload:  # No files of this type to process
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


class TaskManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.file_manager = FileManager(config_manager)
        self.logger = Logger()

    def get_workload(self, directory):
        """Get the total workload for processing"""
        return self.file_manager.get_media_workload(directory)

    def create_worker(self, workload, task_type):
        """Create a worker for processing files"""
        worker = CompressionWorker(workload, self.file_manager, task_type)
        return worker
