from PyQt6 import QtWidgets, QtCore
from core.view.main_window import Ui_Form
from core.model.log_model import LogListModel
from core.controller.wifi_list_controller import WifiListController
from core.services.psiphon_monitor import *
from core.services.network_manager import *
from core.utils.message_box import *
import logging
import time


class QListWidgetHandler(logging.Handler):
    """
    A custom logging handler that sends log messages to a QListWidget
    via a LogListModel.
    """

    def __init__(self, model):
        super().__init__()
        self.model = model

    def emit(self, record):
        # Format the log record and add it to the model.
        level = record.levelname
        message = self.format(record)
        self.model.add_log(message, level)


class MainController(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. Initialize UI components
        self.ui = Ui_Form()
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.ui.setupUi(self.central_widget)

        # 2. Initialize application models and services
        self.model = WifiProfilesModel()
        self.network_manager = NetworkManager()
        self.psiphon_monitor = PsiphonMonitor()
        self.log_model = LogListModel()

        # Connect log model to the UI's ListView
        self.ui.logListView.setModel(self.log_model)
        self.log_model.log_added.connect(self.scroll_log_to_bottom)

        # 3. Setup logging for the application
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()
        self.logger.info("Starting MPA (My-Portable-Apps)")

        # 4. Set default UI values
        self.ui.currentWifiLabel.setText("Not Selected")
        self.ui.wifiStatusValue.setText("Not Connected")
        self.ui.vpnStatusValue.setText("Not Running")
        self.ui.vpnTunnelingValue.setText("Not Running")
        self.ui.netStatusValue.setText("Not Connected")
        self.ui.intervalSpinBox.setValue(20)
        self.ui.stopAutoConfigButton.setEnabled(False)
        self.ui.vpnUseCheckbox.setChecked(False)

        # Setup timer for auto-configuration
        self.autoconfig_timer = QtCore.QTimer(self)
        self.autoconfig_timer.timeout.connect(self.run_once_config)

        # 5. Load initial data and states
        self.load_system_wifi_profiles()
        self.set_current_wifi()
        self.check_all_statuses()

        # Start the background thread for monitoring Psiphon
        self.psiphon_monitor.start()
        self.psiphon_monitor.status_updated.connect(self.update_psiphon_ui)

        # 6. Connect UI signals to controller slots
        self.connect_signals()

    def scroll_log_to_bottom(self):
        """Automatically scrolls the log view to the most recent entry."""
        self.ui.logListView.scrollToBottom()

    def setup_logging(self):
        """Configures log handlers for both console and the application's UI."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Handler for console output
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Handler for the UI's log view
        ui_handler = QListWidgetHandler(self.log_model)
        ui_handler.setFormatter(logging.Formatter('%(message)s'))
        root_logger.addHandler(ui_handler)

    def connect_signals(self):
        """Connects all UI buttons and widgets to their corresponding methods."""
        self.ui.saveWifiProfileButton.clicked.connect(self.handle_save_profile)
        self.ui.chooseWifiButton.clicked.connect(self.handle_switch_wifi)
        self.ui.resetWifiButton.clicked.connect(self.reset_wifi)
        self.ui.connectWifiButton.clicked.connect(self.network_manager.connect_wifi)
        self.ui.disconnectWifiButton.clicked.connect(self.network_manager.disconnect_wifi)
        self.ui.resetVPNButton.clicked.connect(self.reset_vpn)
        self.ui.connectVPNButton.clicked.connect(self.network_manager.start_psiphon)
        self.ui.disconnectVPNButton.clicked.connect(self.network_manager.stop_psiphon)
        self.ui.checkNetButton.clicked.connect(self.check_all_statuses)
        self.ui.setOnceButton.clicked.connect(self.run_once_config)
        self.ui.autoConfigButton.clicked.connect(self.start_auto_config)
        self.ui.stopAutoConfigButton.clicked.connect(self.stop_auto_config)
        self.ui.copyLogButton.clicked.connect(self.handle_copy_log)
        self.ui.clearLogButton.clicked.connect(self.log_model.clear)

    def load_system_wifi_profiles(self):
        """Loads all existing WiFi profiles from the system and saves them to the application's database."""
        self.logger.info("Loading system WiFi profiles...")
        wifi_profiles = self.network_manager.get_wifi_passwords()
        self.model.collect_duplicate_profiles(wifi_profiles)

    def set_current_wifi(self):
        """Retrieves the currently connected WiFi and sets its credentials in the NetworkManager."""
        current_ssid = self.network_manager.get_current_wifi()
        if current_ssid:
            password = self.model.get_password(current_ssid)
            if password:
                self.network_manager.set_wifi_credentials(current_ssid, password)
                self.ui.currentWifiLabel.setText(current_ssid)
                self.logger.info(f"Set current WiFi to: {current_ssid}")

    def update_status_labels(self):
        """
        Updates the UI labels to reflect the current status of Wi-Fi and internet connection.
        If conditions are not met, it prompts the user for action (e.g., reset Wi-Fi or start VPN).
        """
        wifi_connected, wifi_message = self.network_manager.get_wifi_status()
        internet_connected = self.network_manager.get_internet_status()

        self.ui.wifiStatusValue.setText("Connected" if wifi_connected else "Not Connected")
        self.ui.netStatusValue.setText("Connected" if internet_connected else "Not Connected")

        if not internet_connected:
            self.logger.info("Request for Wi-Fi reset due to no internet connection.")
            reply = show_question(
                f"Wi-Fi is connected to {self.network_manager.current_ssid} without internet.\nReset connection?",
                timed=True)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.logger.info("User confirmed Wi-Fi reset.")
                self.reset_wifi()
                time.sleep(2)

        if not self.network_manager.is_psiphon_running():
            self.logger.info("Request to start VPN as it is not running.")
            reply = show_question(f"VPN is not connected.\nConnect VPN?", timed=True)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.logger.info("User confirmed starting VPN.")
                self.network_manager.start_psiphon()
                self.ui.vpnUseCheckbox.setChecked(True)
                time.sleep(2)

        if self.network_manager.is_psiphon_running():
            self.ui.vpnUseCheckbox.setChecked(True)
        self.psiphon_monitor.start()
        return wifi_connected, internet_connected

    def update_psiphon_ui(self, ui_running, tunnel_running, tunnel_active, established_connections):
        """Updates the VPN status labels based on the PsiphonMonitor thread's output."""
        # Main VPN status
        if not ui_running:
            status_text = "Not Running"
        elif not tunnel_running:
            status_text = "Running, Tunnel Stopped"
        elif not tunnel_active:
            status_text = "Running, Tunneling Failed"
        else:
            status_text = f"Running - {time.strftime('%H:%M')}"
        self.ui.vpnStatusValue.setText(status_text)

        # Tunneling status
        if tunnel_active and established_connections:
            tunneling_text = f"Succeed - Active"
        elif tunnel_running and not tunnel_active:
            tunneling_text = "Tunneling - In Progress"
        else:
            tunneling_text = "Not Tunneling"
        self.ui.vpnTunnelingValue.setText(tunneling_text)

    def handle_save_profile(self):
        """Saves a new WiFi profile from the UI inputs and optionally connects to it."""
        ssid = self.ui.ssidInput.text()
        password = self.ui.passwordInput.text()
        wifi_profiles = [(ssid, password)]

        if not ssid or not password:
            self.logger.error("SSID and password must be provided.")
            show_error("SSID and password must be provided.")
            return

        if self.model.collect_duplicate_profiles(wifi_profiles):
            self.logger.info(f"Profile for '{ssid}' saved successfully.")
            reply = show_question(f"Profile for '{ssid}' saved successfully. Do you want to connect now?", timed=True)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                if self.network_manager.is_psiphon_running():
                    self.network_manager.stop_psiphon()

                self.network_manager.set_wifi_credentials(ssid, password)
                self.ui.currentWifiLabel.setText(ssid)
                self.network_manager.connect_wifi()

            self.ui.ssidInput.clear()
            self.ui.passwordInput.clear()
            self.ui.ssidInput.setFocus()
        else:
            self.logger.error(f"Failed to save profile for '{ssid}'.")
            show_error(f"Failed to save profile for '{ssid}'.")

    def handle_switch_wifi(self):
        """Opens a new dialog for the user to select and connect to a different WiFi network."""
        try:
            dialog = WifiListController(self)
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.network_manager.set_wifi_credentials(dialog.selected_ssid, dialog.selected_password)
                display_text = f"{self.network_manager.current_ssid}"
                self.ui.currentWifiLabel.setText(display_text)

                if self.network_manager.is_psiphon_running():
                    self.network_manager.stop_psiphon()

                self.network_manager.connect_wifi()
                self.check_all_statuses()
        except Exception as e:
            self.logger.exception("Error in handle_switch_wifi")
            show_error(f"An error occurred: {e}")

    def check_all_statuses(self):
        """Triggers an update of all network and VPN status labels."""
        self.update_status_labels()

    def run_once_config(self):
        """
        Performs a one-time check and configuration of Wi-Fi and VPN connections based on
        the current network status and UI settings.
        """
        try:
            self.logger.info("Starting one-time network configuration...")
            wifi_status, wifi_message = self.network_manager.get_wifi_status()
            psiphon_status = self.network_manager.is_psiphon_running()
            use_vpn = self.ui.vpnUseCheckbox.isChecked()

            if not wifi_status:
                self.logger.info("Wi-Fi is not connected. Attempting to connect...")
                self.network_manager.connect_wifi()
                time.sleep(3)
                wifi_status, wifi_message = self.network_manager.get_wifi_status()
                if not wifi_status:
                    self.logger.warning("Failed to connect to Wi-Fi.")
                    show_error("Failed to connect to Wi-Fi. Please check credentials or try again.", "Error")
                    return

            internet_status = self.network_manager.get_internet_status()
            if not internet_status:
                self.logger.warning("Internet connection is down. Attempting to fix...")
                self.network_manager.disconnect_wifi()
                self.network_manager.connect_wifi()
                internet_status = self.network_manager.get_internet_status()
                if not internet_status:
                    self.logger.error("Failed to restore internet connection.")
                    show_error("Failed to restore internet connection.", "Error")
                    return

            if use_vpn:
                if not psiphon_status:
                    self.logger.info("VPN is not connected. Attempting to connect...")
                    self.network_manager.start_psiphon()
                    time.sleep(5)
                    if not self.network_manager.is_psiphon_running():
                        self.logger.warning("Failed to connect to VPN.")
                        show_warning("Failed to connect to VPN.", "Warning")
            else:
                if self.network_manager.is_psiphon_running():
                    self.logger.info("VPN is running, but 'Use VPN' is unchecked. Disconnecting VPN...")
                    self.network_manager.stop_psiphon()

            self.logger.info("Network configuration completed successfully.")
            self.update_status_labels()

        except Exception as e:
            self.logger.exception("An unexpected error occurred during auto-config.")
            show_error(f"An unexpected error occurred: {e}", "Error")

    def start_auto_config(self):
        """Starts a repeating timer to automatically check and manage network connections."""
        interval = self.ui.intervalSpinBox.value()
        if interval <= 0:
            self.logger.warning("Check interval must be greater than 0.")
            show_error("Check interval must be greater than 0.", "Error")
            return

        interval_ms = interval * 1000

        # Disable UI elements to prevent user from interfering with the timer.
        self.ui.intervalSpinBox.setReadOnly(True)
        self.ui.autoConfigButton.setEnabled(False)
        self.ui.stopAutoConfigButton.setEnabled(True)

        self.autoconfig_timer.start(interval_ms)
        self.logger.info(f"Auto-configuration started with an interval of {interval} seconds.")
        show_info(f"Auto-configuration started. Checking every {interval} seconds.", "Success")

    def stop_auto_config(self):
        """Stops the automatic network configuration timer and re-enables UI elements."""
        self.autoconfig_timer.stop()

        self.ui.intervalSpinBox.setReadOnly(False)
        self.ui.autoConfigButton.setEnabled(True)
        self.ui.stopAutoConfigButton.setEnabled(False)
        self.logger.info("Auto-configuration stopped.")
        show_info("Auto-configuration stopped.", "Success")

    def reset_wifi(self):
        """Disconnects and then reconnects to the current WiFi network."""
        self.logger.info("Starting Wi-Fi restart...")
        self.network_manager.disconnect_wifi()
        self.network_manager.connect_wifi()
        self.logger.info("Wi-Fi reset completed.")

    def reset_vpn(self):
        """Stops and then restarts the VPN connection."""
        self.logger.info("Starting VPN restart...")
        self.network_manager.stop_psiphon()
        self.network_manager.start_psiphon()
        self.logger.info("VPN reset completed.")

    def handle_copy_log(self):
        """Copies the entire log content from the UI to the system clipboard."""
        clipboard = QtWidgets.QApplication.clipboard()
        log_text = self.log_model.all_logs()
        if log_text:
            clipboard.setText(log_text)
            self.logger.info("Log content copied to clipboard.")
            show_info("Log content copied to clipboard.", "Success")
        else:
            self.logger.warning("No log content to copy.")
            show_warning("No log content to copy.", "Warning")

    def closeEvent(self, event):
        """This method is called when the application window is closing.
        It ensures that the Psiphon monitoring thread is gracefully stopped."""
        self.psiphon_monitor.stop()
        event.accept()