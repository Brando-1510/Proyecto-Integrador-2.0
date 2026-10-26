import os
from PySide6.QtCore import Signal,QObject
from PySide6.QtGui import QFontDatabase,QIcon,QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QInputDialog,QMessageBox,QLabel,QDateEdit,QLineEdit
from app.generated import resources_rc
from app.models.users import Users
from PySide6 import QtCore
from app.views.estilosTipografia import estilos_fuentes
from app.utils.validators import ValidadoresDatos,ValidadoresUI
from app.controllers.user_controller import UserController

class Profile(QObject):
    login_requested=Signal
    user_changed=Signal(object)
    def __init__(self,user:Users,controller:UserController, parent=None):
        super().__init__(parent)
        self.user=user
        self.controller=controller
        self.habilitado=False
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../ui/perfil.ui",
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar el archivo UI: {ruta_ui}")
        self.ui.setWindowTitle("Perfil")
        self.datos_originales={
            "nombre":user.username,
            "email":user.email,
            "fecha":user.birth_date
        }
        self._cargar_fuentes()
        self.tab_datos()
        self.tab_operaciones()
        self.autorizado = self.confirmacion()
    def _cargar_fuentes(self):
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if font_id_manrope == -1 or font_id_source == -1:
            return
        manrope = QFontDatabase.applicationFontFamilies(font_id_manrope)
        source = QFontDatabase.applicationFontFamilies(font_id_source)
        if manrope and source:
            self.ui.setStyleSheet(
                self.ui.styleSheet()+ estilos_fuentes(source[0], manrope[0])
            )
    def _habilitar_edicion(self,*widgets):
        if self.habilitado:
            return
        self.habilitado=True
        respuesta=QMessageBox.question(
            self.ui,"Habilitar Edición",
            "Todos los cambios que se confirmen durante el modo de edición seran\nalmacenados permanentemente",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.No:
            self.habilitado=False
            return
        for widget in widgets:
            if isinstance(widget,(QLineEdit,QDateEdit)):
                widget.setEnabled(True)
            else:
                continue
    def confirmacion(self):
        password, ok = QInputDialog.getText(
            self.ui,"Confirma que eres tú","Introduce tu contraseña",QLineEdit.EchoMode.Password
        )
        if not ok or not password.strip():
            return False
        password = password.strip()
        resultado = self.controller.verify_user(self.user.email, password)
        if not resultado.get("success", False):
            QMessageBox.warning(self.ui, "Error", resultado.get("message", "Contraseña incorrecta"))
            return False
        return True
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
    #*Tab de datos personales
    def tab_datos(self):
        self.ui.habilitarEdicion.clicked.connect(
            lambda: self._habilitar_edicion(
                self.ui.nombreUsuario,self.ui.email,self.ui.inputFecha
            )
        )
        #relacionados a la fecha de nacimiento
        hoy = QtCore.QDate.currentDate()
        fecha_maxima = hoy.addYears(-18)
        self.ui.inputFecha.setCalendarPopup(True)
        self.ui.inputFecha.setMaximumDate(fecha_maxima)
        #* Cambios a los input
        self.ui.nombreUsuario.setText(self.datos_originales.get("nombre",""))
        self.ui.email.setText(self.datos_originales.get("email",""))
        self.ui.inputFecha.setDate(self.datos_originales.get("fecha",""))
        #*Conectar las acciones
        self.ui.confirmar.clicked.connect(self.guardar_cambios)
    def _obtener_cambios(self):
        cambios={}
        nombre=self.ui.nombreUsuario.text().strip().title()
        email=self.ui.email.text().strip()
        fecha = self.ui.inputFecha.date().toPython()
        if not ValidadoresDatos.validar_correo(email):
            QMessageBox.critical(self.ui, "Error", "El Correo no cumple con un formato correcto")
            return
        if nombre !=self.datos_originales["nombre"]:
            cambios["nombre"]=nombre
        if email !=self.datos_originales["email"]:
            cambios["email"]=email
        if fecha!=self.datos_originales["fecha"]:
            cambios["fecha"]=fecha
        return cambios
    def guardar_cambios(self):
        cambios = self._obtener_cambios()
        if not cambios:
            QMessageBox.information(self.ui,"Sin cambios","No se han realizado modificaciones.")
            return
        resultado=self.controller.save_changes(
            user_id=self.user.user_id,
            username=cambios.get("nombre"),
            email=cambios.get("email"),
            fecha=cambios.get("fecha")
        )
        if resultado["success"]:
            QMessageBox.information(self.ui,"Cambios guardados",resultado["message"])
            self.user_changed.emit(resultado.get("usuario"))
        else:
            QMessageBox.warning(self.ui,"Error al guardar",resultado["message"])

    #*Tab de operaciones criticas
    def tab_operaciones(self):
        self.ui.habilitarContrasena.clicked.connect(
            lambda: self._habilitar_edicion(
                self.ui.contra,self.ui.confirmarContra
            )
        )
        self.configurar_password(self.ui.contra)
        self.configurar_password(self.ui.confirmarContra)
        #*Acciones
        self.ui.habilitarContrasena.clicked.connect(
            lambda: self._habilitar_edicion(self.ui.contra,self.ui.confirmarContra)
        )
        self.ui.cambiarContrasena.clicked.connect(self.cambiarContrasena)

    def cambiarContrasena(self):
        if not ValidadoresUI.tienen_contenido(
            self.ui.contra.text().strip(),
            self.ui.confirmarContra.text().strip()
        ):
            QMessageBox.critical(self.ui,"Error","Debe llenar el campo necesario")
            return
        password = self.ui.contra.text().strip()
        password_confirmar = self.ui.confirmarContra.text().strip()
        if not ValidadoresDatos.evaluar_contrasena(self.ui, password):
            return
        if not ValidadoresDatos.comparar_contraseñas(self.ui,password,password_confirmar):
            return
        result = self.controller.change_password(self.user.user_id,password)
        if result["success"]:
            QMessageBox.information(self.ui,"Éxito",result["message"])
            return
        else:
            QMessageBox.warning(self.ui,"Error",result["message"])

    def eliminar_cuenta(self):
        respuesta=QMessageBox.question(
            self.ui,"Eliminar Cuenta",
            "¿Estas seguro que quieres eliminar la cuenta?\nEsta acción no puede revertirse",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.No:
            return