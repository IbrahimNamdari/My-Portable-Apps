import os
import subprocess
import time
import requests
import logging
import re
from core.model.wifi_profiles_model import WifiProfilesModel
from core.utils.message_box import *
from core.utils.paths import resource_path


class NetworkManager:
    """
    Manages network-related operations including Wi-Fi connectivity, internet status
    checks, and Psiphon VPN control.
    """

    def __init__(self):
        # Initialize instance variables and a dedicated logger
        self.current_ssid = None
        self.current_password = None
        self.psiphon_path = resource_path("otherapps/psiphon3.exe")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = WifiProfilesModel()
        self.available_networks = []

        # Define startupinfo to hide the console window for subprocess calls
        self.startupinfo = subprocess.STARTUPINFO()
        self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.startupinfo.wShowWindow = subprocess.SW_HIDE

    def get_wifi_passwords(self):
        """
        Retrieves a list of all saved Wi-Fi profiles and their passwords from the system.
        This method uses 'netsh' commands to gather the information.

        Returns:
            list: A list of tuples, where each tuple contains (ssid, password).
                  Returns an empty list on failure.
        """
        try:
            self.logger.info("Retrieving all Wi-Fi profiles from the system.")

            # Run 'netsh' command to get a list of all user profiles.
            profile_result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                startupinfo=self.startupinfo
            )

            if profile_result.returncode != 0:
                self.logger.error("Error running 'netsh' command to get profiles.")
                return []

            profiles = re.findall(r'All User Profile\s*:\s*(.+)', profile_result.stdout)
            wifi_list = []

            # For each profile, run another command to get the password.
            for ssid in profiles:
                try:
                    self.logger.debug(f"Attempting to get password for profile: {ssid}")
                    password_result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'profile', f'name="{ssid}"', 'key=clear'],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        startupinfo=self.startupinfo
                    )

                    password = "Not Available"
                    match = re.search(r'Key Content\s*:\s*(.+)', password_result.stdout)
                    if match:
                        password = match.group(1).strip()

                    wifi_list.append((ssid, password))
                    self.logger.debug(f"Found profile '{ssid}' with password status: '{password}'")
                except Exception as e:
                    self.logger.error(f"Error getting password for {ssid}: {e}")
                    wifi_list.append((ssid, "Error"))

            self.logger.info(f"Successfully retrieved {len(wifi_list)} Wi-Fi profiles.")
            return wifi_list

        except Exception as e:
            self.logger.exception("General error retrieving Wi-Fi profiles.")
            return []

    def get_current_wifi(self):
        """
        Retrieves the SSID of the currently connected Wi-Fi network.

        Returns:
            str: The SSID of the connected network, or None if not connected.
        """
        try:
            self.logger.debug("Checking for the currently connected Wi-Fi network.")
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=True,
                startupinfo=self.startupinfo
            )

            match = re.search(r'SSID\s*:\s*(.+)', result.stdout)
            if match:
                ssid = match.group(1).strip()
                self.logger.info(f"Currently connected to: {ssid}")
                return ssid

            self.logger.info("Not connected to any Wi-Fi network.")
            return None
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error checking current Wi-Fi connection: {e}")
            return None
        except Exception as e:
            self.logger.exception("Unexpected error in get_current_wifi.")
            return None

    def set_wifi_credentials(self, ssid, password):
        """
        Sets the Wi-Fi credentials to be used for future connection attempts.

        Args:
            ssid (str): The SSID of the Wi-Fi network.
            password (str): The password for the Wi-Fi network.
        """
        self.current_ssid = ssid
        self.current_password = password
        self.logger.info(f"Wi-Fi credentials set for SSID: {ssid}")

    def get_wifi_status(self):
        """
        Checks if the device is currently connected to the specified Wi-Fi network.

        Returns:
            tuple: A tuple containing (bool, str). The boolean indicates if
                   the connection is active, and the string provides a status message.
        """
        if not self.current_ssid:
            self.logger.warning("Wi-Fi credentials not set. Cannot check status.")
            return False, "Wi-Fi not selected"

        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=True,
                startupinfo=self.startupinfo
            )

            if self.current_ssid in result.stdout:
                self.logger.info(f"Connected to Wi-Fi: {self.current_ssid}")
                return True, f"Connected to {self.current_ssid}"
            else:
                self.logger.info(f"Not connected to Wi-Fi: {self.current_ssid}")
                return False, "Not Connected"
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error checking Wi-Fi status: {e}")
            return False, "Error"
        except Exception as e:
            self.logger.exception("Unexpected error in get_wifi_status.")
            return False, "Error"

    def get_available_wifi(self):
        """
        Scans and updates the list of available Wi-Fi networks.
        The list is stored in the `self.available_networks` attribute.
        """
        try:
            self.logger.info("Scanning for available Wi-Fi networks.")
            result = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'networks'],
                startupinfo=self.startupinfo
            ).decode('utf-8')

            if result:
                self.available_networks = [
                    line.split(':')[1].strip()
                    for line in result.split('\n')
                    if 'SSID' in line and 'BSSID' not in line
                ]
                self.logger.info(f"Found {len(self.available_networks)} available Wi-Fi networks.")
            else:
                self.logger.warning("No Wi-Fi networks found.")
                self.available_networks = []
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error scanning for Wi-Fi networks: {e}")
            self.available_networks = []
        except Exception as e:
            self.logger.exception("Unexpected error in get_available_wifi.")
            self.available_networks = []

    def connect_wifi(self):
        """
        Attempts to connect to the configured Wi-Fi network.
        If no network is set, it tries to connect to a known available network.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        is_connected, _ = self.get_wifi_status()
        if is_connected:
            self.logger.info("Wi-Fi is already connected.")
            return True

        if not self.current_ssid or not self.current_password:
            self.logger.warning("Wi-Fi credentials are missing. Trying to auto-select from known profiles.")
            self.get_available_wifi()
            known_profiles = self.model.get_all_profiles_details()

            for ssid, password in known_profiles:
                if ssid in self.available_networks:
                    self.current_ssid = ssid
                    self.current_password = password
                    self.logger.info(f"Auto-selected known network: {ssid}")
                    break

        if not self.current_ssid:
            self.logger.error("No Wi-Fi network selected for connection.")
            return False

        try:
            # Check if a profile for the SSID exists and create it if not.
            profile_result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                check=True,
                startupinfo=self.startupinfo
            )
            if self.current_ssid not in profile_result.stdout:
                self.logger.info(f"Creating Wi-Fi profile for: {self.current_ssid}.")
                self.create_wifi_profile()

            self.logger.info(f"Attempting to connect to Wi-Fi: {self.current_ssid}.")
            subprocess.run(
                f'netsh wlan connect name="{self.current_ssid}"',
                shell=True,
                startupinfo=self.startupinfo
            )
            time.sleep(5)  # Wait for the connection to establish.

            # Verify the connection status.
            new_status, status_message = self.get_wifi_status()
            if new_status:
                self.logger.info("Wi-Fi connected successfully.")
            else:
                self.logger.warning(f"Failed to connect to Wi-Fi: {status_message}.")
            return new_status

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error connecting to Wi-Fi: {e}")
            return False
        except Exception as e:
            self.logger.exception("Unexpected error in connect_wifi.")
            return False

    def disconnect_wifi(self):
        """
        Disconnects from the current Wi-Fi network.

        Returns:
            bool: True if disconnection is successful, False otherwise.
        """
        is_connected, _ = self.get_wifi_status()
        if not is_connected:
            self.logger.info("Wi-Fi is already disconnected.")
            return True

        try:
            self.logger.info("Disconnecting from Wi-Fi.")
            subprocess.run(
                'netsh wlan disconnect',
                shell=True,
                startupinfo=self.startupinfo
            )
            time.sleep(2)  # Wait for disconnection.

            new_status, _ = self.get_wifi_status()
            if not new_status:
                self.logger.info("Wi-Fi disconnected successfully.")
            else:
                self.logger.warning("Failed to disconnect from Wi-Fi.")
            return not new_status
        except Exception as e:
            self.logger.exception("Error disconnecting from Wi-Fi.")
            return False

    def get_internet_status(self):
        """
        Checks for an active internet connection by making a request to a well-known URL.

        Returns:
            bool: True if internet is active, False otherwise.
        """
        try:
            self.logger.debug("Checking for an active internet connection.")
            # Use a reliable endpoint that returns a 204 No Content status.
            response = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=5)
            status = response.status_code == 204

            if status:
                self.logger.info("Internet connection is active.")
            else:
                self.logger.warning("Internet connection is inactive.")
            return status
        except requests.exceptions.RequestException:
            self.logger.error("Internet check failed.")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error in get_internet_status: {e}")
            return False

    def is_psiphon_running(self):
        """
        Checks if the Psiphon executable is currently running in the background.

        Returns:
            bool: True if psiphon3.exe is running, False otherwise.
        """
        try:
            self.logger.debug("Checking if Psiphon is running.")
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                check=True,
                startupinfo=self.startupinfo
            )
            is_running = "psiphon3.exe" in result.stdout.lower()
            self.logger.debug(f"Psiphon is running: {is_running}")
            return is_running
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error checking Psiphon status: {e}")
            return False
        except Exception as e:
            self.logger.exception("Unexpected error in is_psiphon_running.")
            return False

    def start_psiphon(self):
        """
        Starts the Psiphon VPN application.

        Returns:
            bool: True if Psiphon starts successfully, False otherwise.
        """
        if self.is_psiphon_running():
            self.logger.info("Psiphon is already running.")
            return True

        try:
            self.logger.info("Attempting to start Psiphon.")
            subprocess.Popen(self.psiphon_path, startupinfo=self.startupinfo)
            time.sleep(5)  # Wait for the application to initialize.

            if self.is_psiphon_running():
                self.logger.info("Psiphon started successfully.")
                return True
            else:
                self.logger.warning("Psiphon failed to start.")
                return False
        except FileNotFoundError:
            self.logger.error(f"Psiphon executable not found at {self.psiphon_path}.")
            show_error("Psiphon3.exe file not found. Please check the path.", "Error")
            return False
        except Exception as e:
            self.logger.exception("Error starting Psiphon.")
            return False

    def stop_psiphon(self):
        """
        Stops the Psiphon VPN process using `taskkill`.

        Returns:
            bool: True if Psiphon is stopped successfully, False otherwise.
        """
        if not self.is_psiphon_running():
            self.logger.info("Psiphon is already stopped.")
            return True

        try:
            self.logger.info("Attempting to stop Psiphon.")
            subprocess.run(
                'taskkill /IM psiphon3.exe /F',
                shell=True,
                startupinfo=self.startupinfo
            )
            time.sleep(2)  # Wait for the process to terminate.

            if not self.is_psiphon_running():
                self.logger.info("Psiphon stopped successfully.")
                return True
            else:
                self.logger.warning("Psiphon failed to stop.")
                return False
        except Exception as e:
            self.logger.exception("Error stopping Psiphon.")
            return False

    def create_wifi_profile(self):
        """
        Creates a temporary Wi-Fi profile XML file and imports it to the system.
        This is necessary for connecting to a new network programmatically.

        Returns:
            bool: True if the profile is created and added successfully, False otherwise.
        """
        if not self.current_ssid or not self.current_password:
            self.logger.error("Wi-Fi credentials are required to create a profile.")
            return False

        try:
            self.logger.info(f"Creating a Wi-Fi profile for: {self.current_ssid}.")
            profile_content = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{self.current_ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{self.current_ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{self.current_password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""

            # Save the profile content to a temporary XML file.
            file_path = resource_path(f"{self.current_ssid}.xml")
            with open(file_path, "w") as f:
                f.write(profile_content)

            # Add the profile to the system using 'netsh'.
            subprocess.run(
                ["netsh", "wlan", "add", "profile", f"filename={file_path}"],
                check=True,
                startupinfo=self.startupinfo
            )
            os.remove(file_path)  # Clean up the temporary file.
            self.logger.info("Wi-Fi profile created successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error creating Wi-Fi profile: {e}")
            show_error("Failed to create Wi-Fi profile. Check credentials.", "Error")
            return False
        except Exception as e:
            self.logger.exception("Unexpected error in create_wifi_profile.")
            show_error("Failed to create Wi-Fi profile.", "Error")
            return False