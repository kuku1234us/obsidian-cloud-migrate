from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar
from PyQt6.QtCore import pyqtSignal
from utils.logger import Logger

class WorkProgress(QWidget):
    work_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.logger = Logger()  # Initialize singleton logger
        self.init_ui()
        self.total_work = 0
        self.current_progress = 0
        self.is_processing = False

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

    def set_work(self, workload):
        """Set up the progress bar based on the workload array"""
        if not workload:
            self.logger.warning("Empty workload provided to progress bar")
            return
            
        self.reset()
        self.is_processing = True
        
        self.total_work = 0
        for item in workload:
            multiplier = 5 if item.get('type') == 'video' else 1
            self.total_work += item['filesize'] * multiplier
        
        self.progress_bar.setMaximum(100)
        self.logger.info(f"Progress bar initialized with total work: {self.total_work} bytes")

    def update_progress(self, completed_item, status):
        """Update progress based on completed item"""
        if not self.is_processing or not completed_item or not status:
            self.logger.warning("Invalid progress update: processing not active or invalid item/status")
            return
            
        if status == "complete" and self.total_work > 0:
            multiplier = 5 if completed_item['type'] == 'video' else 1
            self.current_progress += completed_item['filesize'] * multiplier
            percentage = min(100, int((self.current_progress / self.total_work) * 100))
            self.progress_bar.setValue(percentage)
            self.logger.debug(f"Progress updated: {percentage}% complete")
            
            if percentage >= 100:
                self.is_processing = False
                self.work_completed.emit()
                self.logger.info("All work completed")
