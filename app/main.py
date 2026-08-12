import sys
from PySide6.QtWidgets import QApplication
from app.generated import resources_rc
from app.windows.createAccount.createAccount import VentanaCrearCuenta
from PySide6.QtGui import QIcon

#!AHORITA SOLO ESTOY PROBANDO PARA VER LA PAGINA DE createAccount
app = QApplication(sys.argv)
ventana = VentanaCrearCuenta()
ventana.setWindowTitle("Empresa")
ventana.setWindowIcon(QIcon(":images/logo.png"))
ventana.show()
sys.exit(app.exec())