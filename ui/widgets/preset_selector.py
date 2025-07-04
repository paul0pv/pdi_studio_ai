# ui/widgets/preset_selector.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
    QLineEdit,
    QCompleter,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from config.presets import load_presets, remove_preset, add_preset
from config.preset_meta import (
    add_to_recent,
    get_recent,
    toggle_favorite,
    get_favorites,
    is_favorite,
    tag_preset,
    untag_preset,
    get_tags_for_preset,
    get_all_tags,
)
import json
import os


class PresetSelector(QWidget):
    preset_applied = pyqtSignal(str, list)  # nombre, pipeline

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(250)
        self.presets = load_presets()
        self.pipeline_source = None  # función que devuelve la pipeline actual

        layout = QVBoxLayout()

        # --- Selector de presets existentes ---
        self.label = QLabel("Presets guardados:")
        self.combo = QComboBox()
        self.combo.addItems(self.presets.keys())
        self.combo.currentTextChanged.connect(self._update_preview)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)

        self.apply_button = QPushButton("Aplicar")
        self.delete_button = QPushButton("Eliminar")

        self.apply_button.clicked.connect(self._apply_preset)
        self.delete_button.clicked.connect(self._delete_preset)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.delete_button)

        # --- Preset tag selector ---
        self.tag_label = QLabel("🏷️ Etiquetas:")
        # self.tag_input = QLineEdit()
        self.tag_input = QComboBox()
        self.tag_input.setEditable(True)
        self.tag_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.tag_input.setDuplicatesEnabled(False)

        # Autocompletado con etiquetas existentes
        existing_tags = get_all_tags()
        completer = QCompleter(existing_tags)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.tag_input.setCompleter(completer)
        self.tag_input.addItems(existing_tags)

        self.tag_input.setPlaceholderText("Separar con comas: retrato, surrealista...")
        self.tag_save_button = QPushButton("Guardar etiquetas")
        self.tag_save_button.clicked.connect(self._save_tags)

        tag_layout = QHBoxLayout()
        tag_layout.addWidget(self.tag_input)
        tag_layout.addWidget(self.tag_save_button)

        # --- History presets ---

        self.recent_label = QLabel("🕘 Recientes:")
        self.recent_combo = QComboBox()
        self.recent_combo.addItems(get_recent())
        self.recent_combo.currentTextChanged.connect(self._load_from_recent)

        # --- Guardar nuevo preset ---
        self.save_label = QLabel("Guardar pipeline actual como preset:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del nuevo preset")
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self._save_current_pipeline)

        save_layout = QHBoxLayout()
        save_layout.addWidget(self.name_input)
        save_layout.addWidget(self.save_button)

        # --- Exportar / Importar ---
        self.export_button = QPushButton("Exportar Preset")
        self.import_button = QPushButton("Importar Preset")

        self.export_button.clicked.connect(self._export_preset)
        self.import_button.clicked.connect(self._import_preset)

        export_layout = QHBoxLayout()
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.import_button)

        # --- Edit presets ---
        self.duplicate_button = QPushButton("Duplicar")
        self.rename_button = QPushButton("Renombrar")

        self.duplicate_button.clicked.connect(self._duplicate_preset)
        self.rename_button.clicked.connect(self._rename_preset)

        manage_layout = QHBoxLayout()
        manage_layout.addWidget(self.duplicate_button)
        manage_layout.addWidget(self.rename_button)

        # --- Ensamblar layout ---
        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        layout.addWidget(self.preview)
        layout.addLayout(button_layout)
        layout.addWidget(self.tag_label)
        layout.addLayout(tag_layout)
        layout.addLayout(export_layout)
        layout.addWidget(self.recent_label)
        layout.addWidget(self.recent_combo)
        layout.addWidget(self.save_label)
        layout.addLayout(save_layout)
        layout.addLayout(manage_layout)

        self.setLayout(layout)

        if self.combo.count() > 0:
            self._update_preview(self.combo.currentText())

    def set_pipeline_source(self, get_pipeline_fn):
        """Define una función que devuelve la pipeline actual para guardar como preset."""
        self.pipeline_source = get_pipeline_fn

    def _update_preview(self, preset_name: str):
        pipeline = self.presets.get(preset_name, [])
        self.preview.setText(
            "\n".join([f"{f['name']} → {f.get('params', {})}" for f in pipeline])
        )
        tags = get_tags_for_preset(preset_name)
        self.tag_input.setText(", ".join(tags))
        self._update_favorite_button()

    def _apply_preset(self):
        name = self.combo.currentText()
        pipeline = self.presets.get(name)
        if pipeline:
            add_to_recent(name)
            self.recent_combo.clear()
            self.recent_combo.addItems(get_recent())
            self.preset_applied.emit(name, pipeline)

    def _delete_preset(self):
        name = self.combo.currentText()
        remove_preset(name)
        self.presets = load_presets()
        self.combo.clear()
        self.combo.addItems(self.presets.keys())
        self.preview.clear()

    def _export_preset(self):
        name = self.combo.currentText()
        if not name or name not in self.presets:
            QMessageBox.warning(self, "Exportar", "Selecciona un preset válido.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Preset", f"{name}.json", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.presets[name], f, indent=4, ensure_ascii=False)
            QMessageBox.information(
                self, "Exportar", f"Preset '{name}' exportado a:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{e}")

    def _import_preset(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Preset", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                pipeline = json.load(f)
                if not isinstance(pipeline, list):
                    raise ValueError(
                        "Formato inválido: se esperaba una lista de filtros."
                    )

            # Usar nombre de archivo como nombre de preset
            preset_name = os.path.splitext(os.path.basename(file_path))[0]
            add_preset(preset_name, pipeline)
            self.presets = load_presets()
            self.combo.clear()
            self.combo.addItems(self.presets.keys())
            QMessageBox.information(
                self, "Importar", f"Preset '{preset_name}' importado correctamente."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo importar:\n{e}")

    def _duplicate_preset(self):
        name = self.combo.currentText()
        if not name or name not in self.presets:
            QMessageBox.warning(self, "Duplicar", "Selecciona un preset válido.")
            return

        new_name, ok = QFileDialog.getSaveFileName(
            self, "Duplicar como...", f"{name}_copy.json", "JSON Files (*.json)"
        )
        if not ok or not new_name:
            return

        try:
            with open(new_name, "w", encoding="utf-8") as f:
                json.dump(self.presets[name], f, indent=4, ensure_ascii=False)

            # Cargar como nuevo preset
            with open(new_name, "r", encoding="utf-8") as f:
                pipeline = json.load(f)
            preset_name = os.path.splitext(os.path.basename(new_name))[0]
            add_preset(preset_name, pipeline)

            self.presets = load_presets()
            self.combo.clear()
            self.combo.addItems(self.presets.keys())
            QMessageBox.information(
                self, "Duplicar", f"Preset duplicado como '{preset_name}'."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo duplicar:\n{e}")

    def _rename_preset(self):
        old_name = self.combo.currentText()
        if not old_name or old_name not in self.presets:
            QMessageBox.warning(self, "Renombrar", "Selecciona un preset válido.")
            return

        new_name, ok = QFileDialog.getSaveFileName(
            self,
            "Renombrar preset",
            f"{old_name}_renombrado.json",
            "JSON Files (*.json)",
        )
        if not ok or not new_name:
            return

        try:
            new_base = os.path.splitext(os.path.basename(new_name))[0]
            pipeline = self.presets[old_name]
            add_preset(new_base, pipeline)
            remove_preset(old_name)

            self.presets = load_presets()
            self.combo.clear()
            self.combo.addItems(self.presets.keys())
            QMessageBox.information(
                self, "Renombrar", f"Preset renombrado a '{new_base}'."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo renombrar:\n{e}")

    def _load_from_recent(self, name: str):
        if name in self.presets:
            self.combo.setCurrentText(name)

    def _toggle_favorite(self):
        name = self.combo.currentText()
        if not name:
            return
        toggle_favorite(name)
        self._update_favorite_button()

    def _update_favorite_button(self):
        name = self.combo.currentText()
        if is_favorite(name):
            self.favorite_button.setText("⭐ Favorito")
        else:
            self.favorite_button.setText("☆ Marcar como favorito")

    def _save_tags(self):
        name = self.combo.currentText()
        if not name:
            return

        current_tags = set(get_tags_for_preset(name))
        new_tags = set(t.strip() for t in self.tag_input.text().split(",") if t.strip())

        # Eliminar etiquetas no deseadas
        for tag in current_tags - new_tags:
            untag_preset(name, tag)

        # Agregar nuevas etiquetas
        for tag in new_tags - current_tags:
            tag_preset(name, tag)

        QMessageBox.information(
            self, "Etiquetas", f"Etiquetas actualizadas para '{name}'."
        )

    def _save_current_pipeline(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setPlaceholderText("⚠️ Ingresa un nombre válido")
            return

        if not self.pipeline_source:
            print("[PresetSelector] No se ha definido fuente de pipeline.")
            return

        pipeline = self.pipeline_source()
        if not pipeline:
            print("[PresetSelector] Pipeline actual vacía.")
            return

        add_preset(name, pipeline)
        self.presets = load_presets()
        self.combo.clear()
        self.combo.addItems(self.presets.keys())
        self.name_input.clear()
