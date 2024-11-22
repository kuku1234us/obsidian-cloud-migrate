# managers/deletion_worker.py

import os
from PyQt6.QtCore import pyqtSignal, QThread
from utils.logger import Logger

class DeletionWorker(QThread):
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, item):
        super().__init__()
        self.workload_item = item
        self.logger = Logger()

    def run(self):
        """Delete the original and compressed files."""
        try:
            # Delete compressed file if it exists
            compressed_path = self.workload_item.get('processed_path')
            if compressed_path and os.path.exists(compressed_path):
                os.remove(compressed_path)
                self.logger.info(f"Deleted compressed file: {compressed_path}")

            # Delete original file
            original_path = self.workload_item.get('path')
            if original_path and os.path.exists(original_path):
                os.remove(original_path)
                self.logger.info(f"Deleted original file: {original_path}")

            self.progress.emit(self.workload_item, 'deletion_complete')

        except Exception as e:
            error_msg = f"Error during deletion of {self.workload_item['path']}: {str(e)}"
            self.logger.error(error_msg)
            self.error.emit(error_msg)
        finally:
            self.finished.emit()
