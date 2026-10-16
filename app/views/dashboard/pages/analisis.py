import os
from PySide6.QtWidgets import QWidget,QVBoxLayout,QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal
from app.utils.visualizations.analysis_charts import AnalysisCharts

class Analisis(QWidget):
    def __init__(self, userBusiness,controller):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.controller=controller
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/analisis.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.lblIndicacion.hide()
        self.ocultar_card()
        self.charts = AnalysisCharts(
        frame_ingresos_gastos=self.ui.frameIngresosGastos,frame_distribucion=self.ui.frameDistribucion,
        frame_evolucion=self.ui.frameEvolucion,
        )
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
        #*Cambios en la interfaz
        self.ui.lblPersonalizar.hide()
        self.ui.contenedorFechas.hide()
        # Conectar el cambio de selección en los QComboBox para activar o desactivar la visibilidad
        self.ui.periodo.currentTextChanged.connect(self.mostrar_dateEdits)
        #* llenar los datos proveniente del controller
        self.actualizar_interfaz()
        self.ui.periodo.currentTextChanged.connect(self.actualizar_interfaz)
    def mostrar_dateEdits(self):
        es_personalizado=(self.ui.periodo.currentText()=="Personalizado")
        self.ui.lblPersonalizar.setVisible(es_personalizado)
        self.ui.contenedorFechas.setVisible(es_personalizado)
    def recolectar_datos(self):
        datos={}
        periodo = self.ui.periodo.currentText()
        datos["business_id"]=self.business.business_id
        datos["rol"]=self.userBusiness.role
        datos["periodo"]=periodo
        if periodo=="Personalizado":
            datos["rango_inicio"] = self.ui.rangoInicio.date().toPython()
            datos["rango_final"] = self.ui.rangoFinal.date().toPython()
        return datos
    def enviar_datos(self):
        datos=self.recolectar_datos()
        resultado=self.controller.analyze_period(datos)
        return resultado
    def llenar_datos_tarjetas(self,resultado):
        ingresos=resultado["comparisons"]["income"]
        gastos=resultado["comparisons"]["expenses"]
        balance=resultado["comparisons"]["balance"]
        estadisticas=resultado["sales_statistics"]
        #*Ingresos tarjeta
        self.ui.valorIngresos.setText(f"C${ingresos["current_value"]}")
        variacion_ing=self.comparar_periodo_anterior(ingresos["percentage_variation"])
        self.establecer_color_aumento(ingresos["direction"],self.ui.estadoIngresos)
        self.ui.estadoIngresos.setText(variacion_ing)
        #*Gastos tarjeta
        self.ui.valorGastos.setText(f"C${gastos["current_value"]}")
        variacion_gas=self.comparar_periodo_anterior(gastos["percentage_variation"])
        self.establecer_color_disminucion(ingresos["direction"],self.ui.estadoGastos)
        self.ui.estadoGastos.setText(variacion_gas)
        #*Balance tarjeta
        self.ui.valorBalance.setText(f"C${balance["current_value"]}")
        variacion_bal=self.comparar_periodo_anterior(balance["percentage_variation"])
        self.establecer_color_aumento(balance["direction"],self.ui.estadoBalance)
        self.ui.estadoBalance.setText(variacion_bal)
        #*Ticket Promedio
        if estadisticas["average_ticket"] is None:
            self.ui.frameTicket.hide()
            self.ui.valorTicket.setText("No hay datos suficientes para \ncalcular la media.")
        else:
            self.ui.valorTicket.setText(str(estadisticas["average_ticket"]))
        self.ui.valorTotalVentas.setText(str(estadisticas["total_sales"]))
        self.ui.valorGeneradoVentas.setText(str(estadisticas["total_amount"]))

    def hallazgos(self, resultado):
        hallazgos = resultado.get("findings", [])
        if not hallazgos:
            self.ui.lblIndicacion.show()
            #self.ui.gastosCategoriaCard.hide()
            return

        #*Hallazgos relacionados a gastos.
        # Categoría que representa el mayor porcentaje.
        hallazgo_gastos = next(
            (
                h for h in hallazgos
                if h.get("type") == "expense_category"
            ), None
        )
        if hallazgo_gastos:
            datos = hallazgo_gastos.get("data", {})
            categorias = datos.get("categories", [])
            categoria = categorias[0] if categorias else "Sin categoría"
            porcentaje = datos.get("percentage", 0)
            importe = datos.get("amount", 0)
            self.ui.gastosCategoriaCard.show()
            self.ui.gastosCategoria.setText(f"{hallazgo_gastos.get("title")}")
            self.ui.gastoCatDesc.setText(
                f"{categoria} es la categoría con mayor peso en la\n estructurade costos, con un importe\n de C$ {importe:,.2f}.")
            self.ui.gastosCatVar.setText(f"{porcentaje:.2f}% del total de gastos")
        # Variación de los gastos
        variacion_gastos = next(
            (
                h for h in hallazgos
                if h.get("type") == "expense_variation"
            ), None
        )
        if variacion_gastos:
            datos=variacion_gastos.get("data",{})
            porcentaje=datos.get("percentage_variation",0)
            direccion= "aumento" if datos["direction"]=="Aumento" else "descenso"
            if porcentaje is not None:
                self.ui.variacionGastosCard.show()
                self.ui.aumentoGasto.setText(variacion_gastos.get("title"))
                self.ui.descAumentoGasto.setText(
                    f"Los gastos totales del período actual registraron un {direccion}\n equivalente al {str(porcentaje)}%."
                )
                self.ui.varAumentoGasto.setText(f"{porcentaje}% vs Período Anterior")
                if direccion=="disminucion":
                    self.ui.variacionGastosCard.setProperty("carta","bueno")
        #*Hallazgos relacionados a ingresos
        #Categoria que representa el mayor porcentaje
        hallazgo_ingresos = next(
            (
                h for h in hallazgos
                if h.get("type") == "income_category"
            ), None
        )
        if hallazgo_ingresos:
            datos = hallazgo_ingresos.get("data", {})
            categorias = datos.get("categories", [])
            categoria = categorias[0] if categorias else "Sin categoría"
            porcentaje = datos.get("percentage", 0)
            importe = datos.get("amount", 0)
            self.ui.categoriaIngresosCard.show()
            self.ui.ingresosCategoria.setText(f"{hallazgo_ingresos.get("title")}")
            self.ui.ingresosCatDesc.setText(
                f"{categoria} es la categoría con mayor peso en la\n estructurade ingresos, con un importe\n de C$ {importe:,.2f}.")
            self.ui.ingresosCatVar.setText(f"{porcentaje:.2f}% del total de ingresos")
        #Variación de los ingresos
        variacion_ingresos = next(
            (
                h for h in hallazgos
                if h.get("type") == "income_variation"
            ), None
        )
        if variacion_ingresos:
            datos=variacion_ingresos.get("data",{})
            porcentaje=datos.get("percentage_variation",0)
            direccion= "aumento" if datos["direction"]=="Aumento" else "descenso"
            if porcentaje is not None:
                self.ui.variacionIngresosCard.show()
                self.ui.aumentoIngresos.setText(variacion_ingresos.get("title"))
                self.ui.aumentoDescIngresos.setText(
                    f"Los ingresos totales del período actual registraron un {direccion}\n equivalente al {str(porcentaje)}%."
                )
                self.ui.aumentoVarIngresos.setText(f"{porcentaje}% vs Período Anterior")
            if direccion=="aumento":
                self.ui.variacionIngresosCard.setProperty("carta","bueno")
        #*Hallazgos relacionados a las ventas
        #Mayor categoria
        hallazgo_ventas = next(
            (
                h for h in hallazgos
                if h.get("type") == "sales_category"
            ), None
        )
        if hallazgo_ventas:
            datos = hallazgo_ventas.get("data", {})
            categorias = datos.get("categories", [])
            categoria = categorias[0] if categorias else "Sin categoría"
            porcentaje = datos.get("percentage", 0)
            importe = datos.get("amount", 0)
            self.ui.categoriaVentasCard.show()
            self.ui.ventasCat.setText(f"{hallazgo_ventas.get("title")}")
            self.ui.ventasDesc.setText(
                f"{categoria} es la categoría más vendida \ncon un importe de C$ {importe:,.2f}.")
            self.ui.ventasVar.setText(f"{porcentaje:.2f}% del total de ventas")
        #variabilidad de las ventas
        variablilidad_ventas=next(
            (
                h for h in hallazgos
                if h.get("type")=="sales_variability"
            ),None
        )
        if variablilidad_ventas:
            datos=variablilidad_ventas.get("data",{})
            self.ui.variabilidadVentasCard.show()
            cv=str(datos.get("coefficient_variation"))
            self.ui.coefVarTitulo.setText(f"{variablilidad_ventas.get("title")}")
            self.ui.coefVarDesc.setText(
                f"Las ventas presentan una variabilidad del\n{cv}% con respecto a la media"
            )
            self.ui.variacionClasificacion.setText(f"Clasificación: {datos.get("classification")}")


    def actualizar_interfaz(self):
        resultado=self.enviar_datos()
        if not resultado["success"]:
            QMessageBox.warning(self,"Error al Cargar Datos",resultado["message"])
            return
        self.llenar_datos_tarjetas(resultado)
        self.charts.actualizar(resultado)
        self.hallazgos(resultado)
    def comparar_periodo_anterior(self,valor):
        if valor is None:
            return "No se puede establecer comparación\n con período anterior"
        return f"▲ {valor}% vs Período Anterior"
    def establecer_color_aumento(self,direccion,lbl):
        if direccion == "Aumento":
            lbl.setProperty("texto","Positivo")
        elif direccion=="Disminución":
            lbl.setProperty("texto","Negativo")
    def establecer_color_disminucion(self,direccion,lbl):
        if direccion == "Aumento":
            lbl.setProperty("texto","Negativo")
        elif direccion=="Disminución":
            lbl.setProperty("texto","Positivo")
    def ocultar_card(self):
        for card in (
            self.ui.gastosCategoriaCard,self.ui.variacionGastosCard,self.ui.categoriaIngresosCard,
            self.ui.variacionIngresosCard,self.ui.categoriaVentasCard,self.ui.variabilidadVentasCard
        ):
            card.hide()


