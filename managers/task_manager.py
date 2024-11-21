# managers/task_manager.py

import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from managers.file_manager import FileManager
from managers.link_manager import LinkManager
from managers.sound_manager import SoundManager
from managers.upload_manager import UploadManager
from utils.logger import Logger
from managers.config_manager import ConfigManager
import re

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
        self.upload_manager = UploadManager()
        self.link_manager = None
        self.workload = None
        self.logger = Logger()
        self.upload_workers = []  # Keep track of upload workers

    def set_vault_path(self, vault_path):
        """Initialize managers with vault path"""
        self.vault_path = vault_path
        self.link_manager = LinkManager(vault_path)
        self.file_manager.set_vault_path(vault_path)
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

    def upload_media_files(self):
        """Upload processed media files to S3"""
        if not self.workload:
            self.logger.warning("No files found in workload")
            return

        # Filter out items that failed processing or don't have valid paths
        files_to_upload = [
            item for item in self.workload 
            if item and not item.get('error') and (item.get('processed_path') or item.get('path'))
        ]
        
        if not files_to_upload:
            self.logger.warning("No valid files available for upload")
            return

        self.start_upload(files_to_upload)

    def start_upload(self, files_to_upload):
        """Start the upload process for files"""
        if not files_to_upload:
            self.logger.warning("No files to upload")
            return

        self.logger.info(f"Found {len(files_to_upload)} files to upload")
        
        # Clean up any existing workers
        self.cleanup()
        
        # Create an upload worker to handle uploads asynchronously
        for item in files_to_upload:
            upload_worker = UploadWorker(item, self.upload_manager)
            upload_worker.progress.connect(self.handle_upload_progress)
            upload_worker.error.connect(lambda msg: self.error.emit(msg))
            upload_worker.finished.connect(lambda worker=upload_worker: self._on_upload_complete(worker))
            self.upload_workers.append(upload_worker)
            upload_worker.start()

    def handle_upload_progress(self, workload_item, bytes_uploaded, total_bytes):
        """Handle progress updates from the upload worker"""
        # Only emit upload_complete when the upload is finished
        if bytes_uploaded >= total_bytes:
            self.progress.emit(workload_item, "upload_complete")
            return

        # Add upload progress information to the workload item
        workload_item['bytes_uploaded'] = bytes_uploaded
        workload_item['total_bytes'] = total_bytes
        workload_item['stage'] = 'upload'
        
        # Emit progress update with current stage
        self.progress.emit(workload_item, "upload_progress")

    def handle_progress(self, item, status):
        """Handle progress updates from workers"""
        if not item:
            return
            
        # Update progress for the item
        if status == 'start':
            item['work_done'] = 0
        elif status == 'progress':
            # Work done is tracked by the individual workers
            pass
        elif status == 'complete':
            # Map 'complete' to the appropriate stage completion status
            if item.get('stage') == 'compression':
                self.progress.emit(item, 'compression_complete')
            elif item.get('stage') == 'upload':
                self.progress.emit(item, 'upload_complete')
            elif item.get('stage') == 'link':
                self.progress.emit(item, 'link_complete')
        else:
            self.progress.emit(item, status)

    def process_videos(self):
        """Process video files in the workload"""
        video_files = [item for item in self.workload if item['type'] == 'video']
        if video_files:
            self.worker = CompressionWorker(video_files, self.file_manager, 'video')
            self.worker.progress.connect(self.handle_progress)
            self.worker.finished.connect(self.process_images)
            self.worker.start()
        else:
            self.process_images()

    def process_images(self):
        """Process image files in the workload"""
        image_files = [item for item in self.workload if item['type'] == 'image']
        if image_files:
            self.worker = CompressionWorker(image_files, self.file_manager, 'image')
            self.worker.progress.connect(self.handle_progress)
            self.worker.finished.connect(self.upload_media_files)  # Upload after processing
            self.worker.start()
        else:
            self.upload_media_files()  # No images to process, move to upload

    def process_links(self):
        """Process markdown files to update media links"""
        if not self.workload:
            self.logger.warning("No workload available for link processing")
            return

        self.logger.info("Starting link replacement process")
        markdown_files = self.file_manager.get_markdown_files()
        
        # Create mapping of original filenames to CloudFront URLs
        media_mapping = {}
        for item in self.workload:
            if item.get('upload_status') == 'success' and 'cloudfront_url' in item:
                original_name = os.path.basename(item['original_path'])
                media_mapping[original_name] = item['cloudfront_url']
        
        if not media_mapping:
            self.logger.warning("No successfully uploaded files to process")
            return
        
        for markdown_file in markdown_files:
            success, message = self.link_manager.replace_cloudfront_links(markdown_file, media_mapping)
            if not success:
                self.error.emit(message)

        # Update progress for all items that were successfully uploaded
        for item in self.workload:
            if item.get('upload_status') == 'success':
                self.progress.emit(item, 'link_complete')

        self.task_completed.emit('links')
        self.all_tasks_completed.emit()
        self.sound_manager.play_complete()

    def cleanup(self):
        """Clean up any running threads"""
        for worker in self.upload_workers:
            if worker.isRunning():
                worker.quit()
                worker.wait()
        self.upload_workers.clear()

    def _on_upload_complete(self, worker):
        """Handle completion of an upload worker"""
        if worker in self.upload_workers:
            self.upload_workers.remove(worker)
            worker.deleteLater()
            
        # Check if all uploads are complete
        if not self.upload_workers:
            self._on_task_complete('upload')

    def _on_task_complete(self, task_type):
        """Handle completion of individual tasks"""
        self.task_completed.emit(task_type)
        
        if task_type == "video":
            self.process_images()
        elif task_type == "image":
            self.upload_media_files()
        elif task_type == "upload":
            self.process_links()

class CompressionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)

    def __init__(self, workload, file_manager, task_type):
        super().__init__()
        self.workload = workload if workload is not None else []
        self.file_manager = file_manager
        self.task_type = task_type
        self._thread = None

    def start(self):
        """Start the worker in a new thread"""
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.run)
        self._thread.start()

    def run(self):
        """Process media files and emit progress"""
        try:
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
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if self._thread:
                self._thread.quit()

    def handle_progress(self, item, status=None, error_message=None):
        """Handle progress updates from file manager"""
        if error_message:
            self.error.emit(error_message)
            return
            
        if not item:
            return
            
        # Map file manager status to compression status
        if status == "complete":
            status = "compression_complete"
        
        self.progress.emit(item, status)

class UploadWorker(QThread):
    progress = pyqtSignal(dict, int, int)  # workload_item, bytes_uploaded, total_bytes
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, workload_item, upload_manager):
        super().__init__()
        self.workload_item = workload_item
        self.upload_manager = upload_manager
        self.logger = Logger()

    def run(self):
        """Upload the file with progress tracking"""
        try:
            # Get file information
            file_path = self.workload_item['path']
            file_size = os.path.getsize(file_path)
            
            # Get compressed filename if it exists, otherwise use original filename
            upload_filename = self.workload_item.get('compressed_filename', os.path.basename(file_path))
            
            def progress_callback(bytes_uploaded):
                self.progress.emit(self.workload_item, bytes_uploaded, file_size)

            # Upload the file with progress tracking
            success, message = self.upload_manager.upload_file_with_progress(
                file_path,
                object_name=upload_filename,
                progress_callback=progress_callback
            )

            if success:
                self.workload_item['upload_status'] = 'success'
                self.workload_item['cloudfront_url'] = self.upload_manager.get_cloudfront_url(upload_filename)
                # Final progress update will be handled by task_manager
            else:
                self.workload_item['upload_status'] = 'failed'
                self.workload_item['upload_error'] = message
                self.error.emit(f"Failed to upload {file_path}: {message}")

        except Exception as e:
            error_msg = f"Error during upload of {self.workload_item['path']}: {str(e)}"
            self.logger.error(error_msg)
            self.workload_item['upload_status'] = 'failed'
            self.workload_item['upload_error'] = str(e)
            self.error.emit(error_msg)
        finally:
            self.finished.emit()
