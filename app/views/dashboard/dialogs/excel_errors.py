import os
from PySide6.QtWidgets import QLabel,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon,QAction
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes

class ExcelErrorsUI:
    def __init__(self,errores:dict):
        self.errores=errores
        self.erroresVentas=errores.get("ventas",[])
        self.erroresMovimientos=errores.get("movimientos",[])
        #* OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        #* CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../ui//dashboard/qdialog/ExcelErrors.ui"
        ))
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
        #* APLICAR TIPOGRAFÍAS
        if manrope_family and source_family:
            estilos_actuales = self.ui.styleSheet()
            estilos_tipografias=estilos_fuentes(source_family,manrope_family)
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)
    def llenar_scrollarea(self):
        layout_ventas = self.ui.scrollAreaWidgetContents.layout()
        layout_movimientos= self.ui.scrollAreaWidgetContents2.layout()
        if self.erroresVentas:
            self.ui.lblVentas.hide()
            for error in self.erroresVentas:
                lbl = QLabel(error)
                layout_ventas.addWidget(lbl)
        if self.erroresMovimientos:
            self.ui.lblMovimientos.hide()
            for error in self.erroresVentas:
                lbl = QLabel(error)
                layout_movimientos.addWidget(lbl)
