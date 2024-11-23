from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QObject
import os
import sys

def get_asset_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SystemTray(QSystemTrayIcon):
    def __init__(self, main_window):
        # Create a parent QObject to ensure proper lifecycle management
        self.parent_object = QObject()
        super().__init__(parent=self.parent_object)
        self.main_window = main_window
        self.setup_tray()

    def setup_tray(self):
        """Setup the system tray icon and menu"""
        # Set icon
        icon_path = get_asset_path("assets/appicon.ico")
        self.setIcon(QIcon(icon_path))
        self.setToolTip('Vault Manager')

        # Create menu
        menu = QMenu()
        
        # Show/Hide action
        show_action = menu.addAction('Show Vault Manager')
        show_action.triggered.connect(self.toggle_window)
        
        # Settings action
        settings_action = menu.addAction('Settings')
        settings_action.triggered.connect(self.main_window.show_settings)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = menu.addAction('Quit')
        quit_action.triggered.connect(self.main_window.quit)

        # Set context menu
        self.setContextMenu(menu)

        # Connect activated signal (for left-click)
        self.activated.connect(self.handle_activation)

    def handle_activation(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window()

    def toggle_window(self):
        """Toggle main window visibility"""
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.activateWindow()  # Bring window to front
