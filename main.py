import sys
from ui_components import ApplicationWindow
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    appScreen = app.primaryScreen()
    screenGeometry = appScreen.geometry()

    applicationWindow = ApplicationWindow(screenGeometry)
    applicationWindow.show()
    sys.exit(app.exec())