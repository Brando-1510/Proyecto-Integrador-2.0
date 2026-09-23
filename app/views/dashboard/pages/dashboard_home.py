import os
from app.views.dashboard.table_models.movements_table_model import MovementsTableModel
from app.views.dashboard.table_models.sales_table_model import SalesTableModel
from PySide6.QtWidgets import QWidget,QHeaderView
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.utils.utilsUI import obtener_icono
from PySide6.QtCore import Qt,Signal

class DashboardHome(QWidget):
    def __init__(self, userBusiness):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/dashboard_home.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
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
        self.ui.lblSaludo.setText(f"Bienvenido, {self.user.username}")
        self.ui.lblNombreNeg.setText(f"{self.business.business_name}")
        pixmap = QPixmap(obtener_icono(self.userBusiness))
        pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ui.lblBusinessIcon.setPixmap(pixmap)
        #*Cambios en la ui
        #TabWidget
        self.ui.tabWidget.tabBar().setExpanding(True)
        #Tablas
        self.ui.ventasTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.movimientosTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.movements_model = MovementsTableModel()
        self.sales_model=SalesTableModel()
        self.ui.movimientosTable.setModel(self.movements_model)
        self.ui.ventasTable.setModel(self.sales_model)
        #*MOSTRAR VENTANA
        self.show()