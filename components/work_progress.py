from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QTextEdit
from PyQt6.QtCore import pyqtSignal
from managers.sound_manager import SoundManager

class WorkProgress(QWidget):
    work_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.total_work = 0
        self.current_progress = 0
        self.sound_manager = SoundManager()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status log
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        layout.addWidget(self.status_log)

    def set_work(self, workload):
        """Set up the progress bar based on the workload array"""
        self.total_work = 0
        for item in workload:
            multiplier = 5 if item.get('type') == 'video' else 1
            self.total_work += item['filesize'] * multiplier
        
        self.current_progress = 0
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.status_log.clear()
        self.log_message("Starting file processing...")

    def update_progress(self, completed_item, status):
        """Update progress based on completed item"""
        if status == "start":
            self.log_message(f"Starting to process {completed_item['type']}: {completed_item['filename']}")
            return
            
        if status == "complete":
            multiplier = 5 if completed_item['type'] == 'video' else 1
            self.current_progress += completed_item['filesize'] * multiplier
            percentage = min(100, int((self.current_progress / self.total_work) * 100))
            self.progress_bar.setValue(percentage)
            self.log_message(f"Completed processing {completed_item['type']}: {completed_item['filename']}")
            
            if percentage >= 100:
                self.work_completed.emit()
                self.log_message("All files processed successfully!")
                self.sound_manager.play_complete()

    def log_message(self, message):
        """Add a message to the status log"""
        self.status_log.append(message)
