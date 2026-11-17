import logging
import os
from pathlib import Path
from tempfile import mkstemp
from PySide6.QtCore import QObject, Signal, Slot
from app.services.report_document_service import ReportDocumentService
logger = logging.getLogger(__name__)

class ReportWorker(QObject):
    finished = Signal(bool, str)
    def __init__(self, service: ReportDocumentService, request: dict, filename: str):
        super().__init__()
        self.service = service
        self.request = dict(request)
        self.filename = filename
    @Slot()
    def run(self):
        temp_path = None
        try:
            pdf = self.service.generate(self.request)
            destination = Path(self.filename)
            if not destination.parent.is_dir():
                raise ValueError("La carpeta de destino ya no está disponible.")
            fd, temp_name = mkstemp(prefix=".finanzen_", suffix=".pdf", dir=str(destination.parent))
            temp_path = Path(temp_name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(pdf)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, destination)
            self.finished.emit(True, str(destination))
        except (PermissionError, ValueError, OSError) as exc:
            logger.exception("No fue posible generar o guardar el informe")
            self.finished.emit(False, str(exc))
        except Exception:
            logger.exception("Error inesperado al generar el PDF")
            self.finished.emit(False, "Ocurrió un error al generar el informe. Consulta el registro de errores.")
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
