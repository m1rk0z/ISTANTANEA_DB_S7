# Stylesheet and UI styling constants for Simatic Manager Retro Theme

SIEMENS_TEAL = "#009999"      # Classic Siemens Petrol Teal
SIEMENS_DARK = "#006666"      # Darker Petrol
WIN_GRAY = "#f0f0f0"          # Classic Windows Gray background
WIN_BORDER = "#a0a0a0"        # Border gray
TEXT_DARK = "#202020"

RETRO_STYLE = f"""
QMainWindow {{
    background-color: {WIN_GRAY};
}}

QMenuBar {{
    background-color: {WIN_GRAY};
    color: {TEXT_DARK};
    border-bottom: 1px solid {WIN_BORDER};
    font-size: 11pt;
}}

QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
}}

QMenuBar::item:selected {{
    background-color: {SIEMENS_TEAL};
    color: white;
}}

QToolBar {{
    background-color: {WIN_GRAY};
    border-bottom: 1px solid {WIN_BORDER};
    spacing: 6px;
    padding: 4px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 3px;
}}

QToolBar QToolButton:hover {{
    background-color: #e0f2f1;
    border: 1px solid {SIEMENS_TEAL};
}}

QToolBar QToolButton:pressed {{
    background-color: #b2dfdb;
}}

QStatusBar {{
    background-color: {WIN_GRAY};
    border-top: 1px solid {WIN_BORDER};
    color: {TEXT_DARK};
    font-size: 10pt;
}}

QSplitter::handle {{
    background-color: {WIN_BORDER};
}}

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
    padding: 3px;
}}

QHeaderView::section {{
    background-color: #e0e0e0;
    color: {TEXT_DARK};
    padding: 5px;
    border: 1px solid {WIN_BORDER};
    font-weight: bold;
    font-size: 10pt;
}}

QTabWidget::pane {{
    border: 1px solid {WIN_BORDER};
    background-color: white;
}}

QTabBar::tab {{
    background-color: #e0e0e0;
    border: 1px solid {WIN_BORDER};
    border-bottom: none;
    padding: 6px 12px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: normal;
}}

QTabBar::tab:selected {{
    background-color: white;
    border-bottom: 1px solid white;
    font-weight: bold;
}}

QTabBar::tab:hover {{
    background-color: #eaeaea;
}}

QPushButton {{
    background-color: {WIN_GRAY};
    color: {TEXT_DARK};
    border: 1px solid {WIN_BORDER};
    border-radius: 3px;
    padding: 5px 15px;
    font-size: 10pt;
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
    color: #a0a0a0;
    border-color: #c0c0c0;
}}

QLineEdit, QSpinBox, QComboBox {{
    background-color: white;
    border: 1px solid {WIN_BORDER};
    border-radius: 2px;
    padding: 3px;
    color: {TEXT_DARK};
    font-size: 10pt;
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {SIEMENS_TEAL};
}}

QGroupBox {{
    border: 1px solid {WIN_BORDER};
    border-radius: 4px;
    margin-top: 10px;
    font-weight: bold;
    color: {SIEMENS_DARK};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 3px;
}}
"""
