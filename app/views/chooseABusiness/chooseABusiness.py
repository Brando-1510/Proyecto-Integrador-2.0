import os
from PySide6.QtWidgets import (QWidget,QGridLayout,QMessageBox)
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.views.chooseABusiness.tarjetaNegocio import TarjetaNegocio
from PySide6.QtCore import Qt,Signal


class VentanaChooseBusiness(QWidget):
    dashboard_requested = Signal(object, object)
    def __init__(self, user, userBusiness_controller):
        super().__init__()
        self.user = user
        self.userBusiness_seleccionado = None
        self.controller = userBusiness_controller
        self.tarjeta_seleccionada = None
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../ui/chooseBusiness.ui"
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        #*CARGAR TIPOGRAFÍAS
        # Manrope
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        # Source Sans 3
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        # VERIFICAR TIPOGRAFÍAS
        if font_id_manrope == -1:
            print("Advertencia: No se pudo cargar Manrope.")
        if font_id_source == -1:
            print("Advertencia: No se pudo cargar Source Sans 3.")

        # OBTENER FAMILIAS REALES
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
        # APLICAR TIPOGRAFÍAS
        if manrope_family and source_family:
            estilos_actuales = self.ui.styleSheet()
            estilos_tipografias = estilos_fuentes(
                source_family,
                manrope_family
            )
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)

        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")
        self.ui.stackedWidget.setCurrentIndex(0)
        #*CARGAR NEGOCIOS
        self.cargar_negocios()
        self.ui.btnEntrar.clicked.connect(self.entrar_al_negocio)
        #*MOSTRAR VENTANA
        self.showMaximized()
    def cambiar_lbl(self,texto):
        self.ui.lblBienvenidaUser.setText(f"Bienvenido, {texto}")
    def cambiar_index(self):
        self.ui.stackedWidget.setCurrentIndex(1)
    def seleccionar_negocio(self, tarjeta):
        if self.tarjeta_seleccionada is not None:
            self.tarjeta_seleccionada.establecer_seleccionada(False)
        # Guardar la nueva tarjeta
        self.tarjeta_seleccionada = tarjeta
        # Mantener visualmente seleccionada
        self.tarjeta_seleccionada.establecer_seleccionada(True)
        # Guardar el UserBusiness correspondiente
        self.userBusiness_seleccionado = tarjeta.negocio
    def entrar_al_negocio(self):
        if not self.userBusiness_seleccionado:
            return
        self.dashboard_requested.emit(self.user,self.userBusiness_seleccionado)
    def cargar_negocios(self):
        resultado = self.controller.load_businesses(self.user.user_id)
        if not resultado["success"]:
            QMessageBox.critical(self,"Error",resultado["message"])
            return
        userBusinesses = resultado["userBusinesses"]
        self.cambiar_lbl(self.user.username)
        if not userBusinesses:
            self.cambiar_index()
            return
        # Obtener el QGridLayout del QWidget contenedor
        layout = self.ui.gridLayoutNegocios.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(20)
        for indice, negocio in enumerate(userBusinesses):
            tarjeta = TarjetaNegocio(negocio)
            tarjeta.seleccionada.connect(self.seleccionar_negocio)
            fila = indice // 2
            columna = indice % 2
            layout.addWidget(tarjeta,fila,columna)