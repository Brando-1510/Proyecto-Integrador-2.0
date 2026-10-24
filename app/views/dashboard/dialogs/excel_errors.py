import os
from PySide6.QtWidgets import QLabel,QMessageBox
from app.errors.import_errors import ImportErrorResult
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.views.estilosTipografia import estilos_fuentes

class ExcelErrorsUI:
    def __init__(self,errores: dict[str, list[ImportErrorResult]]):
        self.errores=errores
        self.erroresVentas=errores.get("ventas",[])
        self.erroresMovimientos=errores.get("movimientos",[])
        self.erroresGenerales = errores.get("generales", [])
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../../ui/dashboard/qdialog/ExcelCategories.ui",
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar el archivo UI: {ruta_ui}")
        self.ui.setWindowTitle("Errores del archivo Excel")
        self.llenar_scrollarea()
    def llenar_scrollarea(self):
        layout_ventas = self.ui.scrollAreaWidgetContents.layout()
        layout_movimientos = self.ui.scrollAreaWidgetContents_2.layout()
        if layout_ventas is None or layout_movimientos is None:
            raise RuntimeError("Los contenedores de errores deben tener un layout.")
        self.ui.lblVentas.setVisible(not bool(self.erroresVentas))
        self.ui.lblMovimientos.setVisible(not bool(self.erroresMovimientos))
        for error in self.erroresVentas:
            layout_ventas.addWidget(self._crear_label_error(error))
        for error in self.erroresMovimientos:
            layout_movimientos.addWidget(self._crear_label_error(error))
    @staticmethod
    def _crear_label_error(error: ImportErrorResult) -> QLabel:
        if error.row_number is not None:
            texto = f"Fila {error.row_number}: {error.message}"
        else:
            texto = error.message
        label = QLabel(texto)
        label.setWordWrap(True)
        return label
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

