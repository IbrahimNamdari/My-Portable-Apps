import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from core.controller.main_controller import MainController
from core.utils.paths import resource_path

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    app_icon_path = resource_path("img/mpas.ico")
    app_icon.addPixmap(QtGui.QPixmap(app_icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
    app.setWindowIcon(app_icon)

    main_window = MainController()
    main_window.setWindowTitle("MPA (My Portable Apps)")
    window_icon = QtGui.QIcon()
    window_icon_path = resource_path("img/mpas.png")
    window_icon.addPixmap(QtGui.QPixmap(window_icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
    main_window.setWindowIcon(window_icon)

    # روش جایگزین برای قرار دادن در مرکز
    main_window.show()
    main_window.move(
        (QtWidgets.QApplication.primaryScreen().availableGeometry().width() - main_window.width()) // 2,
        (QtWidgets.QApplication.primaryScreen().availableGeometry().height() - main_window.height()) // 2
    )

    sys.exit(app.exec())

