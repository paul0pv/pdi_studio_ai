# llm/llm_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
from llm.pipeline_generator import PipelineGenerator
from typing import List, Dict, Any


class LLMWorker(QThread):
    pipeline_ready = pyqtSignal(list)  # Emits the generated pipeline
    fallback_used = pyqtSignal(str)  # Emits the style used in fallback
    error_occurred = pyqtSignal(str)

    def __init__(self, generator: PipelineGenerator, prompt: str, parent=None):
        super().__init__(parent)
        self.generator = generator
        self.prompt = prompt

    def run(self):
        try:
            pipeline = self.generator.generate(self.prompt)
            if pipeline is None:
                self.error_occurred.emit("No se pudo generar una pipeline válida.")
                return

            # Detectar si se usó fallback (opcional: marcarlo en el pipeline)
            if getattr(self.generator, "last_used_fallback", False):
                self.fallback_used.emit(self.generator.last_fallback_style)

            self.pipeline_ready.emit(pipeline)

        except Exception as e:
            self.error_occurred.emit(f"Error en LLMWorker: {e}")
