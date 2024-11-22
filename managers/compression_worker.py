# CompressionWorker class

from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool, QRunnable, pyqtSlot, QThread
from utils.logger import Logger

class CompressionWorker(QObject):
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, workload, file_manager, task_type):
        super().__init__()
        self.workload = workload
        self.file_manager = file_manager
        self.task_type = task_type
        self.logger = Logger()
        self._thread = None
        self.threadpool = QThreadPool()
        self.tasks_remaining = 0

    def start(self):
        """Start the worker in a new thread"""
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.run)
        self.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def run(self):
        """Process media files concurrently and emit progress"""
        try:
            if not self.workload:
                self.finished.emit()
                return

            filtered_workload = [item for item in self.workload if item['type'] == self.task_type]
            if not filtered_workload:
                self.finished.emit()
                return

            self.tasks_remaining = len(filtered_workload)

            for item in filtered_workload:
                task = CompressionTask(item, self.file_manager)
                task.signals.progress.connect(self.handle_progress)
                task.signals.error.connect(self.handle_error)
                task.signals.finished.connect(self.task_finished)
                self.threadpool.start(task)
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()
        # No finally block here because we need to wait until all tasks are finished
        # The finished signal will be emitted when all tasks are done

    def task_finished(self):
        """Called when a single task is finished"""
        self.tasks_remaining -= 1
        if self.tasks_remaining == 0:
            # All tasks are finished
            self.finished.emit()

    def handle_progress(self, item, status):
        """Handle progress updates from tasks"""
        self.progress.emit(item, status)

    def handle_error(self, error_message):
        """Handle errors emitted by tasks"""
        self.error.emit(error_message)

class CompressionTaskSignals(QObject):
    progress = pyqtSignal(dict, str)  # item, status
    error = pyqtSignal(str)
    finished = pyqtSignal()

class CompressionTask(QRunnable):
    def __init__(self, item, file_manager):
        super().__init__()
        self.item = item
        self.file_manager = file_manager
        self.signals = CompressionTaskSignals()
        self.logger = Logger()
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        """Compress a single file"""
        try:
            self.signals.progress.emit(self.item, 'start')
            self.file_manager.compress_single_file(self.item)
            self.signals.progress.emit(self.item, 'compression_complete')
            self.signals.finished.emit()
        except Exception as e:
            error_message = f"Error processing {self.item['path']}: {str(e)}"
            self.logger.error(error_message)
            self.item['error'] = error_message
            self.item['status'] = 'failed'
            self.signals.error.emit(error_message)
            self.signals.finished.emit()
