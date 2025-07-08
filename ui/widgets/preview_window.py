# ui/widgets/preview_window.py

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
    QSlider,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from ui.widgets.histogram_plotter import HistogramPlotter
import cv2
import numpy as np
from skimage import metrics


class PreviewWindow(QWidget):
    def __init__(
        self,
        original_frame: np.ndarray,
        processed_frame: np.ndarray,
        on_apply_callback=None,
        verbose: bool = False,
    ):
        super().__init__()
        self.setWindowTitle("Comparación: Original vs Procesado")
        self.setMinimumSize(960, 540)
        self.on_apply_callback = on_apply_callback
        self.verbose = verbose

        self.original_frame = original_frame
        self.processed_frame = processed_frame
        self.on_apply_callback = on_apply_callback
        self.verbose = verbose
        self.histogram_mode = "grayscale"

        self.split_view_enabled = True

        layout = QVBoxLayout()

        # Validación de entrada
        if original_frame is None or processed_frame is None:
            QMessageBox.critical(self, "Error", "Uno de los frames es inválido.")
            self.close()
            return

        # Imagen principal
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider para split-view
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self._update_split_view)

        # Selector de modo de histograma
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Modo de histograma:")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["grayscale", "rgb"])
        self.mode_selector.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_selector)
        layout.addLayout(mode_layout)

        # Histograma
        self.histogram_plotter = HistogramPlotter(
            mode=self.histogram_mode, verbose=self.verbose
        )
        layout.addWidget(self.histogram_plotter)

        # Métricas
        self.metrics_label = QLabel()
        self.metrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metrics_label.setStyleSheet("font-weight: bold; color: #444;")

        # Botones
        self.toggle_button = QPushButton("Cambiar vista")
        self.toggle_button.clicked.connect(self._toggle_view)

        self.apply_button = QPushButton("Aplicar esta Pipeline")
        self.apply_button.clicked.connect(self._apply_pipeline)

        self.close_button = QPushButton("Cerrar")
        self.close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.toggle_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)

        layout.addWidget(self.image_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.metrics_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self._update_metrics()
        self._update_split_view()

    def _toggle_view(self):
        self.split_view_enabled = not self.split_view_enabled
        self.slider.setVisible(self.split_view_enabled)
        self._update_split_view()

    def _update_split_view(self):
        if self.split_view_enabled:
            alpha = self.slider.value() / 100.0
            blended = self._blend_images(
                self.original_frame, self.processed_frame, alpha
            )
            pixmap = self._convert_frame_to_pixmap(blended)
        else:
            combined = self._side_by_side(self.original_frame, self.processed_frame)
            pixmap = self._convert_frame_to_pixmap(combined)
        self.image_label.setPixmap(pixmap)

    def _blend_images(
        self, img1: np.ndarray, img2: np.ndarray, alpha: float
    ) -> np.ndarray:
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        mask = np.zeros_like(img1, dtype=np.uint8)
        split_col = int(img1.shape[1] * alpha)
        mask[:, :split_col] = 1
        blended = img1 * mask + img2 * (1 - mask)
        return blended.astype(np.uint8)

    def _side_by_side(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        return np.hstack((img1, img2))

    def update_histogram(self, original_frame, processed_frame):
        self.original_frame = original_frame
        self.processed_frame = processed_frame

        if self.histogram_mode == "grayscale":
            hist = self._compute_histogram(processed_frame, mode="grayscale")
        else:
            hist = self._compute_histogram(processed_frame, mode="rgb")

        self.histogram_plotter.update_plot(hist)
        self._update_split_view()
        self._update_metrics()

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
            if self.verbose:
                print(f"[PreviewWindow] ⚠️ Error al calcular métricas: {e}")
            self.metrics_label.setText("Métricas: error")

    def _compute_histogram(self, frame, mode="grayscale"):
        if mode == "grayscale":
            gray = np.mean(frame, axis=2).astype(np.uint8)
            hist, _ = np.histogram(gray, bins=256, range=(0, 256))
            return hist
        elif mode == "rgb":
            hist = np.zeros((3, 256), dtype=int)
            for i in range(3):
                hist[i], _ = np.histogram(frame[:, :, i], bins=256, range=(0, 256))
            return hist

    def _on_mode_changed(self, mode):
        self.histogram_mode = mode
        self.histogram_plotter.mode = mode
        self.histogram_plotter._init_plot()
        self.update_histogram(self.original_frame, self.processed_frame)

    def _convert_frame_to_pixmap(self, frame: np.ndarray) -> QPixmap:
        if frame is None or frame.size == 0:
            return QPixmap()

        if len(frame.shape) == 3:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
        else:
            h, w = frame.shape
            q_image = QImage(frame.data, w, h, w, QImage.Format.Format_Grayscale8)

        return QPixmap.fromImage(q_image).scaled(
            880,
            480,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _apply_pipeline(self):
        if self.on_apply_callback:
            self.on_apply_callback()
        self.close()
