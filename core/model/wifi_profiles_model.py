import sqlite3
import os
import logging
from PyQt6 import QtWidgets
from core.view.duplicate_profiles_dialog import DuplicateProfilesDialog
from core.utils.paths import resource_path

# Path to the SQLite database file.
DB_FILE = resource_path('core/model/data/wifi_profiles.db')


class WifiProfilesModel:
    """
    Manages all database operations related to Wi-Fi profiles, including
    connecting to the database, creating tables, and handling profile data.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_path = DB_FILE
        self.ensure_db_directory()
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def ensure_db_directory(self):
        """Creates the directory for the database file if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
                self.logger.info("Created data directory.")
            except OSError as e:
                self.logger.error(f"Failed to create data directory: {e}")

    def connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.logger.info("Database connection established.")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to the database: {e}")
            self.conn = None

    def create_table(self):
        """Creates the 'profiles' table if it does not already exist."""
        if self.conn:
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS profiles
                    (
                        ssid TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )
                ''')
                self.conn.commit()
                self.logger.info("Database table 'profiles' is ready.")
            except sqlite3.Error as e:
                self.logger.error(f"Error creating table: {e}")

    def collect_duplicate_profiles(self, profiles):
        """
        Checks a list of Wi-Fi profiles for duplicates in the database.
        Handles new profiles and prompts the user for action on duplicates.
        """
        if not self.conn:
            return False

        duplicate_profiles = []
        new_profiles = []

        try:
            for ssid, password in profiles:
                self.cursor.execute('SELECT password FROM profiles WHERE ssid = ?', (ssid,))
                existing_profile = self.cursor.fetchone()

                if existing_profile:
                    # If a profile with the same SSID exists, check if the password is different.
                    if existing_profile[0] != password:
                        self.logger.info(f"Duplicate profile '{ssid}' found with a different password.")
                        duplicate_profiles.append((ssid, password))
                    else:
                        self.logger.info(f"Profile '{ssid}' already exists with same password. Skipping.")
                else:
                    self.logger.info(f"Adding Wi-Fi '{ssid}' as a new profile.")
                    new_profiles.append((ssid, password))

            # Save all new profiles.
            for ssid, password in new_profiles:
                self.save_profile(ssid, password)

            # Handle duplicates by showing a dialog to the user.
            if duplicate_profiles:
                success = self.handle_duplicate_profiles(duplicate_profiles)
                if not success:
                    self.logger.warning("User cancelled duplicate profile handling.")

            self.conn.commit()
            total_processed = len(new_profiles) + len(duplicate_profiles)
            self.logger.info(f"Successfully processed {total_processed} profiles.")
            return True

        except sqlite3.Error as e:
            self.logger.error(f"Database error processing profiles: {e}")
            self.conn.rollback()
            return False

    def save_profile(self, ssid, password):
        """Saves a single Wi-Fi profile to the database."""
        if not self.conn:
            return False
        try:
            self.cursor.execute('INSERT INTO profiles (ssid, password) VALUES (?, ?)', (ssid, password))
            self.conn.commit()
            self.logger.info(f"Profile for '{ssid}' saved successfully.")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Database error saving profile: {e}")
            return False

    def handle_duplicate_profiles(self, duplicate_profiles):
        """
        Displays a dialog to the user to handle multiple duplicate profiles.
        Allows the user to choose to replace or skip each profile.
        """
        if not duplicate_profiles:
            return True

        self.logger.info(f"Showing duplicate dialog for {len(duplicate_profiles)} profiles.")

        # Create and show the duplicate profiles dialog.
        dialog = DuplicateProfilesDialog(duplicate_profiles)
        result = dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            choices = dialog.get_choices()
            success_count = 0

            for ssid, password in duplicate_profiles:
                choice = choices.get(ssid, "skip")

                if choice == "replace":
                    # Update the existing profile with the new password.
                    try:
                        self.cursor.execute('UPDATE profiles SET password = ? WHERE ssid = ?', (password, ssid))
                        success_count += 1
                        self.logger.info(f"Profile for '{ssid}' updated.")
                    except sqlite3.Error as e:
                        self.logger.error(f"Error updating profile '{ssid}': {e}")
                        continue
                elif choice == "skip":
                    self.logger.info(f"Profile for '{ssid}' skipped by the user.")
                else:
                    self.logger.warning(f"Unknown choice '{choice}' for profile '{ssid}'.")

            if success_count > 0:
                self.conn.commit()
                self.logger.info(f"Successfully updated {success_count} duplicate profiles.")
                return True

            self.logger.info("No duplicate profiles were updated (all skipped).")
            return True

        self.logger.info("User cancelled duplicate profile handling.")
        return False

    def get_all_profiles_details(self):
        """Retrieves all saved profiles (SSID and password) from the database."""
        if not self.conn:
            return []
        try:
            self.cursor.execute('SELECT ssid, password FROM profiles')
            profiles = self.cursor.fetchall()
            self.logger.info(f"Retrieved {len(profiles)} profiles from the database.")
            return profiles
        except sqlite3.Error as e:
            self.logger.error(f"Database error retrieving profiles: {e}")
            return []

    def get_password(self, ssid):
        """Retrieves the password for a given SSID."""
        if not self.conn:
            return None
        try:
            self.cursor.execute('SELECT password FROM profiles WHERE ssid = ?', (ssid,))
            result = self.cursor.fetchone()
            if result:
                self.logger.info(f"Password retrieved for '{ssid}'.")
                return result[0]
            else:
                self.logger.warning(f"No password found for '{ssid}'.")
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Database error retrieving password for '{ssid}': {e}")
            return None

    def delete_profile(self, ssid):
        """Deletes a Wi-Fi profile from the database."""
        if not self.conn:
            return False
        try:
            self.cursor.execute('DELETE FROM profiles WHERE ssid = ?', (ssid,))
            if self.cursor.rowcount > 0:
                self.conn.commit()
                self.logger.info(f"Profile for '{ssid}' deleted successfully.")
                return True
            else:
                self.logger.warning(f"Profile for '{ssid}' not found.")
                return False
        except sqlite3.Error as e:
            self.logger.error(f"Database error deleting profile '{ssid}': {e}")
            return False

    def close_connection(self):
        """Closes the database connection gracefully."""
        if self.conn:
            try:
                self.conn.close()
                self.logger.info("Database connection closed.")
            except sqlite3.Error as e:
                self.logger.error(f"Error closing database connection: {e}")
            finally:
                self.conn = None
                self.cursor = None