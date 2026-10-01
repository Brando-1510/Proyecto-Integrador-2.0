import os
from PySide6.QtWidgets import (QWidget,QHeaderView,QVBoxLayout,QFileDialog,QSizePolicy)
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QThread
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.views.dashboard.table_models.movements_table_model import MovementsTableModel
from app.views.dashboard.table_models.sales_table_model import SalesTableModel
from app.workers.excel_import_worker import ExcelImportWorker

class CargarDatos(QWidget):
    def __init__(self, userBusiness):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        #*Datos de la importación
        self.df_movimientos = None
        self.df_ventas = None
        self.selected_file_name = None
        #*Referencias del proceso de importacion
        self.thread = None
        self.worker = None
        #CARGAR ARCHIVO .UI
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../../ui/dashboard/pages/cargar_datos.ui"
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.setSizePolicy(
    QSizePolicy.Policy.Expanding,
    QSizePolicy.Policy.Expanding
)

        # TAB WIDGET
        self.ui.tabWidget.setTabBarAutoHide(False)
        self.ui.tabWidget.tabBar().setExpanding(True)
        self.ui.tabWidget.setDocumentMode(True)
        #*FUENTES
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if font_id_manrope == -1:
            print("Advertencia: No se pudo cargar Manrope.")
        if font_id_source == -1:
            print("Advertencia: No se pudo cargar Source Sans 3.")
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
        if manrope_family and source_family:
            estilos_actuales = self.ui.styleSheet()
            estilos_tipografias = estilos_fuentes(source_family,manrope_family)
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)
        # TABLAS
        self.ui.ventasTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.ui.movimientosTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # Permitir que las tablas crezcan verticalmente
        for table in (
            self.ui.ventasTable,
            self.ui.movimientosTable
        ):
            table.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )

            table.setMinimumHeight(300)

        self.movements_model = MovementsTableModel()
        self.sales_model = SalesTableModel()

        self.ui.movimientosTable.setModel(self.movements_model)
        self.ui.ventasTable.setModel(self.sales_model)
        # ESTADO INICIAL
        self.ui.frameArchivo.hide()
        # Elementos del proceso
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()
        # BOTONES
        self.ui.btnSeleccionarArchivo.clicked.connect(self.select_excel_file)
    # SELECCIONAR ARCHIVO
    def select_excel_file(self):
        if self.thread is not None:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos de Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )
        if not file_path:
            return

        self.selected_file_name = os.path.basename(file_path)
        # Comenzar importación
        self.start_import(file_path)
    #*INICIAR IMPORTACIÓN
    def start_import(self, file_path):
        if self.thread is not None:
            return
        self.ui.frameArchivo.hide()
        # Mostrar elementos de progreso
        self.ui.progressBar.show()
        self.ui.lblEstadoImportacion.show()
        self.ui.lblPorcentaje.show()
        # Estado inicial
        self.ui.progressBar.setValue(0)
        self.ui.lblPorcentaje.setText("0%")
        self.ui.lblEstadoImportacion.setText("Preparando importación...")
        # THREAD
        self.thread = QThread()
        # WORKER
        self.worker = ExcelImportWorker(file_path)
        # Mover worker al thread
        self.worker.moveToThread(self.thread)
        # CONEXIONES
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.update_message)
        self.worker.finished.connect(self.import_finished)
        self.worker.error.connect(self.import_error)
        # FINALIZAR THREAD
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_thread)
        self.thread.finished.connect(self.thread.deleteLater)
        # INICIAR
        self.thread.start()
    # ACTUALIZAR PROGRESO
    def update_progress(self, value):
        self.ui.progressBar.setValue(value)
        self.ui.lblPorcentaje.setText(f"{value}%")
    # ACTUALIZAR MENSAJE
    def update_message(self, message):
        self.ui.lblEstadoImportacion.setText(message)
    # IMPORTACIÓN TERMINADA
    def import_finished(self, result):
        # IMPORTACIÓN FALLIDA
        if not result.success:
            self.ui.lblEstadoImportacion.setText("La importación no pudo completarse.")
            self.ui.lblPorcentaje.setText("Error")
            print("Errores:",result.errors)
            return
        # IMPORTACIÓN EXITOSA
        # Guardar DataFrames
        self.df_ventas = result.sales
        self.df_movimientos = result.movements
        # ACTUALIZAR TABLAS
        self.sales_model.set_data(self.df_ventas)
        self.movements_model.set_data(self.df_movimientos)
        # ACTUALIZAR PROGRESO
        self.ui.progressBar.setValue(100)
        self.ui.lblPorcentaje.setText("100%")
        # MOSTRAR ARCHIVO
        self.ui.lblNombreArchivo.setText(self.selected_file_name)
        self.ui.frameArchivo.show()
        # OCULTAR ELEMENTOS DE PROCESAMIENTO
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()
    #!ERROR DEL WORKER
    def import_error(self, error_message):
        self.ui.lblEstadoImportacion.setText("Ocurrió un error durante la importación.")
        self.ui.lblPorcentaje.setText("Error")
        print("Error:",error_message )
    # LIMPIAR REFERENCIAS DEL THREAD
    def cleanup_thread(self):
        self.worker = None
        self.thread = None