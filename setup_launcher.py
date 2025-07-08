# setup_launcher.py
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QMessageBox,
    QProgressDialog,
)
from PyQt6.QtCore import Qt
import subprocess
import os
import sys
import urllib.request
from config.settings import SettingsManager

MODEL_URL = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
MODEL_DEST = os.path.join("models", "Phi-3-mini-4k-instruct-q4.gguf")
REQUIREMENTS_FILE = "requirements-llm.txt"


def launch_setup_gui(settings: SettingsManager):
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Configuración Inicial de PDI Studio AI")

    layout = QVBoxLayout()

    label = QLabel("¿Desea activar las funciones de IA (modelo de lenguaje)?")
    checkbox_ia = QCheckBox("Activar funciones de IA (requiere conexión a internet)")
    checkbox_model = QCheckBox("Descargar modelo Phi-3-mini ahora")
    checkbox_model.setEnabled(False)

    def toggle_model_checkbox(state):
        checkbox_model.setEnabled(checkbox_ia.isChecked())

    checkbox_ia.stateChanged.connect(toggle_model_checkbox)

    button = QPushButton("Continuar")

    def on_continue():
        llm_enabled = checkbox_ia.isChecked()
        download_model = checkbox_model.isChecked()

        settings.set("llm_enabled", llm_enabled)
        settings.set("suppress_llm_prompt", True)

        if llm_enabled:
            try:
                _install_llm_dependencies(window)
            except Exception as e:
                QMessageBox.critical(
                    window, "Error", f"No se pudieron instalar dependencias: {e}"
                )
                return

            if download_model:
                try:
                    _download_model(window)
                except Exception as e:
                    QMessageBox.critical(
                        window, "Error", f"No se pudo descargar el modelo: {e}"
                    )
                    return

        QMessageBox.information(
            window, "Listo", "✅ Configuración guardada correctamente."
        )
        window.close()

    button.clicked.connect(on_continue)

    layout.addWidget(label)
    layout.addWidget(checkbox_ia)
    layout.addWidget(checkbox_model)
    layout.addWidget(button)
    window.setLayout(layout)
    window.show()
    app.exec()


def _install_llm_dependencies(parent):
    if not os.path.exists(REQUIREMENTS_FILE):
        raise FileNotFoundError(f"No se encontró {REQUIREMENTS_FILE}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def _download_model(parent):
    os.makedirs(os.path.dirname(MODEL_DEST), exist_ok=True)
    progress = QProgressDialog("Descargando modelo...", "Cancelar", 0, 0, parent)
    progress.setWindowTitle("Descarga en curso")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.show()

    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_DEST)
        if not os.path.exists(MODEL_DEST) or os.path.getsize(MODEL_DEST) < 1_000_000:
            raise RuntimeError(
                "El modelo descargado parece estar incompleto o corrupto."
            )
    finally:
        progress.close()
