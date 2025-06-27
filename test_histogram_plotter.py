# test_histogram_plotter.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer  # Import QTimer
import numpy as np
from ui.widgets.histogram_plotter import HistogramPlotter  # Import the widget

print("--- Testing ui/widgets/histogram_plotter.py ---")


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Histogram Plotter Test")
        self.setGeometry(200, 200, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.hist_plotter = HistogramPlotter()
        layout.addWidget(self.hist_plotter)

        # --- Corrected QTimer instantiation and usage ---
        self.timer = QTimer(self)  # Create the QTimer instance, parented to TestWindow

        # Define a list of sample histogram data
        self.sample_hists = [
            np.random.randint(0, 10000, 256, dtype=np.int32),  # Low contrast
            np.random.randint(0, 50000, 256, dtype=np.int32),  # High counts
            np.concatenate(
                (np.zeros(100), np.random.randint(0, 20000, 56), np.zeros(100))
            ),  # Skewed right
            np.concatenate(
                (
                    np.random.randint(0, 20000, 56),
                    np.random.randint(0, 20000, 56),
                    np.zeros(144),
                )
            ),  # Simpler skewed left
            np.ones(256) * 1000,  # Flat histogram
        ]
        self.current_hist_idx = 0

        self.timer.timeout.connect(self.update_test_histogram)
        self.timer.start(1000)  # Update every 1 second

    def update_test_histogram(self):
        """Updates the histogram plot with simulated data."""
        hist_data = self.sample_hists[self.current_hist_idx]
        self.hist_plotter.update_plot(hist_data)
        print(
            f"Updating histogram with sample {self.current_hist_idx + 1}/{len(self.sample_hists)}"
        )
        self.current_hist_idx = (self.current_hist_idx + 1) % len(self.sample_hists)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
