# style_input_preview.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)
from llm.pipeline_generator import PipelineGenerator
from processing.semantic_classifier import classify_style
from processing.filters import FILTER_METADATA
from ui.widgets.preview_window import PreviewWindow
from processing.image_processor import ImageProcessor
from config.preset_meta import tag_preset
from config.presets import add_preset


class StyleInputPreview(QWidget):
    def __init__(self, camera_feed_instance, pipeline_generator: PipelineGenerator):
        super().__init__()
        self.camera_feed = camera_feed_instance
        self.pipeline_generator = pipeline_generator
        self.setWindowTitle("Generador Inteligente de Filtros")
        self.setMinimumHeight(400)

        layout = QVBoxLayout()

        self.style_label = QLabel("Estilo detectado:")
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)

        layout.addWidget(self.style_label)
        layout.addWidget(self.result_display)

        self.setLayout(layout)

        self.apply_button = QPushButton("Aplicar Pipeline a Frame Actual")
        self.apply_button.setEnabled(False)

        layout.addWidget(self.apply_button)

        self.apply_button.clicked.connect(self.apply_pipeline_to_frame)

    def _analyze_prompt(self):
        if not self.prompt:
            self.result_display.setText("⚠️ No se recibió descripción.")
            return

        detected_style = classify_style(self.prompt)
        self.style_label.setText(f"Estilo detectado: {detected_style}")

        pipeline = self.pipeline_generator.generate(self.prompt)
        if not pipeline:
            self.result_display.setText("🚫 No se pudo generar una pipeline válida.")
            return

        import json

        self.pipeline = pipeline
        self.result_display.setText(json.dumps(pipeline, indent=2, ensure_ascii=False))

        self.apply_button.setEnabled(True)

    def set_prompt(self, prompt: str):
        self.prompt = prompt
        self._analyze_prompt()

    def apply_pipeline_to_frame(self):
        if not hasattr(self, "pipeline_generator"):
            raise RuntimeError("PipelineGenerator no fue inicializado correctamente.")

        prompt = getattr(self, "prompt", "").strip()
        preset_name = prompt.strip().lower().replace(" ", "_")[:40]

        if not prompt:
            print("[UI] No hay descripción para generar pipeline.")
            return

        latest_frame = self.camera_feed.get_latest_frame()
        if latest_frame is None:
            print("[UI] No se pudo obtener el frame actual.")
            return

        pipeline = getattr(self, "pipeline", None)
        if not pipeline:
            print("[UI] No hay pipeline generada.")
            return

        if not pipeline:
            print("[UI] Pipeline no válida.")
            return

        processor = ImageProcessor()
        result_frame = processor.apply_custom_pipeline(latest_frame, pipeline)

        add_preset(preset_name, pipeline)
        style = classify_style(prompt)
        if style:
            tag_preset(preset_name, style)

        # Callback para aplicar la pipeline al sistema principal
        def apply_to_main_pipeline():
            from ui.main_window import MainWindow  # evitar import circular si necesario

            main_window = self.parentWidget().window()
            main_window.pipeline_manager.set_pipeline_from_config(pipeline)
            main_window.image_processor.set_pipeline(pipeline)
            main_window.show_status_message(
                "Pipeline del LLM aplicada desde previsualización."
            )

        # Mostrar ventana emergente con comparación
        self.preview_window = PreviewWindow(
            latest_frame, result_frame, on_apply_callback=apply_to_main_pipeline
        )
        self.preview_window.show()
