# ui/widgets/histogram_plotter.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class HistogramPlotter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Create a Matplotlib Figure and Axis
        self.figure = Figure(figsize=(5, 3), dpi=100)  # Adjust size as needed
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)  # One subplot

        # Initial plot setup
        self.ax.set_title("Histograma de escala de grises")
        self.ax.set_xlabel("Intensidad")
        self.ax.set_ylabel("Conteo")
        self.ax.set_xlim([0, 256])  # 0-255 for 8-bit grayscale
        self.ax.set_ylim(
            [0, 25000]
        )  # Initial Y-limit, will auto-scale or can be set dynamically

        (self.line,) = self.ax.plot(np.arange(256), np.zeros(256), color="blue")
        self.figure.tight_layout()  # Adjust layout to prevent labels overlapping

    def update_plot(self, hist_data: np.ndarray):
        """
        Updates the histogram plot with new data.
        hist_data should be a 256-element NumPy array representing pixel counts.
        """
        if hist_data is None or hist_data.size != 256:
            # Handle cases where data is invalid or not yet available
            return

        # Reshape hist_data if it's not 1D (cv2.calcHist returns 2D array)
        hist_data = hist_data.ravel()

        self.line.set_ydata(hist_data)  # Update the Y-data of the plot

        # Auto-scale Y-axis if current max exceeds limits, or set a fixed max
        # A fixed max makes the plot more stable, auto-scaling can make it jumpy.
        current_max = np.max(hist_data)
        if current_max > self.ax.get_ylim()[1]:
            self.ax.set_ylim([0, current_max * 1.1])  # Add 10% padding

        self.canvas.draw_idle()  # Redraw the canvas efficiently
