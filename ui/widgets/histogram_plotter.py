# ui/widgets/histogram_plotter.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class HistogramPlotter(QWidget):
    def __init__(self, parent=None, mode: str = "grayscale", verbose: bool = False):
        """
        mode: 'grayscale' o 'rgb'
        """
        super().__init__(parent)
        self.mode = mode
        self.verbose = verbose
        self.layout = QVBoxLayout(self)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self._init_plot()

    def _init_plot(self):
        self.ax.clear()
        if self.mode == "grayscale":
            self.ax.set_title("Histograma de escala de grises")
            self.ax.set_xlabel("Intensidad")
            self.ax.set_ylabel("Conteo")
            self.ax.set_xlim([0, 256])
            self.ax.set_ylim([0, 25000])
            (self.line,) = self.ax.plot(np.arange(256), np.zeros(256), color="blue")
        elif self.mode == "rgb":
            self.ax.set_title("Histograma RGB")
            self.ax.set_xlabel("Intensidad")
            self.ax.set_ylabel("Conteo")
            self.ax.set_xlim([0, 256])
            self.ax.set_ylim([0, 25000])
            (self.line_r,) = self.ax.plot(
                np.arange(256), np.zeros(256), color="red", label="R"
            )
            (self.line_g,) = self.ax.plot(
                np.arange(256), np.zeros(256), color="green", label="G"
            )
            (self.line_b,) = self.ax.plot(
                np.arange(256), np.zeros(256), color="blue", label="B"
            )
            self.ax.legend(loc="upper right")
        self.figure.tight_layout()

    def update_plot(self, hist_data: np.ndarray):
        """
        Actualiza el histograma con nuevos datos.
        Para escala de grises: array de 256 elementos.
        Para RGB: array de shape (3, 256).
        """
        if hist_data is None or hist_data.size == 0:
            if self.verbose:
                print("[HistogramPlotter] ⚠️ Datos de histograma vacíos o inválidos.")
            return

        if self.mode == "grayscale":
            if hist_data.size != 256:
                if self.verbose:
                    print(
                        "[HistogramPlotter] ⚠️ Histograma inválido para escala de grises."
                    )
                return
            hist_data = hist_data.ravel()
            self.line.set_ydata(hist_data)
            self._rescale_y_axis(hist_data)

        elif self.mode == "rgb":
            if hist_data.shape != (3, 256):
                if self.verbose:
                    print("[HistogramPlotter] ⚠️ Histograma RGB inválido.")
                return
            self.line_r.set_ydata(hist_data[0])
            self.line_g.set_ydata(hist_data[1])
            self.line_b.set_ydata(hist_data[2])
            self._rescale_y_axis(hist_data)

        self.canvas.draw_idle()

    def _rescale_y_axis(self, data: np.ndarray):
        current_max = np.max(data)
        ymin, ymax = self.ax.get_ylim()
        if current_max > ymax or current_max < 0.5 * ymax:
            self.ax.set_ylim([0, max(1000, current_max * 1.1)])
