# ui/widgets/pipeline_manager.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGroupBox,
    QSizePolicy,
    QSpacerItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.widgets.filter_control import FilterControl
from processing.filters import get_default_filter_params, FILTER_METADATA
from processing.validation import validate_filter_params


class PipelineManager(QGroupBox):
    pipeline_updated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__("Pipeline de Procesamiento", parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.filter_controls = []
        self._undo_stack = []
        self._redo_stack = []

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self._build_ui()

    def _build_ui(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_content)
        self.scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area_content.setLayout(self.scroll_area_layout)

        self.scroll_area.setWidget(self.scroll_area_content)
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area_layout.addStretch(1)

    def add_filter_to_pipeline(
        self, filter_name: str, initial_params: dict = None, enabled: bool = True
    ):
        if filter_name not in FILTER_METADATA:
            print(f"[PipelineManager] ❌ Filtro '{filter_name}' no encontrado.")
            return

        if initial_params is None:
            initial_params = get_default_filter_params(filter_name)
        else:
            initial_params = validate_filter_params(filter_name, initial_params)

        if self.filter_controls and self.filter_controls[-1].filter_name == filter_name:
            print(f"[PipelineManager] ⚠️ Filtro '{filter_name}' ya está al final.")
            return

        self._record_history(
            "add", {"name": filter_name, "params": initial_params, "enabled": enabled}
        )
        self._create_filter_control(filter_name, initial_params, enabled)

    def _create_filter_control(self, filter_name, params, enabled):
        index = len(self.filter_controls)
        fc = FilterControl(filter_name, params, index)
        fc.enabled_checkbox.setChecked(enabled)

        fc.params_changed.connect(self._on_filter_params_changed)
        fc.enabled_toggled.connect(self._on_filter_enabled_toggled)
        fc.removed.connect(self._on_filter_removed)
        fc.moved.connect(self._on_filter_moved)
        fc.duplicated.connect(self._on_filter_duplicated)

        self.filter_controls.append(fc)

        if self.scroll_area_layout.count() > 0:
            last = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1)
            if isinstance(last, QSpacerItem):
                self.scroll_area_layout.removeItem(last)

        self.scroll_area_layout.addWidget(fc)
        self.scroll_area_layout.addStretch(1)
        self._emit_pipeline_updated()

    def _on_filter_params_changed(self, name, params, index):
        if 0 <= index < len(self.filter_controls):
            self.filter_controls[index].current_params = params
            self._emit_pipeline_updated()

    def _on_filter_enabled_toggled(self, name, state, index):
        self._emit_pipeline_updated()

    def _on_filter_removed(self, index):
        if 0 <= index < len(self.filter_controls):
            fc = self.filter_controls.pop(index)
            self.scroll_area_layout.removeWidget(fc)
            fc.deleteLater()
            self._update_indices()
            self._record_history(
                "remove",
                {
                    "name": fc.filter_name,
                    "params": fc.current_params,
                    "enabled": fc.enabled_checkbox.isChecked(),
                    "index": index,
                },
            )

    def _on_filter_moved(self, index, direction):
        if direction == "up" and index > 0:
            self.filter_controls[index], self.filter_controls[index - 1] = (
                self.filter_controls[index - 1],
                self.filter_controls[index],
            )
            self._record_history("move", {"index": index, "direction": "up"})
        elif direction == "down" and index < len(self.filter_controls) - 1:
            self.filter_controls[index], self.filter_controls[index + 1] = (
                self.filter_controls[index + 1],
                self.filter_controls[index],
            )
            self._record_history("move", {"index": index, "direction": "down"})
        self._rebuild_layout()
        self._update_indices()

    def _on_filter_duplicated(self, index):
        if 0 <= index < len(self.filter_controls):
            original = self.filter_controls[index]
            self.add_filter_to_pipeline(
                original.filter_name, original.current_params, True
            )
            self._record_history("duplicate", {"index": index})

    def _update_indices(self):
        for i, fc in enumerate(self.filter_controls):
            fc.set_index(i)
        self._emit_pipeline_updated()

    def _rebuild_layout(self):
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        for fc in self.filter_controls:
            self.scroll_area_layout.addWidget(fc)
        self.scroll_area_layout.addStretch(1)

    def _emit_pipeline_updated(self):
        config = [
            fc.get_filter_config()
            for fc in self.filter_controls
            if fc.filter_name in FILTER_METADATA
        ]
        self.pipeline_updated.emit(config)

    def get_current_pipeline_config(self):
        return [
            fc.get_filter_config()
            for fc in self.filter_controls
            if fc.filter_name in FILTER_METADATA
        ]

    def set_pipeline_from_config(self, config: list):
        for fc in self.filter_controls:
            self.scroll_area_layout.removeWidget(fc)
            fc.deleteLater()
        self.filter_controls.clear()

        for entry in config:
            name = entry.get("name")
            params = entry.get("params", {})
            enabled = entry.get("enabled", True)
            if name in FILTER_METADATA:
                self._create_filter_control(name, params, enabled)

    # --- Historial de cambios ---

    def _record_history(self, action, data):
        self._undo_stack.append((action, data))
        self._redo_stack.clear()
        print(f"[Historial] Acción registrada: {action}")

    def undo(self):
        if not self._undo_stack:
            print("[Historial] Nada que deshacer.")
            return
        action, data = self._undo_stack.pop()
        self._redo_stack.append((action, data))
        self._apply_inverse_action(action, data)

    def redo(self):
        if not self._redo_stack:
            print("[Historial] Nada que rehacer.")
            return
        action, data = self._redo_stack.pop()
        self._undo_stack.append((action, data))
        self._apply_action(action, data)

    def _apply_action(self, action, data):
        if action == "add":
            self.add_filter_to_pipeline(data["name"], data["params"], data["enabled"])
        elif action == "remove":
            self._on_filter_removed(data["index"])
        elif action == "move":
            self._on_filter_moved(data["index"], data["direction"])
        elif action == "duplicate":
            self._on_filter_duplicated(data["index"])

    def _apply_inverse_action(self, action, data):
        if action == "add":
            self._on_filter_removed(len(self.filter_controls) - 1)
        elif action == "remove":
            self.add_filter_to_pipeline(data["name"], data["params"], data["enabled"])
        elif action == "move":
            reverse = "down" if data["direction"] == "up" else "up"
            self._on_filter_moved(
                data["index"] + (-1 if reverse == "down" else 1), reverse
            )
        elif action == "duplicate":
            self._on_filter_removed(len(self.filter_controls) - 1)
