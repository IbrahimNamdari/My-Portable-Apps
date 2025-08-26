import logging
from PyQt6.QtCore import QObject, pyqtSignal


class QtSignalHandler(logging.Handler, QObject):
    """
    A custom logging handler that emits log records as a PyQt signal.
    """

    # Signal to emit log messages: (formatted_message, log_level)
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        """Initializes the handler and sets up the log message format."""
        super().__init__()
        QObject.__init__(self, parent)
        self.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    def emit(self, record):
        """
        Emits the formatted log record as a signal.
        """
        msg = self.format(record)
        level = record.levelname
        self.log_signal.emit(msg, level)


def setup_logging():
    """
    Configures the application's logging system.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers.
    if not logger.handlers:
        # File Handler: Logs all messages to a file.
        file_handler = logging.FileHandler('app.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console Handler: Prints INFO level and above messages to the console.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Return the custom handler for GUI integration.
    return QtSignalHandler()