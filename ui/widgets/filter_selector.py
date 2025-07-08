# ui/widgets/filter_selector.py

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QSizePolicy,
    QLineEdit,
)
from PyQt6.QtCore import pyqtSignal


class FilterSelector(QGroupBox):
    filter_selected_to_add = pyqtSignal(str)

    def __init__(self, available_filters: list = None, parent=None):
        super().__init__("Añadir nuevo filtro", parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(120)
        self.setMaximumHeight(180)

        self._filter_metadata = {}
        self._available_filters_list = []
        self._filtered_list = []

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self._build_ui()

        if available_filters:
            self.set_available_filters(available_filters)

    def _build_ui(self):
        # --- Fila de búsqueda ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self._filter_combobox_items)
        search_layout.addWidget(self.search_input)
        self.main_layout.addLayout(search_layout)

        # --- Fila de selección ---
        selection_row_layout = QHBoxLayout()
        selection_row_layout.addWidget(QLabel("Seleccionar filtro:"))

        self.filter_combobox = QComboBox()
        self.filter_combobox.currentIndexChanged.connect(
            self._update_filter_description
        )
        selection_row_layout.addWidget(self.filter_combobox)

        self.add_filter_button = QPushButton("Añadir filtro")
        self.add_filter_button.clicked.connect(self._on_add_filter_clicked)
        selection_row_layout.addWidget(self.add_filter_button)

        self.main_layout.addLayout(selection_row_layout)

        # --- Descripción ---
        self.description_label = QLabel("Selecciona un filtro para ver su descripción.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-style: italic; color: gray;")
        self.main_layout.addWidget(self.description_label)

    def set_available_filters(self, filter_names: list, filter_metadata: dict = None):
        self._available_filters_list = sorted(filter_names)
        self._filtered_list = self._available_filters_list.copy()
        if filter_metadata:
            self._filter_metadata = filter_metadata
        self._refresh_combobox()

    def _refresh_combobox(self):
        self.filter_combobox.clear()
        if self._filtered_list:
            self.filter_combobox.addItems(self._filtered_list)
            self.filter_combobox.setCurrentIndex(0)
            self._update_filter_description(0)
            self.filter_combobox.setEnabled(True)
            self.add_filter_button.setEnabled(True)
        else:
            self.filter_combobox.addItem("No hay filtros disponibles")
            self.filter_combobox.setEnabled(False)
            self.add_filter_button.setEnabled(False)
            self.description_label.setText("No se encontraron filtros.")

    def _filter_combobox_items(self, text: str):
        text = text.lower().strip()
        self._filtered_list = [
            name for name in self._available_filters_list if text in name.lower()
        ]
        self._refresh_combobox()

    def _update_filter_description(self, index: int):
        if index < 0 or index >= len(self._filtered_list):
            self.description_label.setText("Sin descripción.")
            return
        selected = self._filtered_list[index]
        desc = self._filter_metadata.get(selected, {}).get(
            "description", "Sin descripción."
        )
        self.description_label.setText(desc)

    def _on_add_filter_clicked(self):
        selected = self.filter_combobox.currentText()
        if selected and selected != "No hay filtros disponibles":
            self.filter_selected_to_add.emit(selected)
        else:
            print("[FilterSelector] ⚠️ No hay filtro válido seleccionado.")
