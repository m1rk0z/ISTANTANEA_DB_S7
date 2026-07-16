import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Add current directory to path to ensure relative imports inside src work seamlessly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("IstanteS7")
    logger.info("Initializing IstanteS7 Application...")
    
    # Initialize PyQt application
    app = QApplication(sys.argv)
    
    # Launch main window
    window = MainWindow()
    window.show()
    
    # Run application loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
