# Stylesheet and UI styling constants for Simatic Manager Retro Theme

# Siemens Branding Colors
SIEMENS_TEAL = "#009999"      # Classic Siemens Petrol Teal
SIEMENS_DARK = "#006666"      # Darker Petrol
WIN_GRAY = "#f0f0f0"          # Classic Windows Gray background
WIN_BORDER = "#a0a0a0"        # Border gray
TEXT_DARK = "#202020"         # Main dark text color

RETRO_STYLE = f"""
/* Main Application Frame */
QMainWindow {{
    background-color: {WIN_GRAY};
}}

/* General Labels */
QLabel {{
    color: {TEXT_DARK};
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QLabel:disabled {{
    color: #707070;
}}

/* Checkboxes */
QCheckBox {{
    color: {TEXT_DARK};
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QCheckBox:disabled {{
    color: #707070;
}}

/* Menu Bar */
QMenuBar {{
    background-color: {WIN_GRAY};
    color: {TEXT_DARK};
    border-bottom: 1px solid {WIN_BORDER};
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
}}

QMenuBar::item:selected {{
    background-color: {SIEMENS_TEAL};
    color: white;
}}

/* Tool Bar */
QToolBar {{
    background-color: {WIN_GRAY};
    border-bottom: 1px solid {WIN_BORDER};
    spacing: 8px;
    padding: 6px;
}}

QToolBar QLabel {{
    color: {TEXT_DARK};
    font-weight: bold;
}}

QToolBar QLabel:disabled {{
    color: #707070;
}}

QToolBar QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 4px;
    color: {TEXT_DARK};
}}

QToolBar QToolButton:hover {{
    background-color: #e0f2f1;
    border: 1px solid {SIEMENS_TEAL};
}}

QToolBar QToolButton:pressed {{
    background-color: #b2dfdb;
}}

/* Status Bar */
QStatusBar {{
    background-color: {WIN_GRAY};
    border-top: 1px solid {WIN_BORDER};
    color: {TEXT_DARK};
    font-size: 9pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

/* Splitters */
QSplitter::handle {{
    background-color: {WIN_BORDER};
}}

/* Tree and Table Viewers */
QTreeView, QTableView {{
    background-color: white;
    color: {TEXT_DARK};
    border: 1px solid {WIN_BORDER};
    gridline-color: #e0e0e0;
    selection-background-color: {SIEMENS_TEAL};
    selection-color: white;
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QTreeView::item, QTableView::item {{
    padding: 4px;
}}

/* Table Headers */
QHeaderView::section {{
    background-color: #e0e0e0;
    color: {TEXT_DARK};
    padding: 6px;
    border: 1px solid {WIN_BORDER};
    font-weight: bold;
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

/* Tab Widget and Tab Bar */
QTabWidget::pane {{
    border: 1px solid {WIN_BORDER};
    background-color: white;
}}

QTabBar::tab {{
    background-color: #e0e0e0;
    color: #404040;
    border: 1px solid {WIN_BORDER};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 3px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QTabBar::tab:selected {{
    background-color: white;
    color: #000000;
    border-bottom: 1px solid white;
    font-weight: bold;
}}

QTabBar::tab:hover {{
    background-color: #eaeaea;
    color: #000000;
}}

/* Push Buttons */
QPushButton {{
    background-color: {WIN_GRAY};
    color: {TEXT_DARK};
    border: 1px solid {WIN_BORDER};
    border-radius: 3px;
    padding: 6px 16px;
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QPushButton:hover {{
    background-color: #e2f4f4;
    border-color: {SIEMENS_TEAL};
}}

QPushButton:pressed {{
    background-color: #cdeaea;
}}

QPushButton:disabled {{
    background-color: #e0e0e0;
    color: #888888;
    border-color: #c0c0c0;
}}

/* Inputs (LineEdits, SpinBoxes, ComboBoxes) */
QLineEdit, QComboBox, QSpinBox {{
    background-color: white;
    border: 1px solid {WIN_BORDER};
    border-radius: 2px;
    padding: 2px;
    color: {TEXT_DARK};
    font-size: 10pt;
    font-family: "Segoe UI", "Tahoma", sans-serif;
    min-height: 24px;
    height: 24px;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {SIEMENS_TEAL};
}}

QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
    background-color: #e8e8e8;
    color: #707070;
}}

/* Explicitly style QComboBox popup dropdown items to avoid white-text-on-white-background rendering bugs in Windows Dark Mode */
QComboBox QAbstractItemView {{
    background-color: white;
    color: {TEXT_DARK};
    border: 1px solid {WIN_BORDER};
    selection-background-color: {SIEMENS_TEAL};
    selection-color: white;
}}

/* Group Boxes */
QGroupBox {{
    border: 1px solid {WIN_BORDER};
    border-radius: 4px;
    margin-top: 12px;
    font-weight: bold;
    color: {SIEMENS_DARK};
    font-family: "Segoe UI", "Tahoma", sans-serif;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
}}

/* Dialog & QMessageBox Styles for correct contrast in Windows Dark/Light mode */
QDialog, QMessageBox {{
    background-color: {WIN_GRAY};
    color: {TEXT_DARK};
}}

QMessageBox QLabel {{
    color: {TEXT_DARK};
    background-color: transparent;
}}
"""
