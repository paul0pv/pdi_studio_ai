# processing/image_processor.py

import cv2
import numpy as np
import copy
from typing import List, Dict, Any
from processing import filters
from processing.validation import validate_filter_params
from skimage.metrics import (
    peak_signal_noise_ratio as psnr,
    structural_similarity as ssim,
)


class ImageProcessor:
    def __init__(self):
        self.pipeline = []
        self.available_filters = {
            name: info["function"] for name, info in filters.FILTER_METADATA.items()
        }
        print(
            f"[ImageProcessor] Filtros disponibles: {list(self.available_filters.keys())}"
        )

    def add_filter(self, filter_name: str, params: dict = None, index: int = None):
        if filter_name not in self.available_filters:
            print(f"[⚠️] Filtro '{filter_name}' no disponible.")
            return

        if params is None:
            params = filters.get_default_filter_params(filter_name)

        entry = {"name": filter_name, "params": params, "enabled": True}
        if index is None:
            self.pipeline.append(entry)
        else:
            self.pipeline.insert(index, entry)
        print(f"[+] Filtro '{filter_name}' añadido. Pipeline actual: {self.pipeline}")

    def remove_filter(self, index: int):
        if 0 <= index < len(self.pipeline):
            removed = self.pipeline.pop(index)
            print(f"[-] Filtro '{removed['name']}' eliminado.")
        else:
            print(f"[⚠️] Índice {index} fuera de rango.")

    def reorder_filter(self, old_index: int, new_index: int):
        if 0 <= old_index < len(self.pipeline) and 0 <= new_index < len(self.pipeline):
            f = self.pipeline.pop(old_index)
            self.pipeline.insert(new_index, f)
            print(f"[↔️] Filtro reordenado: {old_index} → {new_index}")
        else:
            print(f"[⚠️] Reordenamiento inválido.")

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        processed = frame.copy()
        for entry in self.pipeline:
            if not entry.get("enabled", True):
                continue
            name = entry["name"]
            raw_params = entry.get("params", {})
            params = validate_filter_params(name, raw_params)
            func = self.available_filters.get(name)
            if func:
                try:
                    processed = func(processed, **params)
                except Exception as e:
                    print(f"[❌] Error en filtro '{name}': {e}")
            else:
                print(f"[⚠️] Función para '{name}' no encontrada.")
        return processed

    def apply_custom_pipeline(
        self, frame: np.ndarray, pipeline: List[Dict[str, Any]]
    ) -> np.ndarray:
        processed = frame.copy()
        for entry in pipeline:
            name = entry.get("name")
            raw_params = entry.get("params", {})
            if name not in self.available_filters:
                print(f"[⚠️] Filtro '{name}' no disponible.")
                continue
            params = validate_filter_params(name, raw_params)
            try:
                processed = self.available_filters[name](processed, **params)
            except Exception as e:
                print(f"[❌] Error aplicando '{name}': {e}")
        return processed

    def get_histogram_data(self, gray_image: np.ndarray) -> np.ndarray:
        if gray_image is None or gray_image.size == 0:
            return np.zeros(256, dtype=np.int32)
        if len(gray_image.shape) == 3:
            gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        return hist.flatten()

    def set_pipeline(self, pipeline_config: list):
        validated = []
        for entry in pipeline_config:
            name = entry.get("name")
            if name not in self.available_filters:
                print(f"[⚠️] Filtro '{name}' no reconocido. Omitido.")
                continue
            enabled = entry.get("enabled", True)
            params = entry.get("params", {})
            if "enabled" in params:
                del params["enabled"]
            validated.append({"name": name, "params": params, "enabled": enabled})
        self.pipeline = validated
        print(f"[✓] Pipeline configurado: {self.pipeline}")

    def get_pipeline(self) -> list:
        return copy.deepcopy(self.pipeline)

    def compute_metrics(
        self, original: np.ndarray, processed: np.ndarray
    ) -> Dict[str, float]:
        """Calcula métricas de calidad entre imagen original y procesada."""
        if original.shape != processed.shape:
            processed = cv2.resize(processed, (original.shape[1], original.shape[0]))
        gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        gray_proc = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        return {"psnr": psnr(gray_orig, gray_proc), "ssim": ssim(gray_orig, gray_proc)}

    @property
    def filter_metadata(self):
        return filters.FILTER_METADATA
