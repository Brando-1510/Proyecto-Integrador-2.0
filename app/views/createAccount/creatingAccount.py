#Importaciones
import os
#Importaciones relacionadas a la UI
from PySide6.QtWidgets import QApplication, QWidget,QLineEdit,QMessageBox
from PySide6.QtGui import QFontDatabase,QAction,QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtCore
from app.generated import resources_rc
#Importaciones de la clase Validators (validan cosas)
from app.utils.validators import ValidadoresUI as V, ValidadoresDatos as VD
#Importaciones para el hash de contraseñas
from app.core.security.password import HashPassword as hp

from PySide6.QtSvg import QSvgRenderer
renderer = QSvgRenderer(":/icons/person.svg")

class VentanaCrearCuenta(QWidget):
    def __init__(self):
        super().__init__()
        #* OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        #* CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(directorio_actual,"../../ui/creatingAccount.ui"))
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
            estilos_fuentes = f"""
                /* =========================
                FUENTE GENERAL
                ========================= */
                QWidget {{
                    font-family: "{source_family}";
                }}
                /* =========================
                TÍTULOS PRINCIPALES
                ========================= */
                QLabel[texto="Principal"], QLabel[texto="TituloPrincipal"],
                QLabel[texto="Destacado"], {{
                    font-family: "{manrope_family}";
                    font-weight: bold;
                }}
                /* =========================
                TÍTULOS DE SECCIÓN
                ========================= */
                QLabel[texto="InputTexto"] {{
                    font-family: "{manrope_family}";
                    font-weight: bold;
                }}
                /* =========================
                TÍTULOS SECUNDARIOS
                ========================= */
                QLabel[styleClass="tituloSecundario"] {{
                    font-family: "{source_family}";
                }}
                /* =========================
                TEXTO DE LOS PASOS
                ========================= */
                QLabel[styleClass="textoPaso"] {{
                    font-family: "{source_family}";
                }}
                /* =========================
                LABELS GENERALES
                ========================= */
                QLabel {{
                    font-family: "{source_family}";
                }}
                /* =========================
                INPUTS
                ========================= */
                QLineEdit,
                QDateEdit,
                QComboBox {{
                    font-family: "{source_family}";
                    font-size: 14px;
                }}
                /* =========================
                BOTONES
                ========================= */
                QPushButton {{
                    font-family: "{source_family}";
                }}
            """
            self.ui.setStyleSheet(estilos_actuales + estilos_fuentes)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")

        #* CONECTAR LOS BOTONES A LAS ACCIONES
        #acciones relacionadas a moverse entre las pantallas
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.continuarUno.clicked.connect(lambda: self.avanzar(
            1,self.ui.inputNombre, self.ui.inputCorreo,self.ui.inputContrasena, self.ui.inputContrasenaConfirmar
            ))
        self.ui.volverDos.clicked.connect(lambda: self.cambiar_pagina(0))
        self.ui.continuarDos.clicked.connect(lambda: self.avanzar(
        2,self.ui.inputNegocio,self.ui.tipoNegocio
        ))
        self.ui.volverTres.clicked.connect(lambda: self.cambiar_pagina(1))
        #accion del boton guardar
        self.ui.comenzar.clicked.connect(self.guardar)

        #* CAMBIANDO LOS INPUTS
        #contraseña
        self.configurar_password(self.ui.inputContrasena)
        self.configurar_password(self.ui.inputContrasenaConfirmar)
        #fecha
        self.ui.inputFecha.setDate(QtCore.QDate.currentDate())

        #* MOSTRAR VENTANA
        self.showMaximized()
    def cambiar_pagina(self, indice):
        self.ui.stackedWidget.setCurrentIndex(indice)
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
    def avanzar(self, index, *args):
        # Pasamos los elementos desempaquetados directamente
        if V.tienen_contenido(*args):
            self.cambiar_pagina(index)
        else:
            QMessageBox.critical(self, "Error", "Debe llenar todos los campos para avanzar")
    def guardar(self):
        if not VD.validar_correo(self.ui.inputCorreo.text()):
            QMessageBox.critical(self, "Error", "El Correo no cumple con un formato correcto")
            return
        password = self.ui.inputContrasena.text()
        password_confirmar = self.ui.inputContrasenaConfirmar.text()
        if password != password_confirmar:
            QMessageBox.critical(self,"Error","Las Contraseñas deben de coincidir")
            return
        password_hash = hp.hash_password(password)

