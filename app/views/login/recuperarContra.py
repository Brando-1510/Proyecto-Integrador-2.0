import os
from PySide6.QtWidgets import QWidget,QLineEdit,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon,QAction
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.utils.validators import ValidadoresDatos as VD, ValidadoresUI as V
from app.utils.recoveryCode import EnviarCorreoThread
from app.core.security.password import HashPassword as hp
from PySide6.QtSvg import QSvgRenderer
renderer = QSvgRenderer(":/icons/person.svg")

class VentanaRecuperarContra(QWidget):
    def __init__(self,recovery_controller):
        super().__init__()
        self.controller=recovery_controller
        self.email_thread=None
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
            estilos_tipografias=estilos_fuentes(source_family,manrope_family)
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")

        #* CAMBIANDO LOS INPUTS
        self.configurar_password(self.ui.inputCambiarContra)
        self.configurar_password(self.ui.inputConfirmarContra)

        #* CONECTAR ACCIONES
        self.ui.btnEnviar.clicked.connect(self.enviarCodigo)
        self.ui.btnConfirmar.clicked.connect(self.cambiarContrasena)
        self.ui.btnConfirmarCod.clicked.connect(self.verificar_codigo)
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
    def enviarCodigo(self):
        if not V.tienen_contenido(self.ui.inputCoreo):
            QMessageBox.critical(
                self,
                "Error",
                "Debe llenar el campo solicitado para enviar el código"
            )
            return
        self.ui.btnEnviar.setEnabled(False)
        self.email = self.ui.inputCoreo.text().strip()
        self.respuesta = self.controller.request_recovery(self.email)
        if not self.respuesta["success"]:
            self.ui.btnEnviar.setEnabled(True)
            QMessageBox.warning(
                self,
                "Error",
                self.respuesta["message"]
            )
            return
        datos_codigo = self.respuesta["datos_codigo"]
        self.user_id = datos_codigo["user_id"]
        self.enviarCorreo()

    def enviarCorreo(self):
        datos_codigo = self.respuesta["datos_codigo"]
        self.email_thread = EnviarCorreoThread(datos_codigo["email"],datos_codigo["codigo"])
        self.email_thread.exito_signal.connect(self.correoEnviado)
        self.email_thread.error_signal.connect(self.errorCorreo)
        self.email_thread.start()

    def correoEnviado(self):
        QMessageBox.information(self,"Éxito","El código fue enviado correctamente.")
        self.ui.btnEnviar.setEnabled(True)

    def errorCorreo(self, mensaje):
        QMessageBox.warning(self,"Error",mensaje)
        self.ui.btnEnviar.setEnabled(True)


    def verificar_codigo(self):
        if not V.tienen_contenido(self.ui.inputCodigo):
            QMessageBox.critical(self,"Error","Debe llenar el campo necesario")
            return
        codigo = self.ui.inputCodigo.text().strip()
        result = self.controller.verify_recovery_code(self.user_id,codigo)
        if result["success"]:
            self.recovery = result["recovery"]
            QMessageBox.information(self,"Éxito",result["message"])
            self.ui.stacked.setCurrentIndex(1)
        else:
            QMessageBox.warning(self,"Error",result["message"])


    def cambiarContrasena(self):
        if not V.tienen_contenido(
            self.ui.inputCambiarContra.text().strip(),
            self.ui.inputConfirmarContra.text().strip()
        ):
            QMessageBox.critical(self,"Error","Debe llenar el campo necesario")
            return
        password = self.ui.inputCambiarContra.text().strip()
        password_confirmar = self.ui.inputConfirmarContra.text().strip()
        VD.evaluar_contrasena(self, password)
        if not VD.comparar_contraseñas(self,password,password_confirmar):
            return
        result = self.controller.change_password(self.recovery,password)
        if result["success"]:
            QMessageBox.information(self,"Éxito",result["message"])
            self.close()
        else:
            QMessageBox.warning(self,"Error",result["message"])