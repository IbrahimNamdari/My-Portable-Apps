from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox, QWidget, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from typing import Optional


class TimedQuestionDialog(QDialog):
    """
    A custom dialog that shows a question and automatically selects a default button
    after a specified timeout.
    """

    def __init__(self, title: str, message: str, timeout: int = 10, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.timeout = timeout

        # This is a bit of a hack, but it works
        self.result_button = QMessageBox.StandardButton.No

        layout = QVBoxLayout(self)

        self.message_label = QLabel(message)
        layout.addWidget(self.message_label)

        self.countdown_label = QLabel()
        layout.addWidget(self.countdown_label)

        # Use StandardButton.Yes and StandardButton.No for consistency
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
        self.update_countdown()

    def update_countdown(self):
        """Updates the countdown label and handles the timeout."""
        if self.timeout > 0:
            self.countdown_label.setText(f"Defaulting to 'Yes' in {self.timeout} seconds...")
            self.timeout -= 1
        else:
            self.timer.stop()
            # Automatically 'accept' the dialog after timeout
            self.done(QMessageBox.StandardButton.Yes)

    def accept(self):
        """Overrides the accept method to return the 'Yes' button code."""
        self.timer.stop()
        self.done(QMessageBox.StandardButton.Yes)

    def reject(self):
        """Overrides the reject method to return the 'No' button code."""
        self.timer.stop()
        self.done(QMessageBox.StandardButton.No)


class MessageBox:
    """A helper class to simplify displaying various QMessageBox dialogs."""

    @staticmethod
    def show(
            title: str,
            message: str,
            icon: QMessageBox.Icon = QMessageBox.Icon.Information,
            buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
            parent: Optional[QWidget] = None
    ) -> int:
        """
        Displays a QMessageBox with custom settings.

        Args:
            title: The title of the message box window.
            message: The message text to display.
            icon: The icon for the message box.
            buttons: The standard buttons to show on the message box.
            parent: The parent widget for the message box (optional).

        Returns:
            An integer representing the standard button role that was clicked.
        """
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStandardButtons(buttons)
        return msg.exec()

    @staticmethod
    def error(
            message: str,
            title: str = "Error",
            parent: Optional[QWidget] = None
    ) -> int:
        """Displays an error message box."""
        return MessageBox.show(title, message, QMessageBox.Icon.Critical, QMessageBox.StandardButton.Ok, parent)

    @staticmethod
    def info(
            message: str,
            title: str = "Information",
            parent: Optional[QWidget] = None
    ) -> int:
        """Displays an informational message box."""
        return MessageBox.show(title, message, QMessageBox.Icon.Information, QMessageBox.StandardButton.Ok, parent)

    @staticmethod
    def warning(
            message: str,
            title: str = "Warning",
            parent: Optional[QWidget] = None
    ) -> int:
        """Displays a warning message box."""
        return MessageBox.show(title, message, QMessageBox.Icon.Warning, QMessageBox.StandardButton.Ok, parent)

    @staticmethod
    def success(
            message: str,
            title: str = "Success",
            parent: Optional[QWidget] = None
    ) -> int:
        """Displays a success message box."""
        return MessageBox.show(title, message, QMessageBox.Icon.Information, QMessageBox.StandardButton.Ok, parent)

    @staticmethod
    def question(
            message: str,
            title: str = "Question",
            buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            parent: Optional[QWidget] = None,
            timed: bool = False,
            timeout: int = 10
    ) -> int:
        """
        Displays a question message box with Yes/No buttons.

        Args:
            message: The message text to display.
            title: The title of the message box.
            buttons: The buttons to display (defaults to Yes|No).
            parent: The parent widget (optional).
            timed: If True, uses a custom dialog with a timeout.
            timeout: The duration in seconds before the dialog defaults to 'Yes' (only for timed dialog).

        Returns:
            An integer representing the standard button role that was clicked.
        """
        if timed:
            dialog = TimedQuestionDialog(title, message, timeout, parent)
            return dialog.exec()
        else:
            return MessageBox.show(title, message, QMessageBox.Icon.Question, buttons, parent)


# Convenience functions for quick access
def show_error(message: str, title: str = "Error", parent: Optional[QWidget] = None) -> int:
    """Quickly displays an error message box."""
    return MessageBox.error(message, title, parent)


def show_info(message: str, title: str = "Information", parent: Optional[QWidget] = None) -> int:
    """Quickly displays an informational message box."""
    return MessageBox.info(message, title, parent)


def show_warning(message: str, title: str = "Warning", parent: Optional[QWidget] = None) -> int:
    """Quickly displays a warning message box."""
    return MessageBox.warning(message, title, parent)


def show_success(message: str, title: str = "Success", parent: Optional[QWidget] = None) -> int:
    """Quickly displays a success message box."""
    return MessageBox.success(message, title, parent)


def show_question(
        message: str,
        title: str = "Question",
        parent: Optional[QWidget] = None,
        timed: bool = False,
        timeout: int = 10
) -> int:
    """
    Quickly displays a question message box, with an optional timeout.

    Args:
        message: The message text.
        title: The dialog title.
        parent: The parent widget (optional).
        timed: If True, enables a timeout.
        timeout: The timeout duration in seconds.

    Returns:
        An integer representing the standard button role that was clicked.
    """
    return MessageBox.question(message, title, parent=parent, timed=timed, timeout=timeout)