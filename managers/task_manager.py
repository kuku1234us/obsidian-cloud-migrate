# managers/task_manager.py

import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from managers.file_manager import FileManager
from utils.logger import Logger

class CompressionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, directory, file_manager, task_type):
        super().__init__()
        self.directory = directory
        self.file_manager = file_manager
        self.task_type = task_type

    def run(self):
        if self.task_type == "images":
            self.file_manager.compress_images_in_directory(self.directory, progress_callback=self.progress.emit)
        elif self.task_type == "videos":
            self.file_manager.compress_videos_in_directory(self.directory, progress_callback=self.progress.emit)
        self.finished.emit()


class TaskManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.file_manager = FileManager(config_manager)
        self.logger = Logger()

    def create_worker(self, directory, task_type):
        worker = CompressionWorker(directory, self.file_manager, task_type)
        return worker
