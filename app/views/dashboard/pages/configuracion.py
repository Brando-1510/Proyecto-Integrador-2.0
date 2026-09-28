import os
from PySide6.QtWidgets import QWidget,QVBoxLayout,QListWidgetItem,QSizePolicy
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.utils.utilsUI import llenar_datos_usuarios
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal
from app.models.business import TypeOfBusiness

class Configuracion(QWidget):
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
            directorio_actual,"../../../ui/dashboard/pages/configuracion.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
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
        #*Cambios en el ui
        self.ui.nombreNegocio.setText(self.business.business_name)
        self.ui.descripcion.setPlainText(self.business.description)
        #Tabwidget
        self.ui.tabWidgetDos.setTabBarAutoHide(False)
        self.ui.tabWidgetDos.tabBar().setExpanding(True)
        self.ui.tabWidgetDos.setDocumentMode(True)
        self.ui.tabWidgetDos.tabBar().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Llenar ComboBox
        for business_type in TypeOfBusiness:
            self.ui.tipoNegocio.addItem(business_type.value,business_type)
        # Seleccionar tipo actual
        index = self.ui.tipoNegocio.findData(self.business.type_of_business)
        if index != -1:
            self.ui.tipoNegocio.setCurrentIndex(index)
        for category in self.categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.UserRole, category)
            self.ui.listaCategorias.addItem(item)
"""Recordatorio:
def get_by_business(self, business_id):
    stmt = select(UserBusiness).where(
        UserBusiness.business_id == business_id
    )

    return self.session.scalars(stmt).all()
tengo que hacer un metodo asi en el repositorio"""
