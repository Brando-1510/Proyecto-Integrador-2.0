import os
from PySide6.QtWidgets import QWidget,QVBoxLayout
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal,QDate

class Informes(QWidget):
    def __init__(self, userBusiness):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        #*obtener directorio actual
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*cargar archivo .ui
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/informes.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        self.cambiar_dateEdits()
        self.ui.lblPersonalizar.hide()
        self.ui.contenedorFechas.hide()
        datos=[
            ("Informe Financiero General","general"),("Informe de Ingresos","ingresos"),
            ("Informe de Gastos","gastos"),("Informe de Ventas","ventas")
        ]
        for txt,valor in datos:
            self.ui.comboBox.addItem(txt,userData=valor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self._cargar_fuentes()
        #*Conectar las acciones
        self.ui.periodo.currentTextChanged.connect(self.mostrar_dateEdits)
    def mostrar_dateEdits(self):
        es_personalizado= (self.ui.periodo.currentText() == "Personalizado")
        self.ui.lblPersonalizar.setVisible(es_personalizado)
        self.ui.contenedorFechas.setVisible(es_personalizado)
    def cambiar_dateEdits(self):
        fecha_hoy = QDate.currentDate()
        fecha_ayer = fecha_hoy.addDays(-1)
        self.ui.rangoInicio.setDisplayFormat("yyyy-MM-dd")
        self.ui.rangoInicio.setDate(fecha_ayer)
        self.ui.rangoInicio.setCalendarPopup(True)
        self.ui.rangoFinal.setDisplayFormat("yyyy-MM-dd")
        self.ui.rangoFinal.setDate(fecha_hoy)
        self.ui.rangoFinal.setCalendarPopup(True)
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
    def obtener_datos(self):
        datos={
            "business_id":self.business.business_id,
            "user_id":self.user.user_id,
            "tipo_reporte": self.ui.comboBox.currentData(),
            "periodo":self.ui.periodo.currentText()
        }
        if self.ui.periodo.currentText()=="Personalizado":
            datos["rango_inicio"] = (self.ui.rangoInicio.date().toPython())
            datos["rango_final"] = (self.ui.rangoFinal.date().toPython())
        return datos
