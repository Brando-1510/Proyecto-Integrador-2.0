
import os

from PySide6.QtCore import Signal,QObject
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes


class ExcelCategoriesUI(QObject):
    create_category_requested = Signal(object)
    cancel_importation_requested = Signal()

    def __init__(self, categorias: list[str], parent=None):
        super().__init__(parent)
        self.categorias = categorias

        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../../ui/dashboard/qdialog/ExcelCategories.ui",
            )
        )

        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, parent)

        if not self.ui:
            raise RuntimeError(
                f"No se pudo cargar el archivo UI: {ruta_ui}"
            )

        self._cargar_fuentes()
        self._conectar_signals()
        self.llenar_scrollarea()

    def _cargar_fuentes(self):
        font_id_manrope = QFontDatabase.addApplicationFont(
            ":/fonts/Manrope-Regular.ttf"
        )
        font_id_source = QFontDatabase.addApplicationFont(
            ":/fonts/SourceSans3-Regular.ttf"
        )

        if font_id_manrope == -1 or font_id_source == -1:
            return

        manrope = QFontDatabase.applicationFontFamilies(
            font_id_manrope
        )
        source = QFontDatabase.applicationFontFamilies(
            font_id_source
        )

        if manrope and source:
            self.ui.setStyleSheet(
                self.ui.styleSheet()
                + estilos_fuentes(source[0], manrope[0])
            )

    def _conectar_signals(self):
        self.ui.cancelar.clicked.connect(
            self.cancelar_importacion
        )
        self.ui.crearCategorias.clicked.connect(
            self.crear_categorias
        )

    def llenar_scrollarea(self):
        layout = self.ui.scrollAreaWidgetContents.layout()

        if layout is None:
            layout = QVBoxLayout(
                self.ui.scrollAreaWidgetContents
            )

        for categoria in self.categorias:
            layout.addWidget(QLabel(categoria))

        layout.addStretch()

    def crear_categorias(self):
        self.create_category_requested.emit(
            self.categorias.copy()
        )
        self.ui.accept()

    def cancelar_importacion(self):
        self.cancel_importation_requested.emit()
        self.ui.reject()
