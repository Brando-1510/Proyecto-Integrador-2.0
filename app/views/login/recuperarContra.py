import os
from PySide6.QtWidgets import QWidget,QLineEdit,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon,QAction
from app.generated import resources_rc
from app.utils.validators import ValidadoresDatos as VD, ValidadoresUI as V
from PySide6.QtSvg import QSvgRenderer
renderer = QSvgRenderer(":/icons/person.svg")

class VentanaRecuperarContra(QWidget):
    def __init__(self,user_controller):
        super().__init__()
        self.controller=user_controller
        #* OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        #* CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(directorio_actual,"../../ui/login/recuperarContrasena.ui"))
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

        #* CAMBIANDO LOS INPUTS
        self.configurar_password(self.ui.inputCambiarContra)
        self.configurar_password(self.ui.inputConfirmarContra)

        #* CONECTAR ACCIONES

        #* MOSTRAR VENTANA
        self.show()

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

