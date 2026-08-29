import sys
#*Importaciones relacionadas a PySide6
from PySide6.QtWidgets import QApplication
from app.generated import resources_rc
from PySide6.QtGui import QIcon
#*Importaciones relacionados a la view
from app.views.createAccount.createAccount import VentanaCrearCuenta
from app.views.login.login import VentanaLogin
from app.views.login.recuperarContra import VentanaRecuperarContra
#*Importaciones relacionadas a la base de datos y SQLAlchemy
from app.database.init_db import init_db
from app.database.connection import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.user_services import UserService
from app.controllers.user_controller import UserController


#!AHORITA SOLO ESTOY PROBANDO PARA VER LAS VENTANA QUE VOY HACIENDO
if __name__=="__main__":
    init_db()
    app = QApplication(sys.argv)
    session = SessionLocal()
    user_repository = UserRepository(session)
    user_service = UserService(user_repository)
    user_controller = UserController(user_service)
    #ventana = VentanaLogin(user_controller)
    ventana=VentanaRecuperarContra(user_controller)
    #ventana=VentanaCrearCuenta(user_controller)
    ventana.setWindowTitle("Finanzen")
    ventana.setWindowIcon(QIcon(":images/logo.png"))
    ventana.show()
    sys.exit(app.exec())