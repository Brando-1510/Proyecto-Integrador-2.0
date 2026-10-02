import os
from PySide6.QtWidgets import QWidget, QHeaderView, QVBoxLayout, QFileDialog, QSizePolicy
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
        self.pending_file_name = None

        #*Referencias del proceso de importación
        self.thread = None
        self.worker = None

        # Cargar archivo .UI
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(os.path.join(directorio_actual, "../../../ui/dashboard/pages/cargar_datos.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #*Tab widget
        self.ui.tabWidget.setTabBarAutoHide(False)
        self.ui.tabWidget.tabBar().setExpanding(True)
        self.ui.tabWidget.setDocumentMode(True)

        #*Fuentes
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")

        if font_id_manrope == -1: print("Advertencia: No se pudo cargar Manrope.")
        if font_id_source == -1: print("Advertencia: No se pudo cargar Source Sans 3.")

        manrope_family = QFontDatabase.applicationFontFamilies(font_id_manrope)[0] if font_id_manrope != -1 and QFontDatabase.applicationFontFamilies(font_id_manrope) else None
        source_family = QFontDatabase.applicationFontFamilies(font_id_source)[0] if font_id_source != -1 and QFontDatabase.applicationFontFamilies(font_id_source) else None

        if manrope_family and source_family:
            self.ui.setStyleSheet(self.ui.styleSheet() + estilos_fuentes(source_family, manrope_family))

        #*Tablas
        self.ui.ventasTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.movimientosTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #Permitir que las tablas crezcan verticalmente
        for table in (self.ui.ventasTable, self.ui.movimientosTable):
            table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            table.setMinimumHeight(300)

        # Modelos de las tablas
        self.movements_model = MovementsTableModel()
        self.sales_model = SalesTableModel()
        self.ui.movimientosTable.setModel(self.movements_model)
        self.ui.ventasTable.setModel(self.sales_model)

        # Estado inicial
        self.ui.frameArchivo.hide()
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()

        # Botones
        self.ui.btnSeleccionarArchivo.clicked.connect(self.select_excel_file)
        self.ui.btnCambiarArchivo.clicked.connect(self.change_excel_file)
        self.ui.btnCancelar.clicked.connect(self.cancel_import)

    #*Seleccionar archivo
    def select_excel_file(self):
        if self.thread is not None: return
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "", "Archivos de Excel (*.xlsx *.xls);;Todos los archivos (*)")
        if not file_path: return
        self.start_import(file_path)

    #*Cambiar archivo
    def change_excel_file(self):
        if self.thread is not None: return
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "", "Archivos de Excel (*.xlsx *.xls);;Todos los archivos (*)")
        if not file_path: return
        self.start_import(file_path)

    #*Iniciar importación
    def start_import(self, file_path):
        if self.thread is not None: return

        self.pending_file_name = os.path.basename(file_path)
        self.ui.frameArchivo.hide()

        # Mostrar elementos de progreso
        self.ui.progressBar.show()
        self.ui.lblEstadoImportacion.show()
        self.ui.lblPorcentaje.show()

        # Estado inicial
        self.ui.progressBar.setValue(0)
        self.ui.lblPorcentaje.setText("0%")
        self.ui.lblEstadoImportacion.setText("Preparando importación...")

        # Thread y worker
        self.thread = QThread()
        self.worker = ExcelImportWorker(file_path)
        self.worker.moveToThread(self.thread)

        # Conexiones
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.update_message)
        self.worker.finished.connect(self.import_finished)
        self.worker.error.connect(self.import_error)

        # Finalizar thread
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_thread)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    #*Actualizar progreso
    def update_progress(self, value):
        self.ui.progressBar.setValue(value)
        self.ui.lblPorcentaje.setText(f"{value}%")

    #*Actualizar mensaje
    def update_message(self, message):
        self.ui.lblEstadoImportacion.setText(message)

    #*Importación terminada
    def import_finished(self, result):
        if not result.success:
            self.ui.lblEstadoImportacion.setText("La importación no pudo completarse.")
            self.ui.lblPorcentaje.setText("Error")
            print("Errores:", result.errors)
            self.pending_file_name = None
            return

        #Importación exitosa
        self.selected_file_name = self.pending_file_name
        self.pending_file_name = None
        self.df_ventas = result.sales
        self.df_movimientos = result.movements

        #Actualizar tablas
        self.sales_model.set_data(self.df_ventas)
        self.movements_model.set_data(self.df_movimientos)

        #Actualizar interfaz
        self.ui.progressBar.setValue(100)
        self.ui.lblPorcentaje.setText("100%")
        self.ui.lblNombreArchivo.setText(self.selected_file_name)
        self.ui.frameArchivo.show()

        # Ocultar elementos de procesamiento
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()

    #*Error del worker
    def import_error(self, error_message):
        self.ui.lblEstadoImportacion.setText("Ocurrió un error durante la importación.")
        self.ui.lblPorcentaje.setText("Error")
        print("Error:", error_message)
        self.pending_file_name = None

    #*Cancelar archivo cargado
    def cancel_import(self):
        if self.thread is not None: return

        self.ui.frameArchivo.hide()
        self.df_ventas = None
        self.df_movimientos = None
        self.selected_file_name = None
        self.pending_file_name = None

        self.sales_model.set_data(None)
        self.movements_model.set_data(None)

    #*Limpiar referencias del thread
    def cleanup_thread(self):
        self.worker = None
        self.thread = None