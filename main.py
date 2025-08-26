import sys
from PyQt6 import QtWidgets
from core.controller.main_controller import MainController

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainController()
    main_window.setWindowTitle("Portable Network Manager")

    # روش جایگزین برای قرار دادن در مرکز
    main_window.show()
    main_window.move(
        (QtWidgets.QApplication.primaryScreen().availableGeometry().width() - main_window.width()) // 2,
        (QtWidgets.QApplication.primaryScreen().availableGeometry().height() - main_window.height()) // 2
    )

    sys.exit(app.exec())

