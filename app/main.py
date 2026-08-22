import sys
from PySide6.QtWidgets import QApplication
from app.generated import resources_rc
from app.views.createAccount.createAccount import VentanaCrearCuenta
from app.views.login.login import VentanaLogin
from PySide6.QtGui import QIcon

#!AHORITA SOLO ESTOY PROBANDO PARA VER LAS VENTANA QUE VOY HACIENDO
app = QApplication(sys.argv)
ventana = VentanaCrearCuenta()
#ventana=VentanaLogin()
ventana.setWindowTitle("Empresa")
ventana.setWindowIcon(QIcon(":images/logo.png"))
ventana.show()
sys.exit(app.exec())