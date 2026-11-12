import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QFrame, QSizePolicy, QHBoxLayout, QLabel, QPushButton, QGridLayout,
    QLayout
)
from PySide6.QtGui import QFontDatabase, QPixmap,QMovie
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt,Signal
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.utils.recommendation_presenter import RecommendationPresenter


class Recomendaciones(QWidget):
    solicitud_ia = Signal(str, dict)
    def __init__(self, userBusiness, controller=None):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.controller = controller

        # Cargar interfaz de Qt Designer.
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../../ui/dashboard/pages/recommendations.ui",
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar la interfaz:\n{ruta_ui}")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.addWidget(self.ui)
        self.ui.tabWidget.currentChanged.connect(self.al_cambiar_pestaña)
        self._cargar_fuentes()
        self._ocupado = False
        self.ui.generarAnalisis.clicked.connect(self.enviar_datos)
        self.ui.pushButton.clicked.connect(self.enviar_datos)
        self.actualizar_estado_botones()


    # Configuración inicial
    def _cargar_fuentes(self):
        id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        familias_manrope = QFontDatabase.applicationFontFamilies(id_manrope)
        familias_source = QFontDatabase.applicationFontFamilies(id_source)
        if familias_manrope and familias_source:
            estilos = estilos_fuentes(familias_source[0], familias_manrope[0])
            self.ui.setStyleSheet(self.ui.styleSheet() + estilos)
    def al_cambiar_pestaña(self, index):
        if index == 4:
            self.ui.generarAnalisis.setEnabled(False)
        else:
            self.ui.generarAnalisis.setEnabled(True)
    def actualizar_estado_botones(self, ocupado=None):
        if ocupado is not None:
            self._ocupado = ocupado
        es_asistente = self.ui.tabWidget.currentIndex() == 4
        self.ui.generarAnalisis.setEnabled(not self._ocupado and not es_asistente)
        self.ui.pushButton.setEnabled(not self._ocupado and es_asistente)
    def enviar_datos(self):
        tab_index = self.ui.tabWidget.currentIndex()
        business_id = self.business.business_id
        #*Solicitud al asistente IA
        if tab_index == 4:
            question = self.ui.lineEdit.text().strip()
            if not question:
                QMessageBox.warning(
                    self.ui, "Pregunta vacía","Debes escribir una pregunta."
                )
                return
            datos = {
                "business_id": business_id,
                "question": question
            }
            self.solicitud_ia.emit("assistant", datos)
            return
        #*Análisis financiero
        analysis_types = {
            0: "General",
            1: "Ventas",
            2: "Gastos",
            3: "Ingresos"
        }
        analysis_type = analysis_types.get(tab_index)
        if analysis_type is None:
            return
        datos = {
            "business_id": business_id,
            "analysis_type": analysis_type,
            "periodo": self.ui.periodo.currentText()
        }
        self.solicitud_ia.emit("analysis", datos)
