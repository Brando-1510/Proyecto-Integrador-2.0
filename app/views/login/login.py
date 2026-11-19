"""Inicio de sesión con sugerencias locales y credenciales del sistema operativo."""
import os
from PySide6.QtCore import Qt, Signal, QStringListModel, QSignalBlocker
from PySide6.QtWidgets import QWidget, QLineEdit, QMessageBox, QVBoxLayout, QCompleter
from PySide6.QtGui import QFontDatabase, QIcon, QAction
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.utils.validators import ValidadoresDatos as VD, ValidadoresUI as V
from app.views.estilosTipografia import estilos_fuentes
from app.core.screen_utils import calcular_tamano_pantalla


class VentanaLogin(QWidget):
    crear_cuenta_requested = Signal()
    recuperar_contrasena_requested = Signal()
    login_successful = Signal(object)

    def __init__(self, user_controller, remembered_accounts=None):
        super().__init__()
        self.controller = user_controller
        self.remembered_accounts = remembered_accounts
        self._selected_email = None
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../ui/login/loginU.ui"))
        self.ui = QUiLoader().load(path, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar la interfaz de Login: {path}")
        width, height = calcular_tamano_pantalla(0.8, 0.8)
        self.resize(width, height)
        self.setMinimumSize(900, 600)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self._load_fonts()
        self._setup_password(self.ui.txtContrasena)
        self._setup_remembered_accounts()
        self.ui.btnLogin.clicked.connect(self.login)
        self.ui.txtCorreo.returnPressed.connect(self.login)
        self.ui.txtContrasena.returnPressed.connect(self.login)
        self.ui.btnCrearCuenta.clicked.connect(self.crear_cuenta_requested.emit)
        self.ui.btnRecuperarContrasena.clicked.connect(self.recuperar_contrasena_requested.emit)
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

    def _setup_remembered_accounts(self):
        self.ui.checkBoxRecordar.setText("Recordar mi cuenta en este dispositivo")
        self.ui.checkBoxRecordar.setChecked(False)
        self._model = QStringListModel(self)
        self._completer = QCompleter(self._model, self.ui.txtCorreo)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setMaxVisibleItems(6)
        self.ui.txtCorreo.setCompleter(self._completer)
        self._completer.activated[str].connect(self._select_account)
        self.ui.txtCorreo.textEdited.connect(self._on_email_edited)
        self.ui.checkBoxRecordar.toggled.connect(self._on_remember_toggled)
        self._forget_action = QAction(QIcon(":/icons/closeFile.svg"), "Olvidar esta cuenta", self.ui.txtCorreo)
        self._forget_action.setToolTip("Olvidar esta cuenta de este dispositivo")
        self.ui.txtCorreo.addAction(self._forget_action, QLineEdit.ActionPosition.TrailingPosition)
        self._forget_action.triggered.connect(self._forget_selected)
        self.refresh_remembered_accounts()

    def refresh_remembered_accounts(self):
        accounts = self.remembered_accounts.list_accounts() if self.remembered_accounts else []
        self._model.setStringList(accounts)
        self._forget_action.setVisible(bool(self._selected_email and self._selected_email in accounts))

    def _on_email_edited(self, value):
        # Nunca dejar una contraseña recuperada asociada a otro correo.
        if self._selected_email and value.strip().casefold() != self._selected_email:
            self.ui.txtContrasena.clear()
            self._selected_email = None
            with QSignalBlocker(self.ui.checkBoxRecordar):
                self.ui.checkBoxRecordar.setChecked(False)
            self._forget_action.setVisible(False)

    def _select_account(self, email):
        self._selected_email = email.strip().casefold()
        self.ui.txtCorreo.setText(email)
        self.ui.txtContrasena.clear()
        if self.remembered_accounts:
            result = self.remembered_accounts.lookup(email)
            if result.success and result.secret is not None:
                self.ui.txtContrasena.setText(result.secret)
            with QSignalBlocker(self.ui.checkBoxRecordar):
                self.ui.checkBoxRecordar.setChecked(self.remembered_accounts.is_remembered(email))
            self.refresh_remembered_accounts()

    def _forget_selected(self):
        if not self.remembered_accounts or not self._selected_email:
            return
        if QMessageBox.question(self.ui, "Olvidar cuenta",
             "¿Eliminar esta cuenta y su contraseña guardada de este dispositivo?",
             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self._forget_account()

    def _forget_account(self):
        result = self.remembered_accounts.forget(self._selected_email)
        if not result.success:
            QMessageBox.warning(self.ui, "No se pudo olvidar la cuenta", result.message)
            with QSignalBlocker(self.ui.checkBoxRecordar):
                self.ui.checkBoxRecordar.setChecked(True)
            return
        self.ui.txtContrasena.clear()
        self._selected_email = None
        with QSignalBlocker(self.ui.checkBoxRecordar):
            self.ui.checkBoxRecordar.setChecked(False)
        self.refresh_remembered_accounts()

    def _on_remember_toggled(self, checked):
        # La baja requiere acción explícita. No afecta las otras cuentas recordadas.
        if checked or not self._selected_email or not self.remembered_accounts:
            return
        if not self.remembered_accounts.is_remembered(self._selected_email):
            return
        if QMessageBox.question(self.ui, "Dejar de recordar",
             "¿Dejar de recordar la cuenta seleccionada en este dispositivo?",
             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self._forget_account()
        else:
            with QSignalBlocker(self.ui.checkBoxRecordar):
                self.ui.checkBoxRecordar.setChecked(True)

    def verificar(self):
        if not V.tienen_contenido(self.ui.txtContrasena, self.ui.txtCorreo):
            QMessageBox.warning(self.ui, "Campos obligatorios", "Debes introducir correo y contraseña.")
            return False
        if not VD.validar_correo(self.ui.txtCorreo.text()):
            QMessageBox.warning(self.ui, "Correo inválido", "Introduce un correo electrónico válido.")
            return False
        return True

    def login(self):
        if not self.verificar():
            return
        email = self.ui.txtCorreo.text().strip().casefold()
        password = self.ui.txtContrasena.text()  # NO usar strip() sobre contraseñas.
        self.ui.btnLogin.setEnabled(False)
        try:
            result = self.controller.login(email, password)
        finally:
            self.ui.btnLogin.setEnabled(True)
        if not result.get("success"):
            QMessageBox.warning(self.ui, "Credenciales no válidas", result.get("message", "No se pudo iniciar sesión."))
            return
        if self.ui.checkBoxRecordar.isChecked() and self.remembered_accounts:
            stored = self.remembered_accounts.remember(result["user"].email, password)
            if not stored.success:
                QMessageBox.warning(self.ui, "Recordatorio no disponible", stored.message + " Puedes iniciar sesión normalmente.")
            self.refresh_remembered_accounts()
        self.login_successful.emit(result["user"])

    def limpiar_campos(self):
        self._selected_email = None
        self.ui.txtCorreo.clear()
        self.ui.txtContrasena.clear()
        with QSignalBlocker(self.ui.checkBoxRecordar):
            self.ui.checkBoxRecordar.setChecked(False)
        self.refresh_remembered_accounts()
