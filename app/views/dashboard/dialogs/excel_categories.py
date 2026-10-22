import os
from PySide6.QtWidgets import QLabel,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon,QAction
from PySide6.QtCore import Signal
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes

class ExcelCategoriesUI:
    create_category_requested=Signal(object)
    cancel_importation_requested=Signal()
    def __init__(self,categorias:list):
        self.categorias=categorias
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
        #*Conectar las acciones
        self.ui.cancelar.clicked.connect(self.cancelar_importacion)
        self.ui.crearCategorias.clicked.connect(self.crear_categorias)
    def llenar_scrollarea(self):
        layout_categorias = self.ui.scrollAreaWidgetContents.layout()
        if self.categorias:
            for categoria in self.categorias:
                lbl = QLabel(categoria)
                layout_categorias.addWidget(lbl)
    def crear_categorias(self):
        layout_categorias = self.ui.scrollAreaWidgetContents.layout()
        elementos_categorias=[]
        for i in range(layout_categorias.count()):
            item = layout_categorias.itemAt(i)
            widget=item.widget()
            if widget is not None:
                elementos_categorias.append(widget.text())
        self.create_category_requested.emit(elementos_categorias)
    def cancelar_importacion(self):
        self.cancel_importation_requested.emit()

