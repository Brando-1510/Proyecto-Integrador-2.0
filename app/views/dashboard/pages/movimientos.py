import os
import sys
from app.views.dashboard.table_models.movements_table_model import MovementsTableModel
from app.views.dashboard.table_models.sales_table_model import SalesTableModel
from PySide6.QtWidgets import QWidget,QHeaderView,QVBoxLayout
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal

class Movimientos(QWidget):
    def __init__(self, userBusiness):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.categories=userBusiness.business.categories
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/movimientos.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.tabWidget.setTabBarAutoHide(False)
        self.ui.tabWidget.tabBar().setExpanding(True)
        self.ui.tabWidget.setDocumentMode(True)
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
        #*Cambios en la ui
        self.ui.lblPersonalizar.hide()
        self.ui.contenedorFechas.hide()
        self.ui.lblPersonalizarV.hide()
        self.ui.contenedorFechasV.hide()
        #llenar el combobox
        self.ui.categoriasVentas.addItem("Todas las categorías", None)
        for category in self.categories:
            self.ui.categoriasVentas.addItem(
                category.name,category.category_id
            )
        self.ui.tipoMov.addItem("Todos", None)
        self.ui.tipoMov.addItem("Ingreso", "Ingreso")
        self.ui.tipoMov.addItem("Gasto", "Gasto")
        #tablas
        self.ui.ventasTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.movimientosTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #TabWidget
        self.ui.tabWidget.tabBar().setExpanding(True)
        #Tablas
        self.movements_model = MovementsTableModel()
        self.sales_model=SalesTableModel()
        self.ui.movimientosTable.setModel(self.movements_model)
        self.ui.ventasTable.setModel(self.sales_model)
        #*Conectar las acciones
        # Conectar el cambio de selección en los QComboBox para activar o desactivar la visibilidad
        self.ui.periodoMov.currentTextChanged.connect(self.mostrar_dateEdits)
        self.ui.periodoVentas.currentTextChanged.connect(self.mostrar_dateEdits)
    def mostrar_dateEdits(self):
        # Pestaña Movimientos
        es_personalizado_mov = (self.ui.periodoMov.currentText() == "Personalizado")
        self.ui.lblPersonalizar.setVisible(es_personalizado_mov)
        self.ui.contenedorFechas.setVisible(es_personalizado_mov)
        # Pestaña Ventas
        es_personalizado_ventas = (self.ui.periodoVentas.currentText() == "Personalizado")
        self.ui.lblPersonalizarV.setVisible(es_personalizado_ventas)
        self.ui.contenedorFechasV.setVisible(es_personalizado_ventas)

    def obtener_datos(self):
        tab_actual = self.ui.tuTabWidget.currentIndex()
        datos = {}
        datos["businness_id"]=self.business.business_id
        if tab_actual == 0:
            periodo = self.ui.periodoMov.currentText()
            datos["periodo"] = periodo
            datos["tipo_movimiento"] = (self.ui.tipoMov.currentData())
            datos["descripcion"] = self.ui.buscar.toPlainText().strip() or None
            if periodo == "Personalizado":
                datos["rango_inicio"] = (self.ui.rangoInicio.date().toPyDate())
                datos["rango_final"] = (self.ui.rangoFinal.date().toPyDate())
        else:
            periodo = self.ui.periodoVentas.currentText()
            datos["periodo"] = periodo
            datos["categoria_id"] = (self.ui.categoriasVentas.currentData())
            if periodo == "Personalizado":
                datos["rango_inicio"] = (self.ui.rangoInicioV.date().toPyDate())
                datos["rango_final"] = (self.ui.rangoFinalV.date().toPyDate())
        return datos

