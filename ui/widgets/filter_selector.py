# ui/widgets/filter_selector.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
# We'll remove the direct import of AVAILABLE_FILTERS and FILTER_METADATA here
# as MainWindow will pass them in. This promotes better encapsulation.
# from processing.filters import AVAILABLE_FILTERS, FILTER_METADATA


class FilterSelector(QGroupBox):
    """
    A widget that allows selecting an image processing filter from a list
    and adding it to the pipeline.
    """

    # Signal emitted when the 'Add Filter' button is clicked
    filter_selected_to_add = pyqtSignal(str)  # Emits the name of the filter to add

    def __init__(self, available_filters: list = None, parent=None):
        super().__init__("Add New Filter", parent)  # GroupBox title
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(100)  # Give it some space
        self.setMaximumHeight(150)

        self._filter_metadata = {}  # To store metadata passed by MainWindow
        self._available_filters_list = []  # To store the list of filter names

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self._build_ui()

        # Initialize with provided filters, if any (useful for testing)
        if available_filters:
            self.set_available_filters(available_filters)

    def _build_ui(self):
        """Constructs the UI elements for the filter selector."""
        # --- Filter Selection Row ---
        selection_row_layout = QHBoxLayout()
        selection_row_layout.addWidget(QLabel("Selecccionar filtro:"))

        self.filter_combobox = QComboBox()
        # Do not populate with AVAILABLE_FILTERS here directly, as it will be set later
        self.filter_combobox.currentIndexChanged.connect(
            self._update_filter_description
        )
        selection_row_layout.addWidget(self.filter_combobox)

        self.add_filter_button = QPushButton("Añadir filtro")
        self.add_filter_button.clicked.connect(self._on_add_filter_clicked)
        selection_row_layout.addWidget(self.add_filter_button)

        self.main_layout.addLayout(selection_row_layout)

        # --- Description Area ---
        self.description_label = QLabel("Selecciona un filtro para ver su descripción.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-style: italic; color: gray;")
        self.main_layout.addWidget(self.description_label)

    def set_available_filters(self, filter_names: list, filter_metadata: dict = None):
        """
        Sets the list of available filter names in the QComboBox.
        Args:
            filter_names (list): A list of filter names (strings).
            filter_metadata (dict): The complete FILTER_METADATA dictionary
                                    from processing.filters.
        """
        self._available_filters_list = sorted(
            filter_names
        )  # Sort for consistent display
        if filter_metadata:
            self._filter_metadata = filter_metadata

        self.filter_combobox.clear()
        if self._available_filters_list:
            self.filter_combobox.addItems(self._available_filters_list)
            self.filter_combobox.setCurrentIndex(0)  # Select the first item
            self._update_filter_description(0)  # Update description for the first item
        else:
            self.filter_combobox.addItem("No filters available")
            self.filter_combobox.setEnabled(False)
            self.add_filter_button.setEnabled(False)
            self.description_label.setText("No filters loaded.")

    def _update_filter_description(self, index: int):
        """Updates the description label based on the selected filter."""
        if index < 0 or index >= len(self._available_filters_list):
            self.description_label.setText("No description available.")
            return

        selected_filter_name = self.filter_combobox.currentText()
        # Use the stored metadata
        description = self._filter_metadata.get(selected_filter_name, {}).get(
            "description", "No description available."
        )
        self.description_label.setText(description)

    def _on_add_filter_clicked(self):
        """Emits the signal with the name of the currently selected filter."""
        selected_filter_name = self.filter_combobox.currentText()
        if selected_filter_name and selected_filter_name != "No filters available":
            self.filter_selected_to_add.emit(selected_filter_name)
        else:
            print("FilterSelector: No filter selected to add or none available.")


# --- For standalone testing (optional) ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

    # We need filter metadata for testing the description
    from processing.filters import FILTER_METADATA, AVAILABLE_FILTERS

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("FilterSelector Test")

    selector_widget = FilterSelector()
    # Now you can pass the available filters and metadata for testing
    selector_widget.set_available_filters(AVAILABLE_FILTERS, FILTER_METADATA)

    selector_widget.filter_selected_to_add.connect(
        lambda name: print(f"Filter '{name}' requested to be added.")
    )

    central_widget = QWidget()
    central_layout = QVBoxLayout(central_widget)
    central_layout.addWidget(selector_widget)
    central_layout.addStretch(1)
    window.setCentralWidget(central_widget)

    window.show()
    sys.exit(app.exec())
