# ui/widgets/style_input_preview.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from llm.pipeline_generator import PipelineGenerator
from processing.image_processor import ImageProcessor
from processing.semantic_classifier import classify_style
from config.presets import add_preset
from config.preset_meta import tag_preset
from ui.widgets.preview_window import PreviewWindow


class StyleInputPreview(QWidget):
    def __init__(self, camera_feed, pipeline_applier=None, parent=None):
        super().__init__(parent)
        self.camera_feed = camera_feed
        self.pipeline_applier = pipeline_applier
        self.pipeline_generator = PipelineGenerator()
        self.pipeline = None
        self.prompt = ""

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.label = QLabel("Describe el estilo de imagen que deseas:")
        layout.addWidget(self.label)

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText(
            "Ejemplo: Quiero un estilo pop art con colores saturados..."
        )
        layout.addWidget(self.input_box)

        self.analyze_button = QPushButton("Generar pipeline con IA")
        self.analyze_button.clicked.connect(self._analyze_prompt)
        layout.addWidget(self.analyze_button)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.apply_button = QPushButton("Aplicar al frame actual")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self._apply_pipeline_to_frame)
        layout.addWidget(self.apply_button)

        self.style_label = QLabel("Estilo detectado: -")
        self.style_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.style_label)

    def _analyze_prompt(self):
        self.prompt = self.input_box.toPlainText().strip()
        if not self.prompt:
            self.result_display.setText("⚠️ Por favor ingresa una descripción.")
            return

        try:
            detected_style = classify_style(self.prompt)
            self.style_label.setText(f"Estilo detectado: {detected_style}")
        except Exception as e:
            self.style_label.setText("❌ Error clasificando estilo.")
            self.result_display.setText(str(e))
            return

        pipeline = self.pipeline_generator.generate(self.prompt)
        if not pipeline:
            self.result_display.setText("🚫 No se pudo generar una pipeline válida.")
            return

        import json

        self.pipeline = pipeline
        self.result_display.setText(json.dumps(pipeline, indent=2, ensure_ascii=False))
        self.apply_button.setEnabled(True)

    def _apply_pipeline_to_frame(self):
        if not self.pipeline or not isinstance(self.pipeline, list):
            QMessageBox.warning(self, "Error", "Pipeline no válida.")
            return

        latest_frame = self.camera_feed.get_latest_frame()
        if latest_frame is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el frame actual.")
            return

        processor = ImageProcessor()
        result_frame = processor.apply_custom_pipeline(latest_frame, self.pipeline)

        # Guardar como preset
        preset_name = self.prompt.lower().replace(" ", "_")[:40]
        add_preset(preset_name, self.pipeline)
        try:
            style = classify_style(self.prompt)
            tag_preset(preset_name, style)
        except:
            pass

        # Callback para aplicar al sistema principal
        def apply_to_main_pipeline():
            if self.pipeline_applier:
                self.pipeline_applier(self.pipeline)

        # Mostrar ventana de comparación
        self.preview_window = PreviewWindow(
            latest_frame,
            result_frame,
            on_apply_callback=apply_to_main_pipeline,
            verbose=True,
            show_metrics=True,
            split_view=True,
        )
        self.preview_window.show()
