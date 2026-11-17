import os
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QDate
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.controllers.report_controller import ReportController


class Informes(QWidget):
    def __init__(self, userBusiness, controller: ReportController):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.controller = controller
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual, "../../../ui/dashboard/pages/informes.ui"
        ))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar la interfaz de informes: {ruta_ui}")
        self.cambiar_dateEdits()
        self.ui.lblPersonalizar.hide()
        self.ui.contenedorFechas.hide()
        for label, value in [
            ("Informe Financiero General", "general"),
            ("Informe de Ingresos", "ingresos"),
            ("Informe de Gastos", "gastos"),
            ("Informe de Ventas", "ventas"),
        ]:
            self.ui.comboBox.addItem(label, userData=value)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self._cargar_fuentes()
        self.ui.periodo.currentTextChanged.connect(self.mostrar_dateEdits)
        self.ui.generarInforme.clicked.connect(self.enviar_datos)
        self.controller.generation_started.connect(self._generacion_iniciada)
        self.controller.generation_finished.connect(self._generacion_finalizada)
        self._generacion_iniciada() if self.controller.is_generating else None

    def mostrar_dateEdits(self):
        personalizado = self.ui.periodo.currentText() == "Personalizado"
        self.ui.lblPersonalizar.setVisible(personalizado)
        self.ui.contenedorFechas.setVisible(personalizado)

    def cambiar_dateEdits(self):
        hoy = QDate.currentDate()
        for widget, fecha in ((self.ui.rangoInicio, hoy.addDays(-1)),
                            (self.ui.rangoFinal, hoy)):
            widget.setDisplayFormat("yyyy-MM-dd")
            widget.setDate(fecha)
            widget.setCalendarPopup(True)

    def _cargar_fuentes(self):
        manrope_id = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        source_id = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if manrope_id == -1 or source_id == -1:
            return
        manrope = QFontDatabase.applicationFontFamilies(manrope_id)
        source = QFontDatabase.applicationFontFamilies(source_id)
        if manrope and source:
            self.ui.setStyleSheet(self.ui.styleSheet() + estilos_fuentes(source[0], manrope[0]))

    def obtener_datos(self):
        data = {
            "business_id": self.business.business_id,
            "user_id": self.user.user_id,
            "tipo_reporte": self.ui.comboBox.currentData(),
            "periodo": self.ui.periodo.currentText(),
        }
        if data["periodo"] == "Personalizado":
            data["rango_inicio"] = self.ui.rangoInicio.date().toPython()
            data["rango_final"] = self.ui.rangoFinal.date().toPython()
        return data

    def enviar_datos(self):
        self.controller.generar_informe(self.obtener_datos(), parent=self.ui)

    def _generacion_iniciada(self):
        self.ui.generarInforme.setEnabled(False)
        self.ui.generarInforme.setText("Generando informe…")

    def _generacion_finalizada(self, _success: bool, _message: str):
        self.ui.generarInforme.setEnabled(True)
        self.ui.generarInforme.setText("Generar Informe")

    def actualizar_usuario(self, user):
        self.user = user

    def actualizar_business(self, business):
        self.business = business
