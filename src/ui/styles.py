# Modern dynamic stylesheet for Light & Dark mode support based on OS themes
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt

def is_system_dark_mode():
    """
    Detects if the system is currently using Dark Mode.
    Supports PyQt6 native color schemes and fallback to Windows registry.
    """
    try:
        # Check standard PyQt6 system palette/scheme if available (6.5+)
        scheme = QGuiApplication.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return True
        elif scheme == Qt.ColorScheme.Light:
            return False
    except Exception:
        pass

    # Windows registry check fallback
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False

def get_modern_stylesheet(is_dark=None):
    """
    Generates a high-quality modern stylesheet supporting light and dark themes.
    If is_dark is None, it dynamically auto-detects from the OS.
    """
    if is_dark is None:
        is_dark = is_system_dark_mode()

    if is_dark:
        # Modern Premium Dark Mode (Sleek Zinc / Teal Accent)
        colors = {
            "BG_MAIN": "#18181b",
            "BG_CARD": "#27272a",
            "BG_TREE_TABLE": "#18181b",
            "BG_HEADER": "#202023",
            "BG_BUTTON": "#27272a",
            "BG_DISABLED": "#202023",
            "BG_INPUT": "#202023",
            "TEXT": "#f4f4f5",
            "TEXT_MUTED": "#a1a1aa",
            "TEXT_DISABLED": "#52525b",
            "BORDER": "#3f3f46",
            "GRIDLINE": "#27272a",
            "ACCENT": "#00cccc",
            "HOVER": "#1e3d3d",
            "SCROLL_HANDLE": "#3f3f46"
        }
    else:
        # Modern Premium Light Mode (Sleek Gray-50 / Petrol Teal Accent)
        colors = {
            "BG_MAIN": "#f9fafb",
            "BG_CARD": "#ffffff",
            "BG_TREE_TABLE": "#ffffff",
            "BG_HEADER": "#f3f4f6",
            "BG_BUTTON": "#ffffff",
            "BG_DISABLED": "#f3f4f6",
            "BG_INPUT": "#ffffff",
            "TEXT": "#1f2937",
            "TEXT_MUTED": "#6b7280",
            "TEXT_DISABLED": "#9ca3af",
            "BORDER": "#e5e7eb",
            "GRIDLINE": "#f3f4f6",
            "ACCENT": "#008080",
            "HOVER": "#e0f2f1",
            "SCROLL_HANDLE": "#d1d5db"
        }

    return f"""
    /* Main Application Frame */
    QMainWindow {{
        background-color: {colors["BG_MAIN"]};
    }}

    /* General Labels */
    QLabel {{
        color: {colors["TEXT"]};
        font-size: 10pt;
        font-family: "Segoe UI", sans-serif;
    }}
    QLabel:disabled {{
        color: {colors["TEXT_DISABLED"]};
    }}

    /* Checkboxes */
    QCheckBox {{
        color: {colors["TEXT"]};
        font-size: 10pt;
        font-family: "Segoe UI", sans-serif;
    }}
    QCheckBox:disabled {{
        color: {colors["TEXT_DISABLED"]};
    }}

    /* Menu Bar */
    QMenuBar {{
        background-color: {colors["BG_MAIN"]};
        color: {colors["TEXT"]};
        border-bottom: 1px solid {colors["BORDER"]};
        font-size: 10pt;
        font-family: "Segoe UI", sans-serif;
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 6px 12px;
    }}
    QMenuBar::item:selected {{
        background-color: {colors["ACCENT"]};
        color: white;
    }}

    /* Tool Bar */
    QToolBar {{
        background-color: {colors["BG_CARD"]};
        border-bottom: 1px solid {colors["BORDER"]};
        spacing: 12px;
        padding: 6px;
    }}
    QToolBar QLabel {{
        color: {colors["TEXT"]};
        font-weight: bold;
    }}
    QToolBar QToolButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 6px 10px;
        color: {colors["TEXT"]};
    }}
    QToolBar QToolButton:hover {{
        background-color: {colors["HOVER"]};
        border: 1px solid {colors["ACCENT"]};
    }}
    QToolBar QToolButton:pressed {{
        background-color: {colors["ACCENT"]};
        color: white;
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {colors["BG_MAIN"]};
        border-top: 1px solid {colors["BORDER"]};
        color: {colors["TEXT"]};
        font-size: 9pt;
    }}

    /* Splitters */
    QSplitter::handle {{
        background-color: {colors["BORDER"]};
    }}

    /* Tree and Table Viewers */
    QTreeView, QTableView {{
        background-color: {colors["BG_TREE_TABLE"]};
        color: {colors["TEXT"]};
        border: 1px solid {colors["BORDER"]};
        gridline-color: {colors["GRIDLINE"]};
        selection-background-color: {colors["ACCENT"]};
        selection-color: white;
        font-size: 10pt;
        font-family: "Segoe UI", sans-serif;
    }}
    QTreeView::item, QTableView::item {{
        padding: 6px;
        border-bottom: 1px solid {colors["GRIDLINE"]};
    }}
    QTreeView::item:hover, QTableView::item:hover {{
        background-color: {colors["HOVER"]};
        color: {colors["TEXT"]};
    }}

    /* Table Headers */
    QHeaderView::section {{
        background-color: {colors["BG_HEADER"]};
        color: {colors["TEXT"]};
        padding: 8px;
        border: 1px solid {colors["BORDER"]};
        font-weight: bold;
        font-size: 10pt;
    }}

    /* Tab Widget and Tab Bar */
    QTabWidget::pane {{
        border: 1px solid {colors["BORDER"]};
        background-color: {colors["BG_CARD"]};
    }}
    QTabBar::tab {{
        background-color: {colors["BG_HEADER"]};
        color: {colors["TEXT_MUTED"]};
        border: 1px solid {colors["BORDER"]};
        border-bottom: none;
        padding: 8px 18px;
        margin-right: 4px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-size: 10pt;
    }}
    QTabBar::tab:selected {{
        background-color: {colors["BG_CARD"]};
        color: {colors["TEXT"]};
        border-bottom: 2px solid {colors["ACCENT"]};
        font-weight: bold;
    }}
    QTabBar::tab:hover {{
        background-color: {colors["HOVER"]};
        color: {colors["TEXT"]};
    }}

    /* Push Buttons */
    QPushButton {{
        background-color: {colors["BG_BUTTON"]};
        color: {colors["TEXT"]};
        border: 1px solid {colors["BORDER"]};
        border-radius: 4px;
        padding: 6px 16px;
        font-size: 10pt;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {colors["HOVER"]};
        border-color: {colors["ACCENT"]};
    }}
    QPushButton:pressed {{
        background-color: {colors["ACCENT"]};
        color: white;
    }}
    QPushButton:disabled {{
        background-color: {colors["BG_DISABLED"]};
        color: {colors["TEXT_DISABLED"]};
        border-color: {colors["BORDER"]};
    }}

    /* Inputs */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {colors["BG_INPUT"]};
        border: 1px solid {colors["BORDER"]};
        border-radius: 4px;
        padding: 4px;
        color: {colors["TEXT"]};
        font-size: 10pt;
        min-height: 28px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {colors["ACCENT"]};
    }}
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
        background-color: {colors["BG_DISABLED"]};
        color: {colors["TEXT_DISABLED"]};
    }}
    QComboBox QAbstractItemView {{
        background-color: {colors["BG_INPUT"]};
        color: {colors["TEXT"]};
        border: 1px solid {colors["BORDER"]};
        selection-background-color: {colors["ACCENT"]};
        selection-color: white;
    }}

    /* Group Boxes */
    QGroupBox {{
        border: 1px solid {colors["BORDER"]};
        border-radius: 6px;
        margin-top: 14px;
        font-weight: bold;
        color: {colors["ACCENT"]};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 4px;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {colors["BG_MAIN"]};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {colors["SCROLL_HANDLE"]};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {colors["ACCENT"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: {colors["BG_MAIN"]};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {colors["SCROLL_HANDLE"]};
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {colors["ACCENT"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
    }}

    /* Dialog & QMessageBox Styles */
    QDialog, QMessageBox {{
        background-color: {colors["BG_MAIN"]};
        color: {colors["TEXT"]};
    }}
    QMessageBox QLabel {{
        color: {colors["TEXT"]};
        background-color: transparent;
    }}
    """
