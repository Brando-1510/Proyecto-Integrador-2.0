import os
from PySide6.QtCore import QThread, Slot,Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog, QHeaderView, QMessageBox, QSizePolicy, QVBoxLayout, QWidget
from app.models.user_business import Role
from app.errors.import_errors import ImportErrorType
from app.views.dashboard.dialogs.excel_errors import ExcelErrorsUI
from app.views.dashboard.dialogs.excel_categories import ExcelCategoriesUI
from app.generated import resources_rc
from app.views.dashboard.table_models.movements_table_model import MovementsTableModel
from app.views.dashboard.table_models.sales_table_model import SalesTableModel
from app.views.estilosTipografia import estilos_fuentes
from app.workers.excel_import_worker import ExcelImportWorker
from app.workers.excel_save_worker import ExcelSaveWorker

class CargarDatos(QWidget):
    importacion_exitosa = Signal()
    altura_cambiada = Signal(int)
    def __init__(self, userBusiness, parent=None):
        super().__init__(parent)
        self.userBusiness = userBusiness
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.df_movimientos = None
        self.df_ventas = None
        self.selected_file_name = None
        self.selected_file_path = None
        self.pending_file_name = None
        self.pending_file_path = None
        self.thread = None
        self.worker = None
        self._categories_to_create_pending = None
        self._categories_dialog_open = False
        self._setup_ui()
        self._cargar_fuentes()
        self._setup_models()
        self._connect_signals()
        self._reset_ui_state()

    def _setup_ui(self):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(os.path.join(directorio_actual, "../../../ui/dashboard/pages/cargar_datos.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar el archivo UI en: {ruta_ui}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.altura_cambiada.emit(689)
        self.ui.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if hasattr(self.ui, "tabWidget"):
            self.ui.tabWidget.setTabBarAutoHide(False)
            self.ui.tabWidget.tabBar().setExpanding(True)
            self.ui.tabWidget.setDocumentMode(True)

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

    def _setup_models(self):
        self.movements_model = MovementsTableModel()
        self.sales_model = SalesTableModel()
        self.tabla_movimientos = getattr(self.ui, "movimientosTable", getattr(self.ui, "tableMovimientos", None))
        self.tabla_ventas = getattr(self.ui, "ventasTable", getattr(self.ui, "tableVentas", None))
        self.tabla_movimientos.setMinimumHeight(400)
        self.tabla_movimientos.setMinimumHeight(400)
        for tabla, model in [(self.tabla_movimientos, self.movements_model), (self.tabla_ventas, self.sales_model)]:
            if tabla:
                tabla.setModel(model)
                tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _connect_signals(self):
        self.ui.btnSeleccionarArchivo.clicked.connect(self.select_excel_file)
        self.ui.btnCambiarArchivo.clicked.connect(self.select_excel_file)
        self.ui.btnCancelar.clicked.connect(self.cancel_import)
        self.ui.btnAceptar.clicked.connect(self.save_import)

    def _reset_ui_state(self):
        self.altura_cambiada.emit(689)
        self.ui.frameArchivo.hide()
        self.ui.progressBar.hide()
        self.ui.lblEstadoImportacion.hide()
        self.ui.lblPorcentaje.hide()

    def select_excel_file(self):
        if self._is_processing():
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self.ui, "Seleccionar archivo Excel", "", "Archivos de Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )
        if file_path:
            self.start_import(file_path)
    def start_import(self, file_path: str):
        if self._is_processing():
            return
        self.pending_file_path = file_path
        self.pending_file_name = os.path.basename(file_path)
        self.ui.frameArchivo.hide()
        self.altura_cambiada.emit(689)
        self._show_progress("Preparando importación...")
        self._toggle_buttons(enabled=False)
        self.thread = QThread()
        self.worker = ExcelImportWorker(file_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.update_message)
        self.worker.finished.connect(self.import_finished)
        self.worker.error.connect(self.import_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_thread)
        self.thread.start()

    def save_import(self):
        if self._is_processing():
            return
        if not self.selected_file_path or not self.selected_file_name:
            return
        respuesta = QMessageBox.question(
            self.ui,"Guardar Importación","¿Desea guardar la importación?",
            QMessageBox.StandardButton.Yes| QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        self._start_save_worker()

    def _start_save_worker(self,categories_to_create: list[str] | None = None,):
        if self._is_processing():
            return
        self._show_progress("Preparando guardado...")
        self._toggle_buttons(enabled=False)
        self.thread = QThread(self)
        self.worker = ExcelSaveWorker(
            user_id=self.user.user_id,
            business_id=self.business.business_id,
            file_path=self.selected_file_path,
            file_name=self.selected_file_name,
            df_sales=self.df_ventas,
            df_movements=self.df_movimientos,
            categories_to_create=categories_to_create,
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
    @Slot(int)
    def update_progress(self, value: int):
        self.ui.progressBar.setValue(value)
        self.ui.lblPorcentaje.setText(f"{value}%")
    @Slot(str)
    def update_message(self, message: str):
        self.ui.lblEstadoImportacion.setText(message)
    @Slot(object)
    def import_finished(self, result):
        if not result.success:
            if result.errors:
                self._show_import_errors(result.errors)
            else:
                self._show_unknown_import_error()
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
        self.altura_cambiada.emit(1000)
        self._hide_progress()
        self._toggle_buttons(enabled=True)
    @Slot(object)
    def import_error(self, error):
        self._show_import_error(error)
        self._hide_progress()
        self.pending_file_name = None
        self.pending_file_path = None
        self._toggle_buttons(enabled=True, accept_enabled=False)

    @Slot()
    def save_finished(self):
        self.importacion_exitosa.emit()
        QMessageBox.information(self.ui,"Importación exitosa","Los datos se guardaron correctamente.")
        self._clear_data_state()
        self.ui.frameArchivo.hide()
        self.altura_cambiada.emit(689)
        self._hide_progress()
        self._toggle_buttons(enabled=True, accept_enabled=False)

    @Slot(object)
    def save_error(self, error):
        self._hide_progress()
        if error.error_type == ImportErrorType.CATEGORY_NOT_FOUND:
            missing_categories = error.missing_categories or []
            if not missing_categories:
                self._show_save_error(error)
                self._toggle_buttons(enabled=True, accept_enabled=True)
                return
            #*Solo el gerente puede autorizar la creación.
            if self.userBusiness.role != Role.MANAGER:
                QMessageBox.warning(
                    self.ui,
                    "Categorías no encontradas",
                    "El archivo contiene categorías de ventas que "
                    "no existen para este negocio.\n\n"
                    "Solicite al gerente que cree las categorías "
                    "o que realice la importación.",
                )
                self._toggle_buttons(enabled=True,accept_enabled=False,)
                return
            #*Mostrar el diálogo personalizado.
            dialog = ExcelCategoriesUI(categorias=missing_categories,parent=self,)
            dialog.create_category_requested.connect(self._on_create_categories_requested)
            dialog.cancel_importation_requested.connect(self._on_cancel_categories_requested)
            self._categories_dialog_open = True
            dialog.ui.exec()
            self._categories_dialog_open = False

            # Si el hilo anterior ya terminó, inicia el segundo intento.
            # Si todavía existe, _cleanup_thread se encargará de hacerlo.
            if self._categories_to_create_pending is not None:
                self._try_start_pending_save()
            else:
                # El gerente canceló. Se conserva la vista previa.
                self._toggle_buttons(enabled=True,accept_enabled=True,)
            return

        # Los demás errores siguen el flujo habitual.
        self._show_save_error(error)
        self._toggle_buttons(enabled=True,accept_enabled=True,)

    @Slot(object)
    def _on_create_categories_requested(self, categories: list[str]):
        #*Guarda las categorías autorizadas para el siguiente intento
        self._categories_to_create_pending = categories.copy()

    @Slot()
    def _on_cancel_categories_requested(self):
        #!Cancela la creación de categorías sin guardar la importación
        self._categories_to_create_pending = None

    def _try_start_pending_save(self):
        """
        Inicia el segundo intento únicamente cuando el hilo anterior
        ha sido limpiado y ya no existe una operación de guardado activa.
        """
        if self._categories_to_create_pending is None:
            return
        if self.thread is not None:
            return
        categories = self._categories_to_create_pending
        self._categories_to_create_pending = None
        self._start_save_worker(categories_to_create=categories)

    def _show_import_error(self, error):
        if error.error_type == ImportErrorType.INVALID_FILE:
            QMessageBox.warning(self.ui, "Archivo inválido", error.message)
        elif error.error_type == ImportErrorType.INVALID_DATA:
            QMessageBox.warning(self.ui, "Datos inválidos", error.message)
        else:
            QMessageBox.critical(self.ui, "Error al importar", error.message)
    def _show_save_error(self, error):
        if error.error_type == ImportErrorType.FILE_ALREADY_EXISTS:
            QMessageBox.warning(self.ui, "Archivo ya registrado", error.message)
        elif error.error_type == ImportErrorType.CATEGORY_NOT_FOUND:
            QMessageBox.warning(self.ui, "Categoría no encontrada", error.message)
        elif error.error_type == ImportErrorType.INVALID_DATA:
            QMessageBox.warning(self.ui, "Datos inválidos", error.message)
        elif error.error_type == ImportErrorType.DATABASE_ERROR:
            QMessageBox.critical(self.ui, "Error al guardar", error.message)
        else:
            QMessageBox.critical(self.ui, "Error inesperado", error.message)
    def _show_unknown_import_error(self):
        QMessageBox.critical(self.ui, "Error inesperado", "Ocurrió un error inesperado durante la importación del archivo.")
        self._hide_progress()
        self.pending_file_name = None
        self.pending_file_path = None
        self._toggle_buttons(enabled=True, accept_enabled=False)

    def cancel_import(self):
        if self._is_processing():
            return
        respuesta=QMessageBox.question(
            self.ui,"Cancelar Importación","¿Desea cancelar la importación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self._clear_data_state()
            self.ui.frameArchivo.hide()
            self.altura_cambiada.emit(689)
            self._hide_progress()
            self._toggle_buttons(enabled=True, accept_enabled=False)
        else:
            return
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
        # Si el gerente autoriza las categorías entonces se continua el guardado
        self._try_start_pending_save()

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

    def _show_import_errors(self, errors):
        errores_por_hoja = {
            "ventas": [],
            "movimientos": [],
            "generales": [],
        }
        for error in errors:
            if error.sheet_name == "Ventas":
                errores_por_hoja["ventas"].append(error)
            elif error.sheet_name == "Movimientos":
                errores_por_hoja["movimientos"].append(error)
            else:
                errores_por_hoja["generales"].append(error)
        #*Mostrar los errores de las hojas en el diálogo.
        if errores_por_hoja["ventas"] or errores_por_hoja["movimientos"]:
            dialog = ExcelErrorsUI(errores_por_hoja)
            dialog.ui.exec()
        #*Mostrar los errores que no pertenecen a una hoja.
        if errores_por_hoja["generales"]:
            mensajes = "\n\n".join(error.message for error in errores_por_hoja["generales"])
            QMessageBox.warning(self.ui,"Error durante la importación",mensajes,)
        self._hide_progress()
        self.pending_file_name = None
        self.pending_file_path = None
        self._toggle_buttons(enabled=True, accept_enabled=False)
