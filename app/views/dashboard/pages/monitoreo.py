import os
from PySide6.QtWidgets import QWidget,QVBoxLayout,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal
from app.controllers.monitoring_controller import MonitoringController

class Monitoreo(QWidget):
    def __init__(self, userBusiness,monitoring_controller:MonitoringController):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.controller=monitoring_controller
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/monitoreo.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self._cargar_fuentes()
        #*Conectar acciones
        self.ui.comprobarIntegridad.clicked.connect(self.comprobar_integridad)
        self.ui.optimizadorTablas.clicked.connect(self.optimizar_tablas)

    def enviar_datos(self):
        return self.controller.send_data(self.business.business_id)
    def llenar_labels(self):
        resultado=self.enviar_datos()
        if not resultado["success"]:
            QMessageBox.warning(self.ui,"Error",resultado["message"])
            return
        self.ui.usuarios.setText(f"{str(resultado["empleados"])}")
        self.ui.ventas.setText(f"{str(resultado["ventas"])}")
        self.ui.movimientos.setText(f"{str(resultado["movimientos"])}")
        self.ui.importaciones.setText(f"{str(resultado["importaciones"])}")
    def comprobar_integridad(self):
        resultado = self.controller.check_database_health()
        if not resultado["success"]:
            QMessageBox.warning(self.ui, "Error", resultado["message"])
            return
        labels = {
            "Importaciones": self.ui.importacionesIntegridad,
            "Movimientos": self.ui.movimientosIntegridad,
            "Ventas": self.ui.ventasIntegridad,
            "Negocios": self.ui.negociosIntegridad,
            "Empleados": self.ui.empleadosIntegridad,
        }
        for tabla in resultado["tables"]:
            label = labels.get(tabla["name"])
            if label:
                label.setText(tabla["message"])
    def optimizar_tablas(self):
        resultado=self.controller.optimize_tables()
        if not resultado["success"]:
            QMessageBox.warning(self.ui, "Error", resultado["message"])
            return
        QMessageBox.information(self.ui,"Optimización Éxitosa",resultado["message"])
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