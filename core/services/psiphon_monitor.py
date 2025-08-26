import time
import psutil
import logging
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class PsiphonMonitor(QThread):
    """
    A separate thread for continuously monitoring the status of Psiphon processes.
    It emits a signal with real-time status updates to the main application.
    """

    # Signal emitted with a comprehensive status update.
    # Parameters: ui_running, tunnel_running, tunnel_active, established_connections
    status_updated = pyqtSignal(bool, bool, bool, bool)

    def __init__(self, parent: QObject = None):
        """Initializes the monitor with a logger and status flags."""
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.monitoring = False

    def _check_psiphon_processes(self) -> tuple[bool, bool]:
        """
        Checks for the presence of the main Psiphon processes.

        Returns:
            A tuple containing two booleans: (is_ui_running, is_tunnel_running).
        """
        is_ui_running = False
        is_tunnel_running = False
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info.get('name', '')
                if 'psiphon3.exe' in name.lower():
                    is_ui_running = True
                elif 'psiphon-tunnel-core.exe' in name.lower():
                    is_tunnel_running = True
            return is_ui_running, is_tunnel_running
        except Exception as e:
            self.logger.error(f"Error checking processes: {e}")
            return False, False

    def _check_tunnel_status(self) -> bool:
        """
        Checks if the Psiphon tunnel has an active connection.

        Returns:
            A boolean indicating if the tunnel is active.
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info.get('name') and 'psiphon-tunnel-core.exe' in proc.info.get('name').lower():
                    try:
                        connections = proc.net_connections()
                        for conn in connections:
                            if conn.status == psutil.CONN_ESTABLISHED:
                                return True
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        continue
            return False
        except Exception as e:
            self.logger.error(f"Error checking tunnel status: {e}")
            return False

    def run(self):
        """The main loop for the monitoring thread."""
        self.monitoring = True
        self.logger.info("Psiphon monitoring started.")

        last_connected_status = None

        while self.monitoring:
            try:
                # Check the basic status of Psiphon processes and tunnel
                ui_running, tunnel_running = self._check_psiphon_processes()
                tunnel_active = self._check_tunnel_status()

                # Determine the overall connected status.
                psiphon_connected = ui_running and tunnel_running and tunnel_active

                # Log status changes for a clearer history.
                if psiphon_connected != last_connected_status:
                    if psiphon_connected:
                        self.logger.info("Psiphon tunnel connected successfully.")
                    elif last_connected_status is not None:
                        self.logger.info("Psiphon tunnel disconnected.")
                    else:
                        self.logger.info("Psiphon initial status: Not connected.")
                    last_connected_status = psiphon_connected

                # Emit the signal with the latest status.
                self.status_updated.emit(
                    ui_running,
                    tunnel_running,
                    tunnel_active,
                    psiphon_connected
                )

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

            # Sleep to prevent high CPU usage.
            time.sleep(1)

    def stop(self):
        """Stops the monitoring thread gracefully."""
        self.logger.info("Stopping Psiphon monitoring.")
        self.monitoring = False
        self.wait()