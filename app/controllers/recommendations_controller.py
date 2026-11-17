from app.services.aiRecommendation_service import AIRecommendationService
from app.workers.ai_worker import AIWorker

class RecomendacionesController:
    LABELS = {
        "General": "lblTodas",
        "Ventas": "lblVentas",
        "Gastos": "lblGasto",
        "Ingresos": "lblIngreso"
    }
    STATUS_MESSAGES = {
        "analysis": "Generando el análisis con IA...",
        "assistant": "El asistente está preparando una respuesta..."
    }
    CANCELLED_MESSAGE = "La generación fue cancelada."
    def __init__(self, view, service=None):
        self.view = view
        self.service = service or AIRecommendationService()
        self.worker = None
        self.active_request = None
        self.cancel_requested = False
        self.view.solicitud_ia.connect(self.procesar_solicitud)
        self.view.ui.cancelar.clicked.connect(self.cancelar_solicitud)
        self.view.ui.cancelar.hide()
        self.active_result_label = None

    def procesar_solicitud(self, operation: str, datos: dict):
        if self.worker is not None:
            return
        if operation not in ("analysis", "assistant"):
            return
        self.cancel_requested = False

        self.active_request = {
            "operation": operation,
            "datos": dict(datos)
        }
        self.active_result_label = self._get_result_label()
        self.active_result_label.setMarkdown(self.STATUS_MESSAGES[operation])
        self.view.actualizar_estado_botones(True)
        self.view.ui.cancelar.show()
        self.worker = AIWorker(
            service=self.service,
            datos=datos,
            operation=operation,
            parent=self.view
        )
        self.worker.result_ready.connect(self.mostrar_resultado)
        self.worker.error_occurred.connect(self.mostrar_error)
        self.worker.finished.connect(self._finalizar_worker)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def _get_result_label(self):
        request = self.active_request
        operation = request["operation"]
        if operation == "assistant":
            return self.view.ui.lblAgente
        analysis_type = request["datos"]["analysis_type"]
        widget_name = self.LABELS[analysis_type]
        return getattr(self.view.ui, widget_name)

    def mostrar_resultado(self, response: str):
        if self.cancel_requested:
            return
        text_browser = self._get_result_label()
        text_browser.setMarkdown(response)

    def mostrar_error(self, error: str):
        if self.cancel_requested:
            return
        text_browser = self._get_result_label()
        text_browser.setMarkdown(f"**No se pudo generar el análisis.**\n\n{error}")

    def cancelar_solicitud(self):
        if self.worker is None or not self.worker.isRunning():
            return
        self.cancel_requested = True
        self.active_result_label.setMarkdown(self.CANCELLED_MESSAGE)
        self.worker.cancelar()
        self.view.ui.cancelar.hide()

    def _finalizar_worker(self):
        self.view.actualizar_estado_botones(False)
        self.view.ui.cancelar.hide()
        self.worker = None
        self.active_request = None
        self.active_result_label = None
        self.cancel_requested = False
