# ui/widgets/histogram_plotter_pg.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np


class HistogramPlotter(QWidget):
    def __init__(self, mode="grayscale", parent=None):
        super().__init__(parent)
        self.mode = mode
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setYRange(0, 10000)
        self.plot_widget.showGrid(x=True, y=True)
        layout.addWidget(self.plot_widget)
        self._init_plot()

    def _init_plot(self):
        self.plot_widget.clear()
        if self.mode == "grayscale":
            self.curve = self.plot_widget.plot(pen=pg.mkPen("k", width=2))
        else:
            self.curve_r = self.plot_widget.plot(pen=pg.mkPen("r", width=1))
            self.curve_g = self.plot_widget.plot(pen=pg.mkPen("g", width=1))
            self.curve_b = self.plot_widget.plot(pen=pg.mkPen("b", width=1))

    def update_plot(self, hist):
        if self.mode == "grayscale":
            self.curve.setData(hist)
        else:
            self.curve_r.setData(hist[0])
            self.curve_g.setData(hist[1])
            self.curve_b.setData(hist[2])
