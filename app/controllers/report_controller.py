"""Orquestación de UI; la consulta y el renderizado quedan en ReportWorker."""
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox
from app.services.report_service import ReportService
from app.services.report_document_service import ReportDocumentService
from app.pdf_templates.pdf_generator import PdfGenerator
from app.workers.report_worker import ReportWorker


class ReportController(QObject):
    generation_started = Signal()
    generation_finished = Signal(bool, str)

    def __init__(self, report_service=None, pdf_generator=None, parent=None):
        super().__init__(parent)
        self.report_service = report_service or ReportService()
        self.pdf_generator = pdf_generator or PdfGenerator()
        self.document_service = ReportDocumentService(self.report_service, self.pdf_generator)
        self._thread = None
        self._worker = None
        self._dialog_parent = None

    @property
    def is_generating(self) -> bool:
        return self._thread is not None

    def generar_informe(self, datos: dict, parent=None) -> bool:
        if self.is_generating:
            QMessageBox.information(parent, "Informe en curso", "Ya se está generando un informe.")
            return False
        try:
            if datos.get("tipo_reporte") not in ReportService.REPORT_TYPES:
                raise ValueError("Selecciona un tipo de informe válido.")
            start, end = ReportService.obtener_rango_fechas(datos)
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(parent, "Datos inválidos", str(exc))
            return False

        filename = f"Finanzen_{datos['tipo_reporte']}_{start:%Y%m%d}_{end:%Y%m%d}.pdf"
        path, _ = QFileDialog.getSaveFileName(parent, "Guardar informe PDF", filename, "Documento PDF (*.pdf)")
        if not path:  # Cancelar no se considera error.
            return False
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        if not Path(path).parent.is_dir():
            QMessageBox.warning(parent, "Ubicación inválida", "La carpeta de destino no existe.")
            return False

        self._dialog_parent = parent
        self._thread = QThread(self)
        self._worker = ReportWorker(self.document_service, datos, path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.finished.connect(self._thread.deleteLater)
        self.generation_started.emit()
        self._thread.start()
        return True

    @Slot(bool, str)
    def _on_worker_finished(self, success: bool, message: str):
        self.generation_finished.emit(success, message)
        if success:
            QMessageBox.information(self._dialog_parent, "Informe generado", "El archivo PDF se guardó correctamente.")
        else:
            QMessageBox.warning(self._dialog_parent, "Informe no generado", message)

    @Slot()
    def _on_thread_finished(self):
        self._worker = None
        self._thread = None
        self._dialog_parent = None

    def shutdown(self):
        """Espera a la finalización en curso antes de destruir QThread al salir."""
        thread = self._thread
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait()
