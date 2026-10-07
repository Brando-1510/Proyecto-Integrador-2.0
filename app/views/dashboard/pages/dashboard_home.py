import os
from app.views.dashboard.table_models.movements_model import MovementsTableModel
from app.views.dashboard.table_models.sales_model import SalesTableModel
from PySide6.QtWidgets import QWidget,QHeaderView,QVBoxLayout,QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.utils.utilsUI import obtener_icono
from PySide6.QtCore import Qt,Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardHome(QWidget):
    def __init__(self, userBusiness,home_dashboard_controller):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.home_dashboard_controller=home_dashboard_controller
        self.resultado=home_dashboard_controller.datos_dashboard(self.business.business_id)
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        if layout:
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
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
        self.ui.ventasTable.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.ui.movimientosTable.setSizePolicy(
                QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed
            )
        self.ui.ventasTable.setMinimumHeight(400)
        self.ui.movimientosTable.setMinimumHeight(400)
        #relacionados al controller
        self.configurar_grafica()
        self.cambios_ui_controller()
        self.mostrar_evolucion_ventas()
    def cambios_ui_controller(self):
        self.ui.lblVentasValor.setText(f"C${str(self.resultado["ventas"])}")
        self.ui.lblGastosValor.setText(f"C${str(self.resultado["gastos"])}")
        self.ui.lblIngresosValor.setText(f"C${str(self.resultado["ingresos"])}")
        self.ui.lblUtilidadValor.setText(f"C${str(self.resultado["utilidad"])}")
        for lbl in (
            self.ui.lblVentasPeriodo,self.ui.lblGastosPeriodo,self.ui.lblIngresosPeriodo,
            self.ui.lblUtilidadPeriodo
        ):
            lbl.setText(self.resultado["rango_fecha"])
        self.movements_model.set_data(self.resultado["movimientos_recientes"])
        self.sales_model.set_data(self.resultado["ventas_recientes"])
    #Metodos para crear la gráfica
    def configurar_grafica(self):
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ui.frameGraficoVentas.layout().addWidget(self.canvas)
        self.ui.frameGraficoVentas.setSizePolicy(
        QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed
        )
        self.ui.frameGraficoVentas.setMinimumHeight(400)
    def mostrar_evolucion_ventas(self):
        evolucion = self.resultado["evolucion_ventas"]
        fechas = [fecha for fecha, total in evolucion]
        ventas = [float(total) for fecha, total in evolucion]
        self.ax.clear()
        #Configurar transparencia de fondo en el gráfico y la figura
        self.figure.patch.set_facecolor("none")
        self.ax.set_facecolor("none")
        #Dibujar la línea de ventas usando el color Primario del QSS (#5D38BB)
        self.ax.plot(
            fechas,
            ventas,
            color="#5D38BB",
            marker="o",
            markersize=6,
            markerfacecolor="#5D38BB",
            markeredgecolor="#F7F7F7",
            markeredgewidth=1.5,
            linewidth=2.5,
        )
        self.ax.set_title(
            f"Desempeño de Ventas de {self.business.business_name}",
            color="#0E042F",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        self.ax.set_xlabel("Fecha", color="#46315c", fontsize=10, labelpad=8)
        self.ax.set_ylabel("Ventas", color="#46315c", fontsize=10, labelpad=8)
        self.ax.tick_params(colors="#0E042F", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#A193CC")
            spine.set_alpha(0.5)
        #Rejilla estilizada suave
        self.ax.grid(True, linestyle="--", alpha=0.3, color="#A193CC")
        #Formato y renderizado
        self.figure.autofmt_xdate()
        self.figure.tight_layout()
        self.canvas.draw()