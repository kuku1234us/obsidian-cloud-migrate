# theme_manager.py

"""
Theme Manager for PyQt6 applications with native dark title bar support.
This class applies a dark theme to the entire application, including the title bar on Windows 10/11.
It uses the Windows API to enable dark mode for the title bar without creating a custom title bar.
"""

from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt
import sys
import ctypes
from ctypes import wintypes

class ThemeManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.theme = self.config_manager.get("ui", {}).get("theme", {}).get("dark", {})
        self.font_family = (
            self.config_manager.get("ui", {}).get("font", {}).get("family", "Calibri")
        )
        self.font_size = (
            self.config_manager.get("ui", {}).get("font", {}).get("size", 10)
        )

    def apply_theme(self):
        app = QApplication.instance()
        if app is None:
            raise RuntimeError(
                "No Qt Application found. Create it before applying the theme."
            )

        # Set the application style to Fusion, which allows for better customization
        app.setStyle(QStyleFactory.create("Fusion"))

        app.setPalette(self._get_palette())
        app.setStyleSheet(self._get_stylesheet())

        # Set the default font for the entire application
        font = QFont(self.font_family, self.font_size)
        app.setFont(font)

    def enable_dark_title_bar(self, window):
        if sys.platform == "win32":
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            set_window_attribute.argtypes = [
                wintypes.HWND,
                ctypes.c_uint,
                ctypes.c_void_p,
                ctypes.c_uint,
            ]
            set_window_attribute.restype = ctypes.c_int
            hwnd = int(window.winId())
            value = ctypes.c_int(1)
            set_window_attribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )

    def _get_palette(self):
        palette = QPalette()
        palette.setColor(
            QPalette.ColorRole.Window, QColor(self.theme.get("background", "#1E1E1E"))
        )
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor(self.theme.get("text", "#FFFFFF"))
        )
        palette.setColor(
            QPalette.ColorRole.Base,
            QColor(self.theme.get("table", {}).get("background", "#252526")),
        )
        palette.setColor(
            QPalette.ColorRole.AlternateBase,
            QColor(self.theme.get("table", {}).get("alternate_row", "#2D2D2D")),
        )
        palette.setColor(
            QPalette.ColorRole.ToolTipBase,
            QColor(self.theme.get("background", "#1E1E1E")),
        )
        palette.setColor(
            QPalette.ColorRole.ToolTipText, QColor(self.theme.get("text", "#FFFFFF"))
        )
        palette.setColor(
            QPalette.ColorRole.Text, QColor(self.theme.get("text", "#FFFFFF"))
        )
        palette.setColor(
            QPalette.ColorRole.Button,
            QColor(self.theme.get("button", {}).get("background", "#3C3C3C")),
        )
        palette.setColor(
            QPalette.ColorRole.ButtonText,
            QColor(self.theme.get("button", {}).get("text", "#FFFFFF")),
        )
        palette.setColor(
            QPalette.ColorRole.Highlight, QColor(self.theme.get("accent", "#007ACC"))
        )
        palette.setColor(
            QPalette.ColorRole.HighlightedText,
            QColor(self.theme.get("text", "#FFFFFF")),
        )
        return palette

    def _get_stylesheet(self):
        background_color = self.theme.get("background", "#1E1E1E")
        text_color = self.theme.get("text", "#FFFFFF")
        header_color = self.theme.get("table", {}).get("header", "#2D2D2D")
        grid_color = self.theme.get("table", {}).get("grid", "#3C3C3C")
        table_background_color = self.theme.get("table", {}).get(
            "background", "#252526"
        )
        alternate_row_color = self.theme.get("table", {}).get(
            "alternate_row", "#2D2D2D"
        )
        search_bg_color = self.theme.get("search", {}).get("background", "#2D2D2D")
        search_border_color = self.theme.get("search", {}).get("border", "#3C3C3C")
        search_focus_color = self.theme.get("search", {}).get("focus", "#4CAF50")
        button_background = self.theme.get("button", {}).get("background", "#3C3C3C")
        button_text = self.theme.get("button", {}).get("text", "#FFFFFF")
        button_hover = self.theme.get("button", {}).get("hover", "#505050")
        button_disabled_bg = (
            self.theme.get("button", {})
            .get("disabled", {})
            .get("background", "#2A2A2A")
        )
        button_disabled_text = (
            self.theme.get("button", {}).get("disabled", {}).get("text", "#808080")
        )
        button_radius = self.theme.get("border_radius", {}).get("button", "5px")
        input_radius = self.theme.get("border_radius", {}).get("input", "5px")

        return f"""
        QWidget {{
            font-family: {self.font_family};
            font-size: {self.font_size}pt;
        }}
        QTableWidget {{
            background-color: {table_background_color};
            gridline-color: {grid_color};
            color: {text_color};
        }}
        QTableView {{
            alternate-background-color: {alternate_row_color};
        }}
        QHeaderView {{
            background-color: {header_color};
        }}
        QHeaderView::section {{
            background-color: {header_color};
            color: {text_color};
            padding: 4px;
            border: none;
        }}
        QTableCornerButton::section {{
            background-color: {header_color};
            border: none;
        }}
        QLineEdit {{
            padding-right: 20px;
            border-radius: {input_radius};
            border: 1px solid {search_border_color};
            background-color: {search_bg_color};
            color: {text_color};
        }}
        QLineEdit:focus {{
            border: 1px solid {search_focus_color};
        }}
        QToolButton, QPushButton {{ 
            background-color: {button_background};
            color: {button_text};
            border: none;
            border-radius: {button_radius};
            padding: 5px;
        }}
        QToolButton:hover, QPushButton:hover {{
            background-color: {button_hover};
        }}
        QPushButton:disabled {{
            background-color: {button_disabled_bg};
            color: {button_disabled_text};
        }}
        """
