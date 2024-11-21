# components/file_list_view.py

from PyQt6.QtWidgets import QListView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir
from utils.logger import Logger

class FileListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()  # Initialize singleton logger
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.setModel(self.model)
        self.setSelectionMode(QListView.SelectionMode.MultiSelection)

    def load_files(self, directory):
        # Set the root path of the model to the selected directory
        self.logger.info(f"Loading files from directory: {directory}")
        self.setRootIndex(self.model.setRootPath(directory))
        self.setRootIndex(self.model.index(directory))
        self.setRootIndex(self.model.index(directory))
        # Filter out files that aren't media files (e.g., images, videos)
        media_filters = ["*.jpg", "*.png", "*.gif", "*.mp4", "*.mkv"]
        self.logger.debug(f"Setting media file filters: {media_filters}")
        self.model.setNameFilters(media_filters)
        self.model.setNameFilterDisables(False)
