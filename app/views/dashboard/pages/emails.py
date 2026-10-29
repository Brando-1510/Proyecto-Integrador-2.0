import os
from PySide6.QtWidgets import QWidget,QVBoxLayout,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal,QDate
from app.controllers.emails_controller import EmailController
from app.utils.validators import ValidadoresUI
from app.models.users import Users

class EmailSender(QWidget):
    def __init__(self, userBusiness,controller:EmailController):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.controller=controller
        #*obtener directorio actual
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*cargar archivo .ui
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/mensajes.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        #*Cambios en la interfaz
        self._cargar_fuentes()
        self.actualizar_interfaz()
        self.ui.enviar.clicked.connect(self.enviar_email)
        #comboBox
    def _cargar_fuentes(self):
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if font_id_manrope == -1 or font_id_source == -1:
            return
    def actualizar_interfaz(self,user: Users | None=None):
        if user is not None:
            self.user=user
        self.ui.destinatario.clear()
        resultado = self.controller.get_data(self.business.business_id, self.user.user_id)
        if resultado["success"]:
            empleados = resultado["resultado"]
            for username, rol, email in empleados:
                self.ui.destinatario.addItem(
                    f"{username} • {rol.value}", userData=email
                )
    def enviar_email(self):
        asunto = self.ui.asunto.text().strip()
        cuerpo = self.ui.cuerpo.toPlainText().strip()
        destinatario = self.ui.destinatario.currentData()
        if not ValidadoresUI.tienen_contenido(cuerpo, asunto):
            QMessageBox.critical(self.ui,"Error","Debe completar el asunto y el cuerpo del correo.")
            return
        datos = {
            "remitente": self.user.username,
            "remitente_correo": self.user.email,
            "destinatario": destinatario,
            "asunto": asunto,
            "cuerpo": cuerpo,
        }
        self.ui.enviar.setDisabled(True)
        self.controller.enviar_email(
            datos,on_success=self.email_enviado,on_error=self.error_email,
        )
    def email_enviado(self):
        self.ui.enviar.setDisabled(False)
        QMessageBox.information(self.ui,"Éxito","Correo enviado exitosamente.")
    def error_email(self, mensaje: str):
        self.ui.enviar.setDisabled(False)
        QMessageBox.warning(self.ui,"Error",mensaje)