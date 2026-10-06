import os
from app.core.screen_utils import calcular_tamano_pantalla
from PySide6.QtWidgets import QWidget,QStackedWidget,QPushButton,QVBoxLayout,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Signal
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
#*Importacion de los widgets
from app.views.dashboard.pages.dashboard_home import DashboardHome
from app.views.dashboard.pages.cargar_datos import CargarDatos
from app.views.dashboard.pages.analisis import Analisis
from app.views.dashboard.pages.movimientos import Movimientos
from app.views.dashboard.pages.recomendaciones import Recomendaciones
from app.views.dashboard.pages.informes import Informes
from app.views.dashboard.pages.configuracion import Configuracion
from app.views.dashboard.pages.monitoreo import Monitoreo

class VentanaDashboard(QWidget):
    logout_requested = Signal()
    def __init__(
        self, userBusiness,
        home_dashboard_controller,
    ):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        #*Controllers para las paginas del stackedwidget
        self.home_dashboard_controller=home_dashboard_controller
        #*Obtener directorio actual
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*Cargar archivo ui
        ruta_ui = os.path.normpath(os.path.join(
                directorio_actual,"../../ui/dashboard/dashboard.ui"
            ))
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

        #*Obtener widget del ui
        self.stackedWidget = self.ui.findChild(QStackedWidget,"stackedWidget")

        self.btnHome = self.ui.findChild(QPushButton,"btnHome")
        self.btnCargarDatos=self.ui.findChild(QPushButton,"btnLoadData")
        self.btnAnalisis=self.ui.findChild(QPushButton,"BtnAnalisis")
        self.btnMovimientos=self.ui.findChild(QPushButton,"btnMovimientos")
        self.btnRecomendaciones=self.ui.findChild(QPushButton,"BtnRecomendaciones")
        self.btnInformes=self.ui.findChild(QPushButton,"BtnInformes")
        self.btnConfiguracion=self.ui.findChild(QPushButton,"BtnConfiguracion")
        self.btnMonitoreo=self.ui.findChild(QPushButton,"BtnMonitoreo")
        self.btnLogout = self.ui.findChild(QPushButton, "BtnCerrarSesion")
        #*Cargar tipografías
        # Manrope
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        # Source Sans 3
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        #*Verificar tipografías
        if font_id_manrope == -1:
            print("Advertencia: No se pudo cargar Manrope.")
        if font_id_source == -1:
            print("Advertencia: No se pudo cargar Source Sans 3.")
        #*Obtener familias reales
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
            estilos_tipografias = estilos_fuentes(source_family,manrope_family)
            self.ui.setStyleSheet(estilos_actuales + estilos_tipografias)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes.")
        #* Cargar páginas
        self.cargar_paginas()
        #* Conectar botones
        #cerrar sesion
        self.btnLogout.clicked.connect(self.cerrar_sesion)
        #manejar stackedWidget
        self.btnHome.clicked.connect(self.mostrar_home)
        self.btnCargarDatos.clicked.connect(self.mostar_cargar_datos)
        self.btnAnalisis.clicked.connect(self.mostrar_analisis)
        self.btnMovimientos.clicked.connect(self.mostrar_movimientos)
        self.btnRecomendaciones.clicked.connect(self.mostrar_recomendaciones)
        self.btnInformes.clicked.connect(self.mostrar_informes)
        self.btnConfiguracion.clicked.connect(self.mostrar_configuracion)
        self.btnMonitoreo.clicked.connect(self.mostrar_monitoreo)
        #Mostrar el home al iniciar
        self.mostrar_home()
        #*MOSTRAR VENTANA
        self.showMaximized()
    #*Función para cerrar sesión
    def cerrar_sesion(self):
        respuesta=QMessageBox.question(
            self,"Cerrar Sesión","¿Desea Salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
        else:
            return
    def cargar_paginas(self):
        self.dashboard_home = DashboardHome(self.userBusiness,self.home_dashboard_controller)
        self.stackedWidget.addWidget(self.dashboard_home)
        self.cargar_datos = None
        self.analisis = None
        self.movimientos = None
        self.recomendaciones = None
        self.informes = None
        self.monitoreo = None
        self.configuracion = None
    #*Mostrar Home
    def mostrar_home(self):
        self.stackedWidget.setCurrentWidget(self.dashboard_home)
    #*Mostrar Cargar Datos
    def mostar_cargar_datos(self):
        if self.cargar_datos is None:
            self.cargar_datos = CargarDatos(self.userBusiness)
            self.stackedWidget.addWidget(self.cargar_datos)
        self.stackedWidget.setCurrentWidget(self.cargar_datos)
    #*Mostrar Análisis
    def mostrar_analisis(self):
        if self.analisis is None:
            self.analisis = Analisis(self.userBusiness)
            self.stackedWidget.addWidget(self.analisis)
        self.stackedWidget.setCurrentWidget(self.analisis)
    #*Mostrar Movimientos
    def mostrar_movimientos(self):
        if self.movimientos is None:
            self.movimientos = Movimientos(self.userBusiness)
            self.stackedWidget.addWidget(self.movimientos)
        self.stackedWidget.setCurrentWidget(self.movimientos)
    #*Mostrar Recomendaciones
    def mostrar_recomendaciones(self):
        if self.recomendaciones is None:
            self.recomendaciones = Recomendaciones(self.userBusiness)
            self.stackedWidget.addWidget(self.recomendaciones)
        self.stackedWidget.setCurrentWidget(self.recomendaciones)
    #*Mostrar Informes
    def mostrar_informes(self):
        if self.informes is None:
            self.informes = Informes(self.userBusiness)
            self.stackedWidget.addWidget(self.informes)
        self.stackedWidget.setCurrentWidget(self.informes)
    #*Mostrar Configuración
    def mostrar_configuracion(self):
        if self.configuracion is None:
            self.configuracion = Configuracion(self.userBusiness)
            self.stackedWidget.addWidget(self.configuracion)
        self.stackedWidget.setCurrentWidget(self.configuracion)
    #*Mostrar Monitoreo
    def mostrar_monitoreo(self):
        if self.monitoreo is None:
            self.monitoreo = Monitoreo(self.userBusiness)
            self.stackedWidget.addWidget(self.monitoreo)
        self.stackedWidget.setCurrentWidget(self.monitoreo)