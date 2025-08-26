from PyQt6 import QtWidgets, QtCore
from typing import List, Tuple, Dict


class DuplicateProfilesDialog(QtWidgets.QDialog):
    """
    A dialog box for managing duplicate Wi-Fi profiles.
    It presents a list of duplicate profiles and allows the user to choose
    whether to replace or skip each one.
    """
    def __init__(self, duplicate_profiles: List[Tuple[str, str]], parent: QtWidgets.QWidget = None):
        """
        Initializes the dialog with a list of duplicate profiles.

        Args:
            duplicate_profiles: A list of (ssid, password) tuples for the profiles
                                that already exist in the database.
            parent: The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Duplicate Wi-Fi Profiles")
        self.setModal(True)
        self.setMinimumSize(800, 500)

        self.duplicate_profiles = duplicate_profiles
        self.choices: Dict[str, str] = {}  # {ssid: choice}, where choice is 'replace' or 'skip'

        self._setup_ui()
        self._load_profiles_into_table()

    def _setup_ui(self):
        """Initializes and lays out the widgets for the dialog."""
        layout = QtWidgets.QVBoxLayout(self)

        # Main explanatory label
        label = QtWidgets.QLabel(
            "The following Wi-Fi profiles already exist in the database. "
            "Please choose how to handle each duplicate:"
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        # Table to display profiles
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Wi-Fi Name", "Password", "Replace", "Skip"
        ])

        # Configure table behavior
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Confirmation and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Confirm")
        button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_profiles_into_table(self):
        """Populates the table with data from the duplicate profiles list."""
        self.table.setRowCount(len(self.duplicate_profiles))

        for row, (ssid, password) in enumerate(self.duplicate_profiles):
            # Column for Wi-Fi Name (SSID)
            name_item = QtWidgets.QTableWidgetItem(ssid)
            name_item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            # Column for Password
            password_item = QtWidgets.QTableWidgetItem(password)
            password_item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 1, password_item)

            # Create a button group to manage the radio buttons for this row
            button_group = QtWidgets.QButtonGroup(self)

            # Option to replace the existing profile
            replace_radio = QtWidgets.QRadioButton("Replace")
            replace_radio.setChecked(True)
            button_group.addButton(replace_radio)
            self._set_cell_widget(row, 2, replace_radio)

            # Option to skip saving the new profile
            skip_radio = QtWidgets.QRadioButton("Skip")
            button_group.addButton(skip_radio)
            self._set_cell_widget(row, 3, skip_radio)

            # Set the initial choice and connect signal
            self.choices[ssid] = "replace"
            button_group.buttonClicked.connect(
                lambda btn, s=ssid: self._update_choice(s, btn)
            )

    def _set_cell_widget(self, row: int, col: int, widget: QtWidgets.QWidget):
        """Helper method to place a widget in a table cell with centered alignment."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(widget)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, col, container)

    def _update_choice(self, ssid: str, button: QtWidgets.QAbstractButton):
        """Updates the stored choice for a specific SSID based on a radio button click."""
        if button.text() == "Replace":
            self.choices[ssid] = "replace"
        else: # Assumes the other button is "Skip"
            self.choices[ssid] = "skip"

    def get_choices(self) -> Dict[str, str]:
        """
        Returns a dictionary of the user's choices for each duplicate profile.

        Returns:
            A dictionary where keys are SSIDs and values are 'replace' or 'skip'.
        """
        return self.choices