import os

from PySide6.QtWidgets import (
    QWidget,QStackedWidget,QPushButton,QVBoxLayout,QMessageBox,QSizePolicy,
)
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Signal
from app.core.screen_utils import calcular_tamano_pantalla
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.models.user_business import Role

from app.views.dashboard.pages.dashboard_home import DashboardHome
from app.views.dashboard.pages.cargar_datos import CargarDatos
from app.views.dashboard.pages.analisis import Analisis
from app.views.dashboard.pages.movimientos import Movimientos
from app.views.dashboard.pages.recomendaciones import Recomendaciones
from app.views.dashboard.pages.informes import Informes
from app.views.dashboard.pages.configuracion import Configuracion
from app.views.dashboard.pages.monitoreo import Monitoreo


class VentanaDashboard(QWidget):
    choose_business_requested = Signal(object)
    logout_requested = Signal()
    PERMISOS_PAGINAS = {
        Role.ADMIN: {
            "analisis",
            "recomendaciones",
            "informes",
            "configuracion",
            "monitoreo",
        },
        Role.MANAGER: {
            "analisis",
            "recomendaciones",
            "informes",
            "configuracion",
        },
        Role.FINANCIAL_ANALYST: {
            "analisis",
            "recomendaciones",
            "informes",
        },
        Role.EMPLOYEE: set(),
    }

    def __init__(
        self,userBusiness,home_dashboard_controller,consultation_controler,analysis_controller,
        recommendation_controller,configuration_controller,monitoring_controller
    ):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness

        self.home_dashboard_controller = home_dashboard_controller
        self.consultation_controller = consultation_controler
        self.analysis_controller = analysis_controller
        self.recommendation_controller = recommendation_controller
        self.configuration_controller = configuration_controller
        self.monitoring_controller=monitoring_controller

        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(directorio_actual,"../../ui/dashboard/dashboard.ui",)
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en: {ruta_ui}")
            return
        ancho, alto = calcular_tamano_pantalla(0.8, 0.8)
        self.resize(ancho, alto)
        self.setMinimumSize(900, 570)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.stackedWidget = self.ui.findChild(QStackedWidget, "stackedWidget")
        self.btnHome = self.ui.findChild(QPushButton, "btnHome")
        self.btnCargarDatos = self.ui.findChild(QPushButton, "btnLoadData")
        self.btnAnalisis = self.ui.findChild(QPushButton, "BtnAnalisis")
        self.btnMovimientos = self.ui.findChild(QPushButton, "btnMovimientos")
        self.btnRecomendaciones = self.ui.findChild(QPushButton, "BtnRecomendaciones")
        self.btnInformes = self.ui.findChild(QPushButton, "BtnInformes")
        self.btnConfiguracion = self.ui.findChild(QPushButton, "BtnConfiguracion")
        self.btnMonitoreo = self.ui.findChild(QPushButton, "BtnMonitoreo")
        self.btnLogout = self.ui.findChild(QPushButton, "BtnCerrarSesion")
        self.configurar_permisos_interfaz()

        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
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
        if manrope_family and source_family:
            estilos_actuales = self.ui.styleSheet()
            estilos_tipografias = estilos_fuentes(
                source_family, manrope_family
            )
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")
        self.cargar_paginas()

        self.btnLogout.clicked.connect(self.cerrar_sesion)
        self.btnHome.clicked.connect(self.mostrar_home)
        self.btnCargarDatos.clicked.connect(self.mostrar_cargar_datos)
        self.btnAnalisis.clicked.connect(self.mostrar_analisis)
        self.btnMovimientos.clicked.connect(self.mostrar_movimientos)
        self.btnRecomendaciones.clicked.connect(self.mostrar_recomendaciones)
        self.btnInformes.clicked.connect(self.mostrar_informes)
        self.btnConfiguracion.clicked.connect(self.mostrar_configuracion)
        self.btnMonitoreo.clicked.connect(self.mostrar_monitoreo)
        self.mostrar_home()
        self.showMaximized()

    def configurar_permisos_interfaz(self):
        rol = self.userBusiness.role
        permisos = self.PERMISOS_PAGINAS.get(rol, set())
        botones_por_pagina = {
            "analisis": self.btnAnalisis,
            "recomendaciones": self.btnRecomendaciones,
            "informes": self.btnInformes,
            "configuracion": self.btnConfiguracion,
            "monitoreo": self.btnMonitoreo,
        }
        for pagina, boton in botones_por_pagina.items():
            if boton is not None:
                boton.setVisible(pagina in permisos)

    def tiene_permiso(self, pagina):
        rol = self.userBusiness.role
        permisos = self.PERMISOS_PAGINAS.get(rol, set())
        paginas_comunes = {"home", "cargar_datos", "movimientos"}
        if pagina in paginas_comunes:
            return True
        return pagina in permisos

    def cerrar_sesion(self):
        respuesta = QMessageBox.question(
            self,"Cerrar Sesión","¿Desea salir?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
    def cambiar_vista(self, nuevo_widget):
        for i in range(self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            if widget == nuevo_widget:
                widget.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred,)
            else:
                widget.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored,)
        self.stackedWidget.setCurrentWidget(nuevo_widget)
        self.stackedWidget.adjustSize()
        if hasattr(self.ui, "scrollAreaWidgetContents"):
            self.ui.scrollAreaWidgetContents.adjustSize()

    def cargar_paginas(self):
        self.dashboard_home = DashboardHome(self.userBusiness,self.home_dashboard_controller,)
        self.stackedWidget.addWidget(self.dashboard_home)
        self.cargar_datos = None
        self.analisis = None
        self.movimientos = None
        self.recomendaciones = None
        self.informes = None
        self.monitoreo = None
        self.configuracion = None

    def mostrar_home(self):
        if not self.tiene_permiso("home"):
            return
        self.cambiar_vista(self.dashboard_home)

    def mostrar_cargar_datos(self):
        if not self.tiene_permiso("cargar_datos"):
            return
        if self.cargar_datos is None:
            self.cargar_datos = CargarDatos(self.userBusiness)
            self.cargar_datos.importacion_exitosa.connect(self._actualizar_datos_tras_importacion)
            self.stackedWidget.addWidget(self.cargar_datos)
        self.cambiar_vista(self.cargar_datos)

    def mostrar_analisis(self):
        if not self.tiene_permiso("analisis"):
            return
        if self.analisis is None:
            self.analisis = Analisis(self.userBusiness,self.analysis_controller,)
            self.stackedWidget.addWidget(self.analisis)
        self.cambiar_vista(self.analisis)

    def mostrar_movimientos(self):
        if not self.tiene_permiso("movimientos"):
            return
        if self.movimientos is None:
            self.movimientos = Movimientos(self.userBusiness,self.consultation_controller,)
            self.stackedWidget.addWidget(self.movimientos)
        self.cambiar_vista(self.movimientos)
        self.movimientos.actualizar_interfaz(self.movimientos.ui.tabWidget.currentIndex())

    def mostrar_recomendaciones(self):
        if not self.tiene_permiso("recomendaciones"):
            return
        if self.recomendaciones is None:
            self.recomendaciones = Recomendaciones(self.userBusiness,self.recommendation_controller,)
            self.stackedWidget.addWidget(self.recomendaciones)
        self.cambiar_vista(self.recomendaciones)

    def mostrar_informes(self):
        if not self.tiene_permiso("informes"):
            return
        if self.informes is None:
            self.informes = Informes(self.userBusiness)
            self.stackedWidget.addWidget(self.informes)
        self.cambiar_vista(self.informes)

    def mostrar_configuracion(self):
        if not self.tiene_permiso("configuracion"):
            return
        if self.configuracion is None:
            self.configuracion = Configuracion(self.userBusiness,self.configuration_controller,)
            self.configuracion.choose_business_requested.connect(self.choose_business_requested.emit)
            self.stackedWidget.addWidget(self.configuracion)
        self.cambiar_vista(self.configuracion)

    def mostrar_monitoreo(self):
        if not self.tiene_permiso("monitoreo"):
            return
        if self.monitoreo is None:
            self.monitoreo = Monitoreo(self.userBusiness,self.monitoring_controller)
            self.stackedWidget.addWidget(self.monitoreo)
        self.cambiar_vista(self.monitoreo)

    def _actualizar_datos_tras_importacion(self):
        # Actualizar movimientos.
        if self.movimientos is not None:
            self.movimientos.actualizar_interfaz(
                self.movimientos.ui.tabWidget.currentIndex()
            )

        # Actualizar dashboard principal.
        if self.dashboard_home is not None:
            self.dashboard_home.actualizar_datos()

        # Actualizar análisis financiero.
        if self.analisis is not None:
            self.analisis.actualizar_interfaz()

        # Actualizar recomendaciones.
        if self.recomendaciones is not None:
            self.recomendaciones.actualizar_interfaz()