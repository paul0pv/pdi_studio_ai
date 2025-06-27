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
from ui.widgets.filter_control import FilterControl  # Import our FilterControl widget
from processing.filters import (
    get_default_filter_params,
    FILTER_METADATA,  # Import FILTER_METADATA to validate/get info for new filters
)  # To get default params when adding new filter instances


class PipelineManager(QGroupBox):
    """
    A widget to manage and display the active image processing pipeline.
    It contains multiple FilterControl widgets, allowing reordering and removal.
    """

    # Signals to communicate pipeline changes to MainWindow/ImageProcessor
    # Emits the full, updated pipeline configuration
    pipeline_updated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__("Processing Pipeline", parent)  # GroupBox title
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )  # Can expand vertically

        self.filter_controls = []  # List to hold references to FilterControl widgets

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self._build_ui()

    def _build_ui(self):
        """Constructs the scrollable area for filter controls."""
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # Allow the widget inside to resize

        # This widget will hold all FilterControl instances
        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_content)
        self.scroll_area_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )  # Align controls to top
        self.scroll_area_content.setLayout(self.scroll_area_layout)

        self.scroll_area.setWidget(self.scroll_area_content)
        self.main_layout.addWidget(self.scroll_area)

        # Add a spacer to push filter controls to the top
        self.scroll_area_layout.addStretch(1)

    def _update_filter_indices(self):
        """Updates the internal index of each FilterControl widget."""
        for i, control in enumerate(self.filter_controls):
            control.set_index(i)
        self._emit_pipeline_updated()  # Emit pipeline updated after re-indexing

    def _emit_pipeline_updated(self):
        """Gathers the current pipeline configuration from controls and emits it."""
        current_pipeline_config = []
        for fc in self.filter_controls:
            # Only include filters that have valid names and are part of metadata
            if fc.filter_name in FILTER_METADATA:
                current_pipeline_config.append(fc.get_filter_config())
            else:
                print(
                    f"Warning: Filter '{fc.filter_name}' is not recognized in FILTER_METADATA. Skipping."
                )
        self.pipeline_updated.emit(current_pipeline_config)
        # print("PipelineManager: Emitted pipeline_updated signal.") # Verbose debug

    def get_current_pipeline_config(self) -> list:
        """
        Returns the current pipeline configuration as a list of dictionaries.
        This is useful for saving presets or querying the current state.
        """
        current_pipeline_config = []
        for fc in self.filter_controls:
            if fc.filter_name in FILTER_METADATA:
                current_pipeline_config.append(fc.get_filter_config())
        return current_pipeline_config

    def add_filter_to_pipeline(
        self, filter_name: str, initial_params: dict = None, enabled: bool = True
    ):
        """
        Adds a new filter control to the pipeline manager.
        This is typically called when the user manually adds a filter.
        """
        if filter_name not in FILTER_METADATA:
            print(
                f"PipelineManager: Filter '{filter_name}' not found in FILTER_METADATA. Cannot add."
            )
            return

        if initial_params is None:
            initial_params = get_default_filter_params(filter_name)

        new_index = len(self.filter_controls)
        filter_control = FilterControl(filter_name, initial_params, new_index)
        filter_control.enabled_checkbox.setChecked(enabled)  # Set initial enabled state

        # Connect signals from the new filter control
        filter_control.params_changed.connect(self._on_filter_params_changed)
        filter_control.enabled_toggled.connect(self._on_filter_enabled_toggled)
        filter_control.removed.connect(self._on_filter_removed)
        filter_control.moved.connect(self._on_filter_moved)

        self.filter_controls.append(filter_control)
        # Remove the stretch before adding new widget, then add it back to keep widgets aligned top
        if self.scroll_area_layout.count() > 0:
            last_item = self.scroll_area_layout.itemAt(
                self.scroll_area_layout.count() - 1
            )
            if isinstance(last_item, QSpacerItem):
                self.scroll_area_layout.removeItem(last_item)

        self.scroll_area_layout.addWidget(filter_control)
        self.scroll_area_layout.addStretch(1)  # Add stretch back after adding widget

        self._emit_pipeline_updated()  # Emit pipeline updated after adding a filter

    def set_pipeline_from_config(self, pipeline_config: list):
        """
        Sets the entire pipeline from a given configuration (list of dictionaries).
        This clears existing controls and builds new ones.
        This is called by LLM output or when loading a preset.
        """
        print("PipelineManager: Setting pipeline from configuration...")

        # 1. Clear existing filter controls and their widgets from layout
        for control in self.filter_controls:
            control.deleteLater()  # Mark for deletion
            self.scroll_area_layout.removeWidget(control)  # Remove from layout
        self.filter_controls.clear()  # Clear the list of references

        # Remove the stretch before adding new widgets, will add it back at the end
        if self.scroll_area_layout.count() > 0:
            last_item = self.scroll_area_layout.itemAt(
                self.scroll_area_layout.count() - 1
            )
            if isinstance(last_item, QSpacerItem):
                self.scroll_area_layout.removeItem(last_item)

        # 2. Build new filter controls based on the provided pipeline_config
        for i, filter_entry in enumerate(pipeline_config):
            filter_name = filter_entry.get("name")
            params = filter_entry.get("params", {})
            enabled = filter_entry.get(
                "enabled", True
            )  # Default to enabled if not specified

            if filter_name not in FILTER_METADATA:
                print(
                    f"PipelineManager: Warning: Filter '{filter_name}' from config is not available. Skipping."
                )
                continue  # Skip unknown filters

            filter_control = FilterControl(filter_name, params, i)
            filter_control.enabled_checkbox.setChecked(enabled)

            # Connect signals from the new filter control
            filter_control.params_changed.connect(self._on_filter_params_changed)
            filter_control.enabled_toggled.connect(self._on_filter_enabled_toggled)
            filter_control.removed.connect(self._on_filter_removed)
            filter_control.moved.connect(self._on_filter_moved)

            self.filter_controls.append(filter_control)
            self.scroll_area_layout.addWidget(filter_control)

        self.scroll_area_layout.addStretch(1)  # Add stretch back after all widgets

        self._emit_pipeline_updated()  # Emit pipeline updated after re-building

    # --- Slots for FilterControl signals ---

    def _on_filter_params_changed(self, filter_name: str, new_params: dict, index: int):
        """Updates pipeline when a filter's parameters change."""
        if 0 <= index < len(self.filter_controls):
            self.filter_controls[index].current_params = new_params
            self._emit_pipeline_updated()

    def _on_filter_enabled_toggled(
        self, filter_name: str, enabled_state: bool, index: int
    ):
        """Updates pipeline when a filter's enabled state changes."""
        if 0 <= index < len(self.filter_controls):
            # The FilterControl itself manages its internal enabled state
            # We just need to trigger a pipeline update to reflect this
            self._emit_pipeline_updated()

    def _on_filter_removed(self, index: int):
        """Removes a filter control from the pipeline."""
        if 0 <= index < len(self.filter_controls):
            control_to_remove = self.filter_controls.pop(index)
            self.scroll_area_layout.removeWidget(control_to_remove)
            control_to_remove.deleteLater()  # Important for memory management
            self._update_filter_indices()  # Re-index remaining filters and emit pipeline updated

    def _on_filter_moved(self, index: int, direction: str):
        """Reorders filters in the pipeline."""
        if direction == "up" and index > 0:
            self.filter_controls[index], self.filter_controls[index - 1] = (
                self.filter_controls[index - 1],
                self.filter_controls[index],
            )
            self._rebuild_scroll_area_layout()  # Rebuild layout to reflect new order
            self._update_filter_indices()  # Update indices and emit

        elif direction == "down" and index < len(self.filter_controls) - 1:
            self.filter_controls[index], self.filter_controls[index + 1] = (
                self.filter_controls[index + 1],
                self.filter_controls[index],
            )
            self._rebuild_scroll_area_layout()  # Rebuild layout to reflect new order
            self._update_filter_indices()  # Update indices and emit

    def _rebuild_scroll_area_layout(self):
        """Helper to clear and re-populate the scroll area layout based on current filter_controls order."""
        # Remove all widgets from the layout
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)  # Unparent the widget

        # Add widgets back in the new order
        for control in self.filter_controls:
            self.scroll_area_layout.addWidget(control)

        self.scroll_area_layout.addStretch(1)  # Ensure stretch is at the end


# --- For standalone testing (optional) ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QVBoxLayout,
        QWidget,
        QHBoxLayout,
    )
    from ui.widgets.filter_selector import (
        FilterSelector,
    )  # Need this for testing addition

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("PipelineManager Test")
    window.setGeometry(100, 100, 400, 700)  # Give it some size

    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)

    selector = FilterSelector()
    manager = PipelineManager()

    # Simulate adding filters from selector
    def add_filter_to_manager(filter_name):
        manager.add_filter_to_pipeline(filter_name)
        print(f"Test: Added '{filter_name}' to manager.")

    selector.filter_selected_to_add.connect(add_filter_to_manager)
    manager.pipeline_updated.connect(lambda p: print(f"Test: Pipeline Updated! {p}"))

    main_layout.addWidget(selector)
    main_layout.addWidget(manager)
    # No stretch here for the main_layout, as manager has...

    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
