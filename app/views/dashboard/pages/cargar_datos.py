import os
from PySide6.QtWidgets import QWidget,QHeaderView,QVBoxLayout,QFileDialog,QMessageBox,QSizePolicy
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QThread, Slot
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.views.dashboard.table_models.movements_table_model import MovementsTableModel
from app.views.dashboard.table_models.sales_table_model import SalesTableModel
from app.workers.excel_import_worker import ExcelImportWorker
from app.workers.excel_save_worker import ExcelSaveWorker


class CargarDatos(QWidget):

    def __init__(self, userBusiness, parent=None):
        super().__init__(parent)

        # Contexto de negocio
        self.userBusiness = userBusiness
        self.user = userBusiness.user
        self.business = userBusiness.business

        # Estado de datos
        self.df_movimientos = None
        self.df_ventas = None
        self.selected_file_name = None
        self.selected_file_path = None
        self.pending_file_name = None
        self.pending_file_path = None

        # Referencias de concurrencia
        self.thread = None
        self.worker = None

        # Inicialización de UI y componentes
        self._setup_ui()
        self._cargar_fuentes()
        self._setup_models()
        self._connect_signals()
        self._reset_ui_state()

    # Configuración inicial

    def _setup_ui(self):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(directorio_actual, "../../../ui/dashboard/pages/cargar_datos.ui")
        )

        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)

        if not self.ui:
            raise RuntimeError(f"No se pudo cargar el archivo UI en: {ruta_ui}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.ui.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        if hasattr(self.ui, "tabWidget"):
            self.ui.tabWidget.setTabBarAutoHide(False)
            self.ui.tabWidget.tabBar().setExpanding(True)
            self.ui.tabWidget.setDocumentMode(True)

    def _cargar_fuentes(self):
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")

        manrope_families = QFontDatabase.applicationFontFamilies(font_id_manrope) if font_id_manrope != -1 else []
        source_families = QFontDatabase.applicationFontFamilies(font_id_source) if font_id_source != -1 else []

        if manrope_families and source_families:
            self.ui.setStyleSheet(
                self.ui.styleSheet() + estilos_fuentes(source_families[0], manrope_families[0])
            )

    def _setup_models(self):
        self.movements_model = MovementsTableModel()
        self.sales_model = SalesTableModel()

        # Compatibilidad con ambas nomenclaturas de tablas
        self.tabla_movimientos = getattr(self.ui, "movimientosTable", getattr(self.ui, "tableMovimientos", None))
        self.tabla_ventas = getattr(self.ui, "ventasTable", getattr(self.ui, "tableVentas", None))

        for tabla, model in [
            (self.tabla_movimientos, self.movements_model),
            (self.tabla_ventas, self.sales_model)
        ]:
            if tabla:
                tabla.setModel(model)
                tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                tabla.setMinimumHeight(300)

    def _connect_signals(self):
        self.ui.btnSeleccionarArchivo.clicked.connect(self.select_excel_file)
        self.ui.btnCambiarArchivo.clicked.connect(self.select_excel_file)
        self.ui.btnCancelar.clicked.connect(self.cancel_import)
        self.ui.btnAceptar.clicked.connect(self.save_import)

    def _reset_ui_state(self):
        self.ui.frameArchivo.hide()
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()

    # Gestión de archivos y procesos

    def select_excel_file(self):
        if self._is_processing():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos de Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )

        if file_path:
            self.start_import(file_path)

    def start_import(self, file_path: str):
        if self._is_processing():
            return

        self.pending_file_path = file_path
        self.pending_file_name = os.path.basename(file_path)

        self.ui.frameArchivo.hide()
        self._show_progress("Preparando importación...")
        self._toggle_buttons(enabled=False)

        # Configuración de hilo y worker
        self.thread = QThread()
        self.worker = ExcelImportWorker(file_path)
        self.worker.moveToThread(self.thread)

        # Conexiones del proceso
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.update_message)
        self.worker.finished.connect(self.import_finished)
        self.worker.error.connect(self.import_error)

        # Limpieza de memoria
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_thread)

        self.thread.start()

    def save_import(self):
        if self._is_processing():
            return

        if self.df_ventas is None or self.df_movimientos is None:
            return

        if not self.selected_file_path or not self.selected_file_name:
            return

        self._toggle_buttons(enabled=False)
        self._show_progress("Preparando guardado...")

        self.thread = QThread()
        self.worker = ExcelSaveWorker(
            user_id=self.user.user_id,
            business_id=self.business.business_id,
            file_path=self.selected_file_path,
            file_name=self.selected_file_name,
            df_sales=self.df_ventas,
            df_movements=self.df_movimientos
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.update_message)
        self.worker.finished.connect(self.save_finished)
        self.worker.error.connect(self.save_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_thread)

        self.thread.start()

    # Slots de respuesta

    @Slot(int)
    def update_progress(self, value: int):
        self.ui.progressBar.setValue(value)
        self.ui.lblPorcentaje.setText(f"{value}%")

    @Slot(str)
    def update_message(self, message: str):
        self.ui.lblEstadoImportacion.setText(message)

    @Slot(object)
    def import_finished(self, result):
        if not getattr(result, "success", False):
            error_msg = "\n".join(result.errors) if hasattr(result, "errors") and result.errors else "Error desconocido durante la importación."
            self.import_error(error_msg)
            return

        self.selected_file_name = self.pending_file_name
        self.selected_file_path = self.pending_file_path
        self.pending_file_name = None
        self.pending_file_path = None

        self.df_ventas = result.sales
        self.df_movimientos = result.movements

        self.sales_model.set_data(self.df_ventas)
        self.movements_model.set_data(self.df_movimientos)

        if hasattr(self.ui, "lblNombreArchivo"):
            self.ui.lblNombreArchivo.setText(self.selected_file_name)

        self.ui.frameArchivo.show()
        self._hide_progress()
        self._toggle_buttons(enabled=True)

    @Slot(str)
    def import_error(self, error_message: str):
        self._hide_progress()
        self._toggle_buttons(enabled=True, accept_enabled=False)

        self.pending_file_name = None
        self.pending_file_path = None

        QMessageBox.warning(self, "Error al importar", error_message)

    @Slot()
    def save_finished(self):
        self.ui.progressBar.setValue(100)
        self.ui.lblPorcentaje.setText("100%")

        QMessageBox.information(self, "Importación exitosa", "Los datos se guardaron correctamente.")

        self._clear_data_state()
        self._hide_progress()
        self.ui.frameArchivo.hide()
        self._toggle_buttons(enabled=True)

    @Slot(str)
    def save_error(self, error_message: str):
        if "ya existe en la base de datos" in error_message:
            QMessageBox.warning(self, "Archivo ya registrado", "Este archivo ya fue importado anteriormente para este negocio.")
        elif "no existe para este negocio" in error_message:
            QMessageBox.warning(self, "Categoría no encontrada", error_message)
        else:
            QMessageBox.critical(self, "Error al guardar", f"No se pudieron guardar los datos.\n\n{error_message}")

        self._hide_progress()
        self._toggle_buttons(enabled=True)

    def cancel_import(self):
        if self._is_processing():
            return

        self._clear_data_state()
        self.ui.frameArchivo.hide()
        self._hide_progress()
        self._toggle_buttons(enabled=True, accept_enabled=False)

    # Métodos auxiliares

    def _is_processing(self) -> bool:
        return self.thread is not None and self.thread.isRunning()

    @Slot()
    def _cleanup_thread(self):
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
        if self.thread:
            self.thread.deleteLater()
            self.thread = None

    def _clear_data_state(self):
        self.df_ventas = None
        self.df_movimientos = None
        self.selected_file_name = None
        self.selected_file_path = None
        self.pending_file_name = None
        self.pending_file_path = None

        self.sales_model.set_data(None)
        self.movements_model.set_data(None)

    def _show_progress(self, message: str):
        self.ui.progressBar.setValue(0)
        self.ui.lblPorcentaje.setText("0%")
        self.ui.lblEstadoImportacion.setText(message)
        self.ui.progressBar.show()
        self.ui.lblEstadoImportacion.show()
        self.ui.lblPorcentaje.show()

    def _hide_progress(self):
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()

    def _toggle_buttons(self, enabled: bool, accept_enabled: bool = True):
        self.ui.btnSeleccionarArchivo.setEnabled(enabled)
        self.ui.btnCambiarArchivo.setEnabled(enabled)
        self.ui.btnCancelar.setEnabled(enabled)
        self.ui.btnAceptar.setEnabled(enabled if accept_enabled else False)