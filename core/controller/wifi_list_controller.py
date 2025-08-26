from core.view.wifi_list_window import Ui_wifiList
from PyQt6 import QtWidgets, QtSql, QtCore
from core.utils.message_box import *
from core.model.wifi_profiles_model import *
import logging


class WifiListController(QtWidgets.QDialog):
    """
    Controller for the Wi-Fi list window.
    Manages displaying and interacting with a list of saved Wi-Fi profiles.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize the UI from the generated class
        self.ui = Ui_wifiList()
        self.ui.setupUi(self)

        # Setup a dedicated logger for this class
        self.logger = logging.getLogger(self.__class__.__name__)

        # Variables to store the selected Wi-Fi profile credentials
        self.selected_ssid = None
        self.selected_password = None

        # 1. Initialize database connection and model
        db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(resource_path("core/model/data/wifi_profiles.db"))
        if not db.open():
            self.logger.error("Unable to establish a database connection.")
            show_error("Unable to establish a database connection.", "Could not open database")
            return

        # Create a model to interact with the 'profiles' table
        self.model = QtSql.QSqlTableModel(self, db)
        self.model.setTable("profiles")
        self.model.select()  # Populate the model with data from the table

        # Initialize the application's core Wi-Fi model
        self.wifi_model = WifiProfilesModel()

        # 2. Configure the UI's table view
        self.ui.wifiTableView.setModel(self.model)
        self.model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "Wi-Fi Name")
        self.model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "Password")

        # Adjust table view properties for better usability
        self.ui.wifiTableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.wifiTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.wifiTableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # 3. Connect UI signals to controller methods
        self.connect_signals()

    def connect_signals(self):
        """Connects UI buttons to their corresponding controller methods."""
        self.ui.chooseWifiButton.clicked.connect(self.choose_wifi)
        self.ui.cancel.clicked.connect(self.reject)
        self.ui.deleteWifiButton.clicked.connect(self.delete_wifi)

    def select_wifi(self):
        """
        Retrieves the SSID and password from the currently selected row in the table view.
        Displays a warning if no row is selected.
        """
        selected_indexes = self.ui.wifiTableView.selectionModel().selectedRows()
        if selected_indexes:
            selected_row_index = selected_indexes[0].row()

            ssid_index = self.model.index(selected_row_index, 0)
            password_index = self.model.index(selected_row_index, 1)

            self.selected_ssid = self.model.data(ssid_index)
            self.selected_password = self.model.data(password_index)
        else:
            show_warning("Please select a Wi-Fi profile.", "No Selection")

    def choose_wifi(self):
        """
        Handles the 'Choose Wi-Fi' button click.
        Selects the chosen profile and closes the dialog with an 'Accepted' status.
        """
        try:
            self.select_wifi()
            self.accept()
        except Exception as e:
            self.logger.exception("Error in choose_wifi.")
            show_error(f"An error occurred: {e}", "Error")

    def delete_wifi(self):
        """
        Deletes the selected Wi-Fi profile from the database after a user confirmation.
        Refreshes the table view to show the updated list.
        """
        self.select_wifi()
        if not self.selected_ssid:
            self.logger.warning("No Wi-Fi profile selected for deletion.")
            return

        reply = show_question(f"Are you sure you want to delete '{self.selected_ssid}'?", "Confirm Delete", timed=True)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                success = self.wifi_model.delete_profile(self.selected_ssid)
                if success:
                    # Refresh the table model to reflect the change
                    self.model.select()
                    self.logger.info(f"Successfully deleted profile for: {self.selected_ssid}.")
                    show_info(f"Profile '{self.selected_ssid}' deleted successfully.")
                else:
                    self.logger.error(f"Failed to delete profile for: {self.selected_ssid}.")
                    show_error("Delete failed.")
            except Exception as e:
                self.logger.exception(f"Error deleting Wi-Fi profile: {e}.")
                show_error(f"An error occurred while deleting: {e}", "Error")