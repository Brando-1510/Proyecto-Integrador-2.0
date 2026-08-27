import os
from PySide6.QtWidgets import QApplication, QWidget,QLineEdit,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtCore
from PySide6.QtCore import QRect
from PySide6.QtGui import QIcon,QAction
from app.generated import resources_rc
from app.utils.validators import ValidadoresDatos as VD, ValidadoresUI as V
from PySide6.QtSvg import QSvgRenderer
renderer = QSvgRenderer(":/icons/person.svg")

class VentanaLogin(QWidget):
    def __init__(self,user_controller):
        super().__init__()
        self.controller=user_controller
        #* OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        #* CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(directorio_actual,"../../ui/login.ui"))
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
                BOTONES
                ========================= */
                QPushButton {{
                    font-family: "{source_family}";
                }}
                /* =========================
                TÍTULOS DE SECCIÓN
                ========================= */
                QLabel[texto="InputTexto"],QPushButton[boton="BotonTexto"] {{
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
            """
            self.ui.setStyleSheet(estilos_actuales + estilos_fuentes)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")

        #* MODIFICAR EL QSTACKEDWIDGET
        self.centrar_stacked_widget()
        self.ui.stackRecuperacion.setCurrentIndex(0)
        self.ocultarStackedWidget()

        #* CAMBIANDO LOS INPUTS
        self.configurar_password(self.ui.txtContrasena)
        self.configurar_password(self.ui.txtNuevaContrasena)
        self.configurar_password(self.ui.txtConfirmarContrasena)

        #* CONECTAR ACCIONES
        #cuando el usuario hace click en "Olvidaste la contraseña"
        self.ui.btnRecuperarContrasena.clicked.connect(self.mostrarStackedWidget)
        self.ui.btnRegresarLogin.clicked.connect(self.ocultarStackedWidget)
        self.ui.btnLogin.clicked.connect(self.login)

        #* MOSTRAR VENTANA
        self.showMaximized()

    def centrar_stacked_widget(self):
        # Obtener el ancho y alto de la ventana principal
        ancho_ventana = self.width()
        alto_ventana = self.height()
        # Obtener el ancho y alto actual del QStackedWidget (tu cuadro blanco)
        ancho_stack = self.ui.stackRecuperacion.width()
        alto_stack = self.ui.stackRecuperacion.height()
        # Calcular las coordenadas X e Y para centrarlo exactamente
        nueva_x = (ancho_ventana - ancho_stack) // 2
        nueva_y = (alto_ventana - alto_stack) // 2
        # Aplicar la nueva geometría centrada
        self.ui.stackRecuperacion.setGeometry(QRect(nueva_x, nueva_y, ancho_stack, alto_stack))
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.centrar_stacked_widget()
    def mostrarStackedWidget(self):
        self.ui.stackRecuperacion.raise_()
        self.ui.stackRecuperacion.show()
    def ocultarStackedWidget(self):
        self.ui.stackRecuperacion.hide()
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
        if not V.tienen_contenido([self.ui.txtContrasena,self.ui.txtCorreo]):
            QMessageBox.critical(self, "Error", "Debe llenar todos los campos para Crear la Cuenta")
            return
        if not VD.validar_correo(self.ui.txtCorreo.text()):
            QMessageBox.critical(self, "Error", "El Correo no cumple con un formato correcto")
            return
    def login(self):
        self.verificar()
        email=self.ui.txtCorreo.text()
        password=self.ui.txtContrasena.text()
        result=self.controller.login(email,password)
        if result["success"]:
            QMessageBox.information(
                self,
                "Éxito",
                result["message"]
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                result["message"]
            )
