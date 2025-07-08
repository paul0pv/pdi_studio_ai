# ui/widgets/histogram_worker.py

from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np
from skimage import metrics


class HistogramWorker(QObject):
    finished = pyqtSignal(np.ndarray, dict)  # histograma, métricas

    def __init__(self, original, processed, mode="grayscale"):
        super().__init__()
        self.original = original
        self.processed = processed
        self.mode = mode

    def run(self):
        try:
            if self.mode == "grayscale":
                gray = np.mean(self.processed, axis=2).astype(np.uint8)
                hist, _ = np.histogram(gray, bins=256, range=(0, 256))
            else:
                hist = np.zeros((3, 256), dtype=int)
                for i in range(3):
                    hist[i], _ = np.histogram(
                        self.processed[:, :, i], bins=256, range=(0, 256)
                    )

            with np.errstate(divide="ignore", invalid="ignore"):
                psnr = metrics.peak_signal_noise_ratio(
                    self.original, self.processed, data_range=255
                )
                ssim = metrics.structural_similarity(
                    self.original, self.processed, channel_axis=-1
                )
                diff = np.mean(
                    np.abs(
                        self.original.astype(np.int16) - self.processed.astype(np.int16)
                    )
                )

            self.finished.emit(hist, {"psnr": psnr, "ssim": ssim, "diff": diff})
        except Exception as e:
            print(f"[HistogramWorker] ❌ Error: {e}")
