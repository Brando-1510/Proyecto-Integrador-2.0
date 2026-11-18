from PySide6.QtCore import QObject, QRunnable, Signal, Slot

class AnalysisWorkerSignals(QObject):
    finished = Signal(object)
class AnalysisWorker(QRunnable):
    def __init__(self, controller, data: dict):
        super().__init__()
        self.controller = controller
        self.data = dict(data)
        self.signals = AnalysisWorkerSignals()
    @Slot()
    def run(self):
        try:
            result = self.controller.analyze_period(self.data)
        except Exception:
            result = {"success": False, "message": "No se pudo completar el análisis."}
        self.signals.finished.emit(result)
