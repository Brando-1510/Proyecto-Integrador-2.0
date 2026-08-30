import os
from PySide6.QtWidgets import QWidget,QLineEdit,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtCore
from PySide6.QtGui import QIcon,QAction
from PySide6.QtCore import Signal
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
#Importaciones de la clase Validators (validan cosas)
from app.utils.validators import ValidadoresUI as V, ValidadoresDatos as VD
#Importaciones para el hash de contraseñas
from app.core.security.password import HashPassword as hp

from PySide6.QtSvg import QSvgRenderer
renderer = QSvgRenderer(":/icons/person.svg")

class VentanaCrearCuenta(QWidget):
    volver_login_requested = Signal()
    register_successful = Signal()
    def __init__(self,user_controller):
        super().__init__()
        self.controller=user_controller
        #* OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        #* CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(directorio_actual,"../../ui/createAccount.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui,self)

        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return

        #* CARGAR TIPOGRAFÍAS
        # Manrope
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        # Source Sans 3
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")

        #* VERIFICAR TIPOGRAFÍAS

        if font_id_manrope == -1:
            print("Advertencia: No se pudo cargar Manrope.")

        if font_id_source == -1:
            print("Advertencia: No se pudo cargar Source Sans 3.")

        #* OBTENER FAMILIAS REALES
        manrope_family = None
        source_family = None
        if font_id_manrope != -1:
            familias = QFontDatabase.applicationFontFamilies(font_id_manrope)
            if familias:
                manrope_family = familias[0]
        if font_id_source != -1:
            familias = QFontDatabase.applicationFontFamilies(font_id_source)
            if familias:
                source_family = familias[0]
        # Mostrar familias detectadas
        print("Manrope:", manrope_family)
        print("Source Sans 3:", source_family)

        #* APLICAR TIPOGRAFÍAS
        if manrope_family and source_family:
            estilos_actuales = self.ui.styleSheet()
            estilos_tipografias = estilos_fuentes(source_family,manrope_family)
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")

        #* CAMBIANDO LOS INPUTS
        #relacionado a las contraseñas
        self.configurar_password(self.ui.inputContrasena)
        self.configurar_password(self.ui.inputContrasenaConfirmar)
        #relacionados a la fecha de nacimiento
        hoy = QtCore.QDate.currentDate()
        fecha_maxima = hoy.addYears(-18)
        self.ui.inputFecha.setCalendarPopup(True)
        self.ui.inputFecha.setMaximumDate(fecha_maxima)
        self.ui.inputFecha.setDate(fecha_maxima)

        #*CONECTAR LAS ACCIONES
        self.ui.BtnCrearCuenta.clicked.connect(self.guardar)
        self.ui.BtnLogin.clicked.connect(self.volver_login_requested.emit)

        #* MOSTRAR VENTANA
        self.showMaximized()

    def configurar_password(self, input_password):
        input_password.setEchoMode(QLineEdit.EchoMode.Password)
        accion_ojo = QAction(input_password)
        accion_ojo.setIcon(QIcon(":/icons/openEye.svg"))
        accion_ojo.setCheckable(True)
        input_password.addAction(accion_ojo,
            QLineEdit.ActionPosition.TrailingPosition)
        def cambiar_visibilidad(activado):
            if activado:
                input_password.setEchoMode(QLineEdit.EchoMode.Normal)
                accion_ojo.setIcon(QIcon(":/icons/closeEye.svg"))
            else:
                input_password.setEchoMode(QLineEdit.EchoMode.Password)
                accion_ojo.setIcon(QIcon(":/icons/openEye.svg"))
        accion_ojo.toggled.connect(cambiar_visibilidad)
    def verificar(self):
        pass
    def guardar(self):
        if not V.tienen_contenido(
            self.ui.inputNombre,self.ui.inputCorreo,
            self.ui.inputContrasena,self.ui.inputContrasenaConfirmar
        ):
            QMessageBox.critical(self, "Error", "Debe llenar todos los campos para Crear la Cuenta")
            return
        if not VD.validar_correo(self.ui.inputCorreo.text()):
            QMessageBox.critical(self, "Error", "El Correo no cumple con un formato correcto")
            return
        password = self.ui.inputContrasena.text().strip()
        password_confirmar = self.ui.inputContrasenaConfirmar.text().strip()
        VD.evaluar_contrasena(self,password)
        if not VD.comparar_contraseñas(self,password,password_confirmar):
            return
        name=self.ui.inputNombre.text().strip()
        email=self.ui.inputCorreo.text().strip()
        date = self.ui.inputFecha.date().toPython()
        password_hash=hp.hash_password(password)
        result=self.controller.register_user(
            name,email,date,password_hash
        )
        if result["success"]:
            QMessageBox.information(
                self,
                "Éxito",
                result["message"]
            )
            self.register_successful.emit()
        else:
            QMessageBox.warning(
                self,
                "Error",
                result["message"]
            )
