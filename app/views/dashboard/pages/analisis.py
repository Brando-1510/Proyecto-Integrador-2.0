import os
from datetime import date
from PySide6.QtCore import Qt, QDate, QTimer, QThreadPool, QSignalBlocker, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.utils.visualizations.analysis_charts import AnalysisCharts
from app.utils.format_utils import FormatUtils
from app.workers.analysis_worker import AnalysisWorker

class Analisis(QWidget):
    FINDING_CARDS = {
        "expense_category": "gastosCategoriaCard",
        "expense_variation": "variacionGastosCard",
        "income_category": "categoriaIngresosCard",
        "income_variation": "variacionIngresosCard",
        "sales_category": "categoriaVentasCard",
        "sales_variability": "variabilidadVentasCard",
    }
    def __init__(self, userBusiness, controller):
        super().__init__()
        self.userBusiness = userBusiness
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.controller = controller
        path = os.path.normpath(
            os.path.join(os.path.dirname(__file__),"../../../ui/dashboard/pages/analisis.ui")
        )
        self.ui = QUiLoader().load(path, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar la interfaz de Análisis: {path}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.charts = AnalysisCharts(self.ui.frameIngresosGastos, self.ui.frameDistribucion,self.ui.frameEvolucion)
        self._load_fonts()
        self._pool = QThreadPool.globalInstance()
        self._running = False
        self._pending = False
        self._active_worker = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(260)
        self._timer.timeout.connect(self.actualizar_interfaz)
        self.ui.lblPersonalizar.hide()
        self.ui.contenedorFechas.hide()
        self.ui.lblIndicacion.hide()
        self.ocultar_card()
        today = QDate.currentDate()
        with QSignalBlocker(self.ui.rangoInicio), QSignalBlocker(self.ui.rangoFinal):
            self.ui.rangoInicio.setCalendarPopup(True)
            self.ui.rangoFinal.setCalendarPopup(True)
            self.ui.rangoInicio.setMaximumDate(today)
            self.ui.rangoFinal.setMaximumDate(today)
            self.ui.rangoInicio.setDate(QDate(today.year(), today.month(), 1))
            self.ui.rangoFinal.setDate(today)
        self.ui.periodo.currentTextChanged.connect(self._on_period_changed)
        self.ui.rangoInicio.dateChanged.connect(self._on_date_changed)
        self.ui.rangoFinal.dateChanged.connect(self._on_date_changed)
        self.actualizar_interfaz()

    def _load_fonts(self):
        font1 = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        font2 = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if font1 >= 0 and font2 >= 0:
            a = QFontDatabase.applicationFontFamilies(font1)
            b = QFontDatabase.applicationFontFamilies(font2)
            if a and b:
                self.ui.setStyleSheet(self.ui.styleSheet() + estilos_fuentes(b[0], a[0]))

    def _on_period_changed(self, *_):
        custom = self.ui.periodo.currentText() == "Personalizado"
        self.ui.lblPersonalizar.setVisible(custom)
        self.ui.contenedorFechas.setVisible(custom)
        self._timer.start()

    def _on_date_changed(self, *_):
        if self.ui.periodo.currentText() == "Personalizado":
            self._timer.start()

    def recolectar_datos(self):
        data = {"business_id": self.business.business_id, "user_id": self.user.user_id,
                "periodo": self.ui.periodo.currentText()}
        if data["periodo"] == "Personalizado":
            data["rango_inicio"] = self.ui.rangoInicio.date().toPython()
            data["rango_final"] = self.ui.rangoFinal.date().toPython()
        return data

    def actualizar_interfaz(self, *_):
        self._timer.stop()
        if self._running:
            self._pending = True
            return
        self._start_request()

    def _start_request(self):
        self._running = True
        self._pending = False
        self.ui.lblIndicacion.setText("Analizando datos...")
        self.ui.lblIndicacion.show()
        self._query_in_progress = self.recolectar_datos()
        worker = AnalysisWorker(self.controller, self._query_in_progress)
        self._active_worker = worker
        worker.signals.finished.connect(self._on_finished)
        self._pool.start(worker)

    @Slot(object)
    def _on_finished(self, result):
        self._running = False
        self._active_worker = None
        if self._pending or self.recolectar_datos() != self._query_in_progress:
            self._timer.stop()
            self._start_request()
            return
        is_success = isinstance(result, dict) and bool(result.get("success"))
        self._clear_state(clear_charts=not is_success)
        if not is_success:
            message = result.get("message", "Ocurrió un error al analizar los datos") if isinstance(result, dict) else "Respuesta inválida"
            self.ui.lblIndicacion.setText(message)
            QMessageBox.warning(self.ui, "Error al cargar Análisis", message)
            return
        self.llenar_datos_tarjetas(result)
        self.charts.actualizar(result)
        self.hallazgos(result)
        if not result.get("has_data"):
            self.ui.lblIndicacion.setText("No hay registros financieros para el período seleccionado.")
            self.ui.lblIndicacion.show()
        elif result.get("findings"):
            self.ui.lblIndicacion.hide()
        else:
            self.ui.lblIndicacion.setText("Sin hallazgos relevantes en este período.")
            self.ui.lblIndicacion.show()

    def _clear_state(self, clear_charts=False):
        self.ocultar_card()
        self.ui.lblIndicacion.hide()
        self.ui.frameTicket.show()
        for name in ("valorIngresos", "valorGastos", "valorBalance", "valorTicket", "valorTotalVentas", "valorGeneradoVentas"):
            getattr(self.ui, name).setText("—")
        for name in ("estadoIngresos", "estadoGastos", "estadoBalance"):
            label = getattr(self.ui, name)
            label.clear()
            self._set_property(label, "texto", "Neutro")
        if clear_charts:
            self.charts.mostrar_vacio()

    @staticmethod
    def _set_property(widget, name, value):
        widget.setProperty(name, value)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    @staticmethod
    def obtener_tono_hallazgo(tipo: str, datos: dict) -> str:
        if tipo in (
            "expense_category",
            "income_category",
            "sales_category"
        ):
            return "neutro"
        if tipo == "expense_variation":
            variacion = datos["absolute_variation"]
            if variacion < 0:
                return "bueno"
            if variacion > 0:
                return "atencion"
            return "neutro"
        if tipo == "income_variation":
            variacion = datos["absolute_variation"]
            if variacion > 0:
                return "bueno"
            if variacion < 0:
                return "atencion"
            return "neutro"
        if tipo == "sales_variability":
            return (
                "considerar"
                if datos.get("classification") == "Variabilidad Alta"
                else "neutro"
            )
        return "neutro"

    @staticmethod
    def _compare_text(comp):
        percentage = comp["percentage_variation"]
        absolute = comp["absolute_variation"]
        if absolute == 0:
            return "Sin cambio vs período anterior"
        symbol = "▲" if absolute > 0 else "▼"
        if percentage is None:
            return f"{symbol} C$ {abs(absolute):,.2f} vs período anterior"
        return f"{symbol} {abs(percentage):.2f}% vs período anterior"

    def _style_comparison(self, name, comparison, expense=False):
        label = getattr(self.ui, name)
        direction = comparison["direction"]
        if direction in ("Sin cambio",):
            status = "Neutro"
        elif expense:
            status = "Negativo" if direction == "Aumento" else "Positivo"
        else:
            status = "Positivo" if direction in ("Aumento", "Mejora") else "Negativo"
        self._set_property(label, "texto", status)
        label.setText(self._compare_text(comparison))

    def llenar_datos_tarjetas(self, result):
        comps = result["comparisons"]
        stats = result["sales_statistics"]
        for key, label in (("income", "valorIngresos"), ("expenses", "valorGastos"), ("balance", "valorBalance")):
            getattr(self.ui, label).setText(FormatUtils.format_currency(comps[key]["current_value"]))
        self._style_comparison("estadoIngresos", comps["income"])
        self._style_comparison("estadoGastos", comps["expenses"], expense=True)
        self._style_comparison("estadoBalance", comps["balance"])
        self.ui.valorTicket.setText("Sin ventas" if stats["average_ticket"] is None
                            else FormatUtils.format_currency(stats["average_ticket"]))
        self.ui.valorTotalVentas.setText(str(stats["total_sales"]))
        self.ui.valorGeneradoVentas.setText(FormatUtils.format_currency(stats["total_amount"]))

    def hallazgos(self, result):
        for finding in result.get("findings", []):
            kind = finding.get("type")
            if kind not in self.FINDING_CARDS:
                continue
            card = getattr(self.ui, self.FINDING_CARDS[kind])
            info = finding.get("data", {})
            tono = self.obtener_tono_hallazgo(kind, info)
            self._set_property(card, "carta", tono)
            title = finding.get("title", "")
            description = finding.get("description", "")
            percentage = info.get("percentage")
            variation = info.get("percentage_variation")
            if kind == "expense_category":
                self.ui.gastosCategoria.setText(title)
                self.ui.gastoCatDesc.setText(description)
                self.ui.gastosCatVar.setText(f"{percentage:.2f}% del total de gastos")
            elif kind == "income_category":
                self.ui.ingresosCategoria.setText(title)
                self.ui.ingresosCatDesc.setText(description)
                self.ui.ingresosCatVar.setText(f"{percentage:.2f}% del total de ingresos")
            elif kind == "sales_category":
                self.ui.ventasCat.setText(title)
                self.ui.ventasDesc.setText(description)
                self.ui.ventasVar.setText(f"{percentage:.2f}% del total de ventas")
            elif kind == "expense_variation":
                self.ui.aumentoGasto.setText(title)
                self.ui.descAumentoGasto.setText(description)
                self.ui.varAumentoGasto.setText("Variación porcentual no disponible" if variation is None
                                            else f"{variation:+.2f}% vs período anterior")
            elif kind == "income_variation":
                self.ui.aumentoIngresos.setText(title)
                self.ui.aumentoDescIngresos.setText(description)
                self.ui.aumentoVarIngresos.setText("Variación porcentual no disponible" if variation is None
                                                else f"{variation:+.2f}% vs período anterior")
            elif kind == "sales_variability":
                self.ui.coefVarTitulo.setText(title)
                self.ui.coefVarDesc.setText(description)
                self.ui.variacionClasificacion.setText(f"Clasificación: {info.get('classification') or 'No determinada'}")
            card.show()

    def ocultar_card(self):
        for name in self.FINDING_CARDS.values():
            getattr(self.ui, name).hide()
