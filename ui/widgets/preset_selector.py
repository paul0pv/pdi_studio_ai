# ui/widgets/preset_selector.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QMenu,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from config.presets import (
    load_presets,
    add_preset,
    remove_preset,
    rename_preset,
    export_preset_to_json,
    import_preset_from_json,
)
from config.preset_meta import tag_preset, get_preset_tags


class PresetSelector(QWidget):
    preset_applied = pyqtSignal(str, list)

    def __init__(self, pipeline_applier=None, pipeline_source=None, parent=None):
        super().__init__(parent)
        self.pipeline_applier = pipeline_applier
        self.pipeline_source = pipeline_source
        self.presets = load_presets()
        self.tags = get_preset_tags()
        self.active_filter = None

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self._build_ui()

    def _build_ui(self):
        # Filtro por estilo
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filtrar por estilo:"))
        self.style_filter = QComboBox()
        self.style_filter.addItem("Todos")
        estilos = sorted(set(tag for tags in self.tags.values() for tag in tags))
        self.style_filter.addItems(estilos)
        self.style_filter.currentTextChanged.connect(self._filter_presets)
        filter_row.addWidget(self.style_filter)
        self.layout.addLayout(filter_row)

        # Lista de presets
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_preset_selected)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.layout.addWidget(self.list_widget)

        # Vista previa
        self.preview = QLabel("Vista previa:")
        self.preview.setStyleSheet("font-style: italic; color: gray;")
        self.layout.addWidget(self.preview)

        # Guardar nuevo preset
        name_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del nuevo preset")
        name_row.addWidget(self.name_input)

        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self._save_current_pipeline)
        name_row.addWidget(self.save_btn)
        self.layout.addLayout(name_row)

        self._refresh_list()

    def refresh(self):
        """
        Recarga la lista de presets desde el archivo de configuración.
        """
        self._refresh_list()

    def _refresh_list(self):
        self.list_widget.clear()
        self.presets = load_presets()
        self.tags = get_preset_tags()
        for name in sorted(self.presets.keys()):
            if self.active_filter and self.active_filter != "Todos":
                if self.active_filter not in self.tags.get(name, []):
                    continue
            item = QListWidgetItem(name)
            tags = self.tags.get(name, [])
            if tags:
                item.setToolTip(f"Estilo: {', '.join(tags)}")
            self.list_widget.addItem(item)

    def _filter_presets(self, selected_style):
        self.active_filter = selected_style
        self._refresh_list()

    def _on_preset_selected(self, item):
        name = item.text()
        if name in self.presets:
            import json

            self.preview.setText(
                json.dumps(self.presets[name], indent=2, ensure_ascii=False)
            )
            if self.pipeline_applier:
                self.pipeline_applier(self.presets[name])

    def _save_current_pipeline(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setPlaceholderText("⚠️ Ingresa un nombre válido")
            return

        if not self.pipeline_source:
            QMessageBox.warning(
                self, "Guardar", "No se ha definido la fuente de pipeline."
            )
            return

        pipeline = self.pipeline_source()
        if not pipeline or not isinstance(pipeline, list):
            QMessageBox.warning(self, "Guardar", "La pipeline actual no es válida.")
            return

        add_preset(name, pipeline)
        estilo = self.style_filter.currentText()
        if estilo and estilo != "Todos":
            tag_preset(name, estilo)

        self.name_input.clear()
        self._refresh_list()
        QMessageBox.information(
            self, "Guardado", f"Preset '{name}' guardado correctamente."
        )

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        name = item.text()
        menu = QMenu(self)
        menu.addAction("Renombrar", lambda: self._rename_preset(name))
        menu.addAction("Duplicar", lambda: self._duplicate_preset(name))
        menu.addAction("Eliminar", lambda: self._delete_preset(name))
        menu.addSeparator()
        menu.addAction("Exportar a JSON", lambda: export_preset_to_json(name))
        menu.addAction("Importar desde JSON", self._import_preset)
        menu.exec(self.list_widget.mapToGlobal(pos))

    def _rename_preset(self, old_name):
        from PyQt6.QtWidgets import QInputDialog

        new_name, ok = QInputDialog.getText(self, "Renombrar preset", "Nuevo nombre:")
        if ok and new_name and new_name != old_name:
            rename_preset(old_name, new_name)
            self._refresh_list()
            QMessageBox.information(
                self, "Renombrado", f"Preset renombrado a '{new_name}'."
            )

    def _duplicate_preset(self, name):
        new_name = f"{name}_copy"
        count = 1
        while new_name in self.presets:
            new_name = f"{name}_copy{count}"
            count += 1
        add_preset(new_name, self.presets[name])
        self._refresh_list()
        QMessageBox.information(
            self, "Duplicado", f"Preset duplicado como '{new_name}'."
        )

    def _delete_preset(self, name):
        reply = QMessageBox.question(
            self,
            "Eliminar preset",
            f"¿Estás seguro de que deseas eliminar '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            remove_preset(name)
            self._refresh_list()
            self.preview.clear()
            QMessageBox.information(self, "Eliminado", f"Preset '{name}' eliminado.")

    def _import_preset(self):
        imported = import_preset_from_json()
        if imported:
            self._refresh_list()
            QMessageBox.information(
                self, "Importado", "Preset importado correctamente."
            )

    def set_pipeline_source(self, source_callable):
        """
        Define una función que devuelve la configuración actual del pipeline.
        Esto permite comparar, exportar o duplicar la configuración activa.
        """
        self._pipeline_source = source_callable
