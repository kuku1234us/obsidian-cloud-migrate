# managers/upload_worker.py

from PyQt6.QtCore import pyqtSignal, QThread
from utils.logger import Logger
import os

class UploadWorker(QThread):
    progress = pyqtSignal(dict, int, int)  # item, bytes_uploaded, total_bytes
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, item, upload_manager):
        super().__init__()
        self.workload_item = item
        self.upload_manager = upload_manager
        self.logger = Logger()

    def run(self):
        """Upload the file with progress tracking."""
        try:
            # Get file information
            file_path = self.workload_item.get('processed_path', self.workload_item['path'])
            file_size = os.path.getsize(file_path)

            # Get the filename to use for uploading
            upload_filename = self.workload_item.get('compressed_filename', os.path.basename(file_path))

            def progress_callback(bytes_uploaded):
                self.progress.emit(self.workload_item, bytes_uploaded, file_size)

            # Upload the file
            success, message = self.upload_manager.upload_file_with_progress(
                file_path,
                object_name=upload_filename,
                progress_callback=progress_callback
            )

            if success:
                self.workload_item['upload_status'] = 'success'
                self.workload_item['cloudfront_url'] = self.upload_manager.get_cloudfront_url(upload_filename)
                self.logger.info(f"Uploaded file: {file_path}")
            else:
                self.workload_item['upload_status'] = 'failed'
                self.workload_item['upload_error'] = message
                error_msg = f"Failed to upload {file_path}: {message}"
                self.logger.error(error_msg)
                self.error.emit(error_msg)

        except Exception as e:
            error_msg = f"Error during upload of {self.workload_item['path']}: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            self.workload_item['upload_status'] = 'failed'
            self.workload_item['upload_error'] = str(e)
            self.error.emit(error_msg)
        finally:
            self.finished.emit()
