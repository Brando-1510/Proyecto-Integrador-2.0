import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.generated import resources_rc
from app.database.init_db import init_db
from app.core.app_container import AppContainer
from app.core.app_controller import AppController


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("Finanzen")
    app.setWindowIcon(QIcon(":/images/logo.png"))
    container = AppContainer()
    app_controller = AppController(container)
    app_controller.start()
    exit_code = app.exec()
    app_controller.close()
    sys.exit(exit_code)