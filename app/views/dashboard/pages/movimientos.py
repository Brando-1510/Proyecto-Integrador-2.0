import os
import sys
from app.views.dashboard.table_models.movements_model import MovementsTableModel
from app.views.dashboard.table_models.sales_model import SalesTableModel
from app.views.dashboard.table_models.imports_model import ImportsTableModel
from PySide6.QtWidgets import QWidget,QHeaderView,QVBoxLayout,QMessageBox,QDateEdit
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal,QDate

class Movimientos(QWidget):
    def __init__(self, userBusiness,controller):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.categories=userBusiness.business.categories
        self.controller=controller
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
        self.ui.lblPersonalizarImp.hide()
        self.ui.contenedorFechasImp.hide()
        #llenar el combobox
        self.ui.categoriasVentas.addItem("Todas las categorías", None)
        for category in self.categories:
            self.ui.categoriasVentas.addItem(
                category.name,category.category_id
            )
        self.ui.tipoMov.addItem("Todos", None)
        self.ui.tipoMov.addItem("Ingreso", "Ingreso")
        self.ui.tipoMov.addItem("Gasto", "Gasto")
        #dateedit
        self.cambiar_dateEdits()
        #tablas
        self.ui.ventasTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.movimientosTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.importacionesTablas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #TabWidget
        self.ui.tabWidget.tabBar().setExpanding(True)
        #Tablas
        self.movements_model = MovementsTableModel()
        self.sales_model=SalesTableModel()
        self.imports_model=ImportsTableModel()
        self.ui.movimientosTable.setModel(self.movements_model)
        self.ui.ventasTable.setModel(self.sales_model)
        self.ui.importacionesTablas.setModel(self.imports_model)
        #*Conectar las acciones
        # Conectar el cambio de selección en los QComboBox para activar o desactivar la visibilidad
        self.ui.periodoMov.currentTextChanged.connect(self.mostrar_dateEdits)
        self.ui.periodoVentas.currentTextChanged.connect(self.mostrar_dateEdits)
        self.ui.periodoImportacion.currentTextChanged.connect(self.mostrar_dateEdits)
        #*Cambios en la interfaz relacionado al controller
        self.conectar_acciones_informacion()
        self.ui.tabWidget.currentChanged.connect(self.actualizar_interfaz)
        self.actualizar_interfaz(0)
        self.actualizar_interfaz(1)
        self.actualizar_interfaz(2)
    def mostrar_dateEdits(self):
        # Pestaña Movimientos
        es_personalizado_mov = (self.ui.periodoMov.currentText() == "Personalizado")
        self.ui.lblPersonalizar.setVisible(es_personalizado_mov)
        self.ui.contenedorFechas.setVisible(es_personalizado_mov)
        # Pestaña Ventas
        es_personalizado_ventas = (self.ui.periodoVentas.currentText() == "Personalizado")
        self.ui.lblPersonalizarV.setVisible(es_personalizado_ventas)
        self.ui.contenedorFechasV.setVisible(es_personalizado_ventas)
        # Pestaña Importaciones
        es_personalizado_importaciones = (self.ui.periodoImportacion.currentText() == "Personalizado")
        self.ui.lblPersonalizarImp.setVisible(es_personalizado_importaciones)
        self.ui.contenedorFechasImp.setVisible(es_personalizado_importaciones)

    def obtener_datos(self,tab_actual):
        datos = {}
        datos["business_id"]=self.business.business_id
        if tab_actual == 0:
            periodo = self.ui.periodoMov.currentText()
            datos["periodo"] = periodo
            datos["tipo_movimiento"] = (self.ui.tipoMov.currentData())
            datos["descripcion"] = self.ui.buscar.toPlainText().strip() or None
            if periodo == "Personalizado":
                datos["rango_inicio"] = self.ui.rangoInicio.date().toPython()
                datos["rango_final"] = self.ui.rangoFinal.date().toPython()
        elif tab_actual==1:
            periodo = self.ui.periodoVentas.currentText()
            datos["periodo"] = periodo
            datos["categoria_id"] = (self.ui.categoriasVentas.currentData())
            if periodo == "Personalizado":
                datos["rango_inicio"] = (self.ui.rangoInicioV.date().toPython())
                datos["rango_final"] = (self.ui.rangoFinalV.date().toPython())
        elif tab_actual==2:
            periodo = self.ui.periodoImportacion.currentText()
            datos["periodo"] = periodo
            datos["nombre"] = self.ui.buscarNombre.toPlainText().strip() or None
            if periodo == "Personalizado":
                datos["rango_inicio"] = (self.ui.rangoInicioImp.date().toPython())
                datos["rango_final"] = (self.ui.rangoFinalImp.date().toPython())
        return datos
    def enviar_datos(self,tab_actual):
        datos=self.obtener_datos(tab_actual)
        if tab_actual==0:
            resultado=self.controller.mostrar_movimientos(datos)
        elif tab_actual==1:
            resultado=self.controller.mostrar_ventas(datos)
        elif tab_actual==2:
            resultado=self.controller.mostrar_importaciones(datos)
        return resultado
    def actualizar_interfaz(self,tab_actual):
        resultado=self.enviar_datos(tab_actual)
        if not resultado["success"]:
            QMessageBox.warning(self.ui,"Error al Cargar Datos",resultado["message"])
            return
        if resultado["tipo"] == "Movimientos":
            movimientos = resultado["movimientos"]
            self.movements_model.set_data(resultado["movimientos"])
            self.ui.lblPeriodo.setText(resultado["rango_fecha"])
            if not movimientos:
                QMessageBox.information(
                    self.ui,"No hay datos","No hay registros para mostrar en la tabla"
                )
        elif resultado["tipo"] == "Ventas":
            ventas = resultado["ventas"]
            self.sales_model.set_data(resultado["ventas"])
            self.ui.lblPeriodoV.setText(resultado["rango_fecha"])
        elif resultado["tipo"]=="Importaciones":
            importaciones=resultado["importaciones"]
            self.imports_model.set_data(importaciones)
            self.ui.lblPeriodoImp.setText(resultado["rango_fecha"])
    def conectar_acciones_informacion(self):
        #*Relacionados con la tab de movimientos
        self.ui.periodoMov.currentTextChanged.connect(
            lambda _: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.tipoMov.currentTextChanged.connect(
            lambda _: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.buscar.textChanged.connect(
            lambda: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.rangoFinal.editingFinished.connect(
            lambda: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        #*Relacionados con la tab de Ventas
        self.ui.periodoVentas.currentTextChanged.connect(
            lambda _: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.categoriasVentas.currentTextChanged.connect(
            lambda _: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.rangoFinalV.editingFinished.connect(
            lambda: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        #*Relacionados con la tab de Importaciones
        self.ui.periodoImportacion.currentTextChanged.connect(
            lambda _: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.buscarNombre.textChanged.connect(
            lambda: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
        self.ui.rangoFinalImp.editingFinished.connect(
            lambda: self.actualizar_interfaz(self.ui.tabWidget.currentIndex())
        )
    def cambiar_dateEdits(self):
        fecha_hoy = QDate.currentDate()
        fecha_ayer = fecha_hoy.addDays(-1)
        self.ui.rangoInicio.setDisplayFormat("yyyy-MM-dd")
        self.ui.rangoInicio.setDate(fecha_ayer)
        self.ui.rangoInicio.setCalendarPopup(True)
        self.ui.rangoFinal.setDisplayFormat("yyyy-MM-dd")
        self.ui.rangoFinal.setDate(fecha_hoy)
        self.ui.rangoFinal.setCalendarPopup(True)

        self.ui.rangoInicioV.setDisplayFormat("yyyy-MM-dd")
        self.ui.rangoInicioV.setDate(fecha_ayer)
        self.ui.rangoInicioV.setCalendarPopup(True)
        self.ui.rangoFinalV.setDisplayFormat("yyyy-MM-dd")
        self.ui.rangoFinalV.setDate(fecha_hoy)
        self.ui.rangoFinalV.setCalendarPopup(True)

