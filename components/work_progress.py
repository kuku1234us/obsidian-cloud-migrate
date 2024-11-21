from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar
from PyQt6.QtCore import pyqtSignal
from utils.logger import Logger

class WorkProgress(QWidget):
    work_completed = pyqtSignal()

    # Constants for work calculation
    LINK_REPLACEMENT_WORK = 20000  # 20KB constant work for link replacement
    UPLOAD_WORK_MULTIPLIER = 5     # 5x filesize for upload
    VIDEO_COMPRESSION_MULTIPLIER = 10  # 10x filesize for video compression
    IMAGE_COMPRESSION_MULTIPLIER = 1   # 1x filesize for image compression

    def __init__(self):
        super().__init__()
        self.logger = Logger()  # Initialize singleton logger
        self.init_ui()
        self.total_work = 0
        self.current_progress = 0
        self.is_processing = False
        self.workload = None

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def reset(self):
        """Reset progress bar"""
        self.logger.debug("Resetting progress bar")
        self.total_work = 0
        self.current_progress = 0
        self.progress_bar.setValue(0)
        self.is_processing = False
        self.workload = None

    def calculate_stage_work(self, item, stage):
        """
        Calculate work units for a specific stage of processing.
        
        Args:
            item (dict): Workload item containing file information
            stage (str): Processing stage ('compression', 'upload', or 'link')
            
        Returns:
            int: Amount of work units for the stage
        """
        if stage == 'compression':
            multiplier = self.VIDEO_COMPRESSION_MULTIPLIER if item['type'] == 'video' else self.IMAGE_COMPRESSION_MULTIPLIER
            return item['filesize'] * multiplier
        elif stage == 'upload':
            return item['filesize'] * self.UPLOAD_WORK_MULTIPLIER
        elif stage == 'link':
            return self.LINK_REPLACEMENT_WORK
        return 0

    def calculate_total_work(self, item):
        """
        Calculate total work units for all stages of a workload item.
        
        Args:
            item (dict): Workload item containing file information
            
        Returns:
            int: Total work units for the item
        """
        return sum(self.calculate_stage_work(item, stage) 
                  for stage in ['compression', 'upload', 'link'])

    def set_work(self, workload):
        """Set up the progress bar based on the workload array"""
        if not workload:
            self.logger.warning("Empty workload provided to progress bar")
            return
            
        self.reset()
        self.is_processing = True
        self.workload = workload
        
        # Calculate total work for all items
        self.total_work = sum(self.calculate_total_work(item) for item in workload)
        
        self.progress_bar.setMaximum(100)
        self.logger.info(f"Progress bar initialized with total work: {self.total_work} bytes")

    def update_progress(self, completed_item, status):
        """Update progress based on completed item"""
        if not self.is_processing:
            self.logger.warning("Invalid progress update: processing not active")
            return
            
        if not completed_item or not status:
            self.logger.warning("Invalid progress update: invalid item/status")
            return
            
        if self.total_work <= 0:
            return

        # Map status to stage
        stage_map = {
            'compression_complete': 'compression',
            'upload_complete': 'upload',
            'link_complete': 'link',
            'upload_progress': 'upload'  # Add handling for progress updates
        }
        
        stage = stage_map.get(status)
        if not stage:
            self.logger.warning(f"Unknown status: {status}")
            return
            
        # For completion statuses, check if this stage was already completed
        if status.endswith('_complete'):
            stage_key = f"{stage}_completed"
            if completed_item.get(stage_key):
                self.logger.debug(f"Skipping duplicate completion for {stage}")
                return
            completed_item[stage_key] = True
            
        # Calculate work done for this stage
        if status == 'upload_progress':
            # For upload progress, we calculate partial work based on the stage
            work_done = self.calculate_stage_work(completed_item, stage)
            # Adjust work_done based on bytes_uploaded/total_bytes if available
            if 'bytes_uploaded' in completed_item and 'total_bytes' in completed_item:
                progress = min(1.0, completed_item['bytes_uploaded'] / completed_item['total_bytes'])
                work_done = int(work_done * progress)
        else:
            # For completion statuses, we count the full work for the stage
            work_done = self.calculate_stage_work(completed_item, stage)
        
        self.current_progress += work_done
        percentage = min(100, int((self.current_progress / self.total_work) * 100))
        self.progress_bar.setValue(percentage)
        self.logger.debug(f"Progress updated: {percentage}% complete, stage: {status}")
        
        if percentage >= 100 and self.is_processing:
            self.is_processing = False
            self.work_completed.emit()
            self.logger.info("All work completed")
