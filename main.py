# main.py

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from components.main_window import MainWindow
from managers.config_manager import ConfigManager
from components.theme_manager import ThemeManager
from managers.task_manager import TaskManager
from managers.file_manager import FileManager

def setup_logging():
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    # Initialize application
    app = QApplication(sys.argv)
    
    # Prevent application from quitting when last window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize managers
    config_manager = ConfigManager()
    config_manager.load_config()

    # Apply theme using ThemeManager
    theme_manager = ThemeManager(config_manager)
    theme_manager.apply_theme()
    
    # Initialize task manager
    file_manager = FileManager()
    task_manager = TaskManager(file_manager)
    
    # Create and show main window
    main_window = MainWindow(config_manager, task_manager, file_manager)
    theme_manager.enable_dark_title_bar(main_window)
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    setup_logging()
    main()