# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from config.settings import SettingsManager
from llm.pipeline_generator import PipelineGenerator
from ui.main_window.main_window import MainWindow
from setup_launcher import launch_setup_gui


def main():
    settings = SettingsManager()

    # Lanzar configuración inicial si no existe
    if not os.path.exists(settings.config_path):
        launch_setup_gui(settings)

    # Inicializar aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("PDI Studio AI")

    # Inicializar generador LLM si está habilitado
    llm_enabled = settings.get("llm_enabled", True)
    pipeline_generator = PipelineGenerator() if llm_enabled else None
    #    if llm_enabled and not os.path.exists(MODEL_DEST):
    #        QMessageBox.warning(
    #            self,
    #            "Modelo no encontrado",
    #            "⚠️ El modelo LLM no está disponible. Algunas funciones estarán desactivadas.",
    #        )

    # Crear ventana principal
    main_window = MainWindow(pipeline_generator=pipeline_generator)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error crítico al iniciar la aplicación: {e}")
