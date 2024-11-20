# components/file_list_view.py

from PyQt6.QtWidgets import QListView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir

class FileListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.setModel(self.model)
        self.setSelectionMode(QListView.SelectionMode.MultiSelection)

    def load_files(self, directory):
        # Set the root path of the model to the selected directory
        self.setRootIndex(self.model.setRootPath(directory))
        self.setRootIndex(self.model.index(directory))
        self.setRootIndex(self.model.index(directory))
        # Filter out files that aren't media files (e.g., images, videos)
        self.model.setNameFilters(["*.jpg", "*.png", "*.gif", "*.mp4", "*.mkv"])
        self.model.setNameFilterDisables(False)
