# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from llm.pipeline_generator import PipelineGenerator

if __name__ == "__main__":
    generator = PipelineGenerator()
    try:
        app = QApplication(sys.argv)  # Create the QApplication instance
        main_window = MainWindow(
            pipeline_generator=generator
        )  # Create your main window
        main_window.show()  # Show the main window
        sys.exit(app.exec())  # Start the event loop and exit cleanly
    except Exception as e:
        print(f"Error crítico al iniciar la aplicación: {e}")
