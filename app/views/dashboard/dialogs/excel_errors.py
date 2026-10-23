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
        #* OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        #* CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/qdialog/ExcelErrors.ui"
        ))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        self.ui.setWindowTitle("Errores del archivo Excel")
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

