# style_input_preview.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)
from llm.pipeline_generator import generate_pipeline
from processing.semantic_classifier import classify_style
from processing.image_processor import apply_custom_pipeline
from processing.filters import FILTER_METADATA
from video_capture.camera_feed import get_latest_frame


class StyleInputPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador Inteligente de Filtros")
        self.setMinimumHeight(400)

        layout = QVBoxLayout()

        self.input_label = QLabel("Describe el estilo que deseas:")
        self.input_field = QLineEdit()
        self.analyze_button = QPushButton("Generar Pipeline")
        self.style_label = QLabel("Estilo detectado:")
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.style_label)
        layout.addWidget(self.result_display)

        self.setLayout(layout)

        self.analyze_button.clicked.connect(self.analyze_query)
        self.apply_button = QPushButton("Aplicar Pipeline a Frame Actual")
        layout.addWidget(self.apply_button)

        self.apply_button.clicked.connect(self.apply_pipeline_to_frame)

    def analyze_query(self):
        text = self.input_field.text().strip()
        if not text:
            self.result_display.setText("⚠️ Ingrese una descripción.")
            return

        detected_style = classify_style(text)
        self.style_label.setText(f"Estilo detectado: {detected_style}")

        pipeline = generate_pipeline(text)
        if not pipeline:
            self.result_display.setText("🚫 No se pudo generar una pipeline válida.")
            return

        pretty_output = "\n".join(
            [f"→ {step['name']} | params: {step['params']}" for step in pipeline]
        )
        self.result_display.setText(pretty_output)

    def apply_pipeline_to_frame(self):
        if not self.result_display.toPlainText():
            print("[UI] No hay pipeline generada para aplicar.")
            return

        latest_frame = get_latest_frame()
        if latest_frame is None:
            print("[UI] No se pudo obtener el frame actual.")
            return

        # Reconstruir pipeline desde texto
        pipeline = generate_pipeline(self.input_field.text())
        if not pipeline:
            print("[UI] Pipeline no válida.")
            return

        result_frame = apply_custom_pipeline(latest_frame, pipeline, FILTER_METADATA)

        # Aquí puedes agregar código para visualizar el resultado
        # o emitir una señal para que el frame se muestre en el UI principal
        print("[UI] Pipeline aplicada exitosamente al frame actual.")
