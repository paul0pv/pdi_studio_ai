# ui/main_window/layout_llm_group.py

from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QCheckBox,
)
from PyQt6.QtGui import QMovie
import os


def build_llm_group(main_window):
    group = QGroupBox("Asistente de Estilos (LLM)")
    layout = QVBoxLayout(group)

    main_window.llm_prompt_input = QLineEdit()
    main_window.llm_generate_button = QPushButton("Generar Pipeline con LLM")
    main_window.temperature_input = QDoubleSpinBox()
    main_window.temperature_input.setRange(0.0, 1.0)
    main_window.temperature_input.setValue(0.2)
    main_window.debug_checkbox = QCheckBox("Mostrar prompt generado")
    main_window.llm_status_label = QLabel("LLM: Listo")
    main_window.llm_loading_spinner = QLabel()

    spinner_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "resources", "loading_spinner.gif"
    )
    movie = QMovie(spinner_path)
    if movie.isValid():
        main_window.llm_movie = movie
        main_window.llm_loading_spinner.setMovie(movie)
        main_window.llm_loading_spinner.setFixedSize(32, 32)
        main_window.llm_loading_spinner.hide()

    layout.addWidget(main_window.llm_prompt_input)
    layout.addWidget(main_window.llm_generate_button)
    layout.addWidget(main_window.temperature_input)
    layout.addWidget(main_window.debug_checkbox)
    layout.addWidget(main_window.llm_status_label)
    layout.addWidget(main_window.llm_loading_spinner)
    return group
