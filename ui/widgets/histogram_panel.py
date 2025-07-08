# ui/widgets/histogram_panel.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import QThreadPool, Qt
from ui.widgets.histogram_task import HistogramTask
from ui.widgets.histogram_plotter_pg import HistogramPlotter
from skimage import metrics
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
import csv


class HistogramPanel(QWidget):
    def __init__(self, image_processor, parent=None):
        super().__init__(parent)
        self.image_processor = image_processor
        self.auto_update = True
        self.diff_view_enabled = True
        self.histogram_mode = "grayscale"
        self.original_frame = None
        self.processed_frame = None
        self.thread_pool = QThreadPool.globalInstance()
        self._pending_frame = None
        self._task_running = False

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Estado: Listo")
        layout.addWidget(self.status_label)

        # Selector de modo
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo de histograma:"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["grayscale", "rgb"])
        self.mode_selector.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_selector)

        self.auto_update_checkbox = QCheckBox("Actualización automática")
        self.auto_update_checkbox.setChecked(True)
        self.auto_update_checkbox.stateChanged.connect(self._on_auto_update_toggled)
        mode_layout.addWidget(self.auto_update_checkbox)

        manual_btn = QPushButton("🔁 Actualizar ahora")
        manual_btn.clicked.connect(self._manual_update)
        mode_layout.addWidget(manual_btn)

        layout.addLayout(mode_layout)

        # Histograma
        self.histogram_plotter = HistogramPlotter(mode=self.histogram_mode)
        layout.addWidget(self.histogram_plotter)

        # Métricas
        self.metrics_label = QLabel("Métricas: PSNR: -, SSIM: -, Δabs: -")
        layout.addWidget(self.metrics_label)

        # Vista de diferencia
        self.diff_checkbox = QCheckBox("Mostrar diferencia absoluta")
        self.diff_checkbox.setChecked(True)
        self.diff_checkbox.stateChanged.connect(self._on_diff_toggle)
        layout.addWidget(self.diff_checkbox)

        self.diff_view = pg.ImageView()
        layout.addWidget(self.diff_view)

        # Botones de exportación
        export_layout = QHBoxLayout()
        export_img_btn = QPushButton("📷 Exportar imagen")
        export_csv_btn = QPushButton("📄 Exportar CSV")
        export_img_btn.clicked.connect(self._export_image)
        export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(export_img_btn)
        export_layout.addWidget(export_csv_btn)
        layout.addLayout(export_layout)

    def update_with_frame(self, original_frame, processed_frame):
        if not self.auto_update:
            self._pending_frame = (original_frame, processed_frame)
            return

        if self._task_running:
            self._pending_frame = (original_frame, processed_frame)
            return

        self._start_task(original_frame, processed_frame)

    def _start_task(self, original, processed):
        self._task_running = True
        task = HistogramTask(
            original, processed, self.histogram_mode, callback=self._on_task_finished
        )
        self.status_label.setText("Estado: Procesando...")
        self.thread_pool.start(task)

    def _on_task_finished(self, hist, metrics_dict):
        self._last_histogram = hist
        self.histogram_plotter.update_plot(hist)
        self.metrics_label.setText(
            f"Métricas: PSNR: {metrics_dict['psnr']:.2f}, "
            f"SSIM: {metrics_dict['ssim']:.3f}, Δabs: {metrics_dict['diff']:.1f}"
        )
        self._task_running = False
        self.status_label.setText("Estado: Listo")
        if self._pending_frame:
            next_original, next_processed = self._pending_frame
            self._pending_frame = None
            self._start_task(next_original, next_processed)
        if self.diff_view_enabled:
            diff_img = np.abs(
                self.original_frame.astype(np.int16)
                - self.processed_frame.astype(np.int16)
            ).astype(np.uint8)
            self.diff_view.setImage(diff_img.transpose(1, 0, 2), autoLevels=True)

    def _on_auto_update_toggled(self, state):
        self.auto_update = state == Qt.CheckState.Checked

    def _manual_update(self):
        if self._pending_frame:
            original, processed = self._pending_frame
            self._pending_frame = None
            self._start_task(original, processed)
        elif self.original_frame is not None and self.processed_frame is not None:
            self._start_task(self.original_frame, self.processed_frame)

    def _on_mode_changed(self, mode):
        if mode == self.histogram_mode:
            return
        self.histogram_mode = mode
        self.histogram_plotter.mode = mode
        self.histogram_plotter._init_plot()
        if self.processed_frame is not None:
            self.update_with_frame(self.original_frame, self.processed_frame)

    def _compute_histogram(self, frame, mode):
        if mode == "grayscale":
            gray = np.mean(frame, axis=2).astype(np.uint8)
            hist, _ = np.histogram(gray, bins=256, range=(0, 256))
            return hist
        elif mode == "rgb":
            hist = np.zeros((3, 256), dtype=int)
            for i in range(3):
                hist[i], _ = np.histogram(frame[:, :, i], bins=256, range=(0, 256))
            return hist

    def _update_metrics(self):
        try:
            original = self.original_frame.astype(np.uint8)
            processed = self.processed_frame.astype(np.uint8)
            with np.errstate(divide="ignore", invalid="ignore"):
                psnr = metrics.peak_signal_noise_ratio(
                    original, processed, data_range=255
                )
                ssim = metrics.structural_similarity(
                    original, processed, channel_axis=-1
                )
                diff = np.mean(
                    np.abs(original.astype(np.int16) - processed.astype(np.int16))
                )
            self.metrics_label.setText(
                f"Métricas: PSNR: {psnr:.2f}, SSIM: {ssim:.3f}, Δabs: {diff:.1f}"
            )
        except Exception as e:
            self.metrics_label.setText("Métricas: error")

    def _on_diff_toggle(self, state):
        self.diff_view_enabled = state == Qt.CheckState.Checked
        self.diff_view.setVisible(self.diff_view_enabled)

    def _export_image(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar histograma como imagen", "", "PNG (*.png);;JPG (*.jpg)"
        )
        if path:
            self.histogram_plotter.figure.savefig(path)

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar histograma como CSV", "", "CSV (*.csv)"
        )
        if path:
            hist = getattr(self, "_last_histogram", None)
            if hist is None:
                hist = self._compute_histogram(
                    self.processed_frame, self.histogram_mode
                )
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                if self.histogram_mode == "grayscale":
                    writer.writerow(["Intensidad", "Frecuencia"])
                    for i, val in enumerate(hist):
                        writer.writerow([i, val])
                else:
                    writer.writerow(["Intensidad", "R", "G", "B"])
                    for i in range(256):
                        writer.writerow([i, hist[0][i], hist[1][i], hist[2][i]])
