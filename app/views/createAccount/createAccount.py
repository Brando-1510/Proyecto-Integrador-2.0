import os
from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLineEdit, QMessageBox, QVBoxLayout
from PySide6.QtGui import QFontDatabase, QIcon, QAction
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.core.screen_utils import calcular_tamano_pantalla
from app.utils.validators import ValidadoresUI as V, ValidadoresDatos as VD

class VentanaCrearCuenta(QWidget):
    volver_login_requested = Signal()
    register_successful = Signal(object)
    def __init__(self, user_controller, remembered_accounts=None):
        super().__init__()
        self.controller = user_controller
        self.remembered_accounts = remembered_accounts
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../ui/createAccount.ui"))
        self.ui = QUiLoader().load(path, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar la interfaz Crear Cuenta: {path}")
        width, height = calcular_tamano_pantalla(0.8, 0.8)
        self.resize(width, height)
        self.setMinimumSize(900, 570)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self._load_fonts()
        self._setup_password(self.ui.inputContrasena)
        self._setup_password(self.ui.inputContrasenaConfirmar)
        today = QtCore.QDate.currentDate()
        limit = today.addYears(-18)
        self.ui.inputFecha.setCalendarPopup(True)
        self.ui.inputFecha.setMaximumDate(limit)
        self.ui.inputFecha.setDate(limit)
        self.ui.checkBoxRecordar.setText("Recordar mi cuenta en este dispositivo")
        self.ui.checkBoxRecordar.setChecked(False)
        self.ui.BtnCrearCuenta.clicked.connect(self.guardar)
        self.ui.BtnLogin.clicked.connect(self.volver_login_requested.emit)
        self.showMaximized()

    def _load_fonts(self):
        a = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        b = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if a >= 0 and b >= 0:
            fa, fb = QFontDatabase.applicationFontFamilies(a), QFontDatabase.applicationFontFamilies(b)
            if fa and fb:
                self.ui.setStyleSheet(self.ui.styleSheet() + estilos_fuentes(fb[0], fa[0]))

    @staticmethod
    def _setup_password(line_edit):
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        eye = QAction(line_edit)
        eye.setIcon(QIcon(":/icons/openEye.svg"))
        eye.setCheckable(True)
        line_edit.addAction(eye, QLineEdit.ActionPosition.TrailingPosition)
        def toggle(visible):
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)
            eye.setIcon(QIcon(":/icons/closeEye.svg" if visible else ":/icons/openEye.svg"))
        eye.toggled.connect(toggle)

    def guardar(self):
        if not V.tienen_contenido(self.ui.inputNombre, self.ui.inputCorreo,
                        self.ui.inputContrasena, self.ui.inputContrasenaConfirmar):
            QMessageBox.warning(self.ui, "Campos obligatorios", "Debes completar todos los campos.")
            return
        name = self.ui.inputNombre.text().strip()
        email = self.ui.inputCorreo.text().strip().casefold()
        password = self.ui.inputContrasena.text()  # Preservar caracteres exactos.
        password2 = self.ui.inputContrasenaConfirmar.text()
        if not VD.validar_correo(email) or not VD.validar_nombre(self.ui, name):
            if not VD.validar_correo(email):
                QMessageBox.warning(self.ui, "Correo inválido", "Introduce un correo electrónico válido.")
            return
        if not VD.evaluar_contrasena(self.ui, password):
            return
        if not VD.comparar_contraseñas(self.ui, password, password2):
            return
        self.ui.BtnCrearCuenta.setEnabled(False)
        try:
            result = self.controller.register_user(name, email, self.ui.inputFecha.date().toPython(), password)
        finally:
            self.ui.BtnCrearCuenta.setEnabled(True)
        if not result.get("success"):
            QMessageBox.warning(self.ui, "Error al registrar", result.get("message", "Error inesperado"))
            return
        if self.ui.checkBoxRecordar.isChecked() and self.remembered_accounts:
            stored = self.remembered_accounts.remember(result["user"].email, password)
            if not stored.success:
                QMessageBox.warning(self.ui, "Cuenta creada", "Se creó la cuenta, pero no se pudieron recordar las credenciales. " + stored.message)
        self.register_successful.emit(result["user"])
