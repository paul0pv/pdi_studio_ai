# processing/image_processor.py

import cv2
import numpy as np
from processing import filters
import copy
from typing import List, Dict, Any


class ImageProcessor:
    def __init__(self):
        self.pipeline = []

        self.available_filters = {}
        for filter_name, filter_info in filters.FILTER_METADATA.items():
            self.available_filters[filter_name] = filter_info["function"]

        print(
            f"ImageProcessor: Initialized with available filters: {list(self.available_filters.keys())}"
        )

    def add_filter(self, filter_name: str, params: dict = None, index: int = None):
        """Adds a filter to the processing pipeline."""
        if filter_name not in self.available_filters:
            print(f"Warning: Filter '{filter_name}' not available.")
            return

        if params is None:
            params = filters.get_default_filter_params(filter_name)

        filter_entry = {
            "name": filter_name,
            "params": params,
            "enabled": True,
        }

        if index is None:
            self.pipeline.append(filter_entry)
        else:
            self.pipeline.insert(index, filter_entry)
        print(
            f"ImageProcessor: Added filter '{filter_name}' to pipeline. Current pipeline: {self.pipeline}"
        )

    def remove_filter(self, index: int):
        """Removes a filter from the processing pipeline by index."""
        if 0 <= index < len(self.pipeline):
            removed_filter = self.pipeline.pop(index)
            print(
                f"ImageProcessor: Removed filter '{removed_filter['name']}' from pipeline. Current pipeline: {self.pipeline}"
            )
        else:
            print(f"Warning: Cannot remove filter. Index {index} is out of bounds.")

    def reorder_filter(self, old_index: int, new_index: int):
        """Reorders a filter in the processing pipeline."""
        if 0 <= old_index < len(self.pipeline) and 0 <= new_index < len(self.pipeline):
            filter_to_move = self.pipeline.pop(old_index)
            self.pipeline.insert(new_index, filter_to_move)
            print(
                f"ImageProcessor: Reordered filter from {old_index} to {new_index}. Current pipeline: {self.pipeline}"
            )
        else:
            print(f"Warning: Cannot reorder filter. Index out of bounds.")

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Applies all enabled filters in the pipeline to the given frame.
        """
        processed_frame = frame.copy()

        for filter_entry in self.pipeline:
            # Ensure 'enabled' key exists (though set_pipeline should guarantee this)
            # Use .get() with a default in case of malformed entries for robustness
            if filter_entry.get("enabled", True):  # Access 'enabled' at the top level
                filter_name = filter_entry["name"]
                filter_params = filter_entry.get(
                    "params", {}
                )  # Get params, default to empty dict

                filter_func = self.available_filters.get(filter_name)
                if filter_func:
                    processed_frame = filter_func(processed_frame, **filter_params)
                else:
                    print(f"Warning: Filter function for '{filter_name}' not found.")
        return processed_frame

    def get_histogram_data(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculates the histogram of a grayscale image."""
        if gray_image is None or gray_image.size == 0:
            return np.zeros(256, dtype=np.int32)

        if len(gray_image.shape) == 3:
            gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)

        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        return hist.flatten()

    def set_pipeline(self, pipeline_config: list):
        """
        Sets the entire pipeline from a configuration (e.g., loaded from preset or LLM).
        Ensures each filter entry has a top-level 'enabled' key.
        """
        validated_pipeline = []
        for entry in pipeline_config:
            filter_name = entry.get("name")
            if filter_name not in self.available_filters:
                print(
                    f"Warning: Filter '{filter_name}' in provided pipeline config is not available. Skipping."
                )
                continue

            # Get 'enabled' state, default to True if not present at top level
            enabled_state = entry.get("enabled", True)

            # Get params, default to empty dict if not present
            params = entry.get("params", {})
            # Ensure 'enabled' is NOT duplicated inside 'params' if it was somehow loaded there
            if "enabled" in params:
                del params["enabled"]

            validated_pipeline.append(
                {"name": filter_name, "params": params, "enabled": enabled_state}
            )

        self.pipeline = validated_pipeline
        print(f"ImageProcessor: Pipeline set to: {self.pipeline}")

    def get_pipeline(self) -> list:
        """Returns the current pipeline configuration."""
        return copy.deepcopy(self.pipeline)

    def apply_custom_pipeline(
        self, frame: np.ndarray, pipeline: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Aplica una pipeline externa directamente a un frame, sin alterar la pipeline interna.
        Ideal para pipelines generadas dinámicamente (LLM, presets, etc.).
        """
        processed = frame.copy()

        for entry in pipeline:
            name = entry.get("name")
            params = entry.get("params", {})
            if name not in self.available_filters:
                print(f"ImageProcessor: Filtro '{name}' no disponible. Ignorando.")
                continue

            filter_fn = self.available_filters[name]
            try:
                processed = filter_fn(processed, **params)
            except Exception as e:
                print(f"ImageProcessor: Error aplicando '{name}' → {e}")
                continue

        return processed
