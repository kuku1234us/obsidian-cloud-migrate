# managers/task_manager.py

import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from managers.file_manager import FileManager
from managers.link_manager import LinkManager
from managers.sound_manager import SoundManager
from managers.upload_manager import UploadManager
from managers.config_manager import ConfigManager
from utils.logger import Logger
from managers.compression_worker import CompressionWorker
from managers.deletion_worker import DeletionWorker
from managers.upload_worker import UploadWorker


class TaskManager(QObject):
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)
    all_tasks_completed = pyqtSignal()

    def __init__(self, file_manager):
        super().__init__()
        self.config_manager = ConfigManager()
        self.file_manager = file_manager
        self.sound_manager = SoundManager()
        self.upload_manager = UploadManager()
        self.logger = Logger()
        self.link_manager = None
        self.vault_path = None
        self.workload = []
        self.current_stage = ''
        self.workflow_phases = []
        self.current_phase_index = 0

        # Worker tracking
        self.compression_workers = []
        self.upload_workers = []
        self.deletion_workers = []

        # Task counters
        self.compression_tasks_remaining = 0
        self.upload_tasks_remaining = 0
        self.deletion_tasks_remaining = 0

    def set_vault_path(self, vault_path):
        """Initialize managers with the vault path."""
        self.vault_path = vault_path
        self.link_manager = LinkManager(vault_path)
        self.file_manager.set_vault_path(vault_path)
        self.logger.info(f"Initialized TaskManager with vault: {vault_path}")

    def start_processing(self):
        """Initiate the entire processing workflow."""
        if not self.vault_path:
            self.logger.error("No vault directory selected")
            self.error.emit("No vault directory selected")
            return

        self.prepare_workload()
        if not self.workload:
            self.logger.info("No media files found in vault")
            self.error.emit("No media files found in vault")
            return

        self.initialize_workflow()
        self.start_next_phase()

    def prepare_workload(self):
        """Prepare the workload by getting media files from the vault."""
        self.workload = self.file_manager.get_media_workload(self.vault_path)
        self.logger.info(f"Prepared workload with {len(self.workload)} items")

    def initialize_workflow(self):
        """Initialize the workflow phases."""
        self.workflow_phases = [
            {'name': 'compression', 'method': self.start_compression},
            {'name': 'upload', 'method': self.start_upload},
            {'name': 'link_replacement', 'method': self.process_links},
            {'name': 'deletion', 'method': self.start_deletion},
        ]
        self.current_phase_index = 0

    def start_next_phase(self):
        """Start the next phase in the workflow."""
        if self.current_phase_index < len(self.workflow_phases):
            phase = self.workflow_phases[self.current_phase_index]
            self.current_stage = phase['name']
            self.logger.info(f"Starting phase: {self.current_stage}")
            phase_method = phase['method']
            phase_method()
        else:
            # Workflow is complete
            self.current_stage = 'complete'
            self.logger.info("All tasks completed")
            self.all_tasks_completed.emit()
            self.sound_manager.play_complete()

    def on_phase_completed(self):
        """Handle the completion of the current phase and start the next one."""
        self.current_phase_index += 1
        self.start_next_phase()

    def start_compression(self):
        """Start concurrent compression of images and videos."""
        self.compression_workers = []
        self.compression_tasks_remaining = 0

        # Separate workloads
        video_files = [item for item in self.workload if item['type'] == 'video']
        image_files = [item for item in self.workload if item['type'] == 'image']

        if video_files:
            self.compression_tasks_remaining += 1
            self.start_compression_worker(video_files, 'video')

        if image_files:
            self.compression_tasks_remaining += 1
            self.start_compression_worker(image_files, 'image')

        if self.compression_tasks_remaining == 0:
            # No files to compress, proceed to next phase
            self.on_phase_completed()

    def start_compression_worker(self, files, task_type):
        """Start a compression worker for a given file type."""
        worker = CompressionWorker(files, self.file_manager, task_type)
        worker.progress.connect(self.handle_progress)
        worker.error.connect(self.handle_error)
        worker.finished.connect(lambda: self._on_compression_worker_finished(worker))
        self.compression_workers.append(worker)
        worker.start()

    def _on_compression_worker_finished(self, worker):
        """Handle completion of a compression worker."""
        if worker in self.compression_workers:
            self.compression_workers.remove(worker)
            worker.deleteLater()

        self.compression_tasks_remaining -= 1
        if self.compression_tasks_remaining == 0:
            # All compression tasks are complete
            self.logger.info("Compression phase completed")
            self.on_phase_completed()

    def start_upload(self):
        """Start uploading media files."""
        files_to_upload = [
            item for item in self.workload
            if not item.get('error') and (item.get('processed_path') or item.get('path'))
        ]

        if not files_to_upload:
            self.logger.warning("No valid files available for upload")
            # Proceed to next phase even if no files to upload
            self.on_phase_completed()
            return

        self.upload_workers = []
        self.upload_tasks_remaining = len(files_to_upload)
        self.logger.info(f"Starting upload of {self.upload_tasks_remaining} files")

        for item in files_to_upload:
            self.start_upload_worker(item)

    def start_upload_worker(self, item):
        """Start an upload worker for a given file."""
        worker = UploadWorker(item, self.upload_manager)
        worker.progress.connect(self.handle_upload_progress)
        worker.error.connect(self.handle_error)
        worker.finished.connect(lambda: self._on_upload_worker_finished(worker))
        self.upload_workers.append(worker)
        worker.start()

    def _on_upload_worker_finished(self, worker):
        """Handle completion of an upload worker."""
        if worker in self.upload_workers:
            self.upload_workers.remove(worker)
            worker.deleteLater()

        self.upload_tasks_remaining -= 1
        if self.upload_tasks_remaining == 0:
            # All upload tasks are complete
            self.logger.info("Upload phase completed")
            self.on_phase_completed()

    def process_links(self):
        """Process markdown files to update media links."""
        if not self.workload:
            self.logger.warning("No workload available for link processing")
            self.on_phase_completed()
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
            self.on_phase_completed()
            return

        for markdown_file in markdown_files:
            success, message = self.link_manager.replace_cloudfront_links(markdown_file, media_mapping)
            if not success:
                self.handle_error(message)

        # Emit progress for link replacement
        for item in self.workload:
            if item.get('upload_status') == 'success':
                self.progress.emit(item, 'link_complete')

        self.logger.info("Link replacement phase completed")
        self.on_phase_completed()

    def start_deletion(self):
        """Start deletion of original and compressed media files."""
        self.deletion_workers = []
        self.deletion_tasks_remaining = 0

        # Prepare list of files to delete
        files_to_delete = [
            item for item in self.workload
            if not item.get('error') and (item.get('path') or item.get('processed_path'))
        ]

        if not files_to_delete:
            self.logger.info("No files to delete")
            self.on_phase_completed()
            return

        self.deletion_tasks_remaining = len(files_to_delete)
        self.logger.info(f"Starting deletion of {self.deletion_tasks_remaining} files")

        for item in files_to_delete:
            self.start_deletion_worker(item)

    def start_deletion_worker(self, item):
        """Start a deletion worker for a given file."""
        worker = DeletionWorker(item)
        worker.progress.connect(self.handle_progress)
        worker.error.connect(self.handle_error)
        worker.finished.connect(lambda: self._on_deletion_worker_finished(worker))
        self.deletion_workers.append(worker)
        worker.start()

    def _on_deletion_worker_finished(self, worker):
        """Handle completion of a deletion worker."""
        if worker in self.deletion_workers:
            self.deletion_workers.remove(worker)
            worker.deleteLater()

        self.deletion_tasks_remaining -= 1
        if self.deletion_tasks_remaining == 0:
            # All deletion tasks are complete
            self.logger.info("Deletion phase completed")
            self.on_phase_completed()

    def handle_progress(self, item, status):
        """Handle progress updates from workers."""
        if not item:
            return

        item['current_stage'] = self.current_stage
        self.progress.emit(item, status)

    def handle_upload_progress(self, item, bytes_uploaded, total_bytes):
        """Handle progress updates from upload workers."""
        if bytes_uploaded >= total_bytes:
            self.progress.emit(item, 'upload_complete')
            return

        item['bytes_uploaded'] = bytes_uploaded
        item['total_bytes'] = total_bytes
        item['current_stage'] = self.current_stage
        self.progress.emit(item, 'upload_progress')

    def handle_error(self, error_message):
        """Handle errors emitted by workers."""
        self.logger.error(error_message)
        self.error.emit(error_message)
        # Decide whether to abort the workflow or continue
        # For now, we'll log the error and continue

    def abort_processing(self):
        """Abort the entire processing workflow."""
        self.logger.error("Workflow aborted due to a critical error.")
        # Stop all running workers
        self.stop_all_workers()
        self.error.emit("Processing aborted due to an error.")
        self.current_stage = 'aborted'
        self.current_phase_index = len(self.workflow_phases)

    def stop_all_workers(self):
        """Stop all running workers."""
        for worker in self.compression_workers + self.upload_workers + self.deletion_workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        self.compression_workers.clear()
        self.upload_workers.clear()
        self.deletion_workers.clear()
