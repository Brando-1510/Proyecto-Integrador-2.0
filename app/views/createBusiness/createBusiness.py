import os
from PySide6.QtWidgets import (QWidget,QGridLayout,QMessageBox)
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6 import QtCore
from PySide6.QtCore import Qt,Signal
from app.utils.validators import ValidadoresUI as V, ValidadoresDatos as VD
from app.core.screen_utils import calcular_tamano_pantalla
from PySide6.QtWidgets import QVBoxLayout

class VentanaCreateBusiness(QWidget):
    dashboard_requested = Signal(object)
    def __init__(self, user,business_controller):
        super().__init__()
        self.user = user
        self.controller=business_controller
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../ui/creatingBusiness.ui"
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        ancho, alto = calcular_tamano_pantalla(0.8, 0.8)
        self.resize(ancho, alto)
        self.setMinimumSize(900, 570)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.tipoNegocio.setCurrentIndex(7)
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
        self.showMaximized()
        #*Cambiando los inputs
        hoy = QtCore.QDate.currentDate()
        self.ui.inputFecha.setCalendarPopup(True)
        self.ui.inputFecha.setMaximumDate(hoy)
        self.ui.inputFecha.setDate(hoy)
        #*Conectando las acciones
        self.ui.continuarUno.clicked.connect(lambda: self.avanzar(
            1,self.ui.inputNegocio, self.ui.descripcionInput
            ))
        self.ui.volver.clicked.connect(lambda: self.cambiar_pagina(0))
        self.ui.terminar.clicked.connect(self.guardar_negocio)
    def cambiar_pagina(self, indice):
        self.ui.stackedWidget.setCurrentIndex(indice)
    def avanzar(self, index, *args):
        # Pasamos los elementos desempaquetados directamente
        if V.tienen_contenido(*args):
            self.cambiar_pagina(index)
        else:
            QMessageBox.critical(self, "Error", "Debe llenar todos los campos para avanzar")
    def validar_campos(self):
        if not V.tienen_contenido(
            self.ui.inputNegocio,self.ui.descripcionInput
        ):
            QMessageBox.critical(self, "Error", "Debe llenar todos los campos para Crear el Negocio")
            return None
    def guardar_negocio(self):
        user_id=self.user.user_id
        business_name=self.ui.inputNegocio.text().strip()
        type_of_business=self.ui.tipoNegocio.currentText()
        start_of_operations=self.ui.inputFecha.date().toPython()
        description=self.ui.descripcionInput.toPlainText().strip()
        result=self.controller.create_business(
            user_id,business_name,type_of_business,start_of_operations,description
        )
        if result["success"]:
            QMessageBox.information(
                self,
                "Éxito",
                result["message"]
            )
            self.dashboard_requested.emit(result["userBusiness"])
        else:
            QMessageBox.warning(
                self,
                "Error",
                result["message"]
            )