from PyQt6.QtCore import QAbstractListModel, Qt, QVariant, QModelIndex, pyqtSignal
from PyQt6.QtGui import QColor


class LogListModel(QAbstractListModel):
    """
    A custom QAbstractListModel to manage log messages for a Qt view (e.g., QListView).
    """

    # Custom signal emitted when a new log message is added.
    log_added = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logs = []  # List to store the log messages (strings).
        self._log_levels = []  # List to store the log levels (e.g., "INFO", "ERROR").

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the data for a given index and role.
        """
        if not index.isValid() or index.row() >= self.rowCount():
            return None

        # Return the log message for the DisplayRole.
        if role == Qt.ItemDataRole.DisplayRole:
            return self._logs[index.row()]

        return QVariant()  # Return an invalid QVariant for unsupported roles.

    def rowCount(self, parent=None):
        """Returns the number of rows in the model, which is the number of logs."""
        return len(self._logs)

    def add_log(self, message, level="INFO"):
        """
        Adds a new log message to the model.
        """
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        self._logs.append(message)  # Add the log message.
        self._log_levels.append(level)  # Add the corresponding log level.

        self.endInsertRows()

        self.log_added.emit()

    def clear(self):
        """Clears all log messages from the model."""
        self.beginResetModel()
        self._logs.clear()
        self._log_levels.clear()
        self.endResetModel()

    def all_logs(self):
        """
        Returns all log messages as a single string.
        """
        return "\n".join(self._logs)