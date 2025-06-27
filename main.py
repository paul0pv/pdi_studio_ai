# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the QApplication instance
    main_window = MainWindow()  # Create your main window
    main_window.show()  # Show the main window
    sys.exit(app.exec())  # Start the event loop and exit cleanly
