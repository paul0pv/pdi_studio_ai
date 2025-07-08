# llm/llm_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
from llm.pipeline_generator import PipelineGenerator
# from typing import List, Dict, Any


class LLMWorker(QThread):
    pipeline_ready = pyqtSignal(list)  # Emits the generated pipeline
    fallback_used = pyqtSignal(str)  # Emits the fallback style used
    error_occurred = pyqtSignal(str)  # Emits critical errors

    def __init__(self, generator: PipelineGenerator, prompt: str, parent=None):
        super().__init__(parent)
        self.generator = generator
        self.prompt = prompt
        self.success = False  # Execution state

    def run(self):
        try:
            if not self.prompt.strip():
                self.error_occurred.emit("El prompt está vacío.")
                return

            pipeline = self.generator.generate(self.prompt)

            if pipeline is None or not isinstance(pipeline, list):
                self.error_occurred.emit("No se pudo generar una pipeline válida.")
                return

            if getattr(self.generator, "last_used_fallback", False):
                self.fallback_used.emit(self.generator.last_fallback_style)

            self.pipeline_ready.emit(pipeline)
            self.success = True

        except Exception as e:
            self.error_occurred.emit(f"❌ Error en LLMWorker: {e}")
