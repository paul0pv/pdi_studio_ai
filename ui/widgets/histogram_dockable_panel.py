# ui/widgets/histogram_dockable_panel.py

from PyQt6.QtWidgets import QDockWidget, QWidget
from PyQt6.QtCore import Qt
from ui.widgets.histogram_panel import HistogramPanel


class HistogramDockablePanel(QDockWidget):
    def __init__(self, image_processor, parent=None):
        super().__init__("📊 Histograma y métricas", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        self.panel = HistogramPanel(image_processor)
        self.setWidget(self.panel)

    def update_with_frame(self, original_frame, processed_frame):
        self.panel.update_with_frame(original_frame, processed_frame)
