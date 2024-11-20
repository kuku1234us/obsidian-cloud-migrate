# main.py

from PyQt6.QtWidgets import QApplication
from components.main_window import MainWindow
from managers.config_manager import ConfigManager
from components.theme_manager import ThemeManager
import sys

def main():
    app = QApplication(sys.argv)

    # Load configuration
    config_manager = ConfigManager()
    config_manager.load_config()

    # Apply theme using ThemeManager
    theme_manager = ThemeManager(config_manager)
    theme_manager.apply_theme()

    # Initialize and show the main window
    main_window = MainWindow(config_manager, theme_manager)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()